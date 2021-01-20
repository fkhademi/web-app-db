#!/usr/bin/python

import appsitefunctions
import boto3
import json
import decimal
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from datetime import datetime
import ConfigParser



# Helper class to convert a DynamoDB item to JSON.
class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            if o % 1 > 0:
                return float(o)
            else:
                return int(o)
        return super(DecimalEncoder, self).default(o)

try:
	dynamodb = boto3.resource('dynamodb', 'eu-central-1', verify=False)
	table = dynamodb.Table('pod_history')
	response = table.scan()

	print '''
	<Content-type: text/html\\n\\n>
	<html>
	<head>
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css" integrity="sha384-ggOyR0iXCbMQv3Xipma34MD+dH/1fQ784/j6cY/iJTQUOhcWr7x9JvoRxT2MZw1T" crossorigin="anonymous">
	<title>Multi-Tier Web App</title>
	</head>
	<body>
	'''

	#Start printing the html for the header row
	print '''<center><h3>Wall of Fame</h3></center>
	<table class="table table-hover">
	<thead>
	<tr>
	<th scope="col">ID</th>
	<th scope="col">Name</th>
	<th scope="col">Company</th>
	<th scope="col">Start</th>
	<th scope="col">End</th>
	<th scope="col">Time (s)</th>
	<th scope="col">Comment</th>
	</tr>
	</thead>
	<tbody>'''
	for i in response['Items']:
		json_str = json.dumps(i, cls=DecimalEncoder)
		resp_dict = json.loads(json_str)
		start = resp_dict.get('start_time')
		end = resp_dict.get('completed')
		try:
			start_obj = datetime.strptime(start, '%Y-%m-%dT%H:%M:%S')
		except:
			start_obj = datetime.strptime("2000-01-01T00:00:00", '%Y-%m-%dT%H:%M:%S')
		try:
			end_obj = datetime.strptime(end, '%Y-%m-%dT%H:%M:%S')
		except:
			end_obj = datetime.strptime("2021-01-01T00:00:00", '%Y-%m-%dT%H:%M:%S')
		
		time = (end_obj - start_obj).total_seconds()
		print '<tr>'
		print '<td>%s</td>' %resp_dict.get('user_id')
		print '<td>%s</td>' %resp_dict.get('full_name')
		print '<td>%s</td>' %resp_dict.get('company')
		print '<td>%s</td>' %start_obj
		print '<td>%s</td>' %end_obj
		print '<td>%s</td>' %round(time,2)
		print '<td>%s</td>' %resp_dict.get('comment')
		print '</tr>'

	print '''</tbody>
	/table>
	</body>
	</html>
	'''

except:
	appsitefunctions.printdbservererror()