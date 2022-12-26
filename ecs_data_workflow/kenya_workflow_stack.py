"""
Description: 
This CDK code is used to provision resources
to AWS. It will provision resources to 
run ECS orchestration using Step Functions
and an EventBridge Scheduler

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


class KenyaWorkflowStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, env = None, cluster = None) -> None:
        super().__init__(scope, construct_id, env = env)

        #######################################
        # Create ECS Role
        #######################################
        # create execution role
        ecs_role = iam.Role(
            self, "createExecRole",
            assumed_by=iam.ServicePrincipal("ecs-tasks.amazonaws.com"),
            role_name="databrew-ecs-workflow-role")

        # add to policy
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
                    "s3:*",
                    "secretsmanager:*"
                ]))


        #######################################
        # get docker prod/dev versioning
        #######################################
        docker_version = os.getenv("DOCKER_VERSION")

        #######################################
        # create form extraction
        #######################################
        task_definition = ecs.FargateTaskDefinition(
            self,
            "create-form-extraction-task-definition",
            execution_role=ecs_role,
            task_role=ecs_role,
            family='odk-form-extraction'
        )

        dockerhub_image = f'databrewllc/odk-form-extraction:{docker_version}'

        # Add container to task definition
        container_definition = task_definition.add_container(
            "task-extraction",
            image=ecs.ContainerImage.from_registry(dockerhub_image),
            logging=ecs.LogDriver.aws_logs(stream_prefix="kenya-logs")
        )

        form_extraction = tasks.EcsRunTask(    
            self, "FormExtraction",
            integration_pattern=sfn.IntegrationPattern.RUN_JOB,
            cluster=cluster,
            task_definition=task_definition,
            assign_public_ip=True,
            container_overrides=[
                tasks.ContainerOverride(
                    container_definition=container_definition,
                    environment=[
                        tasks.TaskEnvironmentVariable(
                            name="BUCKET_PREFIX", 
                            value=os.getenv('BUCKET_PREFIX')),
                        tasks.TaskEnvironmentVariable(
                            name="ODK_CREDENTIALS_SECRETS_NAME", 
                            value=os.getenv("ODK_CREDENTIALS_SECRETS_NAME"))]
            )],
            launch_target=tasks.EcsFargateLaunchTarget(platform_version=ecs.FargatePlatformVersion.LATEST)
        )

        #######################################
        # create anomaly detection
        #######################################
        task_definition = ecs.FargateTaskDefinition(
            self,
            "create-anomaly-detection-task-definition",
            execution_role=ecs_role,
            task_role=ecs_role,
            family='anomaly-detection'
        )

        dockerhub_image = f'databrewllc/anomaly-detection:{docker_version}'

        # Add container to task definition
        container_definition = task_definition.add_container(
            "task-anomaly-detection",
            image=ecs.ContainerImage.from_registry(dockerhub_image),
            logging=ecs.LogDriver.aws_logs(stream_prefix="kenya-logs")
        )

        anomaly_detection = tasks.EcsRunTask(    
            self, "AnomalyDetection",
            integration_pattern=sfn.IntegrationPattern.RUN_JOB,
            cluster=cluster,
            task_definition=task_definition,
            assign_public_ip=True,
            container_overrides=[
                tasks.ContainerOverride(
                    container_definition=container_definition,
                    environment=[
                        tasks.TaskEnvironmentVariable(
                            name="BUCKET_PREFIX", 
                            value=os.getenv('BUCKET_PREFIX')),
                        tasks.TaskEnvironmentVariable(
                            name="ODK_CREDENTIALS_SECRETS_NAME", 
                            value=os.getenv("ODK_CREDENTIALS_SECRETS_NAME"))]
            )],
            launch_target=tasks.EcsFargateLaunchTarget(platform_version=ecs.FargatePlatformVersion.LATEST)
        )


        #######################################
        # consolidate into step functions
        #######################################
        # successful step
        pipeline_success = sfn.Succeed(self, "Success")

        # consolidate ecs into step function
        state_machine = sfn.StateMachine(
            self, "KenyaDataPipeline",
            definition = form_extraction.next(anomaly_detection).next(pipeline_success))

        # add event rule to run data pipeline for work time at EAT
        hourly_schedule = events.Rule(
            self, "KenyaDataPipelineTriggerWorkHoursSchedule",
            schedule=events.Schedule.expression("cron(00 5-14 * * ? *)"),
            targets=[targets.SfnStateMachine(state_machine)]
        )

        # add event rule to run at midnight EAT timezone
        midnight_schedule = events.Rule(
            self, "KenyaDataPipelineTriggerMidnightSchedule",
            schedule=events.Schedule.expression("cron(00 21 * * ? *)"),
            targets=[targets.SfnStateMachine(state_machine)]
        )