from constructs import Construct
import aws_cdk as cdk
from aws_cdk.aws_iam import  ManagedPolicy, Role, ServicePrincipal  # Import ManagedPolicy and Role
from aws_cdk.aws_sns import Subscription, SubscriptionProtocol, Topic  # Import SubscriptionProtocol
from aws_cdk.aws_iam import Role, ServicePrincipal
from aws_cdk.aws_lambda import Function, Code, Runtime
from aws_cdk.aws_sqs import Queue
from aws_cdk import aws_iam as iam
from aws_cdk.aws_s3 import Bucket
from aws_cdk.aws_s3_assets import Asset  # Import Asset class
from aws_cdk.aws_sns import Topic, Subscription
from aws_cdk import aws_events as events
from aws_cdk.aws_events import Rule, Schedule
from aws_cdk import aws_events_targets as targets
from aws_cdk import aws_lambda as lambda_
import yaml
from aws_cdk import aws_sns_subscriptions as subscriptions
from aws_cdk import aws_sns as sns


def get_topic_name_from_config(config_data):
    """Extracts the topic name from the configuration data.

    Args:
        config_data (dict): The loaded configuration data from the YAML file.

    Returns:
        str: The extracted topic name.

    Raises:
        KeyError: If the 'topic_name' key is not found in the configuration data.
    """

    try:
        return config_data["topic_name"]
    except KeyError:
        raise KeyError("Missing 'topic_name' key in configuration data")


class AiMarketingGenStack(cdk.Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Retrieve prompt and config file names from context
        prompt_file_name = self.node.try_get_context("prompt_file")
        config_file_name = self.node.try_get_context("config_file")

        if not prompt_file_name or not config_file_name:
            raise ValueError("Missing prompt_file or config_file context variables")
        
        # Assuming 'config_file_name' contains the name of your YAML file without the extension
        config_file_path = f"configs/{config_file_name}.yaml"

        # Load configuration from YAML file directly
        with open(config_file_path, 'r') as file:
            config_data = yaml.safe_load(file)
            
        # IAM Role for Lambda function
        lambda_role = Role(self, "LambdaRole",
                        assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"))
        # Grant permissions to Lambda
        lambda_role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name("AmazonS3FullAccess")
        )
        lambda_role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSNSFullAccess")
        )
        lambda_role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSQSFullAccess")
        )
        lambda_role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name("AmazonTextractFullAccess")  # Corrected policy name
        )

        # Lambda function (receive prompt and config file names as parameters)
        lambda_fn = Function(self, "NicheFinderLambda",
                             runtime=Runtime.PYTHON_3_9,
                             code=Code.from_asset("lambda_handler"),
                             handler="NicheFinder.handler",
                             role=lambda_role,
                             environment={
                                 "S3_BUCKET_NAME": niche_finder_results_bucket.bucket_name,
                                 "SQS_QUEUE_URL": niche_finder_queue.queue_url,
                                 "SNS_TOPIC_ARN": niche_finder_topic.topic_arn,
                                  # Potentially include phone number and email address (modify based on your implementation)
                                 "SNS_PHONE_NUMBER": config_data.get("phone_number"),  # Optional
                                 "SNS_EMAIL_ADDRESS": config_data.get("email_address"),  # Optional
                             })

        # How you trigger the Lambda function will determine how you pass the parameters.
        # Here's an example using CloudWatch Events (replace with your chosen trigger):

        # CloudWatch Events Rule (schedule execution every hour)
        rule = Rule(self, "NicheFinderRule",
                    schedule=Schedule.expression(config_data["cloudwatch_schedule_expression"]))  # Schedule from config

        rule.add_target(targets.LambdaFunction(lambda_fn,
            event=events.RuleTargetInput.from_object({
                "prompt_file": prompt_file_name,
                "config_file": config_file_name,
            })
        ))

         # SNS Subscriptions for notifications
        Subscription(self, "PhoneSubscription",
                     topic=niche_finder_topic,
                     protocol=SubscriptionProtocol.SMS,
                     endpoint=config_data["phone_number"])  # Required

        Subscription(self, "EmailSubscription",
                     topic=niche_finder_topic,
                     protocol=SubscriptionProtocol.EMAIL,
                     endpoint=config_data["email_address"])  # Required