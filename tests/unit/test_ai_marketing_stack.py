import aws_cdk as core
import aws_cdk.assertions as assertions

from ai_marketing.ai_marketing_stack import AiMarketingStack

# example tests. To run these tests, uncomment this file along with the example
# resource in ai_marketing/ai_marketing_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = AiMarketingStack(app, "ai-marketing")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
