import os
import aws_cdk as cdk
from aws_cdk import aws_lambda as lambda_
from constructs import Construct

class LambdaLoggingLayer(Construct):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        try:
 # Get the directory containing this file (lambda_logging_layer.py)
            project_root = os.path.dirname(__file__)
            print("project root is "+ project_root)

            # Construct the path to the directory containing common_resource.py
            layer_path = os.path.join(project_root)  # Assuming the directory structure

            print("the layer path is "+ layer_path)

            # Create the Lambda layer construct
            self.layer = lambda_.LayerVersion(
                self, "LoggingLayerVersion",
                code=lambda_.Code.from_asset(layer_path),
                description="A layer to do logging on Lambda functions",
                compatible_runtimes=[lambda_.Runtime.PYTHON_3_9]
            )
        except Exception as e:
            print(f"Error creating Lambda layer: {str(e)}")
