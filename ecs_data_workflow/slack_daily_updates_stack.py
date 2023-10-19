import os
import aws_cdk as cdk
from aws_cdk import (
    Stack,
    aws_lambda as _lambda,
    aws_lambda_python_alpha as lambda_alpha_,
    aws_iam as iam,
    aws_s3 as s3,
    aws_stepfunctions_tasks as tasks,
    aws_stepfunctions as sfn,
    aws_events as events,
    aws_events_targets as targets,
    aws_sam as sam
)
from constructs import Construct

class SlackDailyUpdatesStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        exec_role = iam.Role(
            self, "SlackDailyUpdatesExecRole",
            assumed_by=iam.ServicePrincipal('lambda.amazonaws.com'),
        )

        # Create bucket object
        if (os.getenv('PIPELINE_STAGE') == 'develop'):
            BUCKET_NAME = 'databrew-testing-databrew.org'
        else:
            BUCKET_NAME = 'databrew.org'

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
                    "logs:*",
                    "secretsmanager:*"
                ]))
        
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
        send_form_submissions_func = lambda_alpha_.PythonFunction(
            self,
            "SlackDailyFormUpdatesFunc",
            entry = "./lambda/send_form_submissions_to_slack",
            index = 'lambda_function.py',
            handler = 'lambda_handler',
            runtime=_lambda.Runtime.PYTHON_3_8,
            role = exec_role,
            timeout=cdk.Duration.minutes(15),
            memory_size=1769,
            ephemeral_storage_size=cdk.Size.mebibytes(10240),
            layers=[aws_sdk_pandas_layer_version],
            environment= {
                'BUCKET_NAME': BUCKET_NAME
            }
        )

        # success object
        success_trigger = sfn.Succeed(self, "Slack Daily Form Updates Success")

        # extract and clean
        fail_trigger = sfn.Fail(self, "Notify Failure in Slack Form Updates!")


        lambda_task = tasks.LambdaInvoke(self, 
                                         "SlackDailyFormUpdatesTask",
                                         lambda_function= send_form_submissions_func)
        lambda_task.add_catch(fail_trigger)
        lambda_task.next(success_trigger)
        
        state_machine = sfn.StateMachine(
            self, "SlackUpdatesStateMachine", definition=lambda_task
        )

        #######################################
        # Eventbridge
        #######################################
        # create scheduler if it is production
        if (os.getenv('PIPELINE_STAGE') == 'production'):
            # add event rule to run data pipeline for work time at EAT\
            # add event rule to run at midnight EAT timezone
            midnight_schedule = events.Rule(
                self, "SlackUpdatesMidnightSchedule",
                schedule=events.Schedule.expression("cron(00 21 * * ? *)"),
                targets=[targets.SfnStateMachine(state_machine)]
            )

        cdk.CfnOutput(self, 'SlackUpdatesStepFunction', 
                      value=state_machine.state_machine_arn,
                      export_name='slackdailyupdates:arn')





