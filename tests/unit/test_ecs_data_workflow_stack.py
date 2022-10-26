import aws_cdk as core
import aws_cdk.assertions as assertions

from ecs_data_workflow.ecs_data_workflow_stack import EcsDataWorkflowStack

# example tests. To run these tests, uncomment this file along with the example
# resource in ecs_data_workflow/ecs_data_workflow_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = EcsDataWorkflowStack(app, "ecs-data-workflow")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
