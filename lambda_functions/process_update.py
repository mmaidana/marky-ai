import json
import boto3
import os

def handler(event, context):
    """
    This Lambda function processes DynamoDB update events before sending them to Firehose.

    - It retrieves the current timestamp using the provided GET_TIMESTAMP_FUNCTION_ARN environment variable.
    - It injects the timestamp into the 'created-date' and 'updated-date' attributes (configurable via environment variables).
    - It can be extended to perform additional data manipulation before sending the record to Firehose.
    """

    created_date_attribute = os.environ['CREATED_DATE_ATTRIBUTE']
    updated_date_attribute = os.environ['UPDATED_DATE_ATTRIBUTE']
    get_timestamp_function_arn = os.environ['GET_TIMESTAMP_FUNCTION_ARN']

    # Get current timestamp
    timestamp_lambda = boto3.client('lambda')
    response = timestamp_lambda.invoke(
        FunctionName=get_timestamp_function_arn,
        InvocationType='RequestResponse'
    )
    timestamp = json.loads(response['Payload'].read())['body']

    for record in event['Records']:
        # Inject timestamp into attributes
        record['dynamodb']['NewImage'][created_date_attribute] = {'S': timestamp}
        record['dynamodb']['NewImage'][updated_date_attribute] = {'S': timestamp}

    # You can potentially modify the record further here before returning

    return event
