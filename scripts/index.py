#!/usr/bin/python
import os.path
import cgi
import appsitefunctions

#This will figure out what module to call based on the URL passed.  /index.py?module=viewdb for example
form = cgi.FieldStorage()
modulename = form.getvalue('module')

appsitefunctions.printsite(modulename,None,None,None)
