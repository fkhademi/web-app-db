#!/usr/bin/python

import urllib3
import json
import boto3
from decimal import Decimal
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import cgi
import os.path
from datetime import datetime
import ConfigParser
import logging

#loads data from the mtwa.conf file to be used in the application
def get_pod_id (): 
	if os.path.exists('/etc/avx/avx.conf'):
		configParser = ConfigParser.RawConfigParser()   
		configFilePath = r'/etc/avx/avx.conf'
		configParser.read(configFilePath)
		pod_id = configParser.get('pod-id', 'PodID')
        logging.warn('Get_pod_id POD ID is %s', pod_id)
        pod_id = pod_id.strip("pod")
        logging.warn('Get_pod_id POD ID is %s', pod_id)
        return (pod_id)
	else:
		print 'ERROR: AVX config file ', os.path.realpath('/etc/avx/avx.conf'), 'not found!'


print("Content-Type: text/html\n\r\n")

def put_new_record(name, company, email, comment, start_time, user_id, dynamodb=None):
    # Insert a new record in DynamoDB
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb', region_name='eu-central-1', verify=False)

    table = dynamodb.Table('pod_history')
    now = datetime.now()
    now = now.strftime("%Y-%m-%dT%H:%M:%S")
    response = table.put_item(
       Item={
            'full_name': name,
            'email': email,
            'completed': now,
            'company': company,
            'comment': comment,
            'start_time': start_time,
            #'id': id,
            'user_id': user_id
        }
    )
    print("Adding new entry:", name, comment)

def get_user_id(pod_num):
    # Get the user ID
    now = datetime.now()
    id = "%s-%s-%s" % (now.year, '{:02d}'.format(now.month), '{:02d}'.format(now.day))
    padded_pod_num = str(pod_num).zfill(3)
    # Set User ID
    user_id = "%s-%s" %(id, padded_pod_num)
    logging.info('[INFO] get_user_id returns UID %s', user_id)
    return(user_id)

def get_attributes(user_id, dynamodb=None):
    # Get the Start Time from the Build Class stored in the buildstart table
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb', region_name='eu-central-1', verify=False)

    table = dynamodb.Table('pod_history')
    response = table.get_item(
       Key={
            'user_id': user_id
        }
    )
    # If the start time is not found, add a default one
    full_name = response['Item']['full_name']
    company = response['Item']['company']
    email = response['Item']['email']
    #id = response['Item']['id']
    start_time = response['Item']['start_time']

    return(full_name, company, email, id, start_time)

if __name__ == '__main__':

    form = cgi.FieldStorage()
    comments = form.getvalue('comments')

    pod_num = get_pod_id()
    user_id = get_user_id(pod_num)

    attributes = get_attributes(user_id)
    full_name = attributes[0]
    company = attributes[1]
    email = attributes[2]
    #id = attributes[3]
    start_time = attributes[4]

    put_resp = put_new_record(full_name, company, email, comments, start_time, user_id)
    print '''
    <Content-type: text/html\\n\\n>
    <html>
    <head>
    <title>Multi-Tier Web App</title>
    </head>
    <body>
    <table border="1">
    <center>
    <div class="alert alert-success" role="alert">Successfully updated the DB!</div>
    </center>
    </table>
    </body>
    </html>
    '''