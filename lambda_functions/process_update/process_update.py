import json
import boto3
import os
from datetime import datetime, timezone

def handler(event, context):
    """
    This Lambda function processes DynamoDB update events before sending them to Firehose.

    - It retrieves the current timestamp using the provided GET_TIMESTAMP_FUNCTION_ARN environment variable or directly using datetime.
    - It injects the timestamp into the 'created-date' and 'updated-date' attributes (configurable via environment variables).
    - It can be extended to perform additional data manipulation before sending the record to Firehose.
    """

    created_date_attribute = os.environ['CREATED_DATE_ATTRIBUTE']
    updated_date_attribute = os.environ['UPDATED_DATE_ATTRIBUTE']
    get_timestamp_function_arn = os.environ.get('GET_TIMESTAMP_FUNCTION_ARN')

    # Get current timestamp
    if get_timestamp_function_arn:
        timestamp_lambda = boto3.client('lambda')
        try:
            response = timestamp_lambda.invoke(
                FunctionName=get_timestamp_function_arn,
                InvocationType='RequestResponse'
            )
            timestamp = json.loads(response['Payload'].read())['body']
        except Exception as e:
            # Handle error, e.g., log the error and use a default timestamp
            print(f"Error retrieving timestamp: {e}")
            timestamp = datetime.now(timezone.utc).isoformat()
    else:
        timestamp = datetime.now(timezone.utc).isoformat()

    for record in event['Records']:
        try:
            new_image = record['dynamodb']['NewImage']
            new_image[created_date_attribute] = {'S': timestamp}
            new_image[updated_date_attribute] = {'S': timestamp}
        except KeyError as e:
            # Handle missing attribute, e.g., log the error
            print(f"Error accessing DynamoDB attribute: {e}")

    # You can potentially modify the record further here before returning

    return event
