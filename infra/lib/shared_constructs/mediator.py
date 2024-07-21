from aws_cdk import aws_sqs as sqs, aws_s3 as s3, aws_sns as sns 
import aws_cdk as cdk
from ..custom_constructs.config_construct import ConfigConstruct
from constructs import Construct
from aws_cdk import aws_logs as logs
import logging

class MediatorStack(cdk.Stack):
    def __init__(self, scope: Construct, id: str,common_stack, **kwargs):
        super().__init__(scope, id, **kwargs)

        try:
            
            # Create Logger Instance
            StackName = cdk.Stack.of(self).stack_name
            logger = common_stack._create_logger(StackName=StackName)

            logger.info("Loading configuration and Referencing Objects in " + StackName)
            # Loading Config Data
            config = ConfigConstruct(self, "InfraConfig", config_file_path="configs/main-infrastructure.yaml")
            logger.info("Infra Configuration data loaded successfully in " + StackName)

            # Loading Mediator Config Data
            mediator_config = ConfigConstruct(self, "MediatorConfig", config_file_path="configs/mediator.yaml")
            logger.info("Mediator Configuration data loaded successfully in " + StackName)
            log_group_name = mediator_config.get_value("log_group_name")

            # Setup for CloudWatch log group
            log_group =  common_stack._create_log_group(log_group_name, StackName= StackName)

            # Setup for S3 buckets
            self.buckets = {}
            for bucket_key, bucket_name in config['bucket_names'].items():
                logger.info(f"Referencing S3 bucket with key: {bucket_key}, name: {bucket_name}")  # Debugging print
                if bucket_key in self.buckets:
                    logger.error(f"Duplicate bucket key detected: {bucket_key}")
                    raise Exception(f"Duplicate bucket key detected: {bucket_key}")
                self.buckets[bucket_key] = s3.Bucket.from_bucket_name(self, bucket_key, bucket_name) 
            
            # Setup for SQS queues remains the same
            self.queues = {}
            for queue_name, queue_config in config['queue_configs'].items():
                logger.info(f"Referencing SQS queue with name: {queue_config['name']}")  # Debugging print
                if queue_name in self.queues:
                    logger.error(f"Duplicate queue name detected: {queue_name}")
                    raise Exception(f"Duplicate queue name detected: {queue_name}")
                self.queues[queue_name] = sqs.Queue.from_queue_arn(self, queue_name, f"arn:aws:sqs:region:account-id:{queue_config['name']}")
            
            # Setup for SNS topics
            self.topics = {}
            for topic_key, topic_name in config['topic_names'].items():
                logger.info(f"Referencing SNS topic with key: {topic_key}, name: {topic_name}")
                if topic_key in self.topics:
                    logger.error(f"Duplicate topic key detected: {topic_key}") 
                    raise Exception(f"Duplicate topic key detected: {topic_key}")
                self.topics[topic_key] = sns.Topic.from_topic_arn(self, topic_key, f"arn:aws:sns:region:account-id:{topic_name}")
        
        except Exception as e:
            logger.error(f"An error occurred: {str(e)}")
            
        end_logger = common_stack._end_logger(StackName=StackName)