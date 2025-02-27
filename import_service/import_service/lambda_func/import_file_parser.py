import io
import json
import csv
import boto3
import os

s3 = boto3.client('s3')
sqs = boto3.client('sqs')


def lambda_handler(event, context):
    print(f"Received event: {json.dumps(event)}")

    bucket_name = os.environ['BUCKET_NAME']
    sqs_queue_url = os.environ['SQS_QUEUE_URL']

    for record in event['Records']:
        key = record['s3']['object']['key']

        response = s3.get_object(Bucket=bucket_name, Key=key)

        csv_file = io.StringIO(response['Body'].read().decode('utf-8'))
        reader = csv.DictReader(csv_file)

        for row in reader:
            sqs.send_message(
                QueueUrl=sqs_queue_url,
                MessageBody=json.dumps(row)
            )

        copy_source = {'Bucket': bucket_name, 'Key': key}
        parsed_key = key.replace('uploaded/', 'parsed/')
        s3.copy_object(CopySource=copy_source, Bucket=bucket_name, Key=parsed_key)

        if key != 'uploaded/':
            s3.delete_object(Bucket=bucket_name, Key=key)

