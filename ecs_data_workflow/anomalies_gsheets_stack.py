"""
Description: 
This CDK stack is used for updating anomalies gsheets
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

class AnomaliesGsheetsStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, env = None, cluster = None) -> None:
        super().__init__(scope, construct_id, env = env)

        if(os.getenv('PIPELINE_STAGE')) == 'develop':
            BUCKET_NAME='databrew-testing-bohemia-lake-db'
            SECRET_ID='dev/gsheetskey'
        else:
            BUCKET_NAME='bohemia-lake-db'
            SECRET_ID='prod/gsheetskey'

        environment_variables = [
                        tasks.TaskEnvironmentVariable(
                            name="BUCKET_NAME", 
                            value=BUCKET_NAME),
                        tasks.TaskEnvironmentVariable(
                            name="GOOGLE_API_SECRET_ID", 
                            value=SECRET_ID),
                        tasks.TaskEnvironmentVariable(
                            name="PIPELINE_STAGE", 
                            value=os.getenv('PIPELINE_STAGE'))
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
        # Step 1: Pipeline Gsheets
        #######################################

        # create task definition: task definition is the 
        # set of guidelines being used for ECS to run Docker container
        # what role you want to use and what is the name use in the console
        task_definition = ecs.FargateTaskDefinition(
            self,
            "create-anomalies-gsheets-task-definition",
            execution_role=ecs_role,
            task_role=ecs_role,
            family='anomalies-gsheets-pipeline',  
        )

        # this is the dockerhub image that points to dockerhub
        dockerhub_image = f'databrewllc/pipeline-gsheets:{docker_version}'

        # attach the container to the task definition
        container_definition = task_definition.add_container(
            "pipeline-gsheets",
            image=ecs.ContainerImage.from_registry(dockerhub_image),
            logging=ecs.LogDriver.aws_logs(stream_prefix="kenya-logs")
        )

        # placeholder runner of the ecs task
        # on when the ecs is being executed
        # gives information on which cluster to run,
        # what is the task definition, container to use, bucket prefix
        pipeline_gsheets = tasks.EcsRunTask(    
            self, "PipelineGsheetsJob",
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
        success_trigger = sfn.Succeed(self, "Anomalies GSheets Pull Success")
        fail_trigger = sfn.Fail(self, "Notify Failure in Anomalies Gsheets Update!")
        pipeline_gsheets.next(success_trigger)
        pipeline_gsheets.add_catch(fail_trigger)

        # consolidate into state machines
        state_machine = sfn.StateMachine(
            self, "PipelineGsheets",
            definition = pipeline_gsheets)
        
        #######################################
        # Eventbridge
        #######################################
        # create scheduler if it is production
        if (os.getenv('PIPELINE_STAGE') == 'production'):
            # add event rule to run at midnight EAT timezone
            midnight_schedule = events.Rule(
                self, "ReportingPipelineTriggerMidnightSchedule",
                schedule=events.Schedule.expression("cron(00 21 * * ? *)"),
                targets=[targets.SfnStateMachine(state_machine)]
            )


        cdk.CfnOutput(self, 'PipelineGsheetsStepFunction', 
                      value=state_machine.state_machine_arn,
                      export_name='pipeline-gsheets:arn')