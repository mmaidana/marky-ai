import aws_cdk as cdk
from constructs import Construct
from aws_cdk import aws_sns as sns
from aws_cdk import aws_sqs as sqs
from aws_cdk import aws_s3 as s3
from aws_cdk import aws_dynamodb as dynamodb
from aws_cdk import aws_kinesis as kinesis
from aws_cdk.aws_iam import Role, ServicePrincipal, PolicyStatement
from aws_cdk.aws_lambda import Function, Code, Runtime #, RuntimeInfo
from aws_cdk import aws_kinesisfirehose as firehose
from aws_cdk import aws_lambda as lambda_
from aws_cdk import aws_iam as iam
import yaml
from aws_cdk import aws_sns_subscriptions as subscriptions
from datetime import datetime
import logging
import os
import uuid
import json

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)


class BulkInfraStack(cdk.Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        # Retrieve prompt and config file names from context
        prompt_file_name = self.node.try_get_context("prompt_file")
        config_file_name = self.node.try_get_context("config_file")

        if not prompt_file_name or not config_file_name:
            raise ValueError("Missing prompt_file or config_file context variables")
        
        #Loading Config Data
        config_data = self._load_config(config_file_name)
        #Loading Prompt Data prompt_data = self._load_prompt(prompt_file_name)

        unique_id = str(uuid.uuid4())  # Generate a unique ID
        data_stream_name = config_data.get("data_stream_name", "default-data-stream") # Get the data stream name from the config file
        s3_bucket_name = config_data["s3_bucket_name"] # Get the S3 bucket name from the config file
        self.s3_bucket = s3.Bucket.from_bucket_name(self, "BucketById",  s3_bucket_name) # Get the S3 bucket name from the config file
        bucket_arn = "arn:aws:s3:::"+ s3_bucket_name       # Create S3 bucket ARN

        # Create SNS Topics and SQS Queues
        sns_topics = self._create_sns_topics(config_data)
        sqs_queues = self._create_sqs_queues(config_data)

        # Subscribe queues to topics
        self._subscribe_queues_to_topics(sns_topics, sqs_queues)

        # Create Kinesis Data Stream for DynamoDB Change Data Capture (CDC)
        data_stream = self._create_data_stream() 

        # Create IAM role for Firehose
        firehose_role = self._create_firehose_role()

        # Create DynamoDB tables
        tables = self._create_dynamodb_tables(config_data, firehose_role, unique_id)  

        # Create Lambda functions
        #get_timestamp_func = self._create_get_timestamp_lambda()
        process_dynamodb_update = self._create_process_update_lambda()
        get_timestamp_function = self._create_get_timestamp_function()
        lambda_processor = self._create_lambda_processor(config_data)        
    

        # Create Firehose delivery streams
        firehose_streams = self._create_firehose_delivery_streams(config_data, firehose_role, lambda_processor)

        # Defining the helper methods for creating resources
        # Create Load Config Method    
        def _load_config(self, config_file):
            config_file_path = os.path.join("configs", f"{config_file}.yaml")  # Construct the full path
            try:
                with open(config_file_path, 'r') as file:
                    config_data = yaml.safe_load(file)
                return config_data
            except FileNotFoundError:
                raise ValueError(f"Config file not found: {config_file_path}")
            except yaml.YAMLError as e:
                raise ValueError(f"Error parsing YAML file: {e}")
        
        # Create Load Prompt Method
        def _load_prompt(self, prompt_file):
            prompt_file_path = os.path.join("configs", f"{prompt_file}.yaml")  # Construct the full path
            try:
                with open(prompt_file, 'r') as file:
                    prompt_data = file.read()
                return prompt_data
            except FileNotFoundError:
                raise ValueError(f"Prompt file not found: {prompt_file}")
            except Exception as e:
                raise ValueError(f"Error loading prompt file: {e}")
            
        # Create SNS Topics Method    
        def _create_sns_topics(self, config_data):
            topic_names = config_data.get('topic_names', {})
            sns_topics = {}
            for topic_name, topic_display_name in topic_names.items():
                sns_topics[topic_name] = sns.Topic(self, topic_display_name)
            return sns_topics
        
        # Create SQS Queues Method
        def _create_sqs_queues(self, config_data):
            queue_configs = config_data.get('queue_configs', {})
            sqs_queues = {}
            for queue_name, queue_config in queue_configs.items():
                queue = sqs.Queue(
                    self,
                    queue_config.get('name', queue_name),
                    visibility_timeout=cdk.Duration.seconds(queue_config.get('visibility_timeout', 300))
                )
                sqs_queues[queue_name] = queue
            return sqs_queues
        
        # Create Subscribe Queues to Topics Method
        def _subscribe_queues_to_topics(self, sns_topics, sqs_queues):
            for topic_name, topic in sns_topics.items():
                queue_name = topic_name  # Assuming topic and queue names match
                queue = sqs_queues.get(queue_name)
            if queue:
                topic.add_subscription(subscriptions.SqsSubscription(queue))

        # Create DynamoDB Tables Method
        def _create_dynamodb_tables(self, config_data, firehose_role, unique_id):
            table_names = config_data.get('table_names', {})
            tables = {}
            for table_name, table_config in table_names.items():
                table = dynamodb.Table(
                    self,
                    table_name-{unique_id},
                    partition_key=dynamodb.Attribute(
                        name="id",
                        type=dynamodb.AttributeType.STRING
                    ),
                    # Add other table attributes based on your requirements
                    stream=dynamodb.StreamViewType.NEW_AND_OLD_IMAGES,
                    removal_policy=cdk.RemovalPolicy.DESTROY,
                )
                tables[table_name] = table
                table.grant_read_data(firehose_role)  # Grant read permissions to Firehose role
            return tables
        
        # Create Kinesis Data Stream with retrieved name
        def _create_data_stream(self):
            data_stream = kinesis.Stream(
                self,
                data_stream_name,
                shard_count=1,  # Adjust shard count as needed
            )
            return data_stream

        # Create Firehose Role Method
        def _create_firehose_role(self):
            firehose_role = Role(
                self, "firehose-role",
                assumed_by=iam.ServicePrincipal("firehose.amazonaws.com"),
                managed_policies=[
                    iam.ManagedPolicy.from_aws_managed_policy_name("AmazonKinesisFirehoseFullAccess"),
                    iam.ManagedPolicy.from_aws_managed_policy_name("AmazonS3FullAccess"),
                    iam.ManagedPolicy.from_aws_managed_policy_name("AWSLambdaExecute")  # Only add if necessary for your use case
                ]
            )
            return firehose_role

        # Lambda function to get the current timestamp
        def _create_get_timestamp_lambda(self):

            get_timestamp_func = lambda_.Function(
                self,
                "get-timestamp-func",
                runtime=lambda_.Runtime.PYTHON_3_9,
                handler="get_timestamp.handler",  # Adjust the handler accordingly
                code=lambda_.Code.from_asset("lambda_functions/get_timestamp")
            )
            return get_timestamp_func
        
        # Lambda function to process DynamoDB update events before sending to Firehose
        def _create_process_update_lambda(self):

            process_dynamodb_update = lambda_.Function(
                self,
                "process-dynamodb-update",
                runtime=lambda_.Runtime.PYTHON_3_9,
                handler="process_dynamodb_update.handler",  # Adjust the handler accordingly
                code=lambda_.Code.from_asset("lambda_functions/process_update")
                #environment={
                #    "TABLE_NAMES": json.dumps(table_names),  # Pass table names to Lambda function
                # Other environment variables if needed
                #}
            )
            return process_dynamodb_update
        
        # Function to generate timestamp for 'created-date' and 'updated-date' attributes
        def _create_get_timestamp_function(self):
            get_timestamp_function = lambda_.Function(
                self,
                "get-timestamp-func",
                runtime=lambda_.Runtime.PYTHON_3_9,
                code=lambda_.Code.from_asset("lambda_functions/get_timestamp"),
                handler="get_timestamp.handler",
            )
            return get_timestamp_function
        
        # Define the Lambda processor
        def _create_lambda_processor(self, config_data):
            table_names = config_data.get('table_names', [])
            # Define the Lambda processor
            lambda_processor = lambda_.Function.from_function_arn(
                self, "LambdaProcessor", process_dynamodb_update.function_arn
            )

            # Grant permissions to Lambda functions
            for table_name in table_names:
                table = tables[table_name]
                table.grant_read_data(process_dynamodb_update)

            return lambda_processor

       
        def _create_firehose_delivery_streams(self, config_data, firehose_role, lambda_processor):
            table_names = config_data.get('table_names', [])
            data_stream_name = config_data.get('data_stream_name', 'default-data-stream')
            s3_bucket_name = config_data.get('s3_bucket_name', 'default-bucket')

            s3_bucket = s3.Bucket(
                self,
                s3_bucket_name
            )

            delivery_stream_names = [data_stream_name] + [f"{name}-firehose" for name in table_names]

            firehose_streams = {}
            for delivery_stream_name in delivery_stream_names:
                firehose_stream = firehose.CfnDeliveryStream(
                    self,
                    delivery_stream_name,
                    # ... Firehose configuration
                    delivery_stream_type="DirectPut",
                    extended_s3_destination_configuration=firehose.CfnDeliveryStream.ExtendedS3DestinationConfigurationProperty(
                        bucket_arn=s3_bucket.bucket_arn,
                        prefix=f"dynamodb-changes/{delivery_stream_name.split('-')[1]}/",  # Use table name from delivery stream name
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
                                    ] + ([
                                        firehose.CfnDeliveryStream.ProcessorParameterProperty(
                                            parameter_name="BufferSizeInMBs",
                                            parameter_value="3"
                                        ),
                                        firehose.CfnDeliveryStream.ProcessorParameterProperty(
                                            parameter_name="BufferIntervalInSeconds",
                                            parameter_value="60"
                                        )
                                    ] if delivery_stream_name == data_stream_name else [])
                                )
                            ]
                        )
                    ),
                    # ... other Firehose configurations
                )
                firehose_streams[delivery_stream_name] = firehose_stream
            return firehose_streams

        # Configure Kinesis Firehose to capture changes from DynamoDB tables
        # Grant Firehose permission to invoke Lambda functions
        firehose_role.add_to_policy(
            statement=iam.PolicyStatement(
                actions=["lambda:InvokeFunction"],
                resources=[get_timestamp_function.function_arn],
            )
        )

        # Add tags to all resources for easy identification
        # Add tags to all resources in the stack
        cdk.Tags.of(self).add("Key", "Value")
