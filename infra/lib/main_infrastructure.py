import aws_cdk as cdk
from constructs import Construct
from aws_cdk import aws_sns as sns 
from aws_cdk.aws_sns import Subscription,  SubscriptionProtocol
from aws_cdk import aws_sqs as sqs
from aws_cdk import aws_s3 as s3
from aws_cdk import aws_dynamodb as dynamodb
from aws_cdk import aws_kinesis as kinesis
from aws_cdk.aws_iam import Role
from aws_cdk import aws_kinesisfirehose as firehose
from aws_cdk import aws_lambda as lambda_
from aws_cdk import aws_iam as iam
import yaml
from aws_cdk import aws_sns_subscriptions as subscriptions
import logging
import uuid
from .custom_constructs.config_construct import ConfigConstruct
from aws_cdk import aws_logs as logs
from aws_cdk.aws_lambda import Code, Runtime
import boto3
import re



class MainInfrastructureStack(cdk.Stack):

    def __init__(self, scope: Construct, construct_id: str, common_stack, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)        

        try:

            # Create Logger Instance
            StackName = cdk.Stack.of(self).stack_name
            logger = common_stack._create_logger(StackName=StackName)
            self.logger = logger


            logger.info("Loading configuration and Creating Constructs in MainInfrastructureStack")
            # Loading Config Data
            config_data = ConfigConstruct(self, "MainInfrastructureConfig", config_file_path="main-infrastructure.yaml")
            logger.info("Configuration data loaded successfully in MainInfrastructureStack")
            log_group_name = config_data.get_value("log_group_name")

            # Define the log group for infrastructure deployment logs
            logger.info("Creating log group for infrastructure deployment logs")
            self.log_group = common_stack._create_log_group(log_group_name, StackName= StackName) 

            shared_config_data = ConfigConstruct(self, "SharedConfig", config_file_path="shared-data.yaml")
            logger.info("Shared Configuration data loaded successfully in MainInfrastructureStack")

            # ... create S3 buckets, DynamoDB tables, etc. using bucket_names and table_names from config_data ...
            unique_id = str(uuid.uuid4())  # Generate a unique ID

            
            self.data_stream_name = config_data.get_value("data-stream-name") # Get the data stream name from the config file
            logger.info(f"Creating Data Stream Name: {self.data_stream_name}")
            
            # Access the 'bucket_names' dictionary and then the 'stream_bucket' value
            bucket_names = config_data.get_value('bucket_names')
            s3_stream_bucket_name = bucket_names.get('data-stream-bucket')
            self.s3_stream_bucket = s3.Bucket.from_bucket_name(self, "BucketById",  s3_stream_bucket_name) # Get the S3 bucket name from the config file
            logger.info(f"Data Stream Bucket Created - Name: {s3_stream_bucket_name}")

            # Create S3 Buckets
            logger.info("Creating S3 Buckets")
            s3_buckets = self._create_s3_buckets(config_data, unique_id)
            
            # Create SNS Topics and SQS Queues
            logger.info("Creating SNS Topics")
            sns_topics = self._create_sns_topics(config_data, unique_id, shared_config_data)
            logger.info("Creating SQS Queues")
            sqs_queues = self._create_sqs_queues(config_data, unique_id)

            # Subscribe queues to topics
            logger.info("Subscribing Queues to Topics")
            self._subscribe_queues_to_topics(sns_topics, sqs_queues)

            # Create Kinesis Data Stream for DynamoDB Change Data Capture (CDC)
            logger.info("Creating Kinesis Data Stream (disabled)")
            #data_stream = self._create_data_stream(config_data) 

            # Create IAM role for Firehose
            logger.info("Creating Firehose Role")
            firehose_role = self._create_firehose_role()

            # Create DynamoDB tables
            logger.info("Creating DynamoDB Tables")
            tables = self._create_dynamodb_tables(config_data, firehose_role, unique_id)
            table_names = config_data.get_value('table_names', [])  

            # Create Lambda functions
            logger.info("Creating Process Update Lambda Function for DynamoDB and Kinesis")
            # Adjust the path to where your lambda_handler directory is located relative to the script execution path
            self.lambda_handler_path = "./infra/lambda_handler/infrastructure"  # Example if you're in /Users/marcelo/dev
            self.logger.info(f"Lambda Handler path: {self.lambda_handler_path}")
            process_dynamodb_update = self._create_process_update_lambda()
            get_timestamp_function = self._create_get_timestamp_function()
            lambda_processor = self._create_lambda_processor(config_data,process_dynamodb_update, tables)        
        
            # Create Firehose delivery streams
            logger.info("Creating Firehose Delivery Streams (Disabled)")
            #firehose_streams = self._create_firehose_delivery_streams(firehose_role, lambda_processor, data_stream_name=self.data_stream_name, s3_bucket=self.s3_stream_bucket, table_names=table_names, unique_id=unique_id, get_timestamp_function=get_timestamp_function)
            end_logger = common_stack._end_logger(StackName=StackName)

        except FileNotFoundError as e:
            #print(f"Error: Configuration file not found - {e}")
            logger.error(f"Error: Configuration file not found - {e}")
            # Handle the error, e.g., raise a custom exception, log the error, etc.
            #cdk.App().synth()  # Optional: Synthesize the CDK CloudFormation template even on error
        except yaml.YAMLError as e:
            #print(f"Error parsing YAML file: {e}")
            logger.error(f"Error parsing YAML file: {e}")
            # Handle the error, e.g., raise a custom exception, log the error, etc.
        except ValueError as e:
            #print(f"Wrong Method or value error: {e}")
            logger.error(f"Wrong Method or value error: {e}")
        except Exception as e:
            #print(f"Error loading configuration - Unexpected error: {e}")
            logger.error(f"Error loading configuration - Unexpected error: {e}")
            # Handle the error, e.g., raise a custom exception, log the error, etc.
            #cdk.App().synth()  # Optional: Synthesize the CDK CloudFormation template even on error


    # Add tags to all resources for easy identification
    def _create_resource_tagger(self, key, value):
        cdk.Tags.of(self).add(key, value)            
        self.logger.info(f"Adding the following tag to resource key:{key} - value:{value}")

            
    # Defining the helper methods for creating resources
    # Create Bucket Method
    def _create_s3_buckets(self, config_data, unique_id):
        bucket_names = config_data.get_value('bucket_names', {})
        s3_buckets = {}
        self._create_resource_tagger("ResourceType", "S3 Bucket")
        for bucket_name, actual_bucket_name in bucket_names.items():
            unique_bucket_name = self._generate_unique_resource_name(actual_bucket_name, unique_id)
            try:
                s3_bucket = self._create_single_s3_bucket(bucket_name, unique_bucket_name)
                s3_buckets[bucket_name] = s3_bucket
                self.logger.info(f"Created S3 bucket '{bucket_name}' with unique name '{unique_bucket_name}'")
                self._create_resource_tagger("BucketName", bucket_name)
            except Exception as e:
                self.logger.error(f"Failed to create S3 bucket '{bucket_name}': {e}")
                self._handle_bucket_creation_error(bucket_name, e)

        return s3_buckets
    
    # Generate Unique Resource Name Method
    def _generate_unique_resource_name(self, base_name, unique_id):
        """
        Generates a unique name for any resource by appending a unique ID.

        Parameters:
        - base_name: The base name of the resource.
        - unique_id: A unique identifier to ensure the resource name is unique.

        Returns:
        A string representing the unique resource name.
        """
        try:
            self.logger.info(f"Generating unique name for {base_name}-{unique_id}")
            return f"{base_name}-{unique_id}"
        except Exception as e:
            self.logger.error(f"Error generating unique name for {base_name}: {e}")
            return None

    def _create_single_s3_bucket(self, bucket_name, unique_bucket_name):
        try:
            return s3.Bucket(
                self, bucket_name,
                bucket_name=unique_bucket_name,
                encryption=s3.BucketEncryption.KMS_MANAGED,
                removal_policy=cdk.RemovalPolicy.DESTROY
            )
        except Exception as e:
            self.logger.error(f"Error creating S3 bucket {bucket_name}: {e}")
            return None

    def _handle_bucket_creation_error(self, bucket_name, error):
        self.logger.error(f"Failed to create bucket {bucket_name}: {error}")
            
    def _create_sns_topics(self, config_data, unique_id, shared_config_data):
        # Retrieve topic names from config_data, defaulting to an empty dictionary if not found
        topic_names = config_data.get_value('topic_names', {})
        sns_topics = {}
        self._create_resource_tagger("ResourceType", "SNS Topic")
        for topic_name, topic_display_name in topic_names.items():
            try:
                # Debugging: Print the type and value of topic_display_name
                #print(f"Debug: topic_name={topic_name}, type={type(topic_display_name).__name__}, value={topic_display_name}")

                # Ensure topic_display_name is a string to prevent runtime errors
                if not isinstance(topic_display_name, str):
                    # Provide a clear error message indicating the expected type and the actual type received
                    raise ValueError(f"Display name for topic '{topic_name}' must be a string, got {type(topic_display_name).__name__}")

                unique_topic_name = self._generate_unique_resource_name(topic_name, unique_id) #f"{topic_name}-{unique_id}" # Append unique ID to topic name
                # Create an SNS topic with the specified name and display name, and store it in the sns_topics dictionary
                sns_topics[topic_name] = sns.Topic(self, id=unique_topic_name, display_name=topic_display_name)
                self.logger.info(f"Created SNS topic '{topic_name}' with display name '{topic_display_name}'")
                Subscription(self, f"EmailSubscription-{topic_name}",
                             topic=sns_topics[topic_name],
                             protocol=SubscriptionProtocol.EMAIL,
                             endpoint=shared_config_data["subscription-email-address"])  # Required
                Subscription(self, f"PhoneSubscription-{topic_name}",
                             topic=sns_topics[topic_name],
                             protocol=SubscriptionProtocol.SMS,
                             endpoint=shared_config_data["subscription-phone-number"])  # Required
                self.logger.info(f"Subscribed email and phone number to SNS topic {topic_name}")
                self._create_resource_tagger("TopicName", topic_name)
            except Exception as e:
                self.logger.error(f"Failed to create SNS topic '{topic_name}': {e}")

        # Return the dictionary of created SNS topics
        return sns_topics
    
    def _create_sqs_queues(self, config_data, unique_id):
        sqs_client = boto3.client('sqs', region_name=config_data.get_value("region"))  # Specify your region
        queue_configs = config_data.get_value('queue_configs', {})
        sqs_queues = {}
        self._create_resource_tagger("ResourceType", "SQS Queue")

        for queue_name, queue_config in queue_configs.items():
            try:
                # Ensure unique names by appending a suffix or modifying the naming strategy
                unique_queue_name = self._generate_unique_resource_name(queue_name, unique_id) #f"{queue_name}-queue-{unique_id}"  # Example modification

                # Check if the SQS queue exists
                queues = sqs_client.list_queues(QueueNamePrefix=queue_config['name'])
                queue_urls = queues.get('QueueUrls', [])

                queue_exists = any(queue_config['name'] in url for url in queue_urls)
                self.logger.info(f"Queue exists: {queue_exists} -  Queue Name: {unique_queue_name} - Queue URL: {queue_urls}")
                if not queue_exists:
                    # Queue does not exist, create it
                    queue = sqs.Queue(
                        self, unique_queue_name,
                        queue_name=queue_config['name'],
                        visibility_timeout=cdk.Duration.seconds(queue_config['visibility_timeout'])
                    )
                    self.logger.info(f"Created SQS queue '{queue_name}' with unique name '{unique_queue_name}'"),
                    sqs_queues[queue_name] = queue
                else:   
                    # Queue already exists
                    self.logger.info(f"Queue '{unique_queue_name}' already exists.")
            except Exception as e:
                self.logger.error(f"Failed to create SQS queue '{queue_name}': {e}")

        return sqs_queues
    
    # Create Subscribe Queues to Topics Method
    def _subscribe_queues_to_topics(self, sns_topics, sqs_queues):
        for topic_name, topic in sns_topics.items():
            # Extract the relevant part of the topic name (modify based on your pattern)
            queue_name_prefix = topic_name.split("-")[0]  # Assuming "-" separates topic and queue names
            #queue_name_pattern = r"(.*?)-"  # Matches everything before the last "-"
            #for topic_name, topic in sns_topics.items():
                # Extract the prefix using the regular expression
                #queue_name_prefix = re.match(queue_name_pattern, topic_name).group(1)
                #self.logger.info(f"Extracted queue name prefix '{queue_name_prefix}' from topic '{topic_name}'")


            # Find the queue that starts with the extracted prefix
            for queue_name, queue in sqs_queues.items():
                if queue_name.startswith(queue_name_prefix):
                    try:
                        topic.add_subscription(subscriptions.SqsSubscription(queue))
                        self.logger.info(f"Subscribed queue '{queue_name}' to topic '{topic_name}'")
                        break  # Exit inner loop once a matching queue is found
                    except Exception as e:
                        self.logger.error(f"Failed to subscribe queue '{queue_name}' to topic '{topic_name}': {e}")
                        continue  # Continue the inner loop to find another matching queue

            # Handle scenario where no matching queue is found for the topic
            else:
               self.logger.error(f"No queue found for topic '{topic_name}' with prefix '{queue_name_prefix}'")


    # Create DynamoDB Tables Method
    def _create_dynamodb_tables(self, config_data, firehose_role, unique_id):
        table_names = config_data.get_value('table_names', {})
        tables = {}
        for table_name, table_config in table_names.items():
            try:
                # Corrected string formatting for table name
                corrected_table_name = self._generate_unique_resource_name(table_name, unique_id) #f"{table_name}-{unique_id}"
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
                self.logger.error(f"Failed to create DynamoDB table '{table_name}': {e}") 
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
            self.logger.info(f"Created Kinesis Data Stream '{data_stream_name}'")
            return data_stream
        except Exception as e:
            self.logger.error(f"Failed to create Kinesis Data Stream: {e}")
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
            self.logger.info("Created Firehose role")
            return firehose_role
        except Exception as e:
            self.logger.error(f"Failed to create Firehose role: {e}")
            # Handle the error, e.g., raise a custom exception, log the error, etc.
            return None
    
    # Lambda function to process DynamoDB update events before sending to Firehose
    def _create_process_update_lambda(self):
        try:
            process_dynamodb_update = lambda_.Function(
                self,
                "process-dynamodb-update",
                runtime=lambda_.Runtime.PYTHON_3_9,
                code=lambda_.Code.from_asset(f"{self.lambda_handler_path}/process_update"),
                handler="process_update.handler",  # Adjust the handler accordingly
                log_group=self.log_group,
                #environment={
                #    "TABLE_NAMES": json.dumps(table_names),  # Pass table names to Lambda function
                #     Other environment variables if needed
                #}
            )
            self.logger.info("Created process update Lambda function")
            return process_dynamodb_update
        except Exception as e:
            self.logger.error(f"Failed to create process update Lambda function: {e}")
            # Handle the error, e.g., raise a custom exception, log the error, etc.
            return None
    
    # Function to generate timestamp for 'created-date' and 'updated-date' attributes
    def _create_get_timestamp_function(self):
        try:
            get_timestamp_function = lambda_.Function(
                self,
                "get-timestamp-func",
                runtime=lambda_.Runtime.PYTHON_3_9,
                code=lambda_.Code.from_asset(f"{self.lambda_handler_path}/get_timestamp"),
                handler="get_timestamp.handler",
                log_group=self.log_group

            )
            self.logger.info("Created get timestamp Lambda function")
            return get_timestamp_function
        except Exception as e:
            self.logger.error(f"Failed to create get timestamp Lambda function: {e}")
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

            self.logger.info("Created Lambda processor")
            # Grant permissions to Lambda functions
            for table_name in table_names:
                table = tables[table_name]
                self.logger.info(f"Granting read permissions to table '{table_name}'")
                table.grant_read_data(process_dynamodb_update)

            return lambda_processor
        except Exception as e:
            self.logger.error(f"Failed to create Lambda processor: {e}")
            # Handle the error, e.g., raise a custom exception, log the error, etc.
            return None

    def _create_firehose_delivery_streams(self, firehose_role, lambda_processor, data_stream_name, s3_bucket, table_names, unique_id, get_timestamp_function):
        delivery_stream_names = [data_stream_name] + [f"{name}-firehose" for name in table_names]
        firehose_streams = {}

        for name in delivery_stream_names:
            unique_delivery_stream_name = f"{name}-{unique_id}"
            prefix = self._determine_prefix(name, data_stream_name)
            if lambda_processor and lambda_processor.function_arn:
                try:
                    firehose_stream = self._create_delivery_stream(unique_delivery_stream_name, prefix, s3_bucket, firehose_role, lambda_processor)
                    firehose_streams[unique_delivery_stream_name] = firehose_stream
                    self._grant_firehose_invoke_lambda_permission(firehose_role, get_timestamp_function)
                    self.logger.info(f"Created Firehose delivery stream '{unique_delivery_stream_name}'")
                except Exception as e:
                    self.logger.error(f"Failed to create Firehose delivery stream '{unique_delivery_stream_name}': {e}")
            else:
                self.logger.error(f"Failed to create Firehose delivery stream '{unique_delivery_stream_name}': Lambda processor is None or its function_arn is not available")
        return firehose_streams

    def _determine_prefix(self, name, data_stream_name):
        try:
            self.logger.info(f"Determining prefix for {name}")
            return f"dynamodb-changes/{name.split('-')[0]}/" if '-' in name else "dynamodb-changes/default/"
        except Exception as e:
            self.logger.error(f"Error determining prefix for {name}: {e}")
            return "dynamodb-changes/error/"

    def _create_delivery_stream(self, unique_delivery_stream_name, prefix, s3_bucket, firehose_role, lambda_processor):
        try:
            
            return firehose.CfnDeliveryStream(
                self,
                unique_delivery_stream_name,
                delivery_stream_type="DirectPut",
                extended_s3_destination_configuration=firehose.CfnDeliveryStream.ExtendedS3DestinationConfigurationProperty(
                    bucket_arn=s3_bucket.bucket_arn,
                    prefix=prefix,
                    compression_format="GZIP",
                    role_arn=firehose_role.role_arn,
                    processing_configuration=self._create_processing_configuration(lambda_processor, unique_delivery_stream_name)
                ),
            ),self.logger.info(f"Created delivery stream {unique_delivery_stream_name}")
            
        except Exception as e:
            self.logger.error(f"Error creating delivery stream {unique_delivery_stream_name}: {e}")
            return None

    def _create_processing_configuration(self, lambda_processor, stream_name):
        try:
            base_parameters = [
                firehose.CfnDeliveryStream.ProcessorParameterProperty(
                    parameter_name="LambdaArn",
                    parameter_value=lambda_processor.function_arn
                )
            ]
            self.logger.info(f"Creating processing configuration for {stream_name}")
            if stream_name.endswith("-1"):  # Assuming the first stream requires additional parameters
                base_parameters += [
                    firehose.CfnDeliveryStream.ProcessorParameterProperty(
                        parameter_name="BufferSizeInMBs",
                        parameter_value="3"
                    ),
                    firehose.CfnDeliveryStream.ProcessorParameterProperty(
                        parameter_name="BufferIntervalInSeconds",
                        parameter_value="60"
                    )
                ]
                self.logger.info(f"Added additional parameters for {stream_name}")
            self.logger.info(f"Processing configuration created for {stream_name}")
            return firehose.CfnDeliveryStream.ProcessingConfigurationProperty(
                enabled=True,
                processors=[firehose.CfnDeliveryStream.ProcessorProperty(type="Lambda", parameters=base_parameters)]
            )
        except Exception as e:
            self.logger.error(f"Error creating processing configuration for {stream_name}: {e}")
            return firehose.CfnDeliveryStream.ProcessingConfigurationProperty(enabled=False)

    def _grant_firehose_invoke_lambda_permission(self, firehose_role, get_timestamp_function):
        try:
            firehose_role.add_to_policy(
                statement=iam.PolicyStatement(
                    actions=["lambda:InvokeFunction"],
                    resources=[get_timestamp_function.function_arn],
                )
            )
            self.logger.info("Granted Firehose invoke permission to Lambda function")
        except Exception as e:
           self.logger.error(f"Failed to grant Firehose invoke permission to Lambda function: {e}")
