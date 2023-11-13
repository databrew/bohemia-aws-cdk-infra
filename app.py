#!/usr/bin/env python3

"""
Author: atediarjo@gmail.com
Description:
This CDK app is used for creating different stacks for 
AWS resource creation. Base is our base infrastructure where
different stacks are going to be appended based on our use-case
"""
import os
import aws_cdk as cdk
from ecs_data_workflow.base_infrastructure_stack import BaseInfrastructureStack
from ecs_data_workflow.reporting_stack import ReportingStack
from ecs_data_workflow.cloudfront_report_stack import CloudFrontReportStack
from ecs_data_workflow.glue_infra_stack import GlueInfraStack
from ecs_data_workflow.odk_batch_stack import OdkBatchStack
from ecs_data_workflow.slack_notification_stack import SlackNotificationStack
from ecs_data_workflow.odk_backup import OdkBackupStack
from ecs_data_workflow.anomalies_gsheets_stack import AnomaliesGsheetsStack
from ecs_data_workflow.metadata_update_stack import MetadataUpdateStack
from ecs_data_workflow.slack_daily_updates_stack import SlackDailyUpdatesStack
from ecs_data_workflow.athena_infra_stack import AthenaInfraStack

# instantiate application
app = cdk.App()

# create default environment for AWS CDK
cdk_default_environment = cdk.Environment(
        account=os.getenv('CDK_DEFAULT_ACCOUNT'), 
        region=os.getenv('CDK_DEFAULT_REGION'))

# Here we create the base infrastructure, which is the cluster
# that will enable us to run several data pipeline 
# as we have more data pipeline, it will be appended
# to this base infrastructure
base_infra = BaseInfrastructureStack(
    app, "BaseInfraStructureStack",
    env = cdk_default_environment
)

# This is the stack used for cloudfront
cloudfront_report = CloudFrontReportStack(
    app, "CloudFrontReportStack",
    env = cdk_default_environment
)

# odk batch for dumping data every 10 mins
odk_batch = OdkBatchStack(
    app, "ODKBatchStack",
    env = cdk_default_environment,
    cluster = base_infra.cluster

)

# This is the stack used for kenya
reporting = ReportingStack(
    app, "ReportingStack",
    env = cdk_default_environment,
    cluster = base_infra.cluster
)

# This is the stack used for kenya
metadata = MetadataUpdateStack(
    app, "MetadataUpdateStack",
    env = cdk_default_environment,
    cluster = base_infra.cluster
)

# this is the glue database setup
glue_db = GlueInfraStack(
    app, "GlueInfraStack",
    env = cdk_default_environment,
)

# this is slack notification
slack_notification = SlackNotificationStack(
    app, 
    "SlackNotificationStack"
)

# backup 
odk_backup = OdkBackupStack(
    app,
    "OdkBackupStack"
)

# google sheets stack
google_sheets = AnomaliesGsheetsStack(
    app,
    "AnomaliesGsheetsStack",
    env = cdk_default_environment,
    cluster = base_infra.cluster
)

# slack daily updates
slack_daily_updates = SlackDailyUpdatesStack(
    app,
    "SlackDailyUpdatesStack",
    env = cdk_default_environment,
)

athena_func = AthenaInfraStack(
    app,
     "AthenaInfraStack",
    env = cdk_default_environment,
)

# serial deps to prevent locking between stack creation
odk_batch.add_dependency(odk_backup)
reporting.add_dependency(odk_batch)
metadata.add_dependency(reporting)
athena_func.add_dependency(metadata)

slack_notification.add_dependency(metadata)


# synthesize to cloudformation
app.synth()
