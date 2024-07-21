import unittest
import aws_cdk as cdk
from lib.main_infrastructure import MainInfrastructureStack
import uuid
from lib.custom_constructs.config_construct import ConfigConstruct
from aws_cdk import aws_s3 as s3
from aws_cdk import aws_sns as sns
from aws_cdk import aws_sqs as sqs
from aws_cdk import aws_dynamodb as dynamodb
from aws_cdk import aws_kinesis as kinesis
from aws_cdk import aws_iam as iam
from aws_cdk import aws_lambda as lambda_
from aws_cdk import aws_kinesisfirehose as firehose
import yaml
import boto3

# Create service clients
s3_client = boto3.client('s3')
sns_client = boto3.client('sns')
sqs_client = boto3.client('sqs')
dynamodb_client = boto3.client('dynamodb')
kinesis_client = boto3.client('kinesis')
iam_client = boto3.client('iam')
lambda_client = boto3.client('lambda')
firehose_client = boto3.client('firehose')

class TestMainInfrastructureStack(unittest.TestCase):

 
    
    def setUp(self):
        self.app = cdk.App()
        self.stack = MainInfrastructureStack(self.app, "TestStack")
        self.stack_creation_test = self.test_stack_creation()
        unique_id =  str(uuid.uuid4())  # Generate a unique ID
        config_data = ConfigConstruct(self,"MainInfrastructureConfig", config_file_path="configs/main-infrastructure.yaml")
        self.s3_buckets_creation_test = self.test_s3_buckets_creation(config_data, unique_id)
         

    def test_stack_creation(self):
        self.assertIsInstance(self.stack, MainInfrastructureStack)
        self.assertEqual(self.stack.stack_name, "TestStack")

    def test_s3_buckets_creation(self, config_data, unique_id):
        s3_buckets = self.stack._create_s3_buckets(config_data, unique_id)
        self.assertIsInstance(s3_buckets, dict)
        self.assertGreater(len(s3_buckets), 0)
        for bucket_name, s3_bucket in s3_buckets.items():
            self.assertIsInstance(s3_bucket, s3.Bucket)
            self.assertEqual(s3_bucket.bucket_name, f"{bucket_name}-{unique_id}")

    # Add more tests for other methods...

if __name__ == '__main__':
    unittest.main()

import unittest
import aws_cdk as cdk
from lib.main_infrastructure import MainInfrastructureStack
from lib.custom_constructs.config_construct import ConfigConstruct

class TestMainInfrastructureStack(unittest.TestCase):

    def setUp(self):
        self.app = cdk.App()
        self.stack = MainInfrastructureStack(self.app, "TestStack")

    def test_stack_creation(self):
        self.assertIsInstance(self.stack, MainInfrastructureStack)
        self.assertEqual(self.stack.stack_name, "TestStack")

    def test_s3_buckets_creation(self):
        config_data = ConfigConstruct(self.stack, "MainInfrastructureConfig", config_file_path="configs/main-infrastructure.yaml")
        unique_id = "test-unique-id"
        s3_buckets = self.stack._create_s3_buckets(config_data, unique_id)
        self.assertIsInstance(s3_buckets, dict)
        self.assertGreater(len(s3_buckets), 0)
        for bucket_name, s3_bucket in s3_buckets.items():
            self.assertIsInstance(s3_bucket, s3.Bucket)
            self.assertEqual(s3_bucket.bucket_name, f"{bucket_name}-{unique_id}")

    def test_sns_topics_creation(self):
        config_data = ConfigConstruct(self.stack, "MainInfrastructureConfig", config_file_path="configs/main-infrastructure.yaml")
        shared_config_data = ConfigConstruct(self.stack, "SharedConfig", config_file_path="configs/shared-data.yaml")
        unique_id = "test-unique-id"
        sns_topics = self.stack._create_sns_topics(config_data, unique_id, shared_config_data)
        self.assertIsInstance(sns_topics, dict)
        self.assertGreater(len(sns_topics), 0)
        for topic_name, sns_topic in sns_topics.items():
            self.assertIsInstance(sns_topic, sns.Topic)
            self.assertEqual(sns_topic.topic_name, f"{topic_name}-{unique_id}")

    def test_sqs_queues_creation(self):
        config_data = ConfigConstruct(self.stack, "MainInfrastructureConfig", config_file_path="configs/main-infrastructure.yaml")
        unique_id = "test-unique-id"
        sqs_queues = self.stack._create_sqs_queues(config_data, unique_id)
        self.assertIsInstance(sqs_queues, dict)
        self.assertGreater(len(sqs_queues), 0)
        for queue_name, sqs_queue in sqs_queues.items():
            self.assertIsInstance(sqs_queue, sqs.Queue)
            self.assertEqual(sqs_queue.queue_name, f"{queue_name}-queue-{unique_id}")

    # Add more tests for other methods...

if __name__ == '__main__':
    unittest.main()
    
import unittest
import aws_cdk as cdk
from lib.main_infrastructure import MainInfrastructureStack
from lib.custom_constructs.config_construct import ConfigConstruct
import uuid
import yaml

class TestMainInfrastructureStack(unittest.TestCase):

    def setUp(self):
        self.app = cdk.App()
        self.stack = MainInfrastructureStack(self.app, "TestStack")

    def test_stack_creation(self):
        self.assertIsInstance(self.stack, MainInfrastructureStack)
        self.assertEqual(self.stack.stack_name, "TestStack")

    def test_s3_buckets_creation(self):
        config_data = ConfigConstruct(self.stack, "MainInfrastructureConfig", config_file_path="configs/main-infrastructure.yaml")
        unique_id = "test-unique-id"
        s3_buckets = self.stack._create_s3_buckets(config_data, unique_id)
        self.assertIsInstance(s3_buckets, dict)
        self.assertGreater(len(s3_buckets), 0)
        for bucket_name, s3_bucket in s3_buckets.items():
            self.assertIsInstance(s3_bucket, s3.Bucket)
            self.assertEqual(s3_bucket.bucket_name, f"{bucket_name}-{unique_id}")

    def test_sns_topics_creation(self):
        config_data = ConfigConstruct(self.stack, "MainInfrastructureConfig", config_file_path="configs/main-infrastructure.yaml")
        shared_config_data = ConfigConstruct(self.stack, "SharedConfig", config_file_path="configs/shared-data.yaml")
        unique_id = "test-unique-id"
        sns_topics = self.stack._create_sns_topics(config_data, unique_id, shared_config_data)
        self.assertIsInstance(sns_topics, dict)
        self.assertGreater(len(sns_topics), 0)
        for topic_name, sns_topic in sns_topics.items():
            self.assertIsInstance(sns_topic, sns.Topic)
            self.assertEqual(sns_topic.topic_name, f"{topic_name}-{unique_id}")

    def test_sqs_queues_creation(self):
        config_data = ConfigConstruct(self.stack, "MainInfrastructureConfig", config_file_path="configs/main-infrastructure.yaml")
        unique_id = "test-unique-id"
        sqs_queues = self.stack._create_sqs_queues(config_data, unique_id)
        self.assertIsInstance(sqs_queues, dict)
        self.assertGreater(len(sqs_queues), 0)
        for queue_name, sqs_queue in sqs_queues.items():
            self.assertIsInstance(sqs_queue, sqs.Queue)
            self.assertEqual(sqs_queue.queue_name, f"{queue_name}-queue-{unique_id}")

    def test_subscribe_queues_to_topics(self):
        sns_topics = {
            "topic1": sns.Topic(self.stack, "Topic1"),
            "topic2": sns.Topic(self.stack, "Topic2")
        }
        sqs_queues = {
            "queue1": sqs.Queue(self.stack, "Queue1"),
            "queue2": sqs.Queue(self.stack, "Queue2")
        }
        self.stack._subscribe_queues_to_topics(sns_topics, sqs_queues)
        for topic_name, topic in sns_topics.items():
            for queue_name, queue in sqs_queues.items():
                if queue_name.startswith(topic_name.split("-")[0]):
                    self.assertIn(queue.queue_arn, topic.subscriptions[0].endpoint)

    def test_create_dynamodb_tables(self):
        config_data = ConfigConstruct(self.stack, "MainInfrastructureConfig", config_file_path="configs/main-infrastructure.yaml")
        firehose_role = self.stack._create_firehose_role()
        unique_id = "test-unique-id"
        tables = self.stack._create_dynamodb_tables(config_data, firehose_role, unique_id)
        self.assertIsInstance(tables, dict)
        self.assertGreater(len(tables), 0)
        for table_name, table in tables.items():
            self.assertIsInstance(table, dynamodb.Table)
            self.assertEqual(table.table_name, f"{table_name}-{unique_id}")

    def test_create_data_stream(self):
        config_data = ConfigConstruct(self.stack, "MainInfrastructureConfig", config_file_path="configs/main-infrastructure.yaml")
        data_stream = self.stack._create_data_stream(config_data)
        self.assertIsInstance(data_stream, kinesis.Stream)

    def test_create_firehose_role(self):
        firehose_role = self.stack._create_firehose_role()
        self.assertIsInstance(firehose_role, iam.Role)
        self.assertEqual(firehose_role.assumed_by.principal_service, "firehose.amazonaws.com")
        self.assertGreater(len(firehose_role.managed_policies), 0)

    def test_create_process_update_lambda(self):
        process_dynamodb_update = self.stack._create_process_update_lambda()
        self.assertIsInstance(process_dynamodb_update, lambda_.Function)
        self.assertEqual(process_dynamodb_update.runtime, lambda_.Runtime.PYTHON_3_9)
        self.assertEqual(process_dynamodb_update.handler, "process_dynamodb_update.handler")

    def test_create_get_timestamp_function(self):
        get_timestamp_function = self.stack._create_get_timestamp_function()
        self.assertIsInstance(get_timestamp_function, lambda_.Function)
        self.assertEqual(get_timestamp_function.runtime, lambda_.Runtime.PYTHON_3_9)
        self.assertEqual(get_timestamp_function.handler, "get_timestamp.handler")

    def test_create_lambda_processor(self):
        config_data = ConfigConstruct(self.stack, "MainInfrastructureConfig", config_file_path="configs/main-infrastructure.yaml")
        process_dynamodb_update = self.stack._create_process_update_lambda()
        tables = self.stack._create_dynamodb_tables(config_data, None, "test-unique-id")
        lambda_processor = self.stack._create_lambda_processor(config_data, process_dynamodb_update, tables)
        self.assertIsInstance(lambda_processor, lambda_.Function)
        self.assertEqual(lambda_processor.function_arn, process_dynamodb_update.function_arn)

    def test_create_firehose_delivery_streams(self):
        firehose_role = self.stack._create_firehose_role()
        lambda_processor = self.stack._create_process_update_lambda()
        data_stream_name = "test-data-stream"
        s3_bucket = s3.Bucket(self.stack, "TestBucket")
        table_names = ["table1", "table2"]
        unique_id = "test-unique-id"
        get_timestamp_function = self.stack._create_get_timestamp_function()
        firehose_streams = self.stack._create_firehose_delivery_streams(firehose_role, lambda_processor, data_stream_name, s3_bucket, table_names, unique_id, get_timestamp_function)
        self.assertIsInstance(firehose_streams, dict)
        self.assertGreater(len(firehose_streams), 0)
        for stream_name, stream in firehose_streams.items():
            self.assertIsInstance(stream, firehose.CfnDeliveryStream)
            self.assertTrue(stream.delivery_stream_type, "DirectPut")
            self.assertEqual(stream.extended_s3_destination_configuration.bucket_arn, s3_bucket.bucket_arn)
            self.assertEqual(stream.extended_s3_destination_configuration.prefix, f"dynamodb-changes/{stream_name.split('-')[0]}/")
            self.assertEqual(stream.extended_s3_destination_configuration.compression_format, "GZIP")
            self.assertEqual(stream.extended_s3_destination_configuration.role_arn, firehose_role.role_arn)
            if stream_name == data_stream_name:
                self.assertEqual(len(stream.extended_s3_destination_configuration.processing_configuration.processors), 1)
                self.assertEqual(stream.extended_s3_destination_configuration.processing_configuration.processors[0].type, "Lambda")
                self.assertEqual(stream.extended_s3_destination_configuration.processing_configuration.processors[0].parameters[0].parameter_name, "LambdaArn")
                self.assertEqual(stream.extended_s3_destination_configuration.processing_configuration.processors[0].parameters[0].parameter_value, lambda_processor.function_arn)
            else:
                self.assertEqual(len(stream.extended_s3_destination_configuration.processing_configuration.processors), 0)

if __name__ == '__main__':
    unittest.main()