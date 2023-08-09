"""
Description: 
This CDK stack is used for mini-batch extraction in ODK

@author: atediarjo@gmail.com
@reviewer: joe@databrew.cc
@createdOn: October, 25th 2022
"""
import os
import aws_cdk as cdk
from aws_cdk import (
    # Duration,
    Stack,
    aws_ec2 as ec2, aws_ecs as ecs,
    aws_ecs_patterns as ecs_patterns,
    aws_applicationautoscaling as appscaling,
    aws_iam as iam,
    aws_stepfunctions_tasks as tasks,
    aws_stepfunctions as sfn,
    aws_events as events,
    aws_events_targets as targets
)
from constructs import Construct

class OdkBatchStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, env = None, cluster = None) -> None:
        super().__init__(scope, construct_id, env = env)
        environment_variables = [
                        tasks.TaskEnvironmentVariable(
                            name="BUCKET_PREFIX", 
                            value=os.getenv('BUCKET_PREFIX')),
                        tasks.TaskEnvironmentVariable(
                            name="ODK_CREDENTIALS_SECRETS_NAME", 
                            value=os.getenv("ODK_CREDENTIALS_SECRETS_NAME")),
                        tasks.TaskEnvironmentVariable(
                            name="PIPELINE_STAGE", 
                            value=os.getenv('PIPELINE_STAGE')),
                        tasks.TaskEnvironmentVariable(
                            name="ODK_SERVER_ENDPOINT", 
                            value=os.getenv('ODK_SERVER_ENDPOINT')),
                        tasks.TaskEnvironmentVariable(
                            name="CF_DISTRIBUTION_ID", 
                            value=cdk.Fn.import_value('cf-distribution-id')),
                    ]
        
        #######################################
        # Create ECS Role
        #######################################
        # create execution role: role is what your ECS will assume
        ecs_role = iam.Role(
            self, "createExecRole",
            assumed_by=iam.ServicePrincipal("ecs-tasks.amazonaws.com")
     )

        # each role has a policy attached to it
        ecs_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                resources=["*"],
                actions=[
                    "ecr:GetAuthorizationToken",
                    "ecr:BatchCheckLayerAvailability",
                    "ecr:GetDownloadUrlForLayer",
                    "ecr:BatchGetImage",
                    "logs:CreateLogStream",
                    "logs:PutLogEvents",
                    "cloudfront:CreateInvalidation",
                    "s3:*",
                    "secretsmanager:*",
                ]))
        
        #######################################
        # get docker prod/dev versioning
        #######################################
        docker_version = os.getenv("PIPELINE_STAGE")

        #######################################
        # Step 1: Create Form extraction
        #######################################

        # create task definition: task definition is the 
        # set of guidelines being used for ECS to run Docker container
        # what role you want to use and what is the name use in the console
        task_definition = ecs.FargateTaskDefinition(
            self,
            "create-form-extraction-task-definition",
            execution_role=ecs_role,
            task_role=ecs_role,
            family='odk-form-extraction',  
        )

        # this is the dockerhub image that points to dockerhub
        dockerhub_image = f'databrewllc/odk-form-extraction:{docker_version}'

        # attach the container to the task definition
        container_definition = task_definition.add_container(
            "task-extraction",
            image=ecs.ContainerImage.from_registry(dockerhub_image),
            logging=ecs.LogDriver.aws_logs(stream_prefix="kenya-logs")
        )

        # placeholder runner of the ecs task
        # on when the ecs is being executed
        # gives information on which cluster to run,
        # what is the task definition, container to use, bucket prefix
        # where to fetch the odk credentials in AWS
        form_extraction = tasks.EcsRunTask(    
            self, "ODKFormExtractionJob",
            integration_pattern=sfn.IntegrationPattern.RUN_JOB,
            cluster=cluster,
            task_definition=task_definition,
            assign_public_ip=True,
            container_overrides=[
                tasks.ContainerOverride(
                    container_definition=container_definition,
                    environment= environment_variables
            )],
            launch_target=tasks.EcsFargateLaunchTarget(platform_version=ecs.FargatePlatformVersion.LATEST)
        )

        #######################################
        # Step Functions
        #######################################

        # success object
        success_trigger = sfn.Succeed(self, "Don't worry be happy")

        # extract and clean
        extract_odk_pipeline = form_extraction
        extract_odk_fail_trigger = sfn.Fail(self, "Notify Failure in extract and cleaning!")
        
        extract_clean_parallel = sfn.Parallel(
            self, 
            'Extract and Clean',
        )
        extract_clean_parallel.branch(extract_odk_pipeline)
        extract_clean_parallel.add_catch(extract_odk_fail_trigger)

        

        parallel = extract_clean_parallel.next(success_trigger)

        # consolidate into state machines
        state_machine = sfn.StateMachine(
            self, "ODKBatch",
            definition = parallel)
        
        #######################################
        # Eventbridge
        #######################################
        # create scheduler if it is production
        if (os.getenv('PIPELINE_STAGE') == 'production'):
                    # add event rule to run data pipeline for work time at EAT
            update_schedule = events.Rule(
                self, "ODKBatchRefreshRate",
                schedule=events.Schedule.expression("rate(10 minutes)"),
                targets=[targets.SfnStateMachine(state_machine)]
            )

        cdk.CfnOutput(self, "StepFunctionName", value=state_machine.state_machine_arn)