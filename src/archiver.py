import json
import os
import time
import boto3

s3 = boto3.client('s3')

def lambda_handler(event, context):
    # Dynamically find the bucket passed in by CloudFormation parameters
    target_bucket = os.environ.get('BUCKET_NAME')

    for record in event['Records']:
        if record['eventName'] == 'INSERT':
            new_image = record['dynamodb']['NewImage']
            
            # Unpack DynamoDB JSON structure to clean Python dictionary
            clean_item = {k: list(v.values())[0] for k, v in new_image.items()}
            
            # Structure a clean data lake key path: year/month/day/file.json
            current_time = time.strftime("%Y/%m/%d")
            s3_key = f"raw-logs/{current_time}/{clean_item['id']}.json"
            
            # Write to S3 Data Lake
            s3.put_object(
                Bucket=target_bucket,
                Key=s3_key,
                Body=json.dumps(clean_item),
                ContentType='application/json'
            )
            print(f"Archived item {clean_item['id']} to S3 Data Lake bucket: {target_bucket}")
            
    return {"statusCode": 200, "body": "Stream archive completed"}
