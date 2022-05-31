import boto3
import csv
from datetime import datetime

ec2 = boto3.resource('ec2', region_name='eu-west-1')
volumes = ec2.volumes.all()
#volumes = ec2.volumes.filter(Filters=[{'Name': 'state', 'Values': ['available']},])
out = [volume for volume in volumes]
result = []

dtformat = datetime.now().strftime("%Y%m%d%H%M")

for volume in out:
    name = ''
    owner = ''

    if  volume.tags:

        for tag in volume.tags:
            if tag['Key'] == "Name" or tag['Key'] == "name":
                name = tag['Value']
                
        for tag in volume.tags:
            if tag['Key'] == "Owner" or tag['Key'] == "owner":
                owner = tag['Value']
            
    i = {

        "ID" : volume.id,
        "Name" : name,
        "Owner" : owner,
        "State": volume.state,
        "Type" : volume.volume_type,
        "Size" : volume.size

    }
    result.append(i)

keys = set().union(*(d.keys() for d in result))

with open(f'allebs_{dtformat}.csv', 'w', newline='') as output_file:
    dict_writer = csv.DictWriter(output_file, keys)
    dict_writer.writeheader()
    dict_writer.writerows(result)


