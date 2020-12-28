#!/usr/bin/python
import os.path
import cgi
import socket
import os
import urllib
import time
import ConfigParser

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

	print "<div class=\"alert alert-danger\" role=\"alert\">ERROR: APPLICATION SERVER UNAVAILABLE</div>"

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
	<div class="alert alert-danger" role="alert">ERROR: DATABASE SERVER UNAVAILABLE</div>

	</body>
	</html>
	'''

def getserverparam(param_name):

	# print param_name, "param_name<BR>" #db
    
	for each in os.environ.keys():	
		#Uncomment the next line if you want to see all of the values that could be used

		each_value = os.environ[each]

		each_value_string = str(each_value)

		each_string = str(each)

		if each_string == param_name:			
			servervalue = each_value_string
			return servervalue


	return None
	
def setcolor(protocolvalue):
	if protocolvalue == 'HTTP':
		return 'red'
	elif protocolvalue == 'HTTPS':
		return 'green'
	else:
		return 'black'

def finddnsresolver():
	#This function will find the local DNS server to be used in another function for finding the IP address of the host.
	dnsfile = open('/etc/resolv.conf').read().splitlines()
	for each in dnsfile:
		nameserverstring = each[:10]
		if nameserverstring == "nameserver":
			dns_ip = each[11:]
			return dns_ip
	return None

def removehtmlheaders(htmlcode):
	#This function is designed to remove the HTML headers that are adder so that Apache on the APP server will not give a 500 error due to bad headers.
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
	#This code establishes a connection to the DNS server to get the host's IP address.  This is to get the real IP address.  
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	sock.connect((finddnsresolver(),53)) # sock.connect(("nameserver",53))
	ipaddress=(sock.getsockname()[0])
	sock.close()

	#This get the hostname as defined in /etc/hostname
	hostname = (socket.gethostname())

	#Use OS environment variables gather information
	serverport = getserverparam('SERVER_PORT')

	servernames=importconfiguration() 
	MyFQDN=servernames[3]
	
	
	if getserverparam('REQUEST_SCHEME') != None:  
		serverprotocol = str.upper(getserverparam('REQUEST_SCHEME'))
	
		return (hostname,ipaddress,serverprotocol,serverport,MyFQDN)
	else:
		serverprotocol = 'Unknown'
		return (hostname,ipaddress,serverprotocol,serverport,MyFQDN)

	#IF YOU WANT TO FIGURE OUT WHAT VARIABLES CAN BE USED, UNCOMMENT THE NEXT LINE TO ADD OTHER INFORMATION AND REFRESH THE WEBPAGE
	# cgi.test() 

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
		return ("Error","Cannot resolve","Error","Error","Error")
	else:
		#This get the hostname as defined in /etc/hostname
		hostname = (socket.gethostname())
		hostname = hostname.replace("app", "db")
		port = 3306
		protocol = "TCP"
		status = "Up"
		return (DBHostname,hostname,ipaddress,protocol,port,status)


def enterdbformhtml():
	
	print '<center>'
	print '<table>'
	print '<tr>'
	print '<td>'
	print '<form action="commitdb-web.py" method="POST" id="usrform">'
	print '  <b>Name:</b><br>'
	print '  <input type="text" name="name" value="Mickey Mouse">'
	print '  <br><br>'
	print '  <b>Notes:</b><br>'
	print '  <textarea rows="6" cols="50" name="notes" form="usrform">Hot Dog, Hot Dog, Hot Diggy Dog!</textarea>'
	print '  <br><br>'
	print '  <b>Number of records to create:</b><br>'
	print '  <input type="number" name="count" min="1" max="1000" value="1">'
	print '  <br><br>'
	print '  <input type="submit" value="Submit">'
	print '</form>'
	print '</td>'
	print '</tr>'
	print '</table>'
	print '</center>'

def cleardbformhtml():

	print '<!-- Start of form -->'
	print '<center>'
	print '<table>'
	print '<tr>'
	print '<td>'
	print '<form action="cleardb-web.py" method="POST" id="usrform">'
	print '  <b><br> Enter <font color="red">ERASE </font>to clear the database:</b><br>'
	print '  <input type="text" name="command" value="">'
	print '  <br><br>'
	print '  <input type="submit" value="Submit">'
	print '</form>'
	print '</td>'
	print '</tr>'
	print '</table>'

	print '</center>'

def printserverinfo(fqdn,hostname,ipaddress,webprotocol,serverport):

	localtime = time.strftime("%Y-%m-%d %H:%M:%S")

	protocol_color = setcolor(webprotocol)
	
	print '<b>FQDN:</b> %s<br>' %fqdn
	print '<b>Hostname:</b> %s<br>' %hostname
	print '<b>IPv4:</b> %s<br>'  %ipaddress
	print '<b>Protocol:</b> %s<br>' %webprotocol
	print '<b>Port:</b> %s<br>' %serverport
	print '<b>System Time:</b> %s<br>' %localtime
	print '<b>Status:</b><font color="green"> Up</font><br>'

def printdbinfo(fqdn,hostname,ipaddress,webprotocol,serverport,status):

	localtime = time.strftime("%Y-%m-%d %H:%M:%S")

	protocol_color = setcolor(webprotocol)
	if status == 'Up':
		print '<b>FQDN:</b> %s<br>' %fqdn
		print '<b>Hostname:</b> %s<br>' %hostname
		print '<b>IPv4:</b> %s<br>'  %ipaddress
		print '<b>Protocol:</b> %s<br>' %webprotocol
		print '<b>Port:</b> %s<br>' %serverport
		print '<b>System Time:</b> %s<br>' %localtime
		print '<b>Status:</b><font color="green"> %s</font><br>' %status
	elif status == 'Down':
		print '<b>FQDN:</b> %s<br>' %fqdn
		print '<b>Hostname:</b> %s<br>' %hostname
		print '<b>IPv4:</b> %s<br>'  %ipaddress
		print '<b>Protocol:</b> %s<br>' %webprotocol
		print '<b>Port:</b> %s<br>' %serverport
		print '<b>System Time:</b> n/a<br>'
		print '<b>Status:</b><font color="red"> %s</font><br>' %status

def printsite(modulename,formname_or_cmd,formnotes,formcount):

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

				# print 'StartTitleInfo' #db
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

				#This gets and sets the values for the app server 
				try:
					appserverresponse = urllib.urlopen('http://%s:8080/appserverinfo.py'%AppServerHostname)
					appserverhtml = removehtmlheaders(appserverresponse.read())
					print appserverhtml
				except:
					print '<b>FQDN:</b> %s<br>' %AppServerHostname
					print '<b>Hostname:</b> n/a<br>'
					print '<b>IPv4:</b> n/a<br>'
					print '<b>Protocol:</b> n/a<br>'
					print '<b>Port:</b> n/a<br>'
					print '<b>System Time:</b> n/a<br>'
					print '<b>Status:</b><font color="red"> Down</font><br>'

			if each == '<!-- StartDBServerInfo -->':

				#This gets and sets the values for the app server 
				try:
					dbserverresponse = urllib.urlopen('http://%s:8080/dbserverinfo.py'%AppServerHostname)
					dbserverhtml = removehtmlheaders(dbserverresponse.read())
					print dbserverhtml
				except:
					print '<b>FQDN:</b> %s<br>' %DBHostname
					print '<b>Hostname:</b> n/a<br>'
					print '<b>IPv4:</b> n/a<br>'
					print '<b>Protocol:</b> n/a<br>'
					print '<b>Port:</b> n/a<br>'
					print '<b>System Time:</b> n/a<br>'
					print '<b>Status:</b><font color="red"> Down</font><br>'

			if each == '<!-- StartCustom -->':
				#This uses to value passed from the URL to basically set which .py script is used for this section.
				if modulename != None:
					if modulename == 'enterdb':
						enterdbformhtml()
					elif modulename == 'resetdb':
						cleardbformhtml()
					elif modulename == 'commitdb':
						#Here formname_or_cmd is used as the NAME which was entered into the form
						try:
							urlstr = 'http://%s:8080/commitdb-app.py?name=%s&notes=%s&count=%s'%(AppServerHostname,formname_or_cmd,formnotes,formcount)
							appserverresponse = urllib.urlopen(urlstr)
							appserverhtml = removehtmlheaders(appserverresponse.read())
							print appserverhtml
						except:
							printappservererror()

					elif modulename == 'cleardb':
						#Here formname_or_cmd is used as the COMMAND which was entered into the form
						try:
							urlstr = 'http://%s:8080/cleardb-app.py?command=%s'%(AppServerHostname,formname_or_cmd)
							appserverresponse = urllib.urlopen(urlstr)
							appserverhtml = removehtmlheaders(appserverresponse.read())
							print appserverhtml
						except:
							printappservererror()
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
