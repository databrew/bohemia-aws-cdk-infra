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
    aws_events_targets as targets
)
from constructs import Construct

class SlackNotificationStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        
        msg_queue = sqs.Queue(
            self, 'SlackMessages'
        )

        # Lambda Function 1
        sf_to_sqs_func  = lambda_alpha_.PythonFunction(
            self,
            "StepFuncToSQS",
            entry = "./lambda/sf_to_sqs",
            index = 'sf_to_sqs.py',
            handler = 'lambda_handler',
            runtime=_lambda.Runtime.PYTHON_3_11,
            environment= {
                'QUEUE_URL': msg_queue.queue_url
            }
        )

        # Lambda Function 2
        send_to_slack_func = lambda_alpha_.PythonFunction(
            self,
            "SendToSlack",
            entry = "./lambda/send_to_slack",
            index = 'send_to_slack.py',
            handler = 'lambda_handler',
            runtime=_lambda.Runtime.PYTHON_3_11,
        )

        event_rule = events.Rule(
            self, 
            "SendToSlackRule",
            event_pattern=events.EventPattern(
                detail={
                    "status": ["FAILED"],
                    "stateMachineArn": ["arn:aws:states:us-east-1:381386504386:stateMachine:MyStateMachine-88nrpzlrn"]
                },
                detail_type=["Step Functions Execution Status Change"],
                source=["aws.states"]
            )
        )

        # add new rule to target
        event_rule.add_target(
            targets.LambdaFunction(sf_to_sqs_func)
        )



