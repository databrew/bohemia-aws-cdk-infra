import os
import aws_cdk as cdk
from aws_cdk import (
    # Duration,
    Stack,
    aws_lambda as _lambda,
    CfnOutput,
    aws_lambda_python_alpha as lambda_alpha_,
    aws_sqs as sqs,
    aws_events as events,
    aws_events_targets as targets, 
    aws_lambda_event_sources as event_sources,
    aws_iam as iam,
    aws_s3 as s3,
    aws_sam as sam,
    aws_s3_notifications as s3n
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
                    "logs:CreateLogStream",
                    "logs:PutLogEvents"
                ]))

        # Create bucket object
        BUCKET='bohemia-lake-db'
        if(os.getenv('PIPELINE_STAGE')):
            BUCKET = 'databrew-testing-' + BUCKET
        bucket = s3.Bucket.from_bucket_name(self, "UseExistingBucket", BUCKET)


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
            layers=[aws_sdk_pandas_layer_version]
        )

        bucket.add_event_notification(
            s3.EventType.OBJECT_CREATED, 
            s3n.LambdaDestination(staging_func),
            s3.NotificationKeyFilter(prefix="metadata/zip_staging")
        )


        # Lambda Function for sending messages to Slack
        promote_func = lambda_alpha_.PythonFunction(
            self,
            "PromoteToProdMetadata",
            entry = "./lambda/metadata_promote_data_to_prod",
            index = 'lambda_function.py',
            handler = 'lambda_handler',
            runtime=_lambda.Runtime.PYTHON_3_8,
            role = exec_role,
            layers=[aws_sdk_pandas_layer_version]
        )

        bucket.add_event_notification(
            s3.EventType.OBJECT_CREATED, 
            s3n.LambdaDestination(promote_func),
            s3.NotificationKeyFilter(prefix="metadata/zip_prod")
        )



