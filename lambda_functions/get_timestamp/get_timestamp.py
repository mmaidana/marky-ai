import json
from datetime import datetime, timezone

def handler(event, context):
    """
    This Lambda function retrieves the current UTC timestamp.
    """
    try:
        timestamp = datetime.now(timezone.utc).isoformat()
    except Exception as e:
        # Log the error or handle it appropriately
        print(f"Error generating timestamp: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Failed to generate timestamp'})
        }
    return {
        'statusCode': 200,
        'body': json.dumps(timestamp)
    }
