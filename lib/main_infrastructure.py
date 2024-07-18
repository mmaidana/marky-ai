import aws_cdk as cdk
from constructs import Construct
from aws_cdk import aws_sns as sns 
from aws_cdk.aws_sns import Subscription,  SubscriptionProtocol
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
import logging
import uuid
from aws_cdk import aws_logs as logs
from .custom_constructs.config_construct import ConfigConstruct
from aws_cdk import aws_sns_subscriptions as subscriptions

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)


class MainInfrastructureStack(cdk.Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        try:
            # Loading Config Data
            config_data = ConfigConstruct(self, "MainInfrastructureConfig", config_file_path="configs/main-infrastructure.yaml") 
            shared_config_data = ConfigConstruct(self, "SharedConfig", config_file_path="configs/shared-data.yaml")

            # ... create S3 buckets, DynamoDB tables, etc. using bucket_names and table_names from config_data ...
            unique_id = str(uuid.uuid4())  # Generate a unique ID
            self.data_stream_name = config_data.get_value("data_stream_name") # Get the data stream name from the config file

            # Access the 'bucket_names' dictionary and then the 'stream_bucket' value
            bucket_names = config_data.get_value('bucket_names')
            s3_stream_bucket_name = bucket_names.get('data-stream-bucket')
            self.s3_stream_bucket = s3.Bucket.from_bucket_name(self, "BucketById",  s3_stream_bucket_name) # Get the S3 bucket name from the config file

            # Create S3 Buckets
            s3_buckets = self._create_s3_buckets(config_data, unique_id)
            
            # Create SNS Topics and SQS Queues
            sns_topics = self._create_sns_topics(config_data, unique_id, shared_config_data)
            sqs_queues = self._create_sqs_queues(config_data, unique_id)

            # Subscribe queues to topics
            self._subscribe_queues_to_topics(sns_topics, sqs_queues)

            # Create Kinesis Data Stream for DynamoDB Change Data Capture (CDC)
            #data_stream = self._create_data_stream(config_data) 

            # Create IAM role for Firehose
            firehose_role = self._create_firehose_role()

            # Create DynamoDB tables
            tables = self._create_dynamodb_tables(config_data, firehose_role, unique_id)
            table_names = config_data.get_value('table_names', [])  

            # Create Lambda functions
            process_dynamodb_update = self._create_process_update_lambda()
            get_timestamp_function = self._create_get_timestamp_function()
            lambda_processor = self._create_lambda_processor(config_data,process_dynamodb_update, tables)        
        
            # Create Firehose delivery streams
            #firehose_streams = self._create_firehose_delivery_streams(firehose_role, lambda_processor, data_stream_name=self.data_stream_name, s3_bucket=self.s3_stream_bucket, table_names=table_names, unique_id=unique_id, get_timestamp_function=get_timestamp_function)

            # Add tags to all resources for easy identification
            cdk.Tags.of(self).add("Key", "Value")

        except FileNotFoundError as e:
            print(f"Error: Configuration file not found - {e}")
            # Handle the error, e.g., raise a custom exception, log the error, etc.
            #cdk.App().synth()  # Optional: Synthesize the CDK CloudFormation template even on error
        except yaml.YAMLError as e:
            print(f"Error parsing YAML file: {e}")
            # Handle the error, e.g., raise a custom exception, log the error, etc.
        except ValueError as e:
            print(f"Wrong Method or value error: {e}")
        except Exception as e:
            print(f"Error loading configuration - Unexpected error: {e}")
            # Handle the error, e.g., raise a custom exception, log the error, etc.
            #cdk.App().synth()  # Optional: Synthesize the CDK CloudFormation template even on error
            
    # Defining the helper methods for creating resources
    # Create Bucket Method
    def _create_s3_buckets(self, config_data, unique_id):
        bucket_names = config_data.get_value('bucket_names', {})
        s3_buckets = {}

        for bucket_name, actual_bucket_name in bucket_names.items():
            try:
                 # Append a UUID to the actual bucket name to ensure uniqueness
                unique_bucket_name = f"{actual_bucket_name}-{unique_id}"
                s3_bucket = s3.Bucket(
                    self, bucket_name,
                    bucket_name=unique_bucket_name,
                    encryption=s3.BucketEncryption.KMS_MANAGED,
                    removal_policy=cdk.RemovalPolicy.DESTROY
                )
                s3_buckets[bucket_name] = s3_bucket
            except Exception as e:
                print(f"Failed to create bucket {bucket_name}: {e}")

        return s3_buckets
            
    def _create_sns_topics(self, config_data, unique_id, shared_config_data):
        # Retrieve topic names from config_data, defaulting to an empty dictionary if not found
        topic_names = config_data.get_value('topic_names', {})
        sns_topics = {}

        for topic_name, topic_display_name in topic_names.items():
            try:
                # Debugging: Print the type and value of topic_display_name
                #print(f"Debug: topic_name={topic_name}, type={type(topic_display_name).__name__}, value={topic_display_name}")

                # Ensure topic_display_name is a string to prevent runtime errors
                if not isinstance(topic_display_name, str):
                    # Provide a clear error message indicating the expected type and the actual type received
                    raise ValueError(f"Display name for topic '{topic_name}' must be a string, got {type(topic_display_name).__name__}")

                unique_topic_name = f"{topic_name}-{unique_id}" # Append unique ID to topic name
                # Create an SNS topic with the specified name and display name, and store it in the sns_topics dictionary
                sns_topics[topic_name] = sns.Topic(self, id=unique_topic_name, display_name=topic_display_name)
                Subscription(self, f"EmailSubscription-{topic_name}",
                             topic=sns_topics[topic_name],
                             protocol=SubscriptionProtocol.EMAIL,
                             endpoint=shared_config_data["subscription-email-address"])  # Required
                Subscription(self, f"PhoneSubscription-{topic_name}",
                             topic=sns_topics[topic_name],
                             protocol=SubscriptionProtocol.SMS,
                             endpoint=shared_config_data["subscription-phone-number"])  # Required
            except Exception as e:
                print(f"Failed to create SNS topic '{topic_name}': {e}")

        # Return the dictionary of created SNS topics
        return sns_topics
    
    def _create_sqs_queues(self, config_data, unique_id):
        queue_configs = config_data.get_value('queue_configs', {})
        sqs_queues = {}

        for queue_name, queue_config in queue_configs.items():
            try:
                # Ensure unique names by appending a suffix or modifying the naming strategy
                unique_queue_name = f"{queue_name}-queue-{unique_id}"  # Example modification

                # Check if the unique name already exists to avoid conflicts
                if unique_queue_name in self.node.children:
                    raise ValueError(f"A construct with the name {unique_queue_name} already exists in the stack")

                # Create the SQS queue with the unique name
                queue = sqs.Queue(
                    self, unique_queue_name,
                    queue_name=queue_config['name'],
                    visibility_timeout=cdk.Duration.seconds(queue_config['visibility_timeout'])
                )
                sqs_queues[queue_name] = queue
            except Exception as e:
                print(f"Failed to create SQS queue '{queue_name}': {e}")

        return sqs_queues
    
    # Create Subscribe Queues to Topics Method
    def _subscribe_queues_to_topics(self, sns_topics, sqs_queues):
        for topic_name, topic in sns_topics.items():
            # Extract the relevant part of the topic name (modify based on your pattern)
            queue_name_prefix = topic_name.split("-")[0]  # Assuming "-" separates topic and queue names

            # Find the queue that starts with the extracted prefix
            for queue_name, queue in sqs_queues.items():
                if queue_name.startswith(queue_name_prefix):
                    try:
                        topic.add_subscription(subscriptions.SqsSubscription(queue))
                        #print(f"Subscribed queue '{queue_name}' to topic '{topic_name}'")
                        break  # Exit inner loop once a matching queue is found
                    except Exception as e:
                        print(f"Failed to subscribe queue '{queue_name}' to topic '{topic_name}': {e}")
                        continue  # Continue the inner loop to find another matching queue

            # Handle scenario where no matching queue is found for the topic
            else:
                print(f"No queue found for topic '{topic_name}' with prefix '{queue_name_prefix}'")


    # Create DynamoDB Tables Method
    def _create_dynamodb_tables(self, config_data, firehose_role, unique_id):
        table_names = config_data.get_value('table_names', {})
        tables = {}
        for table_name, table_config in table_names.items():
            try:
                # Corrected string formatting for table name
                corrected_table_name = f"{table_name}-{unique_id}"
                # Ensure the construct ID is unique within the stack
                construct_id = f"{corrected_table_name}-{unique_id}"
                table = dynamodb.Table(
                    self,
                    construct_id,
                    #table_name=corrected_table_name,
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
            except Exception as e:
                print(f"Failed to create DynamoDB table '{table_name}': {e}") 
        return tables
    
    # Create Kinesis Data Stream with retrieved name
    def _create_data_stream(self, config_data):
        try:
            data_stream_name = config_data.get_value('data_stream_name', 'default-data-stream')
            data_stream = kinesis.Stream(
                self,
                data_stream_name,
                shard_count=1,  # Adjust shard count as needed
                removal_policy=cdk.RemovalPolicy.DESTROY
            )
            return data_stream
        except Exception as e:
            print(f"Failed to create Kinesis Data Stream: {e}")
            # Handle the error, e.g., raise a custom exception, log the error, etc.
            return None

    # Create Firehose Role Method
    def _create_firehose_role(self):
        try:
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
        except Exception as e:
            print(f"Failed to create Firehose role: {e}")
            # Handle the error, e.g., raise a custom exception, log the error, etc.
            return None
    
    # Lambda function to process DynamoDB update events before sending to Firehose
    def _create_process_update_lambda(self):
        try:
            process_dynamodb_update = lambda_.Function(
                self,
                "process-dynamodb-update",
                runtime=lambda_.Runtime.PYTHON_3_9,
                handler="process_dynamodb_update.handler",  # Adjust the handler accordingly
                code=lambda_.Code.from_asset("lambda_handler/infrastructure/process_update")
                #environment={
                #    "TABLE_NAMES": json.dumps(table_names),  # Pass table names to Lambda function
                # Other environment variables if needed
                #}
            )
            return process_dynamodb_update
        except Exception as e:
            print(f"Failed to create process update Lambda function: {e}")
            # Handle the error, e.g., raise a custom exception, log the error, etc.
            return None
    
    # Function to generate timestamp for 'created-date' and 'updated-date' attributes
    def _create_get_timestamp_function(self):
        try:
            get_timestamp_function = lambda_.Function(
                self,
                "get-timestamp-func",
                runtime=lambda_.Runtime.PYTHON_3_9,
                code=lambda_.Code.from_asset("lambda_handler/infrastructure/get_timestamp"),
                handler="get_timestamp.handler",
            )
            return get_timestamp_function
        except Exception as e:
            print(f"Failed to create get timestamp Lambda function: {e}")
            # Handle the error, e.g., raise a custom exception, log the error, etc.
            return None
    
    # Define the Lambda processor
    def _create_lambda_processor(self, config_data, process_dynamodb_update, tables):
        table_names = tables.keys()
        try:
            # Define the Lambda processor
            lambda_processor = lambda_.Function.from_function_arn(
                self, "LambdaProcessor", process_dynamodb_update.function_arn
            )

            # Grant permissions to Lambda functions
            for table_name in table_names:
                table = tables[table_name]
                table.grant_read_data(process_dynamodb_update)

            return lambda_processor
        except Exception as e:
            print(f"Failed to create Lambda processor: {e}")
            # Handle the error, e.g., raise a custom exception, log the error, etc.
            return None

    
    def _create_firehose_delivery_streams(self, firehose_role, lambda_processor, data_stream_name, s3_bucket, table_names, unique_id, get_timestamp_function):
        
        # Initialize a counter for unique name generation
        counter = 1
    
        delivery_stream_names = [data_stream_name] + [f"{name}-firehose" for name in table_names]
        firehose_streams = {}

        # Grant Firehose permission to invoke Lambda functions
        def _grant_firehose_invoke_lambda_permission(firehose_role, get_timestamp_function):
            try:
                firehose_role.add_to_policy(
                    statement=iam.PolicyStatement(
                        actions=["lambda:InvokeFunction"],
                        resources=[get_timestamp_function.function_arn],
                    )
                )
            except Exception as e:
                print(f"Failed to grant Firehose invoke permission to Lambda function: {e}")

        for name in delivery_stream_names:
            # Append a counter to ensure uniqueness
            unique_delivery_stream_name = f"{name}-{unique_id}"
            counter += 1
    
            # Directly use the table name for the prefix if available, else use a default
            prefix = f"dynamodb-changes/{name.split('-')[0]}/" if '-' in name else "dynamodb-changes/default/"
    
            if lambda_processor and lambda_processor.function_arn:
                try:
                    firehose_stream = firehose.CfnDeliveryStream(
                        self,
                        unique_delivery_stream_name,
                        delivery_stream_type="DirectPut",
                        extended_s3_destination_configuration=firehose.CfnDeliveryStream.ExtendedS3DestinationConfigurationProperty(
                            bucket_arn=s3_bucket.bucket_arn,
                            prefix=prefix,  # Use table name from delivery stream name
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
                                        ] if name == data_stream_name else [])
                                    )
                                ]
                            )
                        ),
                    )
                    firehose_streams[unique_delivery_stream_name] = firehose_stream
                    _grant_firehose_invoke_lambda_permission(firehose_role, get_timestamp_function)
                except Exception as e:
                    print(f"Failed to create Firehose delivery stream '{unique_delivery_stream_name}': {e}")
            else:
                print(f"Failed to create Firehose delivery stream '{unique_delivery_stream_name}': Lambda processor is None or its function_arn is not available")
        return firehose_streams