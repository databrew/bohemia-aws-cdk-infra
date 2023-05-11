import os
import aws_cdk as cdk
from aws_cdk import (
    # Duration,
    Stack,
    aws_s3 as s3,
    aws_cloudfront as cloudfront
)
from constructs import Construct
import os

class CloudFrontReportStack(Stack):

    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        output_bucket_name = os.getenv('PIPELINE_STAGE') + '-' +  "kwale-reporting-bucket"
        bucket = s3.Bucket(
            self, "CFBucket",
            bucket_name= output_bucket_name,
            versioned=True,
            encryption=s3.BucketEncryption.S3_MANAGED
        )

        # distribution = cloudfront.CloudFrontWebDistribution(
        #     self, "CFDistribution",
        #     origin_configs=[
        #         cloudfront.SourceConfiguration(
        #             s3_origin_source=cloudfront.S3OriginConfig(
        #                 s3_bucket_source=bucket.bucket_name
        #             ),
        #             behaviors=[cloudfront.Behavior(is_default_behavior=True)],
        #         )
        #     ],
        # )

        cdk.CfnOutput(self, "BucketArn", value=bucket.bucket_arn)
        # cdk.CfnOutput(self, "DistributionURL", value=distribution.distribution_domain_name)
