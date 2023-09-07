import os
import aws_cdk as cdk
from aws_cdk import (
    # Duration,
    Stack,
    aws_lambda as _lambda
)
from constructs import Construct
import os

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
        sf_to_sqs_func  = _lambda.Function(
            self,
            "LambdaFunction1",
            runtime=_lambda.Runtime.PYTHON_3_6,
            handler="sf_to_sqs.handler",  # Modify the handler based on your script structure
            code=_lambda.Code.from_asset("lambda/sf_to_sqs.py"),
        )

        # Lambda Function 2
        send_to_slack_func = _lambda.Function(
            self,
            "LambdaFunction2",
            runtime=_lambda.Runtime.PYTHON_3_6,
            handler="send_to_slack.handler",  # Modify the handler based on your script structure
            code=_lambda.Code.from_asset("lambda/send_to_slack.py"),
        )
