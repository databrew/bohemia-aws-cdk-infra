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

        # create log bucket
        log_bucket=s3.Bucket(self, "LogBucket",
                             object_ownership=s3.ObjectOwnership.OBJECT_WRITER)

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
            default_behavior=cloudfront.BehaviorOptions(origin=origins.S3Origin(bucket)),
            enable_logging =True,
            log_bucket = log_bucket,
            log_file_prefix="distribution-access-logs/data-ops/",
            log_includes_cookies=True
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
            default_behavior=cloudfront.BehaviorOptions(origin=origins.S3Origin(monitoring_icf_bucket)),
            enable_logging =True,
            log_bucket = log_bucket,
            log_file_prefix="distribution-access-logs/monitoring-icf/",
            log_includes_cookies=True
        )

        cdk.CfnOutput(self, "MonitoringICFBucketArn", value=monitoring_icf_bucket.bucket_arn)
        cdk.CfnOutput(self, "MonitoringICFDistributionURL", value=monitoring_icf_distribution.distribution_domain_name)
        cdk.CfnOutput(self, "MonitoringICFDistributionID", 
                      value=monitoring_icf_distribution.distribution_id,
                      export_name='monitoring-icf-cf-distribution-id')
        

        # Monitoring Pharmacy reporting bucket
        output_bucket_name = os.getenv('BUCKET_PREFIX') + "bohemia-reporting-pharmacy-monitoring"
        monitoring_pharmacy_bucket = s3.Bucket(
            self, "MonitoringPharmacyBucket",
            bucket_name= output_bucket_name,
            versioned=True,
            encryption=s3.BucketEncryption.S3_MANAGED
        )

        monitoring_pharmacy_distribution = cloudfront.Distribution(
            self, "MonitoringPharmacyDistribution",
            default_root_object= 'index.html',
            default_behavior=cloudfront.BehaviorOptions(origin=origins.S3Origin(monitoring_pharmacy_bucket)),
            enable_logging =True,
            log_bucket = log_bucket,
            log_file_prefix="distribution-access-logs/monitoring-pharmacy/",
            log_includes_cookies=True
        )

        cdk.CfnOutput(self, "MonitoringPharmacyBucketArn", value=monitoring_pharmacy_bucket.bucket_arn)
        cdk.CfnOutput(self, "MonitoringPharmacyDistributionURL", value=monitoring_pharmacy_distribution.distribution_domain_name)
        cdk.CfnOutput(self, "MonitoringPharmacyDistributionID", 
                      value=monitoring_pharmacy_distribution.distribution_id,
                      export_name='monitoring-pharmacy-cf-distribution-id')
        

        # Monitoring Lab reporting bucket
        output_bucket_name = os.getenv('BUCKET_PREFIX') + "bohemia-reporting-lab-monitoring"
        monitoring_lab_bucket = s3.Bucket(
            self, "MonitoringLabBucket",
            bucket_name= output_bucket_name,
            versioned=True,
            encryption=s3.BucketEncryption.S3_MANAGED
        )

        monitoring_lab_distribution = cloudfront.Distribution(
            self, "MonitoringLabDistribution",
            default_root_object= 'index.html',
            default_behavior=cloudfront.BehaviorOptions(origin=origins.S3Origin(monitoring_lab_bucket)),
            enable_logging =True,
            log_bucket = log_bucket,
            log_file_prefix="distribution-access-logs/monitoring-lab/",
            log_includes_cookies=True
        )

        cdk.CfnOutput(self, "MonitoringLabBucketArn", value=monitoring_lab_bucket.bucket_arn)
        cdk.CfnOutput(self, "MonitoringLabDistributionURL", value=monitoring_lab_distribution.distribution_domain_name)
        cdk.CfnOutput(self, "MonitoringLabDistributionID", 
                      value=monitoring_lab_distribution.distribution_id,
                      export_name='monitoring-lab-cf-distribution-id')
        

        # CRA reporting bucket
        output_bucket_name = os.getenv('BUCKET_PREFIX') + "bohemia-reporting-cra-monitoring"
        monitoring_cra_bucket = s3.Bucket(
            self, "MonitoringCRABucket",
            bucket_name= output_bucket_name,
            versioned=True,
            encryption=s3.BucketEncryption.S3_MANAGED
        )

        monitoring_cra_distribution = cloudfront.Distribution(
            self, "MonitoringCRADistribution",
            default_root_object= 'index.html',
            default_behavior=cloudfront.BehaviorOptions(origin=origins.S3Origin(monitoring_cra_bucket)),
            enable_logging =True,
            log_bucket = log_bucket,
            log_file_prefix="distribution-access-logs/monitoring-cra/",
            log_includes_cookies=True
        )

        cdk.CfnOutput(self, "MonitoringCRABucketArn", value=monitoring_cra_bucket.bucket_arn)
        cdk.CfnOutput(self, "MonitoringCRADistributionURL", value=monitoring_cra_distribution.distribution_domain_name)
        cdk.CfnOutput(self, "MonitoringCRADistributionID", 
                      value=monitoring_cra_distribution.distribution_id,
                      export_name='monitoring-cra-cf-distribution-id')
        



        


