import os
import aws_cdk as cdk
from aws_cdk import (
    # Duration,
    Stack,
    aws_lambda as _lambda,
    CfnOutput,
    aws_lambda_python_alpha as lambda_alpha_,
    aws_lambda_event_sources as event_sources,
    aws_iam as iam,
    aws_s3 as s3,
    aws_sam as sam
)
from constructs import Construct

class MetadataDataQualityStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        exec_role = iam.Role(
            self, "MetadataDataQualityExecRole",
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
                    "logs:*"
                ]))

        # Create bucket object
        TARGET_BUCKET_NAME='bohemia-lake-db'
        if(os.getenv('PIPELINE_STAGE')):
            TARGET_BUCKET_NAME = 'databrew-testing-' + TARGET_BUCKET_NAME
        
        bucket = s3.Bucket(self, "UNIT-TEST-HERE", versioned=True)


        aws_sdk_pandas_layer = sam.CfnApplication(
            self,
            "awssdkpandas-layer",
            location=sam.CfnApplication.ApplicationLocationProperty(
                application_id="arn:aws:serverlessrepo:us-east-1:336392948345:applications/aws-sdk-pandas-layer-py3-8",
                semantic_version="3.0.0",  # Get the latest version from https://serverlessrepo.aws.amazon.com/applications
            ),
        )

        aws_sdk_pandas_layer_arn = aws_sdk_pandas_layer.get_att("Outputs.WranglerLayer38Arn").to_string()
        aws_sdk_pandas_layer_version = _lambda.LayerVersion.from_layer_version_arn(self, "awssdkpandas-layer-version", aws_sdk_pandas_layer_arn)

        # Lambda Function for sending messages to Slack
        staging_func = lambda_alpha_.PythonFunction(
            self,
            "StagingMetadata",
            entry = "./lambda/metadata_data_quality_test",
            index = 'lambda_function.py',
            handler = 'lambda_handler',
            runtime=_lambda.Runtime.PYTHON_3_8,
            role = exec_role,
            layers=[aws_sdk_pandas_layer_version],
            timeout=cdk.Duration.minutes(15),
            environment= {
                'DQ_TEST_BUCKET_NAME': bucket.bucket_name,
                'TARGET_BUCKET_NAME': TARGET_BUCKET_NAME
            }
        )

        staging_func.add_event_source(
            event_sources.S3EventSource(bucket,
                                        events=[s3.EventType.OBJECT_CREATED],
                                        filters=[s3.NotificationKeyFilter(prefix="zip_staging/")])
        )

        # Lambda Function for sending messages to Slack
        prod_func = lambda_alpha_.PythonFunction(
            self,
            "PromoteMetadata",
            entry = "./lambda/metadata_promote_data_to_prod",
            index = 'lambda_function.py',
            handler = 'lambda_handler',
            runtime=_lambda.Runtime.PYTHON_3_8,
            role = exec_role,
            layers=[aws_sdk_pandas_layer_version],
            timeout=cdk.Duration.minutes(15),
            environment= {
                'DQ_TEST_BUCKET_NAME': bucket.bucket_name,
                'TARGET_BUCKET_NAME': TARGET_BUCKET_NAME
            }
        )

        prod_func.add_event_source(
            event_sources.S3EventSource(bucket,
                                        events=[s3.EventType.OBJECT_CREATED],
                                        filters=[s3.NotificationKeyFilter(prefix="zip_prod/")])
        )