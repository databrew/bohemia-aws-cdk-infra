"""
Description: 
This CDK code is used to create the base infrastructure
every other stack will be fetching values from the base infrastructure

@author: atediarjo@gmail.com
@reviewer: joe@databrew.cc
@createdOn: December, 25th 2022
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

class BaseInfrastructureStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

                # create vpc
        self.vpc = ec2.Vpc(
            self,
            "databrew-data-workflows-vpc",
            nat_gateways=0,
            subnet_configuration=[{
                'name': 'public-subnet-1',
                'subnetType': ec2.SubnetType.PUBLIC,
                'cidrMask': 24}]
        )

        # create cluster for ECS
        self.cluster = ecs.Cluster( 
            self,
            "CreateCluster",
            vpc=self.vpc,
            cluster_name='databrew-data-workflows-cluster',
            container_insights=False
        )
