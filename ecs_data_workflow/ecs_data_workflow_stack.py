import os
from aws_cdk import (
    # Duration,
    Stack,
    aws_ec2 as ec2, aws_ecs as ecs,
    aws_ecs_patterns as ecs_patterns,
    aws_applicationautoscaling as appscaling,
    aws_iam as iam,
)
from constructs import Construct

from ecs_data_workflow.fargate_stack import FargateStack

class EcsDataWorkflowStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

                # create vpc
        vpc = ec2.Vpc(self, "MyVpc", max_azs=3)
        
        # create cluster for ECS
        cluster = ecs.Cluster(
            self, 
            "CreateCluster", 
            vpc=vpc,
            cluster_name='databrew-data-workflow',
        )
        
        # create execution role
        execution_role = iam.Role(
            self, "ecs-devops-execution-role", 
            assumed_by=iam.ServicePrincipal("ecs-tasks.amazonaws.com"), 
            role_name="ecs-devops-execution-role")

        # add to policy
        execution_role.add_to_policy(
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
                    ] ))

        odk_extraction_fargate_stack = FargateStack(
            self, 
            'CreateDataExtractionFargateStack',
            cluster=cluster,
            dockerhub_image="aryton/databrew-wf-data-extraction",
            execution_role=execution_role,
            family="data-extraction",
            environment={
                "BUCKET_PREFIX" : os.getenv('BUCKET_PREFIX'),
                "ODK_CREDENTIALS_SECRETS_NAME": os.getenv('ODK_CREDENTIALS_SECRETS_NAME')}
        )

        odk_extraction_fargate_stack_test = FargateStack(
            self, 
            'CreateDataExtractionFargateStack',
            cluster=cluster,
            dockerhub_image="aryton/databrew-wf-data-extraction",
            execution_role=execution_role,
            family="data-extraction-extra",
            environment={
                "BUCKET_PREFIX" : os.getenv('BUCKET_PREFIX'),
                "ODK_CREDENTIALS_SECRETS_NAME": os.getenv('ODK_CREDENTIALS_SECRETS_NAME')}
        )

        # # add task definition
        # task_definition = ecs.FargateTaskDefinition(
        #     self, "data-extraction-task-definition", 
        #     execution_role=execution_role, 
        #     task_role=execution_role,
        #     family="data-extraction"
        # )

        # # Add container to task definition
        # data_extraction_container = task_definition.add_container(
        #     "task-extraction", 
        #     image=ecs.ContainerImage.from_registry("aryton/databrew-wf-data-extraction"),
        #     logging=ecs.LogDrivers.aws_logs(stream_prefix="databrew-wf"),
        #     environment={
        #         "BUCKET_PREFIX" : os.getenv('BUCKET_PREFIX'),
        #         "ODK_CREDENTIALS_SECRETS_NAME": os.getenv('ODK_CREDENTIALS_SECRETS_NAME')}
        # )

        # # schedule in Fargate
        # data_extraction_scheduled_task = ecs_patterns.ScheduledFargateTask(  
        #     self, "createScheduledFargateTask",
        #     desired_task_count= 1, 
        #     cluster=cluster,
        #     scheduled_fargate_task_definition_options=ecs_patterns.ScheduledFargateTaskDefinitionOptions(task_definition = task_definition),
        #     schedule=appscaling.Schedule.expression("rate(1 day)"),
        #     platform_version=ecs.FargatePlatformVersion.LATEST
        # )
