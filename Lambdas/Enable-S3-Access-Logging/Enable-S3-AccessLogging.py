import json
import boto3
import datetime
from botocore.exceptions import ClientError

class EnableAccessLogging:
    def __init__(self, context):
        self._s3_service_client_us_gov_west_1 = boto3.client("s3",region_name="us-gov-west-1")
        self._s3_service_resource_us_gov_west_1 = boto3.resource("s3",region_name="us-gov-west-1")
        self._iam_service_client_us_gov_west_1 = boto3.client("sts",region_name="us-gov-west-1")
        self.get_lambda_region = context.invoked_function_arn[22:35]



    def list_all_buckets(self):
        """ List all buckets and append them to a list """
        self._all_buckets = [buckets['Name'] for buckets in self._s3_service_client_us_gov_west_1.list_buckets()['Buckets']]
        for num, list_buckets in enumerate(self._all_buckets, start= 1):
            print(f"{num}- {list_buckets}")
    
    def get_account_num(self):
        """ Get account number """
        self.account_number = self._iam_service_client_us_gov_west_1.get_caller_identity()['Account']
        self.access_logs_bucket = f"access-centralized-logging-{self.account_number}"
    
    def get_bucket_location(self):
        """ Get bucket region """  
        for bucket_location in self._all_buckets:
            self.bucket_region = self._s3_service_client_us_gov_west_1.get_bucket_location(Bucket= bucket_location)['LocationConstraint']


    def get_bucket_date_time(self):
        """ Get date """
        self.year = datetime.date.today().year
        self.month = datetime.date.today().month
        self.day = datetime.date.today().day
      
    def put_bucket_prefix(self):
        for add_prefix in self._all_buckets:
            if self.access_logs_bucket in add_prefix:
                for bucket in self._all_buckets:
                    self._s3_service_client_us_gov_west_1.put_object(
                        Bucket= self.access_logs_bucket,
                        Key= f"awslogs/{self.account_number}/vpcflowlogs/{self.bucket_region}/{bucket}/{self.year}/{self.month}/{self.day}"
                        )
    def enable_access_logging(self):
        """ Enable access loging in all buckets and send them to a target bucket """
        bucket_acl = self._s3_service_resource_us_gov_west_1.BucketAcl(self.access_logs_bucket)
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
        # The below exeption is if the bucket already has the ACL permission to ignore the "ClientError" and contriune with the "put_bucket_logging()".
        for check_acl_status in bucket_acl_grants:
            try:
                response = bucket_acl.put(
                    AccessControlPolicy={
                    'Grants': bucket_acl_grants,
                    'Owner': {
                        'ID': canonical_id                
                    }})
            except ClientError:
                continue


        for items in self._all_buckets:
            use_to_compare_region = self._s3_service_client_us_gov_west_1.get_bucket_location(Bucket= items)['LocationConstraint']
            if use_to_compare_region == self.get_lambda_region:
                response = self._s3_service_client_us_gov_west_1.put_bucket_logging(
                    Bucket = items,
                    BucketLoggingStatus= {
                        'LoggingEnabled': {
                            'TargetBucket': self.access_logs_bucket,
                            'TargetPrefix': f"awslogs/{self.account_number}/vpcflowlogs/{self.bucket_region}/{items}/{self.year}/{self.month}/{self.day}/"
                        }
                    }
                )


def lambda_handler(event, context):
    object_1 = EnableAccessLogging(context)
    object_1.list_all_buckets()
    object_1.get_account_num()
    object_1.get_bucket_location()
    object_1.get_bucket_date_time()
    object_1.put_bucket_prefix()
    object_1.enable_access_logging()
