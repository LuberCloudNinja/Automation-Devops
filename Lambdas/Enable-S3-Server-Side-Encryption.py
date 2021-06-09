import json
import boto3

def lambda_handler(event, context):
    s3_buckets = boto3.client("s3")
    all_buckets = []

    for buckets in s3_buckets.list_buckets()['Buckets']:
        all_buckets.append(buckets['Name'])

    for items in all_buckets:
        response = s3_buckets.put_bucket_encryption(
    Bucket=items,
        ServerSideEncryptionConfiguration={
        'Rules': [
            {
                'ApplyServerSideEncryptionByDefault': {
                    'SSEAlgorithm': 'AES256'
                },
                'BucketKeyEnabled': False
            },
        ]
    },)
