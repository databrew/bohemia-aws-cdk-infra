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
    aws_lambda as _lambda,
    aws_lambda_python_alpha as lambda_alpha_,
    aws_ecs_patterns as ecs_patterns,
    aws_applicationautoscaling as appscaling,
    aws_iam as iam,
    aws_stepfunctions_tasks as tasks,
    aws_stepfunctions as sfn,
    aws_events as events,
    aws_events_targets as targets,
    aws_athena as athena
)
from constructs import Construct


class AthenaInfraStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, env = None, cluster = None) -> None:
        super().__init__(scope, construct_id, env = env)

        # Create bucket object
        if (os.getenv('PIPELINE_STAGE') == 'develop'):
            OUTPUT_BUCKET_NAME = 'develop-athena-query-results'
        else:
            OUTPUT_BUCKET_NAME = 'athena-query-results'

        cfn_work_group = athena.CfnWorkGroup(
            self,
            "WorkGroupAthenaID",
            name="wg-athena",
            description="Run athena queries for myapp",
            work_group_configuration=athena.CfnWorkGroup.WorkGroupConfigurationProperty(
                result_configuration=athena.CfnWorkGroup.ResultConfigurationProperty(
                    output_location=f"s3://{OUTPUT_BUCKET_NAME}/"
                ),
            ),

        )

        exec_role = iam.Role(
            self, "AthenaLambdaExecRole",
            assumed_by=iam.ServicePrincipal('lambda.amazonaws.com'),
        )
        # each role has a policy attached to it
        exec_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                resources=["*"],
                actions=[
                    "sqs:*",
                    "kms:Decrypt",
                    "ssm:*",
                    "s3:*",
                    "logs:*",
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
                f'arn:aws:athena:us-east-1:{self.account}:workgroup/wg-athena'
            ],
        )

        # Lambda Function for sending messages to Slack
        athena_func = lambda_alpha_.PythonFunction(
            self,
            "AthenaFunc",
            entry = "./lambda/athena",
            index = 'lambda_function.py',
            handler = 'lambda_handler',
            role = exec_role,
            runtime=_lambda.Runtime.PYTHON_3_10,
            timeout=cdk.Duration.minutes(15),
            memory_size=1769,
            ephemeral_storage_size=cdk.Size.mebibytes(10240),
            environment= {
                'OUTPUT_BUCKET_NAME': OUTPUT_BUCKET_NAME
            }
        )

        athena_func.add_to_role_policy(statement_athena)

        statement_glue = iam.PolicyStatement(
            actions=["glue:GetTable", "glue:GetPartitions"],
            resources=["*"],
        )

        athena_func.add_to_role_policy(statement_glue)