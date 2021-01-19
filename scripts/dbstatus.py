#!/usr/bin/python

import appsitefunctions
import cgi
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

#print '<Content-type: text/html\\n\\n>'
#        <html>

try:
    url = "https://dynamodb.eu-central-1.amazonaws.com"
    r = requests.get(url=url,verify=False)
    substring = "healthy"
    r = r.text
    if substring in r:
        print '''
        <Content-type: text/html\\n\\n>
        <html>
        <head>
        <title>Multi-Tier Web App</title>
        </head>
        <body>
        Up
        </body>
        </html>
        '''  
    else:
        print '''
        <Content-type: text/html\\n\\n>
        <html>
        <head>
        <title>Multi-Tier Web App</title>
        </head>
        <body>
        Down
        </body>
        </html>
        '''  
except:
    print '''
    <Content-type: text/html\\n\\n>
    <html>
    <head>
    <title>Multi-Tier Web App</title>
    </head>
    <body>
    Down
    </body>
    </html>
    '''  