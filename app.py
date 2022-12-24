#!/usr/bin/env python3
import os
import aws_cdk as cdk
from ecs_data_workflow.kenya_workflow_stack import KenyaWorkflowStack


app = cdk.App()
KenyaWorkflowStack(
    app, "KenyaWorkflowStack",
    env=cdk.Environment(
        account=os.getenv('CDK_DEFAULT_ACCOUNT'), 
        region=os.getenv('CDK_DEFAULT_REGION'))
)

app.synth()
