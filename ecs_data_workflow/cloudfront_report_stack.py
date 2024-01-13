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

        # data-ops reporting bucket
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


        # Monitoring ICF reporting bucket
        output_bucket_name = os.getenv('BUCKET_PREFIX') + "bohemia-reporting-icf-monitoring"
        monitoring_icf_bucket = s3.Bucket(
            self, "MonitoringICFBucket",
            bucket_name= output_bucket_name,
            versioned=True,
            encryption=s3.BucketEncryption.S3_MANAGED
        )

        monitoring_icf_distribution = cloudfront.Distribution(
            self, "MonitoringICFDistribution",
            default_root_object= 'index.html',
            default_behavior=cloudfront.BehaviorOptions(origin=origins.S3Origin(monitoring_icf_bucket))
        )

        cdk.CfnOutput(self, "MonitoringICFBucketArn", value=monitoring_icf_bucket.bucket_arn)
        cdk.CfnOutput(self, "MonitoringICFDistributionURL", value=monitoring_icf_distribution.distribution_domain_name)
        cdk.CfnOutput(self, "MonitoringICFDistributionID", 
                      value=monitoring_icf_distribution.distribution_id,
                      export_name='monitoring-icf-cf-distribution-id')


