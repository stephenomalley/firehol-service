import aws_cdk as core
import aws_cdk.assertions as assertions

from firehol_service.firehol_service_stack import FireholServiceStack


# example tests. To run these tests, uncomment this file along with the example
# resource in firehol_service/firehol_service_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = FireholServiceStack(app, "firehol-service")
    assertions.Template.from_stack(stack)
