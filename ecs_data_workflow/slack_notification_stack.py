import os
import aws_cdk as cdk
from aws_cdk import (
    # Duration,
    Stack,
    aws_lambda as _lambda,
    CfnOutput,
    aws_lambda_python_alpha as lambda_alpha_,
)
from constructs import Construct

class SlackNotificationStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        # output_bucket_name = os.getenv('BUCKET_PREFIX') + "bohemia-reporting"
        # bucket = s3.Bucket(
        #     self, "CFBucket",
        #     bucket_name= output_bucket_name,
        #     versioned=True,
        #     encryption=s3.BucketEncryption.S3_MANAGED
        # )

        # distribution = cloudfront.Distribution(
        #     self, "CfDistribution",
        #     default_root_object= 'index.html',
        #     default_behavior=cloudfront.BehaviorOptions(origin=origins.S3Origin(bucket))
        # )

        # cdk.CfnOutput(self, "BucketArn", value=bucket.bucket_arn)
        # cdk.CfnOutput(self, "DistributionURL", value=distribution.distribution_domain_name)
        # cdk.CfnOutput(self, "DistributionID", 
        #               value=distribution.distribution_id,
        #               export_name='cf-distribution-id')
        # Lambda Function 1
        sf_to_sqs_func  = lambda_alpha_.PythonFunction(
            self,
            "StepFuncToSQS",
            entry = "./lambda/sf_to_sqs.py",
            index = 'sf_to_sqs.py',
            handler = 'lambda_handler',
            runtime=_lambda.Runtime.PYTHON_3_11
        )

        # Lambda Function 2
        send_to_slack_func = lambda_alpha_.PythonFunction(
            self,
            "SendToSlack",
            entry = "./lambda/send_to_slack.py",
            index = 'send_to_slack.py',
            handler = 'lambda_handler',
            runtime=_lambda.Runtime.PYTHON_3_11
        )

