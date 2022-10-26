#!/usr/bin/env python3
import os
import aws_cdk as cdk
from ecs_data_workflow.ecs_data_workflow_stack import EcsDataWorkflowStack


app = cdk.App()
EcsDataWorkflowStack(
    app, "EcsDataWorkflowStack",
    env=cdk.Environment(
        account=os.getenv('CDK_DEFAULT_ACCOUNT'), 
        region=os.getenv('CDK_DEFAULT_REGION'))
)

app.synth()
