"""
Description: 
This CDK code is used to provision resources
to AWS. It will provision resources to 
run ECS orchestration using Step Functions
and an EventBridge Scheduler

Running w/ 4 CPU and 30 GB mem to accomodate RMD creation

@author: atediarjo@gmail.com
@reviewer: joe@databrew.cc
@createdOn: October, 25th 2022
"""
import os
import aws_cdk as cdk
from aws_cdk import (
    Duration,
    Stack,
    aws_ec2 as ec2, aws_ecs as ecs,
    aws_ecs_patterns as ecs_patterns,
    aws_applicationautoscaling as appscaling,
    aws_iam as iam,
    aws_stepfunctions_tasks as tasks,
    aws_stepfunctions as sfn,
    aws_events as events,
    aws_events_targets as targets,
    Fn
)
from constructs import Construct


class ReportingStack(Stack):

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
            assumed_by=iam.ServicePrincipal("ecs-tasks.amazonaws.com"),
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
                    "athena:*",
                    "glue:*"
                ]))
        
        statement_athena = iam.PolicyStatement(
            actions=[
                "athena:GetQueryExecution",
                "athena:StartQueryExecution",
                "athena:GetQueryResults",
                "s3:*"
            ],
            resources=[
                f'arn:aws:athena:us-east-1:{self.account}:workgroup/primary'
            ],
        )

        statement_glue = iam.PolicyStatement(
            actions=["glue:GetTable", "glue:GetPartitions"],
            resources=["*"],
        )



        #######################################
        # get docker prod/dev versioning
        #######################################
        docker_version = os.getenv("PIPELINE_STAGE")


        #######################################
        # Step 3a: Placeholder Create Reporting Pipeline
        #######################################
        # create task definition: task definition is the 
        # set of guidelines being used for ECS to run Docker container
        # what role you want to use and what is the name use in the console
        task_definition = ecs.FargateTaskDefinition(
            self,
            "pipeline-reporting-task-definition",
            execution_role=ecs_role,
            task_role=ecs_role,
            family='pipeline-reporting',
            memory_limit_mib= 61440,
            cpu=8192
        )

        # this is the dockerhub image that points to dockerhub
        dockerhub_image = f'databrewllc/pipeline-reporting:{docker_version}'

        # attach the container to the task definition
        container_definition = task_definition.add_container(
            "pipeline-reporting-container",
            image=ecs.ContainerImage.from_registry(dockerhub_image),
            logging=ecs.LogDriver.aws_logs(stream_prefix="kenya-logs"),
            memory_limit_mib= 61440,
            cpu=8192
        )

        task_definition.add_to_task_role_policy(statement_athena)
        task_definition.add_to_task_role_policy(statement_glue)

        # ento pipeline dump
        reporting_pipeline = tasks.EcsRunTask(    
            self, "ReportingJob",
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

        # reporting parallels
        reporting_fail_trigger = sfn.Fail(self, "Notify Failure in reporting!")

        reporting_pipeline.add_catch(reporting_fail_trigger)

        parallel = (reporting_pipeline).next(success_trigger)

        parallel.add_retry(
            max_attempts=3,
            interval=Duration.seconds(10),
        )

        # consolidate into state machines
        state_machine = sfn.StateMachine(
            self, "ReportingPipeline",
            definition = parallel)
        
        #######################################
        # Eventbridge
        #######################################

        if (os.getenv('PIPELINE_STAGE') == 'production'):
            # add event rule to run data pipeline for work time at EAT
            schedule = events.Rule(
                self, "ReportingPipelineTriggerWorkHoursSchedule",
                schedule=events.Schedule.rate(cdk.Duration.hours(12)),
                targets=[targets.SfnStateMachine(state_machine)]
            )

        cdk.CfnOutput(self, 
                      'ReportingStepFunction', 
                      value=state_machine.state_machine_arn,
                      export_name='report:arn')