#!/usr/bin/python

import appsitefunctions
import cgi
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

dbvalues = appsitefunctions.getdbinfo()
fqdn = dbvalues[0]
host = dbvalues[1]
ipaddress = dbvalues[2]
webprotocol = dbvalues[3]
port = dbvalues[4]
status = dbvalues[5]

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
        <table border="1">
        '''
        appsitefunctions.printdbinfo(fqdn,host,ipaddress,webprotocol,port,"Up")

        print '''
        </table>
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
        <table border="1">
        '''
        appsitefunctions.printdbinfo(fqdn,"","","","","Down")

        print '''
        </table>
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
    <table border="1">
    '''
    appsitefunctions.connectionerror()

    print '''
    </table>
    </body>
    </html>
    '''