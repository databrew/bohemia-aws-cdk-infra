import os
import aws_cdk as cdk
from aws_cdk import (
    # Duration,
    Stack,
    aws_s3 as s3,
    aws_cloudfront as cloudfront,
    aws_cloudfront_origins as origins
)
from constructs import Construct
import os

class CloudFrontReportStack(Stack):

    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        output_bucket_name = os.getenv('BUCKET_PREFIX') + "bohemia-reporting"
        bucket = s3.Bucket(
            self, "CFBucket",
            bucket_name= output_bucket_name,
            versioned=True,
            encryption=s3.BucketEncryption.S3_MANAGED
        )

        distribution = cloudfront.Distribution(
            self, "CfDistribution",
            default_root_object= 'index.html',
            default_behavior=cloudfront.BehaviorOptions(origin=origins.S3Origin(bucket))
        )

        cdk.CfnOutput(self, "BucketArn", value=bucket.bucket_arn)
        cdk.CfnOutput(self, "DistributionURL", value=distribution.distribution_domain_name)
        cdk.CfnOutput(self, "DistributionID", 
                      value=distribution.distribution_id,
                      export_name='cf-distribution-id')
