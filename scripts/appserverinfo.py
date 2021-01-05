#!/usr/bin/python

import appsitefunctions
import cgi

servervalues = appsitefunctions.getserverinfo()

host = servervalues[0]
ipaddress = servervalues[1]
webprotocol = servervalues[2]
port = servervalues[3]
fqdn = servervalues[4]

#Start HTML print out, headers are printed so the Apache server on APP does not produce a malformed header 500 server error
print '''
<Content-type: text/html\\n\\n>
<html>
<head>
<title>Multi-Tier Web App</title>
</head>
<body>
<table border="1">
'''
appsitefunctions.printserverinfo(fqdn,host,ipaddress,webprotocol,port)

print '''
</table>
</body>
</html>
'''