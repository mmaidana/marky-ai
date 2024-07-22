from constructs import Construct
import aws_cdk as cdk
from aws_cdk.aws_iam import  Role  # Import ManagedPolicy and Role
from aws_cdk.aws_lambda import Function, Code, Runtime
from aws_cdk import aws_iam as iam
from aws_cdk.aws_events import Rule, Schedule
from aws_cdk import aws_events_targets as targets
from infra.lib.custom_constructs.config_construct import ConfigConstruct
from aws_cdk import aws_logs as logs
from aws_cdk.aws_lambda import Code, Runtime
import os

class NicheFinderStack(cdk.Stack):

    def __init__(self, scope: Construct, construct_id: str, common_stack, mediator_stack, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        try:
            # Create Logger Instance
            StackName = cdk.Stack.of(self).stack_name
            logger = common_stack._create_logger(StackName=StackName)
            self.logger = logger

            logger.info("Loading " + StackName + " configuration")
            # Loading Config Data
            config_data = ConfigConstruct(self, "ConsumerNicheFinderConfig", config_file_path="consumer-niche-finder.yaml")
            log_group_name = config_data.get_value("log_group_name")

            logger.info("Loading Shared Data configuration")
            # Loading Shared Data Config
            shared_config_data = ConfigConstruct(self, "SharedDataConfig", config_file_path="shared-data.yaml")

            logger.info("Loading Prompt Data configuration")
            # Loading Prompt Data
            prompt_data = ConfigConstruct(self, "PromptConfig", config_file_path="prompts/niche-finder-prompt.yaml")

            # Setup for CloudWatch log group
            log_group =  common_stack._create_log_group(log_group_name, StackName= StackName)

            #  Get the S3 bucket, SQS queue, and SNS topic from the MediatorStack
            niche_finder_s3_bucket =  mediator_stack.buckets['niche-finder-bucket']
            logger.info(f"Debug: bucket_name={niche_finder_s3_bucket.bucket_name}")

            niche_finder_queue = mediator_stack.queues['niche-finder-queue']
            logger.info(f"Debug: queue_name={niche_finder_queue.queue_name}")

            niche_finder_topic = mediator_stack.topics['niche-finder-topic']
            logger.info(f"Debug: topic_name={niche_finder_topic.topic_name}")

            # IAM Role for Lambda function
            logger.info("Creating Lambda role")
            lambda_role = self._create_lambda_role()
            

            # Lambda function
            logger.info("Creating Lambda function") 
            # Adjust the path to where your lambda_handler directory is located relative to the script execution path
            lambda_handler_path = "./infra/lambda_handler/consumer"  # Example if you're in /Users/marcelo/dev
            self.logger.info(f"Lambda Handler path: {lambda_handler_path}")
            lambda_fn = self._create_lambda_fn(lambda_role, shared_config_data, prompt_data, niche_finder_s3_bucket, niche_finder_queue, niche_finder_topic, lambda_handler_path)

            # CloudWatch Events Rule for Lambda function
            logger.info("Creating CloudWatch Events rule for Lambda function")
            cloud_watch_event = self._create_cloudwatch_rule_for_lambda(lambda_fn, config_data)

        except Exception as e:
           logger.error(f"Error initializing NicheFinder: {str(e)}")

        
        end_logger = common_stack._end_logger(StackName=StackName)
        

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
            self.logger.info("Lambda role created successfully")
            return lambda_role
        except Exception as e:
            self.logger.error(f"Error creating Lambda role: {str(e)}")
            return None


    
    #  Create Lambda function    
    def _create_lambda_fn(self, lambda_role, shared_config_data, prompt_data, niche_finder_s3_bucket, niche_finder_queue, niche_finder_topic, lambda_handler_path):
        try:
            # Lambda function (receive prompt and config file names from config data construct)
            lambda_fn = Function(self, "NicheFinderLambdaFn",
                                 runtime=Runtime.PYTHON_3_9,
                                 code=Code.from_asset(F"{lambda_handler_path}"),
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
            self.logger.info("Lambda function created successfully")
            return lambda_fn
        except Exception as e:
            self.logger.error(f"Error creating Lambda function: {str(e)}")
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
            self.logger.info("CloudWatch Events Rule created successfully")
            #return rule

        except Exception as e:
            self.logger.error(f"Error creating CloudWatch Events Rule: {str(e)}")

# from aws_cdk import core
# from aws_cdk.aws_events import Schedule, Rule, EventTarget
# from aws_cdk.aws_events_targets import LambdaFunction

# class MyStack(core.Stack):

#     def __init__(self, scope: core.Construct, construct_id: str, **kwargs) -> None:
#         super().__init__(scope, construct_id, **kwargs)

#         # Define Lambda function (replace with your actual Lambda construct)
#         get_niches_lambda = Fn.get_att(
#             "get_niches_lambda.Arn"  # Replace with your Lambda function logical ID
#         )

#         # Create CloudWatch Events rule - trigger every minute
#         get_niches_rule = Rule(
#             self, "get_niches_rule",
#             description="Trigger get_niches Lambda function every minute",
#             schedule=Schedule.cron(minute="*", hour="*", day_of_month="*", month="*", year="*")
#         )

#         # Add Lambda function as target for the rule
#         get_niches_rule.add_target(EventTarget(get_niches_lambda))

# app = core.App()
# MyStack(app, "get-niches-stack")
# app.synth()
