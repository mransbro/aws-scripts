#!/usr/bin/env python

import boto3
import time
import csv
import argparse

s3 = boto3.resource('s3')


parser = argparse.ArgumentParser(
    description='''Get all buckets and their lifecycle policy'''
    )
parser.add_argument('--csv', type=str, help='Output to CSV file')
args = parser.parse_args()


timestr = time.strftime("%Y%m%d%H%M%s")
filename = f"s3_lifecycle_{timestr}.csv"
results = []
fields = ['Bucket', 'Lifecycle']

print('Checking buckets...')

for bucket in s3.buckets.all():
    try:
        rules = bucket.Lifecycle().rules
    except:
        rules = 'No Policy'
    if args.csv is None:
        print(f"{bucket.name}, {rules}")
    else:
        results.append([bucket.name, rules])

if args.csv is None:
    with open(f"./{filename}", 'w') as f:
        write = csv.writer(f)
        write.writerow(fields)
        write.writerows(results)
