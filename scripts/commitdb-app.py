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

def put_new_record(name, email, comment, dynamodb=None):
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb', region_name='eu-central-1', verify=False)

    table = dynamodb.Table('build')
    response = table.put_item(
       Item={
            'name': name,
            'email': email,
            'completed': datetime.utcnow().isoformat(),
            'comment': comment
        }
    )
    print("Adding new entry:", name, comment)


if __name__ == '__main__':

        form = cgi.FieldStorage()
        arg1 = form.getvalue('name')
        arg2 = form.getvalue('email')
        arg3 = form.getvalue('comments')
        print arg1
        print arg2
        print arg3
        put_resp = put_new_record(arg1, arg2, arg3)
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