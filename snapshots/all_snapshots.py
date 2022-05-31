import boto3
import csv
from datetime import datetime

ec2 = boto3.resource('ec2', region_name='eu-west-1')

snapshots = ec2.snapshots.all()
out = [snapshot for snapshot in snapshots]
result = []

dtformat = datetime.now().strftime("%Y%m%d%H%M")

for snapshot in out:
    name = ''
    owner = ''

    if  snapshot.tags:

        for tag in snapshot.tags:
            if tag['Key'] == "Name" or tag['Key'] == "name":
                name = tag['Value']
                
        for tag in snapshot.tags:
            if tag['Key'] == "Owner" or tag['Key'] == "owner":
                owner = tag['Value']
            
    i = {

        "ID" : snapshot.id,
        "Name" : name,
        "Owner" : owner,
        "State": snapshot.state,
        "Type" : snapshot.volume_id,
        "Size" : snapshot.volume_size,
        "StorageTier" : snapshot.storage_tier

    }
    result.append(i)

keys = set().union(*(d.keys() for d in result))

with open(f'allsnapshot_{dtformat}.csv', 'w', newline='') as output_file:
    dict_writer = csv.DictWriter(output_file, keys)
    dict_writer.writeheader()
    dict_writer.writerows(result)

