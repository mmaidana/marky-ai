import json
import boto3

def handler(event, context):
    """
    This Lambda function retrieves the current timestamp in UTC.
    """
    timestamp = boto3.client('cloudwatch').get_time().get('currentTime')
    return {
        'statusCode': 200,
        'body': json.dumps(timestamp)
    }
