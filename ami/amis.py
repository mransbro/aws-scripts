import boto3
from rich.console import Console
from rich.table import Table

'''
This script gets the ami of all running ec2 instances and displays the output in a table as shown below.

                                                            AMIs in use                                                             
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Name                                                ┃ AMI ID                ┃ AMI Name                                            ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ not set                                             │ ami-0b1c217770f6cd8ca │ ['amazon-eks-node-1.21-v20210813']                  │
│ not set                                             │ ami-0b1c217770f6cd8ca │ ['amazon-eks-node-1.21-v20210813']                  │
│ not set                                             │ ami-0b1c217770f6cd8ca │ ['amazon-eks-node-1.21-v20210813']                  │
│ internal.msn.eu.prod1-backoffice.ack.backoffice-mo… │ ami-0ebe84b8bd248439c │ ['amzn2-base-0.0.18']                               │
│ internal.msn.eu.inf1.services.ms-teams-bot          │ ami-00d8ca85f82c14c39 │ ['amzn2-base-0.0.20']                               │
│ internal.msn.eu.pre1.services.grpsv-kafka.1c        │ ami-03d89e4842c01443e │ []                                                  │
│ internal.msn.eu.inf1.inf.docker-host                │ ami-0ebe84b8bd248439c │ ['amzn2-base-0.0.18']                               │
│ internal.msn.eu.inf1.inf.jumpbox-inf                │ ami-00d9ca88f82c14c39 │ ['amzn2-base-0.0.20']                               │
'''

table = Table(title="AMIs in use")
table.add_column("Name")
table.add_column("AMI ID")
table.add_column("AMI Name")

ec2 = boto3.client('ec2')

# Get a list of all running instances
instances = ec2.describe_instances(Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])


instances_list = []

# Iterate over the instances
for instance in instances['Reservations']:
    for i in instance['Instances']:
        # Get the instance name and AMI ID
        name = [tag['Value'] for tag in i['Tags'] if tag['Key'] == 'Name']
        if not name:
            name = 'not set'
        else: 
            name = name[0]
        ami = i['ImageId']
        # Add this information to the list of dictionaries
        instances_list.append({'name': name, 'ami': ami})


unique_amis = list(set([item['ami'] for item in instances_list]))
ami_info = ec2.describe_images(ImageIds=unique_amis)



for d in instances_list:
    ami_name = [item['Name'] for item in ami_info['Images'] if item['ImageId'] == d['ami']]
    table.add_row(d['name'], d['ami'],str(ami_name))

console = Console()
console.print(table)
