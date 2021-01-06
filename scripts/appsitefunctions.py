#!/usr/bin/python
import os.path
import cgi
import socket
import os
import urllib
import time
import ConfigParser
import requests

# Turn on debug mode.
import cgitb
cgitb.enable()

#loads data from the mtwa.conf file to be used in the application
def importconfiguration (): 
	if os.path.exists('/etc/avx/avx.conf'):
		configParser = ConfigParser.RawConfigParser()   
		configFilePath = r'/etc/avx/avx.conf'
		configParser.read(configFilePath)

		WebServerName = configParser.get('avx-config', 'WebServerName')
		AppServerName = configParser.get('avx-config', 'AppServerName')
		DBServerName = configParser.get('avx-config', 'DBServerName')
		MyFQDN = configParser.get('avx-config', 'MyFQDN')
		return (WebServerName, AppServerName, DBServerName, MyFQDN)
	else:
		print 'ERROR: AVX config file ', os.path.realpath('/etc/avx/avx.conf'), 'not found!'

def printappservererror():

	print "<center><div class=\"alert alert-danger\" role=\"alert\">ERROR: APPLICATION SERVER UNAVAILABLE</div></center>"

def printdbservererror():

	#Start HTML print out, headers are printed so the Apache server on APP does not produce a malformed header 500 server error
	print '''
	<Content-type: text/html\\n\\n>
	<html>
	<head>
	<link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css" integrity="sha384-ggOyR0iXCbMQv3Xipma34MD+dH/1fQ784/j6cY/iJTQUOhcWr7x9JvoRxT2MZw1T" crossorigin="anonymous">
	<title></title>
	</head>
	<body>
	<center>
	<div class="alert alert-danger" role="alert">ERROR: DATABASE SERVER UNAVAILABLE</div>
	</center>
	</body>
	</html>
	'''

def connectionerror():
	print "<center><div class=\"alert alert-danger\" role=\"alert\">STATUS: DOWN</div></center>"

def connectionworks():
	print "<center><div class=\"alert alert-success\" role=\"alert\">STATUS: UP</div></center>"


def getserverparam(param_name):
    # This will get session properties like src_port, src_addr, etc
	for each in os.environ.keys():	
		#Uncomment the next line if you want to see all of the values that could be used
		each_value = os.environ[each]
		each_value_string = str(each_value)

		each_string = str(each)

		if each_string == param_name:			
			servervalue = each_value_string
			return servervalue
	return None

def removehtmlheaders(htmlcode):
	#This function is designed to remove the HTML headers that are added so that Apache on the APP server will not give a 500 error due to bad headers.
	splitcode = htmlcode.split('\n')

	#Delete the first 7 elements in the list.  This is the first section of generic HTML code to be removed.
	deletecount = 7
	while deletecount > 0:
		del splitcode[0]
		deletecount-=1
	
	#Delete the last 5 elements in the list.  This is the last section of generic HTML code to be removed.
	listposition = int(len(splitcode) - 1)
	deletecount = 5
	while deletecount > 0:
		del splitcode[listposition]
		listposition -=1
		deletecount-=1

	noheaderhtml = '\n'.join(splitcode)
	return noheaderhtml

def getserverinfo():
	#This get the hostname as defined in /etc/hostname
	hostname = (socket.gethostname())

	#Use OS environment variables gather information
	serverport = getserverparam('SERVER_PORT')
	ipaddress = getserverparam('SERVER_ADDR')
	servername = getserverparam('SERVER_NAME')
	serverprotocol = getserverparam('SERVER_PROTOCOL')
	
	return (hostname,ipaddress,serverprotocol,serverport,servername)

def getclientinfo():
	#Gathers client information
	clientip = getserverparam('REMOTE_ADDR')
	# print 'clientip', clientip #db
	clientport = getserverparam('REMOTE_PORT')
	# print 'clientport', clientport #db
	xff = getserverparam('HTTP_X_FORWARDED_FOR')
	# print 'xff', xff #db
	return (clientip,clientport,xff)

def getdbinfo():
	servernames=importconfiguration() 
	DBHostname=servernames[2]
	#This code establishes a connection to the DNS server to get the host's IP address.  This is to get the real IP address.  
	try:
		ipaddress = socket.gethostbyname(DBHostname) # your os sends out a dns query
	except Exception as e:
		return ("Error","Cannot resolve","Error","Error","Error","Down")
	else:
		#This get the hostname as defined in /etc/hostname
		hostname = (socket.gethostname())
		hostname = hostname.replace("app", "db")
		port = 443
		protocol = "TCP"
		status = "Up"
		return (DBHostname,hostname,ipaddress,protocol,port,status)


def enterdbformhtml():
	
	print '''<div class="container" style="width:600px"; margin:0 auto;>
	<form action="commitdb-web.py" method="POST" id="usrform">

	<div class="form-group"> <!-- Name field -->
		<label class="control-label " for="name">* Name</label>
		<input class="form-control" id="name" name="name" type="text" required="required"/>
	</div>
	
	<div class="form-group"> <!-- Email field -->
		<label class="control-label " for="email">* Email</label>
		<input class="form-control" id="email" name="email" type="email" required="required"/>
	</div>
	
	<div class="form-group"> <!-- Comments field -->
		<label class="control-label " for="comments">Comments</label>
		<textarea class="form-control" cols="40" id="comments" name="comments" rows="10"></textarea>
	</div>
	
	<div class="form-group">
		<button class="btn btn-primary " name="submit" type="submit">Submit</button>
	</div>
	</form>'''

def printserverinfo(fqdn,hostname,ipaddress,webprotocol,serverport):

	localtime = time.strftime("%Y-%m-%d %H:%M:%S")
	
	print '<b>FQDN:</b> %s<br>' %fqdn
	print '<b>Hostname:</b> %s<br>' %hostname
	print '<b>IPv4:</b> %s<br>'  %ipaddress
	print '<b>Protocol:</b> %s<br>' %webprotocol
	print '<b>Port:</b> %s<br>' %serverport
	print '<b>System Time:</b> %s<br>' %localtime
	connectionworks()

def printdbinfo(fqdn,hostname,ipaddress,webprotocol,serverport,status):

	localtime = time.strftime("%Y-%m-%d %H:%M:%S")

	if status == 'Up':
		print '<b>FQDN:</b> %s<br>' %fqdn
		print '<b>Hostname:</b> %s<br>' %hostname
		print '<b>IPv4:</b> %s<br>'  %ipaddress
		print '<b>Protocol:</b> %s<br>' %webprotocol
		print '<b>Port:</b> %s<br>' %serverport
		print '<b>System Time:</b> %s<br>' %localtime
		connectionworks()
	elif status == 'Down':
		connectionerror()

def printsite(modulename,form_name,form_email,form_comments):

	if os.path.exists('base.html'):
		basehtml = open('base.html').read().splitlines()

		print 'Content-type: text/html\n\n'

		#This gets and sets the values for the server
		clientvalues = getclientinfo()
		clientipaddress = clientvalues[0]
		clientportnum = clientvalues[1]
		xff = clientvalues[2]
		servervalues = getserverinfo()
		host = servervalues[0]
		ipaddress = servervalues[1]
		webprotocol = servervalues[2]
		port = servervalues[3]
		fqdn = servervalues[4]

		#This section will grab the name of the app server host name from the mtwa.conf file
		servernames=importconfiguration() 
		WebServerHostname=servernames[0]
		AppServerHostname=servernames[1]
		DBHostname=servernames[2]

		for each in basehtml: 
			print each #This will print the lines from base.html that is loaded into the FOR LOOP
			
			#This prints the server information in the HTML title.
			if each == '<!-- StartTitleInfo -->':
				print '<title>%s / %s [%s]</title>'%(host,ipaddress,webprotocol)

			if each == '<!-- StartClientInfo -->':
				localtime = time.strftime("%Y-%m-%d %H:%M:%S")

				print '<b>IPv4:</b> %s<br>' %clientipaddress
				print '<b>Port:</b> %s<br>' %clientportnum
				print '<b>X-Forwarded-For:</b> %s<br>' %xff
				print '<b>System Time:</b> %s<br>' %localtime


			#This print the local web server information
			if each == '<!-- StartWebServerInfo -->':
				
				#This will print that infomation for the HTML table in base.html
				printserverinfo(WebServerHostname,host,ipaddress,webprotocol,port)

			#This print the local web server information
			if each == '<!-- StartAppServerInfo -->':
				check = ("ping -c 1 {}".format(AppServerHostname))
				result = os.popen(check).read()
				if not "0 received" in result:
					try:
						appserverresponse = urllib.urlopen('http://%s:8080/appserverinfo.py'%AppServerHostname)
						appserverhtml = removehtmlheaders(appserverresponse.read())
						print appserverhtml
					except:
						connectionerror()
				else:
					connectionerror()


				#This gets and sets the values for the app server

			if each == '<!-- StartDBServerInfo -->':

				#This gets and sets the values for the app server 
				check = ("ping -c 1 {}".format(AppServerHostname))
				result = os.popen(check).read()
				if not "0 received" in result:
					try:
						dbserverresponse = urllib.urlopen('http://%s:8080/dbserverinfo.py'%AppServerHostname)
						dbserverhtml = removehtmlheaders(dbserverresponse.read())
						print dbserverhtml
					except:
						connectionerror()
				else:
					connectionerror()

			if each == '<!-- StartCustom -->':
				if modulename != None:
					if modulename == 'enterdb':
						enterdbformhtml()
					elif modulename == 'commitdb':
						check = ("ping -c 1 {}".format(AppServerHostname))
						result = os.popen(check).read()
						if not "0 received" in result:

						#Here form_name is used as the NAME which was entered into the form
							try:
								urlstr = 'http://%s:8080/commitdb-app.py?name=%s&email=%s&comments=%s'%(AppServerHostname,form_name,form_email,form_comments)
								appserverresponse = urllib.urlopen(urlstr)
								appserverhtml = removehtmlheaders(appserverresponse.read())
								print appserverhtml
							except:
								printdbservererror()
						else:
							connectionerror()

					else:
						try:
							urlstr = 'http://%s:8080/%s.py'%(AppServerHostname,modulename)
							appserverresponse = urllib.urlopen(urlstr)
							appserverhtml = removehtmlheaders(appserverresponse.read())
							print appserverhtml
						except:
							printappservererror()			
	else:
		print 'ERROR: Base HTML file ', os.path.realpath('base.html'), 'is missing'

