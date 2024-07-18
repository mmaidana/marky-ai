from constructs import Construct
import aws_cdk as cdk
from aws_cdk.aws_iam import  ManagedPolicy, Role, ServicePrincipal  # Import ManagedPolicy and Role
from aws_cdk.aws_lambda import Function, Code, Runtime
from aws_cdk import aws_iam as iam
from aws_cdk import aws_events as events
from aws_cdk.aws_events import Rule, Schedule
from aws_cdk import aws_events_targets as targets
from lib.custom_constructs.config_construct import ConfigConstruct

class NicheFinder(cdk.Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Loading Config Data
        config_data = ConfigConstruct(self, "MainInfrastructureConfig", config_file_path="configs/main-infrastructure.yaml") 
            
        # IAM Role for Lambda function
        lambda_role = self._create_lambda_role()

        # Lambda function 
        lambda_fn = self._create_lambda_fn(lambda_role)

        # CloudWatch Events Rule for Lambda function
        self._create_cloudwatch_rule_for_lambda(lambda_fn, config_data)        

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
    def _create_lambda_fn(self, lambda_role):
        try:
            # Lambda function (receive prompt and config file names from config data construct)
            lambda_fn = Function(self, "NicheFinderLambdaFn",
                                 runtime=Runtime.PYTHON_3_9,
                                 code=Code.from_asset("lambda_handler"),
                                 handler="NicheFinder.handler",
                                 role=lambda_role,
                                 environment={
                                     "S3_BUCKET_NAME": niche_finder_results_bucket.bucket_name,
                                     "SQS_QUEUE_URL": niche_finder_queue.queue_url,
                                     "SNS_TOPIC_ARN": niche_finder_topic.topic_arn,
                                     "SNS_PHONE_NUMBER": config_data.get("phone_number"),  # Optional
                                     "SNS_EMAIL_ADDRESS": config_data.get("email_address"),  # Optional
                                 })
            return lambda_fn
        except Exception as e:
            print(f"Error creating Lambda function: {str(e)}")
            return None
        

    # Create CloudWatch Events Rule for Lambda function
    # How you trigger the Lambda function will determine how you pass the parameters.
    # Here's an example using CloudWatch Events (replace with your chosen trigger):
    def _create_cloudwatch_rule_for_lambda(self, lambda_fn, config_data):
        try:
            # CloudWatch Events Rule (schedule execution every hour)
            rule = Rule(self, "NicheFinderRule",
                        schedule=Schedule.expression(config_data["cloudwatch_schedule_expression"]))
            # Schedule from config

            rule.add_target(targets.LambdaFunction(lambda_fn,
                event=events.RuleTargetInput.from_object({
                    "prompt_file": prompt_file_name,
                    "config_file": config_file_name,
                })
            ))
        except Exception as e:
            print(f"Error creating CloudWatch Events Rule: {str(e)}")