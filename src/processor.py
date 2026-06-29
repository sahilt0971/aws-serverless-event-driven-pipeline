import json
import os
import uuid
import boto3

dynamodb = boto3.resource('dynamodb')
sns = boto3.client('sns')

TABLE_NAME = os.environ.get('TABLE_NAME', 'UserActivityLog')
TOPIC_ARN = os.environ.get('TOPIC_ARN')

def lambda_handler(event, context):
    table = dynamodb.Table(TABLE_NAME)
    
    for record in event['Records']:
        try:
            # Parse SQS Body payload
            payload = json.loads(record['body'])
            unique_id = str(uuid.uuid4())
            
            # Enrich data package with architectural metadata
            enriched_item = {
                'id': unique_id,
                'user_id': payload.get('user_id', 'anonymous'),
                'action': payload.get('action', 'unknown'),
                'timestamp': payload.get('timestamp', '0000-00-00'),
                'processed_by': context.function_name
            }
            
            # Write to DynamoDB Hot Storage
            table.put_item(Item=enriched_item)
            print(f"Successfully committed ID {unique_id} to DynamoDB.")
            
            # Fan out an event via SNS if Topic ARN is valid
            if TOPIC_ARN:
                sns.publish(
                    TopicArn=TOPIC_ARN,
                    Message=json.dumps(enriched_item),
                    Subject="New Data Enriched"
                )
                
        except Exception as e:
            print(f"Error processing record: {str(e)}")
            raise e
            
    return {"statusCode": 200, "body": "Batch processed successfully"}
