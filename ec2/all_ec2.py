import boto3
import csv
from datetime import datetime


ec2 = boto3.client('ec2')
response = ec2.describe_instances()
ec2_reservations = response['Reservations']
ec2_list = [e['Instances'][0] for e in ec2_reservations]
ec2_output = []

dtformat = datetime.now().strftime("%Y%m%d%H%M")


for instance in ec2_list:
    name = ''
    owner = ''

    for tag in instance['Tags']:
        if tag['Key'] == "Name" or tag['Key'] == "name":
            name = tag['Value']
            
    for tag in instance['Tags']:
        if tag['Key'] == "Owner" or tag['Key'] == "owner":
            owner = tag['Value']
            
    i = {
        "Owner" : owner,
        "Name" : name,
        "InstanceType" : instance['InstanceType'],
        "InstanceId" : instance['InstanceId'],
        "State": instance['State']['Name'],
    }
    ec2_output.append(i)

keys = set().union(*(d.keys() for d in ec2_output))

with open(f'allec2_{dtformat}.csv', 'w', newline='') as output_file:
    dict_writer = csv.DictWriter(output_file, keys)
    dict_writer.writeheader()
    dict_writer.writerows(ec2_output)
