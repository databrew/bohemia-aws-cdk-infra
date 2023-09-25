import os
import aws_cdk as cdk
from aws_cdk import (
    # Duration,
    Stack,
    aws_lambda as _lambda,
    CfnOutput,
    aws_lambda_python_alpha as lambda_alpha_,
    aws_lambda_event_sources as event_sources,
    aws_iam as iam,
    aws_s3 as s3,
    aws_sam as sam,
    aws_stepfunctions_tasks as tasks,
    aws_stepfunctions as sfn,
    aws_events as events,
    aws_events_targets as targets
)
from constructs import Construct

class OdkBackupStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        exec_role = iam.Role(
            self, "OdkBackupExecRole",
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
                    "s3:*",
                    "logs:*",
                    "secretsmanager:*"
                ]))

        # Create bucket object
        if (os.getenv('PIPELINE_STAGE') == 'develop'):
            SECRET_ID = 'test/odk-credentials'
        else:
            SECRET_ID = 'prod/odk-credentials'
        
        bucket = s3.Bucket(self, "OdkBackupS3Bucket", versioned=True)

        # Lambda Function for sending messages to Slack
        backup_func = lambda_alpha_.PythonFunction(
            self,
            "OdkBackupFunc",
            entry = "./lambda/odk_backup",
            index = 'lambda_function.py',
            handler = 'lambda_handler',
            runtime=_lambda.Runtime.PYTHON_3_11,
            role = exec_role,
            timeout=cdk.Duration.minutes(15),
            memory_size=1769,
            ephemeral_storage_size=10240,
            environment= {
                'BUCKET_NAME': bucket.bucket_name,
                'SECRET_ID': SECRET_ID
            }
        )

        # success object
        success_trigger = sfn.Succeed(self, "ODK Backup Success")

        # extract and clean
        fail_trigger = sfn.Fail(self, "Notify Failure in ODK Backup!")


        lambda_task = tasks.LambdaInvoke(self, 
                                         "OdkBackupTask",
                                         lambda_function= backup_func)
        lambda_task.add_catch(fail_trigger)
        lambda_task.next(success_trigger)
        
        state_machine = sfn.StateMachine(
            self, "OdkBackupStateMachine", definition=lambda_task
        )

        #######################################
        # Eventbridge
        #######################################
        # create scheduler if it is production
        if (os.getenv('PIPELINE_STAGE') == 'production'):
            # add event rule to run data pipeline for work time at EAT\
            # add event rule to run at midnight EAT timezone
            midnight_schedule = events.Rule(
                self, "OdkBackupMidnightSchedule",
                schedule=events.Schedule.expression("cron(00 21 * * ? *)"),
                targets=[targets.SfnStateMachine(state_machine)]
            )

        cdk.CfnOutput(self, 'OdkBackupStepFunction', 
                      value=state_machine.state_machine_arn,
                      export_name='odkbackup:arn')

