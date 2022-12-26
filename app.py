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
from ecs_data_workflow.kenya_workflow_stack import KenyaWorkflowStack


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

# This is the stack used for kenya
kenya_workflow = KenyaWorkflowStack(
    app, "KenyaWorkflowStack",
    env = cdk_default_environment,
    cluster = base_infra.cluster
)

# synthesize to cloudformation
app.synth()
