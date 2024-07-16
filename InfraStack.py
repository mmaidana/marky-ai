import aws_cdk as cdk
from aws_cdk import aws_sns as sns
from aws_cdk import aws_sqs as sqs
from aws_cdk import aws_s3 as s3
from aws_cdk import aws_dynamodb as dynamodb
from aws_cdk import aws_kinesis as kinesis
from aws_cdk import aws_kinesis as kinesis
from aws_cdk.aws_iam import Role, ServicePrincipal, PolicyStatement
from aws_cdk.aws_lambda import Function, Code, Runtime
from aws_cdk import aws_kinesisfirehose as firehose
from aws_cdk import aws_lambda as lambda_
from aws_cdk import aws_iam as iam


class InfraStack(cdk.Stack):

    def __init__(self, scope: cdk.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create SNS Topics
        niche_finder_notifications = sns.Topic(self, "niche-finder-notifications")
        affiliate_program_notifications = sns.Topic(self, "affiliate-program-notifications")
        campaign_notifications = sns.Topic(self, "campaign-notifications")
        campaign_content_notifications = sns.Topic(self, "campaign-content-notifications")
        campaign_metrics_notifications = sns.Topic(self, "campaign-metrics-notifications")

        # Create SQS Queues with Visibility Timeout set to None
        niche_finder_queue = sqs.Queue(
            self,
            "niche-finder-queue",
            visibility_timeout=None,
        )
        affiliate_program_queue = sqs.Queue(
            self,
            "affiliate-program-queue",
            visibility_timeout=None,
        )
        campaign_queue = sqs.Queue(self, "campaign-queue", visibility_timeout=None)
        campaign_content_queue = sqs.Queue(
            self, "campaign-content-queue", visibility_timeout=None
        )
        campaign_metrics_queue = sqs.Queue(
            self, "campaign-metrics-queue", visibility_timeout=None
        )

        # Subscribe Queues to Topics
        niche_finder_queue.subscribe(niche_finder_notifications)
        affiliate_program_queue.subscribe(affiliate_program_notifications)
        campaign_queue.subscribe(campaign_notifications)
        campaign_content_queue.subscribe(campaign_content_notifications)
        campaign_metrics_queue.subscribe(campaign_metrics_notifications)

        # Create S3 Bucket with Versioning
        niche_finder_results_bucket = s3.Bucket(
            self, "niche-finder-results-bucket", versioning=True
        )

        # Define Enums for DynamoDB Tables (you can customize these)
        class Status(cdk.Enum):
            NEW = "new"
            RUNNING = "running"
            PAUSED = "paused"
            TERMINATED = "terminated"

        class CostType(cdk.Enum):
            ON_DEMAND = "on-demand"
            USAGE = "usage"
            SUBSCRIPTION_BASED = "subscription-based"
            OTHER = "other"

        class ServiceType(cdk.Enum):
            AI_SERVICE = "ai-service"
            INFRASTRUCTURE = "infrastructure"
            THIRD_PARTY_TOOL = "third-party-tool"
            DEVTOOL = "devtool"

        # Create DynamoDB Tables
        ai_niche_research_table = dynamodb.Table(
            self,
            "ai-niche-research",
            partition_key=dynamodb.Attribute(
                name="niche-id", type=dynamodb.AttributeType.STRING
            ),
            removal_policy=cdk.RemovalPolicy.DESTROY,
            # Add other table attributes here
            attribute_definitions=[
                dynamodb.AttributeDefinition(
                    name="niche-name", type=dynamodb.AttributeType.STRING
                ),
                dynamodb.AttributeDefinition(
                    name="niche-description", type=dynamodb.AttributeType.STRING
                ),
                dynamodb.AttributeDefinition(
                    name="niche-rank", type=dynamodb.AttributeType.NUMBER
                ),
                dynamodb.AttributeDefinition(
                    name="processed", type=dynamodb.AttributeType.BOOLEAN
                ),
                dynamodb.AttributeDefinition(
                    name="status", type=dynamodb.AttributeType.ENUM, enum=Status
                ),
                dynamodb.AttributeDefinition(
                    name="cost-id", type=dynamodb.AttributeType.STRING
                ),
                dynamodb.AttributeDefinition(
                    name="created-date", type=dynamodb.AttributeType.STRING
                ),
                dynamodb.AttributeDefinition(
                    name="updated-date", type=dynamodb.AttributeType.STRING
                ),
                dynamodb.AttributeDefinition(
                    name="updated-by", type=dynamodb.AttributeType.STRING
                ),
                dynamodb.AttributeDefinition(
                    name="comments", type=dynamodb.AttributeType.STRING
                ),
            ],
        )

        subscription_service_cost_table = dynamodb.Table(
            self,
            "subscription-service-cost",
            partition_key=dynamodb.Attribute(
                name="cost-id", type=dynamodb.AttributeType.STRING
            ),
            removal_policy=cdk.RemovalPolicy.DESTROY,
            # Add other table attributes here
            attribute_definitions=[
                dynamodb.AttributeDefinition(
                    name="service", type=dynamodb.AttributeType.STRING
                ),
                dynamodb.AttributeDefinition(
                    name="cost-type", type=dynamodb.AttributeType.ENUM, enum=CostType
                ),
                dynamodb.AttributeDefinition(
                    name="service-type", type=dynamodb.AttributeType.ENUM, enum=ServiceType
                ),
                dynamodb.AttributeDefinition(
                    name="updated-date", type=dynamodb.AttributeType.STRING
                ),
                dynamodb.AttributeDefinition(
                    name="updated-by", type=dynamodb.AttributeType.STRING
                ),
                dynamodb.AttributeDefinition(
                    name="comments", type=dynamodb.AttributeType.STRING
                ),
            ],
        )

        ai_affiliate_program_research_table = dynamodb.Table(
            self,
            "ai-affiliate-program-research",
            partition_key=dynamodb.Attribute(
                name="affiliate-program-id", type=dynamodb.AttributeType.STRING
            ),
            removal_policy=cdk.RemovalPolicy.DESTROY,
            # Add other table attributes here
            attribute_definitions=[
                dynamodb.AttributeDefinition(
                    name="affiliate-program-name", type=dynamodb.AttributeType.STRING
                ),
                dynamodb.AttributeDefinition(
                    name="affiliate-program-rank", type=dynamodb.AttributeType.NUMBER
                ),
                dynamodb.AttributeDefinition(
                    name="processed", type=dynamodb.AttributeType.BOOLEAN
                ),
                dynamodb.AttributeDefinition(
                    name="status", type=dynamodb.AttributeType.ENUM, enum=Status
                ),
                dynamodb.AttributeDefinition(
                    name="cost-id", type=dynamodb.AttributeType.STRING
                ),
                dynamodb.AttributeDefinition(
                    name="created-date", type=dynamodb.AttributeType.STRING
                ),
                dynamodb.AttributeDefinition(
                    name="updated-date", type=dynamodb.AttributeType.STRING
                ),
                dynamodb.AttributeDefinition(
                    name="updated-by", type=dynamodb.AttributeType.STRING
                ),
                dynamodb.AttributeDefinition(
                    name="comments", type=dynamodb.AttributeType.STRING
                ),
            ],
        )

        # Create Kinesis Data Stream for DynamoDB Change Data Capture (CDC)
        ai_marketing_stream = kinesis.Stream(self, "ai-marketing-streaming")

        # IAM Role for Firehose to access DynamoDB
        firehose_role = Role(
            self, "firehose-role", assumed_by=ServicePrincipal("firehose.amazonaws.com")
        )
        firehose_role.add_managed_policy(
            managed_policy_arn="arn:aws:iam::aws:policy/service-role/AmazonKinesisFirehoseDeliveryRole"
        )
        ai_niche_research_table.grant_read(firehose_role)
        subscription_service_cost_table.grant_read(firehose_role)
        ai_affiliate_program_research_table.grant_read(firehose_role)

        # Create Kinesis Firehose Delivery Stream to S3
        firehose_delivery_stream = firehose.DeliveryStream(
            self,
            "ai-marketing-firehose",
            destinations=[
                firehose.S3Destination(
                    bucket=niche_finder_results_bucket,
                    prefix="dynamodb-changes/ai-marketing/",
                    compression_format=firehose.CompressionFormat.GZIP,
                )
            ],
            role=firehose_role,
            source=ai_marketing_stream,
        )
        # Configure Kinesis Firehose to capture changes from DynamoDB tables

        # Lambda function to get the current timestamp
        get_timestamp_func = lambda_.Function(
            self,
            "get-timestamp-func",
            runtime=lambda_.Runtime.PYTHON_3_9,
            code=lambda_.Code.asset("lambda_functions/get_timestamp.py"),
            handler="get_timestamp.handler",
        )

        # Lambda function to process DynamoDB update events before sending to Firehose
        process_dynamodb_update = Function(
            self,
            "process-dynamodb-update",
            runtime=lambda_.Runtime.PYTHON_3_9,
            code=lambda_.Code.asset("lambda_functions/process_dynamodb_update.py"),
            handler="process_dynamodb_update.handler",
            # Add other necessary properties for the Lambda function
        )
        # DynamoDB Tables
        # Your DynamoDB table definitions follow here...

        ai_niche_research_table = dynamodb.Table(
            self,
            "ai-niche-research",
            partition_key=dynamodb.Attribute(
                name="niche-id", type=dynamodb.AttributeType.STRING
            ),
            removal_policy=cdk.RemovalPolicy.DESTROY,
            # Add other table attributes here
            attribute_definitions=[
                dynamodb.AttributeDefinition(
                    name="niche-name", type=dynamodb.AttributeType.STRING
                ),
                dynamodb.AttributeDefinition(
                    name="niche-description", type=dynamodb.AttributeType.STRING
                ),
                dynamodb.AttributeDefinition(
                    name="niche-rank", type=dynamodb.AttributeType.NUMBER
                ),
                dynamodb.AttributeDefinition(
                    name="processed", type=dynamodb.AttributeType.BOOLEAN
                ),
                dynamodb.AttributeDefinition(
                    name="status", type=dynamodb.AttributeType.ENUM, enum=Status
                ),
                dynamodb.AttributeDefinition(
                    name="cost-id", type=dynamodb.AttributeType.STRING
                ),
                dynamodb.AttributeDefinition(
                    name="created-date", type=dynamodb.AttributeType.STRING
                ),
                dynamodb.AttributeDefinition(
                    name="updated-date", type=dynamodb.AttributeType.STRING
                ),
                dynamodb.AttributeDefinition(
                    name="updated-by", type=dynamodb.AttributeType.STRING
                ),
                dynamodb.AttributeDefinition(
                    name="comments", type=dynamodb.AttributeType.STRING
                ),
            ],
        )

        subscription_service_cost_table = dynamodb.Table(
            self,
            "subscription-service-cost",
            partition_key=dynamodb.Attribute(
                name="cost-id", type=dynamodb.AttributeType.STRING
            ),
            removal_policy=cdk.RemovalPolicy.DESTROY,
            # Add other table attributes here
            attribute_definitions=[
                dynamodb.AttributeDefinition(
                    name="service", type=dynamodb.AttributeType.STRING
                ),
                dynamodb.AttributeDefinition(
                    name="cost-type", type=dynamodb.AttributeType.ENUM, enum=CostType
                ),
                dynamodb.AttributeDefinition(
                    name="service-type", type=dynamodb.AttributeType.ENUM, enum=ServiceType
                ),
                dynamodb.AttributeDefinition(
                    name="updated-date", type=dynamodb.AttributeType.STRING
                ),
                dynamodb.AttributeDefinition(
                    name="updated-by", type=dynamodb.AttributeType.STRING
                ),
                dynamodb.AttributeDefinition(
                    name="comments", type=dynamodb.AttributeType.STRING
                ),
            ],
        )

        ai_affiliate_program_research_table = dynamodb.Table(
            self,
            "ai-affiliate-program-research",
            partition_key=dynamodb.Attribute(
                name="affiliate-program-id", type=dynamodb.AttributeType.STRING
            ),
            removal_policy=cdk.RemovalPolicy.DESTROY,
            # Add other table attributes here
            attribute_definitions=[
                dynamodb.AttributeDefinition(
                    name="affiliate-program-name", type=dynamodb.AttributeType.STRING
                ),
                dynamodb.AttributeDefinition(
                    name="affiliate-program-rank", type=dynamodb.AttributeType.NUMBER
                ),
                dynamodb.AttributeDefinition(
                    name="processed", type=dynamodb.AttributeType.BOOLEAN
                ),
                dynamodb.AttributeDefinition(
                    name="status", type=dynamodb.AttributeType.ENUM, enum=Status
                ),
                dynamodb.AttributeDefinition(
                    name="cost-id", type=dynamodb.AttributeType.STRING
                ),
                dynamodb.AttributeDefinition(
                    name="created-date", type=dynamodb.AttributeType.STRING
                ),
                dynamodb.AttributeDefinition(
                    name="updated-date", type=dynamodb.AttributeType.STRING
                ),
                dynamodb.AttributeDefinition(
                    name="updated-by", type=dynamodb.AttributeType.STRING
                ),
                dynamodb.AttributeDefinition(
                    name="comments", type=dynamodb.AttributeType.STRING
                ),
            ],
        )

        # Create Kinesis Data Stream for DynamoDB Change Data Capture (CDC)
        ai_marketing_stream = kinesis.Stream(self, "ai-marketing-streaming")

        # IAM Role for Firehose to access DynamoDB
        firehose_role = Role(
            self, "firehose-role", assumed_by=ServicePrincipal("firehose.amazonaws.com")
        )
        firehose_role.add_managed_policy(
            managed_policy_arn="arn:aws:iam::aws:policy/service-role/AmazonKinesisFirehoseDeliveryRole"
        )
        ai_niche_research_table.grant_read(firehose_role)
        subscription_service_cost_table.grant_read(firehose_role)
        ai_affiliate_program_research_table.grant_read(firehose_role)

        # Create Kinesis Firehose Delivery Stream to S3
        firehose_delivery_stream = firehose.DeliveryStream(
            self,
            "ai-marketing-firehose",
            destinations=[
                firehose.S3Destination(
                    bucket=niche_finder_results_bucket,
                    prefix="dynamodb-changes/ai-marketing/",
                    compression_format=firehose.CompressionFormat.GZIP,
                )
            ],
            role=firehose_role,
            source=ai_marketing_stream,
        )
        # Configure Kinesis Firehose to capture changes from DynamoDB tables

        # Function to generate timestamp for 'created-date' and 'updated-date' attributes
        get_timestamp_function = Function(
            self,
            "getN_3_9",
            code=Code.asset("lambda_functions/process_update.py"),
            handler="process_update.handler",
            environment={
                "CREATED_DATE_ATTRIBUTE": "created-date",
                "UPDATED_DATE_ATTRIBUTE": "updated-date",
                "GET_TIMESTAMP_FUNCTION_ARN": get_timestamp_function.arn,
            },
        )

        # Grant Firehose permission to invoke Lambda functions
        firehose_role.add_to_policy(
            statement=PolicyStatement(
                actions=["lambda:InvokeFunction"],
                resources=[get_timestamp_function.arn],
            )
        )

        # Delivery stream for ai-niche-research table
        ai_niche_research_stream = firehose.DeliveryStream(
            self,
            "ai-niche-research-firehose",
            destinations=[
                firehose.S3Destination(
                    bucket=niche_finder_results_bucket,
                    prefix="dynamodb-changes/ai-niche-research/",
                    compression_format=firehose.CompressionFormat.GZIP,
                )
            ],
            role=firehose_role,
            source=ai_marketing_stream,
            transformations=[
                firehose.Transform(
                    name="ProcessUpdate",
                    type=firehose.TransformType.LAMBDA,
                    lambda_function=process_dynamodb_update,
                )
            ],
        )
        ai_niche_research_table.add_stream(stream=ai_niche_research_stream)

        # Delivery streams for subscription_service_cost and ai_affiliate_program_research (similar to above)
        # ... You can repeat the same pattern for the remaining tables

        # Add tags to all resources for easy identification
        self.add_tags_to_resource(niche_finder_notifications)
        self.add_tags_to_resource(affiliate_program_notifications)
        self.add_tags_to_resource(campaign_notifications)
        self.add_tags_to_resource(campaign_content_notifications)
        self.add_tags_to_resource(campaign_metrics_notifications)
        # ... and so on for all resources


        
