          import json
          import boto3


          class EnableS3Versioning:
              def __init__(self):
                  self._s3 = boto3.client('s3')
                  self.all_buckets = []

              def list_buckets(self):
                  for buckets in self._s3.list_buckets()['Buckets']:
                      s3_buckets = buckets['Name']
                      self.all_buckets.append(s3_buckets)
              
              def enable_bucket_versioning(self):
                  for items in self.all_buckets:
                      versioning = self._s3.put_bucket_versioning(
                          Bucket=items,
                          VersioningConfiguration={
                              'Status': 'Enabled'
                              })
                  listing_them_all = [s3_enabled_version for s3_enabled_version in self.all_buckets]
                  for item in listing_them_all:
                      print(f"We eneabled versioning in bucket: '{item}'.")

          def lambda_handler(event, context):
              s3 = EnableS3Versioning()
              s3.list_buckets()
              s3.enable_bucket_versioning()

