import boto3
import csv
from datetime import datetime
from rich.console import Console
from rich.table import Table
import argparse
from re import match

'''
This script gets the ami of all running ec2 instances and displays the output in a table as shown below.

                                                            AMIs in use                                                             
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━┓
┃ Instance                                                        ┃ AMI ID                ┃ AMI Name                          ┃ Env              ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━┩
│ i-0b3996078be13cfd7                                             │ ami-0b1c217770f6cd7ca │ amazon-eks-node-1.21-v20210813    │ not_set          │
│ i-0bd549090e4666430                                             │ ami-0b1c217770f6cd7ca │ amazon-eks-node-1.21-v20210813    │ not_set          │
│ i-038577fd01031f081                                             │ ami-0b1c217770f6cd7ca │ amazon-eks-node-1.21-v20210813    │ not_set          │
│ internal.msm.gb.prod1-backoffice.agg.backoffice-mongodb1.2      │ ami-0ebe54b8bd248439c │ amzn2-base-0.0.18                 │ prod1-backoffice │
│ internal.msm.gb.inf1.services.ms-teams-bot                      │ ami-00d9ca85f82c14c39 │ amzn2-base-0.0.20                 │ inf1             │
'''

def main():
    my_parser = argparse.ArgumentParser(description='All AMIs')
    my_parser.add_argument('--csv', help='Save output to CSV', action='store_true')
    filters = my_parser.add_mutually_exclusive_group()
    filters.add_argument('--id', help='Filter by AMI ID.', action='store', type=str, dest='id')
    filters.add_argument('--name', help='Filter by AMI Name.', action='store', type=str, dest='name')
    my_parser.add_argument('--env', help='Filter by Env tag', action='store', type=str, dest='env')
    conditionals = my_parser.add_mutually_exclusive_group()
    conditionals.add_argument('--lt', help='', action='store_true')
    conditionals.add_argument('--gt', help='', action='store_true')
    args = my_parser.parse_args()

    table = Table(title="AMIs in use")
    table.add_column("Instance")
    table.add_column("AMI ID")
    table.add_column("AMI Name")
    table.add_column("Env")

    ec2 = boto3.client('ec2')

    all_instances = ec2.describe_instances(Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])
    instances_list = []

    # Double loop as describe_instances is paginated
    for instance in all_instances['Reservations']:
        for i in instance['Instances']:
            
            # Get the instance name tag
            instance = [tag['Value'] for tag in i['Tags'] if tag['Key'] == 'Name']
            if not instance:
                instance = i['InstanceId']
            else: 
                instance = instance[0]

            # Get the instance env tag
            env = [tag['Value'] for tag in i['Tags'] if tag['Key'] == 'env']
            if not env:
                env = 'not_set'
            else:
                env = env[0]
            
            ami_image = i['ImageId']

            instances_list.append({'instance': instance, 'ami_image': ami_image, 'env': env})


    unique_amis = list(set([item['ami_image'] for item in instances_list]))
    unique_ami_info = ec2.describe_images(ImageIds=unique_amis)

    # Add the ami name
    for d in instances_list:
        for item in unique_ami_info['Images']:
            if item['ImageId'] == d['ami_image']:
                ami_name = item['Name']
        d['ami_name'] = ami_name

    # Filter output
    if args.id:
        instances_list = [ami for ami in instances_list if ami['ami_image'] == args.id]

    if args.name:
        instances_list = [ami for ami in instances_list if match(args.name[:10],ami['ami_name'])]

        if args.gt:
            instances_list = [ami for ami in instances_list if ami['ami_name'] > args.name]
        elif args.lt:
            instances_list = [ami for ami in instances_list if ami['ami_name'] < args.name]
        else:
            instances_list = [ami for ami in instances_list if ami['ami_name'] == args.name]

    if args.env:
        instances_list = [ami for ami in instances_list if ami['env'] == args.env]


    keys = set().union(*(d.keys() for d in instances_list))

    if args.csv:
        dtformat = datetime.now().strftime("%Y%m%d%H%M")

        with open(f'allamis_{dtformat}.csv', 'w', newline='') as output_file:
            dict_writer = csv.DictWriter(output_file, keys)
            dict_writer.writeheader()
            dict_writer.writerows(instances_list)
            print('Output saved in CSV file.')
    else:
        for d in instances_list:
            table.add_row(d['instance'], d['ami_image'], d['ami_name'], d['env'])
        console = Console()
        console.print(table)

if __name__ == '__main__':
    main()
