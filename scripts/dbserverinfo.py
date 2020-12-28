#!/usr/bin/python

import appsitefunctions
import cgi
import pymysql

dbvalues = appsitefunctions.getdbinfo()
# (hostname,ipaddress,protocol,port,status)
fqdn = dbvalues[0]
host = dbvalues[1]
# print host, 'host'
ipaddress = dbvalues[2]
# print ipaddress, 'ipaddress'
webprotocol = dbvalues[3]
# print webprotocol, "webprotocol"
port = dbvalues[4]
# print port, 'port'
status = dbvalues[5]


try:
	conn = pymysql.connect(
	    db='appdemo',
	    user='appdemo',
	    passwd='appdemo',
	    host=ipaddress)
	c = conn.cursor()
				
	#Grab the table data from the database.
	c.execute("SELECT version()")

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
    appsitefunctions.printdbinfo(fqdn,"","","","","Down")

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
    appsitefunctions.printdbinfo(fqdn,host,ipaddress,webprotocol,port,status)

    print '''
    </table>
    </body>
    </html>
    '''  



