import aws_cdk as cdk
import yaml
import os
from constructs import Construct
from aws_cdk import aws_logs as logs
import logging

class ConfigConstruct(Construct):
    def __init__(self, scope: Construct, construct_id: str, config_file_path: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Calculate the absolute path to the config file
        # Assuming the structure:
        # / (project root)
        #   /lib/custom_constructs/custom_construct.py
        #   /configs/config.yaml
        # And you're executing from the project root (/)
        base_dir = os.path.dirname(os.path.realpath(__file__))  # Gets the directory of the current file
        project_root = os.path.join(base_dir, '..', '..')  # Navigate up to the project root
        abs_config_path = os.path.join(project_root, 'configs', config_file_path)  # Construct the path to the config file
        #print(F"abs_config_path: {abs_config_path}")

        try:
            with open(abs_config_path, 'r') as f:
                self.config = yaml.safe_load(f)
        except FileNotFoundError as e:
            raise ValueError(f"Config file not found: {abs_config_path}") from e
        except yaml.YAMLError as e:
            raise ValueError(f"Error parsing YAML file: {e}") from e

    def get_value(self, key, default=None):
        try:
            return self.config.get(key)
        except KeyError:
            return default
    
    def __getitem__(self, key):
        try:
            # Leverage the existing get_value method
            return self.get_value(key)
        except KeyError:
            # Handle key not found error
            raise KeyError(f"Key not found: {key}")
    



    ## not using this method
    def _load_prompt(self, prompt_file):
        prompt_file_path = os.path.join("configs", f"{prompt_file}.yaml")  # Construct the full path
        try:
            with open(prompt_file_path, 'r') as file:  # Use prompt_file_path here
                prompt_data = file.read()
            return prompt_data
        except FileNotFoundError:
            raise ValueError(f"Prompt file not found: {prompt_file_path}")  # Updated to prompt_file_path for accurate error message
        except Exception as e:
            raise ValueError(f"Error loading prompt file: {e}")