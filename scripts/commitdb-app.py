#!/usr/bin/python

import urllib3
import json
import boto3
from decimal import Decimal
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import cgi
import os.path
from datetime import datetime


print("Content-Type: text/html\n\r\n")

class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            if o % 1 > 0:
                return float(o)
            else:
                return int(o)
        return super(DecimalEncoder, self).default(o)

def put_new_record(name, email, comment, start_time, dynamodb=None):
    # Insert a new record in DynamoDB
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb', region_name='eu-central-1', verify=False)

    table = dynamodb.Table('build')
    response = table.put_item(
       Item={
            'name': name,
            'email': email,
            'completed': datetime.utcnow().isoformat(),
            'comment': comment,
            'starttime': start_time
        }
    )
    print("Adding new entry:", name, comment)

def get_start_time(id, dynamodb=None):
    # Get the Start Time from the Build Class stored in the buildstart table
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb', region_name='eu-central-1', verify=False)

    table = dynamodb.Table('buildstart')
    response = table.get_item(
       Key={
            'id': id
        }
    )
    # If the start time is not found, add a default one
    try:
        json_str = json.dumps(response['Item'], cls=DecimalEncoder)
    except:
        return("2000-01-01T00:00:00.000000")
    else:
        resp_dict = json.loads(json_str)
        return(resp_dict.get('starttime'))

if __name__ == '__main__':

    form = cgi.FieldStorage()
    arg1 = form.getvalue('name')
    arg2 = form.getvalue('email')
    arg3 = form.getvalue('comments')
    # Get the date
    now = datetime.now()
    id = "%s-%s-%s" %(now.year, now.month, now.day)
    # Query the table to find the start time on this specific day
    start_time = get_start_time(id)
        
    put_resp = put_new_record(arg1, arg2, arg3, start_time)
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