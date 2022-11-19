# description: 
# This CDK code is used to provision resources
# to AWS. It will provision resources to 
# run ECS orchestration using Step Functions
# and an EventBridge Scheduler
#
# author: atediarjo@gmail.com
# reviewer: joe@databrew.cc
# createdOn: October, 25th 2022

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


class EcsDataWorkflowStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # create vpc
        vpc = ec2.Vpc(
            self,
            "MyVpc",
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
                ]))

        #######################################
        # This section where you append each
        # scheduled microservices to ECS
        # Everytime you add new stack, it will
        # create new microservices to the cluster
        #######################################
        task_definition = ecs.FargateTaskDefinition(
            self,
            "create-task-definition",
            execution_role=ecs_role,
            task_role=ecs_role,
            family='odk-form-extraction'
        )

        dockerhub_image = 'databrewllc/odk-form-extraction'

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
                        tasks.TaskEnvironmentVariable(name="BUCKET_PREFIX", value=os.getenv('BUCKET_PREFIX')),
                        tasks.TaskEnvironmentVariable(name="ODK_CREDENTIALS_SECRETS_NAME", value=os.getenv("ODK_CREDENTIALS_SECRETS_NAME"))]
            )],
            launch_target=tasks.EcsFargateLaunchTarget(platform_version=ecs.FargatePlatformVersion.LATEST)
        )

        # consolidate ecs into step function
        state_machine = sfn.StateMachine(self, "EcsWorkflowStateMachine",
                                         definition = form_extraction.next(
                                            sfn.Succeed(self, "SuccessfulExtraction")))

        # add event rule to step function to run code on scheduled intervals
        scheduler = events.Rule(
            self, "EcsWorkflowScheduler",
            schedule=events.Schedule.expression("cron(59 23 * * ? *)"),
            targets=[targets.SfnStateMachine(state_machine)]
        )

