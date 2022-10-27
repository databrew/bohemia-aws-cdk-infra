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
        vpc = ec2.Vpc(
            self,
            "MyVpc", 
            cidr="10.0.0.0/16",
            nat_gateways=0,
            subnet_configuration=[{
                'name': 'public-subnet-1',
                'subnetType': ec2.SubnetType.PUBLIC,
                'cidrMask': 24}]
        )
        
        # create cluster for ECS
        cluster = ecs.Cluster(
            self, 
            "CreateCluster", 
            vpc=vpc,
            cluster_name='databrew-data-workflow',
        )
        
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
                    ] ))

        # this is the section where you append each 
        # scheduled microservices to ECS

        # sample 1: create fargate stack with 1 day schedule
        odk_extraction_fargate_stack = FargateStack(
            self, 
            'dextract1',
            cluster=cluster,
            dockerhub_image="aryton/databrew-wf-data-extraction",
            ecs_role=ecs_role,
            family="data-extraction-one-day",
            environment={
                "BUCKET_PREFIX" : os.getenv('BUCKET_PREFIX'),
                "ODK_CREDENTIALS_SECRETS_NAME": os.getenv('ODK_CREDENTIALS_SECRETS_NAME')},
            cron_expr="rate(1 day)"
        )

        # sample 2: create fargate stack with 5 days schedule
        odk_extraction_fargate_stack_test = FargateStack(
            self, 
            'dextract2',
            cluster=cluster,
            dockerhub_image="aryton/databrew-wf-data-extraction",
            ecs_role=ecs_role,
            family="data-extraction-five-days",
            environment={
                "BUCKET_PREFIX" : os.getenv('BUCKET_PREFIX'),
                "ODK_CREDENTIALS_SECRETS_NAME": os.getenv('ODK_CREDENTIALS_SECRETS_NAME')},
            cron_expr="rate(5 days)"
        )
