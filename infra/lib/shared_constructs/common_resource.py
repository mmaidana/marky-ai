from aws_cdk import aws_sqs as sqs, aws_s3 as s3, aws_sns as sns 
import aws_cdk as cdk
from ..custom_constructs.config_construct import ConfigConstruct
from constructs import Construct
from aws_cdk import aws_logs as logs
import logging
import os

class CommonResourceStack(cdk.Stack):
    def __init__(self, scope: Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        try:
            # Create Logger Instance
            StackName = cdk.Stack.of(self).stack_name
            self.logger = self._create_logger(StackName=StackName)

            self.logger.info("Loading Shared configurations")
            # Loading Shared Configuration Data
            shared_config = ConfigConstruct(self, "SharedConfig", config_file_path="shared-data.yaml")
            self.logger.info("Shared Configuration data loaded successfully in " + StackName)

            # Create Log Group based on name in shared configuration
            log_group_name = shared_config.get_value("log_group_name")
            self.log_group = self._create_log_group(log_group_name, StackName= StackName) 
            
            # End Logger
            self.end_logger = self._end_logger(StackName=StackName) 

        except Exception as e:
            print.error(f"An error occurred: {str(e)}")
            raise

        # Create Logger Instance
    def _create_logger(self, StackName):
        try:
            logger = logging.getLogger(__name__)
            logger.setLevel(logging.INFO)
            logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)
            logger.info(f"                                                    ")
            logger.info(f"----------------------------------------------------")
            logger.info(f"---------- Logger created  at {StackName} ----------")
            logger.info(f"----------------------------------------------------")
            logger.info(f"                                                    ")
        except Exception as e:
            print(f"An error occurred while creating the logger: {str(e)}")
            raise
        return logger
    
    # Define a log group for CloudWatch logs
    def _create_log_group(self, log_group_name, StackName):
        try:
            self.logger.info(f"Creating Log Group name =  {log_group_name} for Stack Name = {StackName}")
            log_group = logs.LogGroup(
            self, f"{StackName}CloudWatchLogs",
            log_group_name=log_group_name,
            retention=logs.RetentionDays.ONE_MONTH,  # Corrected to use RetentionDays enum  # Keep logs for 30 days
            removal_policy=cdk.RemovalPolicy.DESTROY
            )
            self.logger.info(f"{log_group_name} Log Group created successfully")
            return log_group
        except Exception as e:
            print.error(f"An error occurred while creating the log group: {str(e)}")
            raise
    
    # End the logger in the Stack
    def _end_logger(self, StackName):
        try:
            self.logger.info(f"                                                    ")
            self.logger.info(f"----------------------------------------------------")
            self.logger.info(f"---------- Logger ended at {StackName} ----------")
            self.logger.info(f"----------------------------------------------------")
            self.logger.info(f"                                                    ")
        except Exception as e:
            print(f"An error occurred while ending the logger: {str(e)}")
            raise