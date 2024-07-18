import unittest
from aws_cdk import core
from lib.shared_constructs.mediator import MediatorStack

class TestMediatorStack(unittest.TestCase):
    def setUp(self):
        self.app = core.App()
        self.stack = MediatorStack(self.app, "TestStack")

    def test_stack_creation(self):
        self.assertIsNotNone(self.stack)

    def test_s3_buckets(self):
        self.assertIsNotNone(self.stack.buckets)
        self.assertEqual(len(self.stack.buckets), 2)  # Update the expected count based on your configuration

    def test_sqs_queues(self):
        self.assertIsNotNone(self.stack.queues)
        self.assertEqual(len(self.stack.queues), 3)  # Update the expected count based on your configuration

    def test_sns_topics(self):
        self.assertIsNotNone(self.stack.topics)
        self.assertEqual(len(self.stack.topics), 4)  # Update the expected count based on your configuration

if __name__ == '__main__':
    unittest.main()
import unittest
from aws_cdk import aws_sqs as sqs, aws_s3 as s3, aws_sns as sns 
from aws_cdk import aws_cdk as cdk
from lib.custom_constructs.config_construct import ConfigConstruct
from constructs import Construct
from lib.shared_constructs.mediator import MediatorStack

class TestMediatorStack(unittest.TestCase):
    def test_mediator_stack(self):
        app = cdk.App()
        stack = MediatorStack(app, "TestStack")

        # Assert the existence of S3 buckets
        self.assertTrue(stack.buckets)
        self.assertIsInstance(stack.buckets["bucket_key"], s3.Bucket)

        # Assert the existence of SQS queues
        self.assertTrue(stack.queues)
        self.assertIsInstance(stack.queues["queue_name"], sqs.Queue)

        # Assert the existence of SNS topics
        self.assertTrue(stack.topics)
        self.assertIsInstance(stack.topics["topic_key"], sns.Topic)

if __name__ == '__main__':
    unittest.main()
    
import unittest
from aws_cdk import core
from lib.shared_constructs.mediator import MediatorStack

class TestMediatorStack(unittest.TestCase):
    def setUp(self):
        self.app = core.App()
        self.stack = MediatorStack(self.app, "TestStack")

    def test_stack_creation(self):
        self.assertIsNotNone(self.stack)

    def test_s3_buckets(self):
        self.assertIsNotNone(self.stack.buckets)
        self.assertEqual(len(self.stack.buckets), 2)  # Update the expected count based on your configuration

    def test_sqs_queues(self):
        self.assertIsNotNone(self.stack.queues)
        self.assertEqual(len(self.stack.queues), 3)  # Update the expected count based on your configuration

    def test_sns_topics(self):
        self.assertIsNotNone(self.stack.topics)
        self.assertEqual(len(self.stack.topics), 4)  # Update the expected count based on your configuration

    def test_bucket_instance_types(self):
        for bucket_key, bucket in self.stack.buckets.items():
            self.assertIsInstance(bucket, s3.Bucket)

    def test_queue_instance_types(self):
        for queue_name, queue in self.stack.queues.items():
            self.assertIsInstance(queue, sqs.Queue)

    def test_topic_instance_types(self):
        for topic_key, topic in self.stack.topics.items():
            self.assertIsInstance(topic, sns.Topic)

if __name__ == '__main__':
    unittest.main()