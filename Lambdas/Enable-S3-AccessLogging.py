import json
import boto3

class EnableAccessLogging:
    def __init__(self):
        self._s3_service_client = boto3.client("s3")
        self._s3_service_resource = boto3.resource("s3")
        self._iam_service_client = boto3.client("sts")
            
    def list_all_buckets(self):
        """ List all buckets and append them to a list """
        self._all_buckets = [buckets['Name'] for buckets in self._s3_service_client.list_buckets()['Buckets']]
        for num, list_buckets in enumerate(self._all_buckets, start= 1):
            print(f"{num}- {list_buckets}")
    
    def get_account_num(self):
        """ Get account number """
        self.account_number = self._iam_service_client.get_caller_identity()['Account']
        self.access_logs_bucket = f"access-logging-{self.account_number}"
        
    def put_bucket_prefix(self):
        """ Add Prefix in Bucket where access logs are going to be added to isolate each logs per bucket"
        for add_prefix in self._all_buckets:
            if self.access_logs_bucket in add_prefix:
                for x in self._all_buckets:
                    self._s3_service_client.put_object(
                        Bucket= self.access_logs_bucket,
                        Key= f"{self.account_number}/{x}/"
                        )
    def enable_access_logging(self):
        """ Enable access loging in all buckets and send them to a target bucket """
        bucket_acl = self._s3_service_resource.BucketAcl(self.access_logs_bucket)
        bucket_acl_grants = bucket_acl.grants
        bucket_acl_grants.append(             
                {
                    'Grantee': {
                        'Type': 'Group',
                        'URI': 'http://acs.amazonaws.com/groups/s3/LogDelivery'
                    },
                    'Permission': 'WRITE'
                }
                )
                
        bucket_acl_grants.append(                
                {
                    'Grantee': {
                        'Type': 'Group',
                        'URI': 'http://acs.amazonaws.com/groups/s3/LogDelivery'
                    },
                    'Permission': 'READ_ACP'
                }
                )
                
        canonical_id = bucket_acl.owner['ID']
        response = bucket_acl.put(
            AccessControlPolicy={
            'Grants': bucket_acl_grants,
            'Owner': {
                'ID': canonical_id                
            }})
            
        
        for list_s3_buckets in self._all_buckets:
            for items in self._all_buckets:
                response = self._s3_service_client.put_bucket_logging(
                    Bucket = items,
                    BucketLoggingStatus= {
                        'LoggingEnabled': {
                            'TargetBucket': self.access_logs_bucket,
                            'TargetPrefix': f"{self.account_number}/{items}/"
                        }
                    }
                )


def lambda_handler(event, context):
    object_1 = EnableAccessLogging()
    object_1.list_all_buckets()
    object_1.get_account_num()
    object_1.put_bucket_prefix()
    object_1.enable_access_logging()

