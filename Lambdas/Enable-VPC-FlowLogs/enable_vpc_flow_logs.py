import boto3
import json
from botocore.exceptions import ClientError

class EnableVpcFlowLogs:
    """ The below instances of the class "EnableVpcFlowLogs" are used for authentication """
    def __init__(self):
        self._ec2_resource = boto3.resource("ec2")
        self._ec2_client = boto3.client("ec2")
        self._centralized_vpc_flowlogs="ARN OF THE VPC LOGS S3 BUCKET"
    
    
    def get_all_vpcs(self):
        """ Get all VPCs in the account """
        self.all_vpc = [vpc.id for vpc in self._ec2_resource.vpcs.all()]
        print("Please see VPC/s below:")
        for num, vpc_s in enumerate(self.all_vpc, start=1):
            print(f"{num}- {vpc_s}")
        print(f"This account has {num} VPC/s total.")
    

    def create_flow_logs(self):
        """ Enable VPC Flow Logs """
        response = self._ec2_client.describe_flow_logs()
        list_of_vpc_flowlogs = []
        for vpc_ids in response['FlowLogs']:
	        for key, value in vpc_ids.items():
	            if key == "ResourceId":
	                vpc = ''.join(value)
	                list_of_vpc_flowlogs.append(vpc)
        print(list_of_vpc_flowlogs)
        for check_logs_status in self.all_vpc:
            if check_logs_status not in list_of_vpc_flowlogs:
                print(check_logs_status)
                self._ec2_client.create_flow_logs(
                                        ResourceIds=[check_logs_status],
                                        ResourceType="VPC",
                                        TrafficType="ALL",
                                        LogDestinationType='s3',
                                        LogDestination=self._centralized_vpc_flowlogs
                                        ) 
                
def lambda_handler(event, context):
    obj_1 = EnableVpcFlowLogs()
    obj_1.get_all_vpcs()
    obj_1.create_flow_logs()
       
        
    

        
