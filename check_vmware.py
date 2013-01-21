#!/usr/bin/python
# WTFPL (Do What The Fuck You Want To Public License)
#
#           DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE
#                   Version 2, December 2004
#
#Copyright (C) 2013 Ferran Serafini <fsm.systems@gmail.com>
#
#Everyone is permitted to copy and distribute verbatim or modified
#copies of this license document, and changing it is allowed as long
#as the name is changed.
#
#           DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE
#  TERMS AND CONDITIONS FOR COPYING, DISTRIBUTION AND MODIFICATION
#
# 0. You just DO WHAT THE FUCK YOU WANT TO.

import sys, time
import os
import urllib
import random

def checkSpaceOk(datastoreName,datastorecapacity,datastorefree,war,cri):
	datastore=[]
        ocupation= int(datastorecapacity) - int(datastorefree)
	res=sizeof_fmt(int(datastorefree))
	percent_used = 100 * ocupation/int(datastorecapacity)
	if int(percent_used) <= int(war):
		status ='ok' 
		
	else:
			if int(percent_used) >= int(war):
				if int(percent_used) >= int(cri):
					status='critical' 	#CRI
				else:
					status='warning'	#WAR
	return status

def sizeof_fmt(num):
    for x in ['bytes','KB','MB','GB','TB']:
        if num < 1024.0:
            return "%3.1f %s" % (num, x)
        num /= 1024.0

def evaluate_errors(out,war,cri):
	STATE_WARNING=1
        STATE_OK=0
        STATE_CRITICAL=2
	if int(len(out['NOK'])) != 0:
		print 'NOK: '+str(out['NOK']) + ' OK: '+str(out['OK'])
		return STATE_CRITICAL
	else:
		if int(len(out['WAR'])) != 0:
			print 'NOK: '+str(out['WAR']) + ' OK: '+str(out['OK'])
			return STATE_WARNING	
		else:
			print 'NOK: '+str(out['NOK']) + ' OK: '+str(out['OK'])
			return STATE_OK
			
def getDatastoresStatus(url,username,password,war,cri):
	datastores={}
	oks=[]
	errors=[]
	warn=[]
	conn = urllib.urlopen("https://"+username+":"+password+"@"+url+"/folder?dcPath=ha-datacenter")
	web_out = conn.read()
	ws1=web_out.split('<td><a href="/folder?dcPath=ha%2ddatacenter&amp;dsName=')
	for i in ws1:
		if not i.startswith('<!DOCTYPE html'):
		#yeah we are now in datastore rows :)
			datastoreName= i.split('">')[0]
			otherinfo=i.split('>')
			datastorecapacity = otherinfo[4].split('</td')[0]
			datastorefree = otherinfo[6].split('</td')[0]
			status=checkSpaceOk(datastoreName,datastorecapacity,datastorefree,war,cri)	
			ocupation= int(datastorecapacity) - int(datastorefree)
			percent_used = 100 * ocupation/int(datastorecapacity)
			if status.startswith('ok'):
				oks.append(datastoreName +' - '+sizeof_fmt(int(datastorefree)) +' free - '+ str(percent_used) +' % used')
			if status.startswith('critical'):
				errors.append(datastoreName+' - '+sizeof_fmt(int(datastorefree)) +' free - '+ str(percent_used) + ' % used')
			if status.startswith('warning'):	
				warn.append(datastoreName+' - '+sizeof_fmt(int(datastorefree)) +' free - '+ str(percent_used) +' % used')
	datastores['OK']=oks
	datastores['NOK']=errors
	datastores['WAR']=warn
	return datastores

def getserver(serverlist):
	servers=serverlist.split(',')
	r=random.randint(0,1)
	return servers[r]

def main(url,username,password,cmd,war,cri):
        okresponse=[]
        if cmd == 'DATASTORES':
                errors=getDatastoresStatus(url,username,password,war,cri)
                sysexit=evaluate_errors(errors,war,cri)
        elif cmd == 'HOSTS':
                errors=getHosts()
#                sysexit=evaluate_errors(errors,1)
        else:
           print 'Desconocido...'
        sys.exit(sysexit)


if __name__ == "__main__":
    if len(sys.argv) <= 4:
        print "Usage:"
        print sys.argv[0], " <url> <username> <password> <DATASTORES | HOSTS>"
        sys.exit(1)
    serverlist = sys.argv[1]
    url = getserver(serverlist)
    username = sys.argv[2]
    password = sys.argv[3]
    cmd= sys.argv[4]
    war= sys.argv[5]
    cri= sys.argv[6]
    main(url,username,password,cmd,war,cri)

