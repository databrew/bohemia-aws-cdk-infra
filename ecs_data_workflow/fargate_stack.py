import os
from constructs import Construct
from aws_cdk import (
    # Duration,
    Stack,
    aws_ec2 as ec2, aws_ecs as ecs,
    aws_ecs_patterns as ecs_patterns,
    aws_applicationautoscaling as appscaling,
    aws_iam as iam,
)
class FargateStack(Construct):

    def __init__(
        self, 
        scope: Construct, 
        id: str, *, 
        cluster=None, 
        dockerhub_image=None, 
        ecs_role=None, 
        family=None,
        environment=None,
        cron_expr=None):

        super().__init__(scope, id)
        # # add task definition
        task_definition = ecs.FargateTaskDefinition(
            self, 
            "create-task-definition", 
            execution_role=ecs_role, 
            task_role=ecs_role,
            family=family
        )

        # Add container to task definition
        data_extraction_container = task_definition.add_container(
            "task-extraction", 
            image=ecs.ContainerImage.from_registry(dockerhub_image),
            logging=ecs.LogDrivers.aws_logs(stream_prefix="databrew-wf"),
            environment=environment
        )

        # schedule in Fargate
        data_extraction_scheduled_task = ecs_patterns.ScheduledFargateTask(  
            self, "_scheduled_",
            desired_task_count= 1, 
            cluster=cluster,
            scheduled_fargate_task_definition_options=ecs_patterns.ScheduledFargateTaskDefinitionOptions(
                task_definition = task_definition,
                
            ),
            schedule=appscaling.Schedule.expression(cron_expr),
            platform_version=ecs.FargatePlatformVersion.LATEST
        )