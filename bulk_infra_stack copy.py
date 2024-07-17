import aws_cdk as cdk
from constructs import Construct
from aws_cdk import aws_sns as sns
from aws_cdk import aws_sqs as sqs
from aws_cdk import aws_s3 as s3
from aws_cdk import aws_dynamodb as dynamodb
from aws_cdk import aws_kinesis as kinesis
from aws_cdk.aws_iam import Role, ServicePrincipal, PolicyStatement
from aws_cdk.aws_lambda import Function, Code, Runtime
from aws_cdk import aws_kinesisfirehose as firehose
from aws_cdk import aws_lambda as lambda_
from aws_cdk import aws_iam as iam
import yaml
from aws_cdk import aws_sns_subscriptions as subscriptions
from datetime import datetime


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

class BulkInfraStack(cdk.Stack):

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

        bucket_name=config_data["s3_bucket_name"]           

        # Create SNS Topics
        #niche_finder_notifications = sns.Topic(self, "niche-finder-notifications")
        affiliate_program_notifications = sns.Topic(self, "affiliate-program-notifications")
        campaign_notifications = sns.Topic(self, "campaign-notifications")
        campaign_content_notifications = sns.Topic(self, "campaign-content-notifications")
        campaign_metrics_notifications = sns.Topic(self, "campaign-metrics-notifications")

        # Create SQS Queues with Visibility Timeout set to None
        #niche_finder_queue = sqs.Queue(
        #    self,
        #    "niche-finder-queue",
        #    visibility_timeout=300,
        #)
        affiliate_program_queue = sqs.Queue(self, "affiliate-program-queue", visibility_timeout=cdk.Duration.seconds(300))
        campaign_queue = sqs.Queue(self, "campaign-queue", visibility_timeout=cdk.Duration.seconds(300))
        campaign_content_queue = sqs.Queue(self, "campaign-content-queue", visibility_timeout=cdk.Duration.seconds(300))
        campaign_metrics_queue = sqs.Queue(self, "campaign-metrics-queue", visibility_timeout=cdk.Duration.seconds(300))

        # Subscribe Queues to Topics
        #niche_finder_queue.subscribe(niche_finder_notifications)
        # Correctly subscribe SQS queues to SNS topics
        affiliate_program_notifications.add_subscription(subscriptions.SqsSubscription(affiliate_program_queue))
        campaign_notifications.add_subscription(subscriptions.SqsSubscription(campaign_queue))
        campaign_content_notifications.add_subscription(subscriptions.SqsSubscription(campaign_content_queue))
        campaign_metrics_notifications.add_subscription(subscriptions.SqsSubscription(campaign_metrics_queue))

        # Create S3 Bucket with Versioning
        #niche_finder_results_bucket = s3.Bucket(
        #    self, "niche-finder-results-bucket", versioning=True
        #)

        # Define Enums for DynamoDB Tables (you can customize these)
        #class Status(Enum):
        #    NEW = "new"
        #    RUNNING = "running"
        #    PAUSED = "paused"
        #    TERMINATED = "terminated"

        #class CostType(Enum):
        #    ON_DEMAND = "on-demand"
        #    USAGE = "usage"
        #    SUBSCRIPTION_BASED = "subscription-based"
        #    OTHER = "other"

        #class ServiceType(Enum):
        #   AI_SERVICE = "ai-service"
        #    INFRASTRUCTURE = "infrastructure"
        #    THIRD_PARTY_TOOL = "third-party-tool"
        #    DEVTOOL = "devtool"

        # Create DynamoDB Tables

        # Generate a unique identifier, e.g., current timestamp
        unique_id = datetime.now().strftime("%Y%m%d%H%M%S")

        # Append the unique identifier to the table names
        ai_affiliate_program_research_table = dynamodb.Table(
            self,
            f"ai-affiliate-program-research-{unique_id}",
            partition_key=dynamodb.Attribute(
                name="affiliate-program-id", type=dynamodb.AttributeType.STRING
            ),
            stream=dynamodb.StreamViewType.NEW_AND_OLD_IMAGES,
            removal_policy=cdk.RemovalPolicy.DESTROY,
        )

        subscription_service_cost_table = dynamodb.Table(
            self,
            f"subscription-service-cost-{unique_id}",
            partition_key=dynamodb.Attribute(
                name="cost-id", type=dynamodb.AttributeType.STRING
            ),
            stream=dynamodb.StreamViewType.NEW_AND_OLD_IMAGES,
            removal_policy=cdk.RemovalPolicy.DESTROY,
        )

        # Assuming ai_niche_research_table is defined elsewhere in your code, apply the same pattern
        ai_niche_research_table = dynamodb.Table(
            self,
            f"ai-niche-research-{unique_id}",
            partition_key=dynamodb.Attribute(
                name="niche-id", type=dynamodb.AttributeType.STRING
            ),
            stream=dynamodb.StreamViewType.NEW_AND_OLD_IMAGES,
            removal_policy=cdk.RemovalPolicy.DESTROY,
        )

        # Create Kinesis Data Stream for DynamoDB Change Data Capture (CDC)
        ai_marketing_stream = kinesis.Stream(self, "ai-marketing-streaming")

        # IAM Role for Firehose to access DynamoDB

        firehose_role = Role(
            self, "firehose-role",
            assumed_by=iam.ServicePrincipal("firehose.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonKinesisFirehoseFullAccess"),
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonS3FullAccess"),
                iam.ManagedPolicy.from_aws_managed_policy_name("AWSLambdaExecute")  # Only add if necessary for your use case
            ]
        )
  

        ai_niche_research_table.grant_read_data(firehose_role)
        subscription_service_cost_table.grant_read_data(firehose_role)
        ai_affiliate_program_research_table.grant_read_data(firehose_role)
        bucket_arn = "arn:aws:s3:::" + bucket_name
        # Replace with the actual ARN of your Lambda function
        #lambda_function_arn = boto3.client('lambda').get_function(FunctionName='your-lambda-function-name')['Configuration']['FunctionArn']


        # Create Kinesis Firehose Delivery Stream to S3

        # Lambda function to get the current timestamp
        get_timestamp_func = lambda_.Function(
            self,
            "get-timestamp-func",
            runtime=lambda_.Runtime.PYTHON_3_9,
            handler="get_timestamp.handler",  # Adjust the handler accordingly
            code=lambda_.Code.from_asset("lambda_functions/get_timestamp")
        )
        
        # Function to generate timestamp for 'created-date' and 'updated-date' attributes
        get_timestamp_function = lambda_.Function(
            self,
            "getN_3_9",
            runtime=lambda_.Runtime.PYTHON_3_9,  # Specify the runtime environment
            code=lambda_.Code.from_asset("lambda_functions/get_timestamp"),
            handler="get_timestamp.handler",
        )
        
        # Replace with the actual ARN of your Lambda function
        get_timestamp_function_arn = get_timestamp_function.function_arn

        # Lambda function to process DynamoDB update events before sending to Firehose
        process_dynamodb_update = lambda_.Function(
            self,
            "process-dynamodb-update",
            runtime=lambda_.Runtime.PYTHON_3_9,
            code=lambda_.Code.from_asset("lambda_functions/process_update"),  # Adjusted to point to a directory
            handler="process_dynamodb_update.handler",
            # Add other necessary properties for the Lambda function
        )

        # Define the S3 bucket
        s3_bucket = s3.Bucket.from_bucket_name(self, "BucketById", bucket_name)

        # Define the Lambda processor
        lambda_processor = lambda_.Function.from_function_arn(
            self, "LambdaProcessor", process_dynamodb_update.function_arn
        )

        # Create the Firehose delivery stream with a Lambda processor
        firehose_delivery_stream = firehose.CfnDeliveryStream(
            self,
            "ai-marketing-firehose",
            delivery_stream_type="DirectPut",
            extended_s3_destination_configuration=firehose.CfnDeliveryStream.ExtendedS3DestinationConfigurationProperty(
                bucket_arn=s3_bucket.bucket_arn,
                prefix="dynamodb-changes/ai-marketing/",
                compression_format="GZIP",
                role_arn=firehose_role.role_arn,
                processing_configuration=firehose.CfnDeliveryStream.ProcessingConfigurationProperty(
                    enabled=True,
                    processors=[
                        firehose.CfnDeliveryStream.ProcessorProperty(
                            type="Lambda",
                            parameters=[
                                firehose.CfnDeliveryStream.ProcessorParameterProperty(
                                    parameter_name="LambdaArn",
                                    parameter_value=lambda_processor.function_arn
                                ),
                                # Specifying the buffer size for the Lambda processor
                                firehose.CfnDeliveryStream.ProcessorParameterProperty(
                                    parameter_name="BufferSizeInMBs",
                                    parameter_value="3"
                                ),
                                # Reintroduced: Specifying the buffer interval for the Lambda processor
                                firehose.CfnDeliveryStream.ProcessorParameterProperty(
                                    parameter_name="BufferIntervalInSeconds",
                                    parameter_value="60"
                                )
                            ]
                        )
                    ]
                )
            )
        )
         

        # Configure Kinesis Firehose to capture changes from DynamoDB tables

        # Grant Firehose permission to invoke Lambda functions
        firehose_role.add_to_policy(
            statement=iam.PolicyStatement(
                actions=["lambda:InvokeFunction"],
                resources=[get_timestamp_function.function_arn],
            )
        )

        # Delivery stream for ai-niche-research table
        ai_niche_research_stream = firehose.CfnDeliveryStream(
            self,
            "ai-niche-research-firehose",
            delivery_stream_type="DirectPut",
            extended_s3_destination_configuration=firehose.CfnDeliveryStream.ExtendedS3DestinationConfigurationProperty(
                bucket_arn=s3_bucket.bucket_arn,
                prefix="dynamodb-changes/ai-niche-research/",
                compression_format="GZIP",
                role_arn=firehose_role.role_arn,
                processing_configuration=firehose.CfnDeliveryStream.ProcessingConfigurationProperty(
                    enabled=True,
                    processors=[
                        firehose.CfnDeliveryStream.ProcessorProperty(
                            type="Lambda",
                            parameters=[
                                firehose.CfnDeliveryStream.ProcessorParameterProperty(
                                    parameter_name="LambdaArn",
                                    parameter_value=lambda_processor.function_arn
                                )
                            ]
                        )
                    ]
                )
            ),
            # Note: The source property does not directly map to CfnDeliveryStream. You might need to configure this separately.
        )


        # Delivery streams for subscription_service_cost and ai_affiliate_program_research (similar to above)
        # ... You can repeat the same pattern for the remaining tables

        # Add tags to all resources for easy identification
        #self.add_tags_to_resource(niche_finder_notifications)
        # Add tags to all resources in the stack
        cdk.Tags.of(self).add("Key", "Value")
        # ... and so on for all resources