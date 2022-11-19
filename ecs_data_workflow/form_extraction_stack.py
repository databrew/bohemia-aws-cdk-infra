import os
from constructs import Construct
from aws_cdk import (
    # Duration,
    Stack,
    aws_ec2 as ec2, aws_ecs as ecs,
    aws_ecs_patterns as ecs_patterns,
    aws_applicationautoscaling as appscaling,
    aws_iam as iam,
    aws_stepfunctions_tasks as tasks,
    aws_stepfunctions as sfn
)
class FormExtractionStack(Construct):

    def __init__(
        self, 
        scope: Construct, 
        id: str, *, 
        cluster=None, 
        ecs_role=None):

        super().__init__(scope, id)
        # direct dockerhub_image
        dockerhub_image = 'databrewllc/odk-form-extraction'
        # add task definition
        task_definition = ecs.FargateTaskDefinition(
            self,
            "create-task-definition",
            execution_role=ecs_role,
            task_role=ecs_role,
            family='odk-form-extraction'
        )

        # Add container to task definition
        container_definition = task_definition.add_container(
            "task-extraction",
            image=ecs.ContainerImage.from_registry(dockerhub_image),
            logging=ecs.LogDrivers.aws_logs(stream_prefix="databrew-wf")
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
            launch_target=tasks.EcsFargateLaunchTarget(
                platform_version=ecs.FargatePlatformVersion.LATEST)
        )