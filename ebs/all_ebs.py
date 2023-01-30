import boto3
import csv
from datetime import datetime
from rich.console import Console
from rich.table import Table
import argparse

'''
This script gets all EBS volumes and displays the output in a table as shown below.

                                                           All EBS volumes
┏━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━┓
┃ ID                    ┃ Name                                              ┃ Owner      ┃ State     ┃ Type     ┃ Size ┃
┡━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━┩
│ vol-653ad4aa          │ internal.msn.eu.prod1.ack.ack-config.2.data       │            │ available │ standard │ 10   │
│ vol-713ad4be          │ internal.msn.eu.prod1.ack.ack-config.3.data       │            │ available │ standard │ 10   │
│ vol-0d12e1c2          │ internal.msn.eu.prod1.services.service-pool1-glu… │            │ available │ gp2      │ 200  │
│ vol-064799214cc69ad68 │ internal.msn.eu.inf1.inf.artifactory-ha.3.cache   │            │ in-use    │ gp2      │ 500  │
│ vol-051748c5444cf2276 │ internal.msn.eu.prod1-backoffice.ack.backoffice-… │            │ in-use    │ gp2      │ 10   │
│ vol-0d869f827340771ac │ internal.msn.eu.prod1-backoffice.ack.backoffice-… │            │ in-use    │ gp2      │ 40   │
│ vol-00c9881fe9484d1e2 │ internal.msn.eu.sit1.ack.ack-config-db.2.data     │            │ available │ gp2      │ 40   │
│ vol-01db27527a5327c8e │ internal.msn.eu.sit1.ack.ack-config-db.2.log      │            │ available │ gp2      │ 10   │
'''


def main():
    my_parser = argparse.ArgumentParser(description='All EBS volumes')
    my_parser.add_argument('--csv', help='Save output to CSV', action='store_true')
    my_parser.add_argument('--state', help='Filter output by volume state.', action='store', dest='state')
    my_parser.add_argument('--type', help='Filter output by volume type.', action='store', dest='type')
    my_parser.add_argument('--size', help='Filter output by volume size.', type=int, action='store', dest='size')
    conditionals = my_parser.add_mutually_exclusive_group()
    conditionals.add_argument('--lt', help='Less than given size.', action='store_true')
    conditionals.add_argument('--gt', help='Greater than given size.', action='store_true')
    args = my_parser.parse_args()

    table = Table(title='All EBS volumes')
    table.add_column('ID')
    table.add_column('Name')
    table.add_column('Owner')
    table.add_column('State')
    table.add_column('Type')
    table.add_column('Size (GB)')

    ec2 = boto3.resource('ec2', region_name='eu-west-1')

    volumes = ec2.volumes.all()
    out = [volume for volume in volumes]
    ebs_list = []

    for volume in out:
        name = ''
        owner = ''

        if volume.tags:

            for tag in volume.tags:
                if tag['Key'] == 'Name' or tag['Key'] == 'name':
                    name = tag['Value']

            for tag in volume.tags:
                if tag['Key'] == 'Owner' or tag['Key'] == 'owner':
                    owner = tag['Value']

        i = {
            'ID': volume.id,
            'Name': name,
            'Owner': owner,
            'State': volume.state,
            'Type': volume.volume_type,
            'Size': volume.size
        }
        ebs_list.append(i)

    if args.state:
        ebs_list = [vol for vol in ebs_list if vol['State'] == args.state]

    if args.type:
        ebs_list = [vol for vol in ebs_list if vol['Type'] == args.type]

    if args.gt:
        ebs_list = [vol for vol in ebs_list if vol['Size'] > args.size]

    if args.lt:
        ebs_list = [vol for vol in ebs_list if vol['Size'] < args.size]

    keys = set().union(*(d.keys() for d in ebs_list))

    if args.csv:
        dtformat = datetime.now().strftime("%Y%m%d%H%M")

        with open(f'allebs_{dtformat}.csv', 'w', newline='') as output_file:
            dict_writer = csv.DictWriter(output_file, keys)
            dict_writer.writeheader()
            dict_writer.writerows(ebs_list)
            print('Output saved in CSV file.')
    else:
        for d in ebs_list:
            table.add_row(str(d['ID']), str(d['Name']), str(d['Owner']), str(d['State']), str(d['Type']), str(d['Size']))
        console = Console()
        console.print(table)


if __name__ == '__main__':
    main()
