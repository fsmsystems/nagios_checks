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
import XenAPI

def check_sr(session):
# This check the PBD of the XenServers if they are correctly attached to ISCSI storage
# We need to filter the non shared storage like Local, DVD, etc and get only the shared lvmiscsi device. You can change this using session.xenapi.SR.get_type
  errors=[]
  oks=[]
  out={}
  try:
	pbds = session.xenapi.PBD.get_all()
	for pbd in pbds:
		mypbd=session.xenapi.PBD.get_record(pbd)
		if mypbd['currently_attached'] == True :
			if session.xenapi.SR.get_shared(mypbd['SR']) == True :
				if 'lvmoiscsi' in session.xenapi.SR.get_type(mypbd['SR']):
					oks.append(session.xenapi.SR.get_name_label(mypbd['SR']) +' on ' +session.xenapi.host.get_name_label(mypbd['host']))
		else: 
			if session.xenapi.SR.get_shared(mypbd['SR']) == True :
                                if 'lvmoiscsi' in session.xenapi.SR.get_type(mypbd['SR']):
					errors.append(session.xenapi.SR.get_name_label(mypbd['SR']) + ' on ' +session.xenapi.host.get_name_label(mypbd['host']))
  except Exception, e:
            print ('Error retreiving list: %s' % str(e))
            raise
  out['OK']=oks
  out['NOK']=errors
  return out 


def sizeof_fmt(num):
    for x in ['bytes','KB','MB','GB','TB']:
        if num < 1024.0:
            return "%3.1f %s" % (num, x)
        num /= 1024.0

 
def check_disk(session,warn,cri):
  errors=[]
  oks=[]
  war=[]
  out={}
  C_TOLERANCE=cri
  W_TOLERANCE=warn
  try:
	sr=session.xenapi.SR.get_all()
	for sruuid in sr:
		if 'lvmoiscsi' in session.xenapi.SR.get_type(sruuid):
			srnamelabel = session.xenapi.SR.get_name_label(sruuid) 
			physical_size = int(session.xenapi.SR.get_record(sruuid)['physical_size'])
			physical_utilisation = int(session.xenapi.SR.get_record(sruuid)['physical_utilisation'])
			result = physical_size - physical_utilisation
			percent = 100 * physical_utilisation/physical_size
			if int(percent) <= int(W_TOLERANCE):
				oks.append(srnamelabel +': '+ str(sizeof_fmt(result))+' free : '+str(percent)+' % used')
			else:
				if int(percent) >= int(W_TOLERANCE):
					if int(percent) >= int(C_TOLERANCE):
						errors.append(srnamelabel +': '+ str(sizeof_fmt(result))+' free : '+str(percent)+' % used')
					else:
						war.append(srnamelabel +': '+ str(sizeof_fmt(result))+' free : '+str(percent)+' % used')
  except Exception, e:
            print ('Error retreiving list: %s' % str(e))
            raise
  out['OK']=oks
  out['WAR']=war
  out['NOK']=errors
  return out


def evaluate_tree_states(out):
        STATE_WARNING=1
        STATE_OK=0
        STATE_CRITICAL=2
	if len(out['NOK']) != 0:
		print 'NOK: '+str(out['NOK']) + ' OK: '+str(out['OK'])
		return STATE_CRITICAL
	else:
		if len(out['WAR']) != 0:
			print 'NOK: '+str(out['WAR']) + ' OK: '+str(out['OK'])
			return STATE_WARNING
		else:
			print 'NOK: '+str(out['NOK']) + ' OK: '+str(out['OK'])
			return STATE_OK
		

def evaluate_errors(out,WTOLERANCE):
# The WTOLERANCE - is the maximum fail tolerance for the results. For example, to mark as warning when a host of pool is down, call this funcion with 1, but if you want to get a critical for this host down, set WTOLERANCE to -1
	STATE_WARNING=1
	STATE_OK=0
	STATE_CRITICAL=2
#We want to see All output, first NOK, you can uncomment print lines if you want.
	print 'NOK: '+str(out['NOK']) + ' OK: '+str(out['OK'])
	if len(out['NOK']) == 0:
		return STATE_OK
	elif len(out['NOK']) == WTOLERANCE:
#		print "WARNING "+str(out['NOK']) 
		return STATE_WARNING
	else:
#		print "CRITICAL "+str(out['NOK'])
		return STATE_CRITICAL

def check_host(session):
#This function check the 'enabled' flag and if not but the host have the flag MAINTENANCE_MODE=True returns a softly warning
  errors=[]
  oks=[]
  out={}
  try:
	for s in session.xenapi.host.get_all():
        	server=session.xenapi.host.get_name_label(s)
		hrecord = session.xenapi.host.get_record(s)
		if hrecord['enabled'] == True:
			oks.append(server +' -> Enabled = ' + str(hrecord['enabled']))
		else:
			oconfig=hrecord['other_config']
			if oconfig['MAINTENANCE_MODE'] == 'true':
				errors.append(server + ' Is in MAINTENANCE_MODE, possible IT operation' )
			else:
				errors.append(server + ' -> Enabled = ' + str(hrecord['enabled']))	
  except Exception, e:
            print ('Error retreiving data: %s' % str(e))
	    errors.append( str(e))
            raise

  out['OK']=oks
  out['NOK']=errors
  return out

def check_metrics(session,warn,cri):
  errors=[]
  oks=[]
  war=[]
  out={}
  C_TOLERANCE=cri
  W_TOLERANCE=warn
  try:
	for host in session.xenapi.host.get_all():	
	#	print session.xenapi.host.get_record(host) 
		vms_in_host=session.xenapi.host.get_resident_VMs(host)
		for vm in vms_in_host:
			if not  session.xenapi.VM.get_is_a_template(vm) and not  session.xenapi.VM.get_is_control_domain(vm):
				nom=session.xenapi.VM.get_name_label(vm)	
				records=session.xenapi.VM.get_metrics(vm)
				print nom + str(records)
  except Exception, e:
            print ('Error retreiving list: %s' % str(e))
            raise
  out['OK']=oks
  out['WAR']=war
  out['NOK']=errors
  return out


def main(session,cmd,war,cri):
	okresponse=[]
	if cmd == 'SR':
		errors=check_sr(session)
		sysexit=evaluate_errors(errors,-1)
	elif cmd == 'HOSTS':
		errors=check_host(session)
		sysexit=evaluate_errors(errors,1)
	elif cmd == 'DISK':
		errors=check_disk(session,war,cri)
		sysexit=evaluate_tree_states(errors)
	elif cmd == 'METRICS':
		errors=check_metrics(session,war,cri)
		sysexit=evaluate_tree_states(errors)
	else:
	   print 'Desconocido...'
	session.xenapi.session.logout()
	sys.exit(sysexit)


if __name__ == "__main__":
    if len(sys.argv) <= 4:
        print "Usage:"
        print sys.argv[0], " <url> <username> <password> <SR | HOSTS>"
        sys.exit(1)
    url = sys.argv[1]
    username = sys.argv[2]
    password = sys.argv[3]
    cmd= sys.argv[4]
    war= sys.argv[5]
    cri= sys.argv[6]	
    #Try if is master, if not, get master IP like a boss
    try:
	session = XenAPI.Session('https://'+url)
	session.xenapi.login_with_password(username, password)
    except XenAPI.Failure, e:
      if e.details[0]=='HOST_IS_SLAVE':
        session=XenAPI.Session('https://'+e.details[1])
        session.login_with_password(username, password)
      else:
        raise
    main(session,cmd,war,cri)
