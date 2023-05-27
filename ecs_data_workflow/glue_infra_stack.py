import os
import aws_cdk as cdk
from aws_cdk import (
    # Duration,
    Stack,
    aws_s3 as s3,
)
from constructs import Construct
import os

class GlueInfraStack(Stack):

    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        output_bucket_name = os.getenv('BUCKET_PREFIX') + "bohemia-lakehouse-db"
        bucket = s3.Bucket(
            self, "lakehouse-infra",
            bucket_name= output_bucket_name,
            versioned=True,
            encryption=s3.BucketEncryption.S3_MANAGED
        )

        cdk.CfnOutput(self, "BucketArn", value=bucket.bucket_arn)
