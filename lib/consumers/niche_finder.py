from constructs import Construct
import aws_cdk as cdk
from aws_cdk.aws_iam import  Role  # Import ManagedPolicy and Role
from aws_cdk.aws_lambda import Function, Code, Runtime
from aws_cdk import aws_iam as iam
from aws_cdk import aws_events as events
from aws_cdk.aws_events import Rule, Schedule
from aws_cdk import aws_events_targets as targets
from lib.custom_constructs.config_construct import ConfigConstruct

class NicheFinderStack(cdk.Stack):

    def __init__(self, scope: Construct, construct_id: str, mediator_stack, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        try:
            # Loading Config Data
            config_data = ConfigConstruct(self, "ConsumerNicheFinderConfig", config_file_path="configs/consumer-niche-finder.yaml")

            # Loading Shared Data Config
            shared_config_data = ConfigConstruct(self, "SharedDataConfig", config_file_path="configs/shared-data.yaml")

            # Loading Prompt Data
            prompt_data = ConfigConstruct(self, "PromptConfig", config_file_path="lambda_handler/consumer/niche-finder/prompts/niche-finder-prompt.yaml")

            #  Get the S3 bucket, SQS queue, and SNS topic from the MediatorStack
            niche_finder_s3_bucket =  mediator_stack.buckets['niche-finder-bucket']
            #print(f"Debug: bucket_name={niche_finder_s3_bucket.bucket_name}")

            niche_finder_queue = mediator_stack.queues['niche-finder-queue']
            #print(f"Debug: queue_name={niche_finder_queue.queue_name}")

            niche_finder_topic = mediator_stack.topics['niche-finder-topic']
            #print(f"Debug: topic_name={niche_finder_topic.topic_name}")

            # IAM Role for Lambda function
            lambda_role = self._create_lambda_role()

            # Lambda function 
            lambda_fn = self._create_lambda_fn(lambda_role, shared_config_data, prompt_data, niche_finder_s3_bucket, niche_finder_queue, niche_finder_topic)

            # CloudWatch Events Rule for Lambda function
            cloud_watch_event = self._create_cloudwatch_rule_for_lambda(lambda_fn, config_data)

        except Exception as e:
           print(f"Error initializing NicheFinder: {str(e)}")

    # Create Lambda role    
    def _create_lambda_role(self):
        try:
            # IAM Role for Lambda function
            lambda_role = Role(self, "NicheFinderLambdaRole",
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
            return lambda_role
        except Exception as e:
            print(f"Error creating Lambda role: {str(e)}")
            return None
        
    #  Create Lambda function    
    def _create_lambda_fn(self, lambda_role, shared_config_data, prompt_data, niche_finder_s3_bucket, niche_finder_queue, niche_finder_topic):
        try:
            # Lambda function (receive prompt and config file names from config data construct)
            lambda_fn = Function(self, "NicheFinderLambdaFn",
                                 runtime=Runtime.PYTHON_3_9,
                                 code=Code.from_asset("lambda_handler"),
                                 handler="NicheFinder.handler",
                                 role=lambda_role,
                                 environment={
                                     "NICHE_FINDER_S3_BUCKET_NAME": niche_finder_s3_bucket.bucket_name,
                                     "NICHE_FINDER_SQS_QUEUE_URL": niche_finder_queue.queue_url,
                                     "NICHE_FINDER_SNS_TOPIC_ARN": niche_finder_topic.topic_arn,
                                     "NICHE_FINDER_SNS_PHONE_NUMBER": shared_config_data.get_value("subscription-phone-number"), 
                                     "NICHE_FINDER_SNS_EMAIL_ADDRESS": shared_config_data.get_value("subscription-email-address"),
                                     "NICHE_FINDER_PROMPT_DATA": prompt_data.get_value("prompt")
                                 })
            return lambda_fn
        except Exception as e:
            print(f"Error creating Lambda function: {str(e)}")
            return None
        

    # Create CloudWatch Events Rule for Lambda function
    # How you trigger the Lambda function will determine how you pass the parameters.
    # Here's an example using CloudWatch Events (replace with your chosen trigger):
    def _create_cloudwatch_rule_for_lambda(self, lambda_fn, config_data):
        scheduler=config_data.get_value("cloudwatch_schedule_expression")
        try:
            # CloudWatch Events Rule (schedule execution every hour)
            rule = Rule(self, "NicheFinderRule",
                        schedule=Schedule.expression(scheduler))
            # Add Lambda function as target
            rule.add_target(targets.LambdaFunction(lambda_fn))

        except Exception as e:
            print(f"Error creating CloudWatch Events Rule: {str(e)}")