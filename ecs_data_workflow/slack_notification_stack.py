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
    aws_iam as iam
)
from constructs import Construct

class SlackNotificationStack(Stack):
    def __init__(self, scope: Construct, id: str, state_machine_arns = None) -> None:
        super().__init__(scope, id, state_machine_arns = state_machine_arns)


        exec_role = iam.Role(
            self, "SlackNotificationExecRole",
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
                    "states:ListStateMachines",
                    "states:ListActivities",
                    "states:DescribeStateMachine",
                    "states:DescribeStateMachineForExecution",
                    "states:ListExecutions",
                    "states:DescribeExecution",
                    "states:GetExecutionHistory",
                    "states:DescribeActivity",
                    "logs:CreateLogStream",
                    "logs:PutLogEvents"
                ]))
        
        msg_queue = sqs.Queue(
            self, 'SlackMessages'
        )

        sqs_event_source = event_sources.SqsEventSource(msg_queue)

        # Lambda Function to capture step function results to SQS
        sf_to_sqs_func  = lambda_alpha_.PythonFunction(
            self,
            "StepFuncToSQS",
            entry = "./lambda/sf_to_sqs",
            index = 'sf_to_sqs.py',
            handler = 'lambda_handler',
            runtime=_lambda.Runtime.PYTHON_3_11,
            environment= {
                'QUEUE_URL': msg_queue.queue_url
            },  
            role= exec_role
        )

        # Lambda Function for sending messages to Slack
        send_to_slack_func = lambda_alpha_.PythonFunction(
            self,
            "SendToSlack",
            entry = "./lambda/send_to_slack",
            index = 'send_to_slack.py',
            handler = 'lambda_handler',
            runtime=_lambda.Runtime.PYTHON_3_11,
            role = exec_role
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

        # send to slack event source
        send_to_slack_func.add_event_source(
            sqs_event_source
        )



