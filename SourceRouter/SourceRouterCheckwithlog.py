#! /usr/bin/env python

#*--------------------------------------------------------------
#* SourceRouterCheck.py
#*
#*--------------------------------------------------------------
#*@author:Gowdhaman Mohan

import os.path
import sys
file_path = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.path.pardir))
if file_path not in sys.path:
    sys.path.insert(0,file_path) 
import cling
import re
from netaddr import IPAddress,IPNetwork
from lib import lib
from log import log
import jtextfsm as textfsm
from   SorceRouterTracePath import stracePath

class SourceRouterCheck:
    
        def __init__(self):
            self.username,self.password=lib.getRouterCredentials()
            #self.hostName=sourceIP
	    
	def intializeLoggerModule(self,fileName,name):
	    log(fileName,name)      
	    
        def connect(self,hostName,username='madhan.endla',password='Srirama2498!',attempt=1):
            try:
		log.info("Login to %s router ",str(hostName))
                routerHanlder=cling.Cling(hostname=hostName,username=username,password=password,personality='ios',max_login_attempts=3,pexpect_timeout=200,pexpect_read_loop_timeout=0.5)
                routerHanlder.login()
                return routerHanlder
            except Exception as e:
                if "Authentication" in str(e):
		    if attempt == 1:
			routerHandler=self.connect(hostName,"fallback","De7lc3-S!!",2)			
                    msg="Error.Authentication failed"
                    log.warning('Authentication error. %s',str(e))
		    
                elif "timed-out" in str(e):
		    if attempt == 1:
			routerHandler=self.connect(hostName,"fallback","De7lc3-S!!",2)		    
                    msg="Erro.Connection timed out error"
                    log.warning('Connection timed out error. %s',str(e))
                elif "refused" in str(e):
		    if attempt == 1:
			routerHandler=self.connect(hostName,"fallback","De7lc3-S!!",2)		    
                    msg="Error.Connection refused error"
                    log.warning('Connection refused  error. %s',str(e))
                else:    
		    if attempt == 1:
			routerHandler=self.connect(hostName,"fallback","De7lc3-S!!",2)		    
                    msg='Error.Connecting to router '+hostName+' got failed. Error msg '+str(e)
                    log.warning('Connecting to router got error. %s',str(e))
                return msg
        
        def runCommand(self,routerHandler,command,hostName):
	    output=""
            try:
                output=routerHandler.run_command(command)
		log.info("%s Command output %s ",str(command),str(output))
                return output
            except Exception as e:
                if "closed" in str(e):
                    log.warning('Connection got closed. Error msg %s',str(e))
                    routerHandler=self.connect(hostName)
		    if "Error" in str(routerHandler):
			log.warning('Connection got closed.So skipping source roter operation')
			return "Errorrun"
                    self.runCommand(routerHandler,command,hostName)
                else:
                    for i in range(0,3):
                        try:
                            output=routerHandler.run_command(command)
                            return output
                        except Exception as e:
			    if "closed" in str(e):
				log.warning('Connection got closed. Error msg %s',str(e))
				#routerHandler=self.connect(hostName)
				#if "Error" in str(routerHandler):
				 #   log.warning('Connection got closed.So skipping source router finding operations')
				  #  return "Errorrun"	
				               
                log.warning("Exception occured while executing %s command on %s router . Error message %s",str(command),str(hostName),str(e))
                return "Errorrun"
        
        def parsingShowIPRouter(self,output,command):
            try:
                if output:
                    peAddress=""
                    match=re.match(r'.*,\s+from\s+(\d+\.\d+\.\d+\.\d+),.*',str(output),re.DOTALL)
                    if match:
                        peAddress=match.group(1)
                    return peAddress
            except Exception as e:
                    log.warning('Exception occured while parsing \'%s\' command output : %s',str(command),str(output))
                    return "ErrorParser"
        
        def parsingShowBgpAll(self,output,command):
            try:
                if output:
                    peAdress=""
                    match=re.match(r'.*\s*from\s+(\d+\.\d+\.\d+\.\d+)\s*.*best.*',str(output),re.DOTALL)
                    if match:
                        peAdress=match.group(1)
                    return peAdress
            except Exception as e:
                    log.warning('Exception occured while parsing \'%s\' command output : %s',str(command),str(output))
		    return "ErrorParser"    
                        
        def parsingShowBgpForPrefix(self,output,command,threeoctect,sourceIPs):
            try:
                if output:
                    longestPrefixAddress=""
		    list1=str(output).split('\r\n')
		    first=0
		    for line in list1:
			match=re.match(r'.(>i|i|)((\d+\.\d+\.\d+\.)\d+\/(\d+)).*',str(line),re.M|re.I|re.DOTALL)
			if match:
			    matchip=match.group(3)
			    if str(threeoctect).strip() == str(matchip).strip():
				if IPAddress(str(sourceIPs)) in IPNetwork(str(match.group(2))):
				    if first == 0:
					longestPrefixAddress=match.group(2)
					mask=int(match.group(4))
					first=1
				    else:
					if mask <  int(match.group(4)):
					    longestPrefixAddress=match.group(2)    		
                    return longestPrefixAddress
            except Exception as e:
                    log.warning('Exception occured while parsing \'%s\' command output : %s',str(command),str(output))
		    return "ErrorParser"
        
        def parsingVRFTable(self,output,command):
	    try:
		if output:
		    vrfName=""
		    match=re.match(r'.*table\s+(.*)\).*Advertised.*',str(output),re.M|re.I|re.DOTALL)
		    if match:
			vrfName=match.group(1)
		    return vrfName
	    except Exception as e:
		log.warning('Exception occured while parsing \'%s\' command output : %s',str(command),str(output))
		return "ErrorParser"	
	    
        def checkSoureRouter(self,output,command):
                try:
                    if output:
                        match=re.match(r'.*directly\s*connected.*',str(output),re.DOTALL)
                        if match:
                            return "Yes"
                        else:
			    match=re.match(r'.*Local.*0\.0\.0\.0\s*from\s*0\.0\.0\.0.*best',str(output),re.DOTALL)
			    if match:
				return "Yes"
			    else:
				match=re.match(r'.*from\s*0\.0\.0\.0.*best',str(output),re.DOTALL)
				if match:
				    return "Yes"
				else:
				    return "No"
                except Exception as e:
                        log.warning('Exception occured while parsing \'%s\' command output : %s',str(command),str(output))
                        return "ErrorParser"
		    
        def findSourceRouter(self,hostname,sourceIPs,username,password):
	    Next=0
	    Previous=0
	    pHandler=""
	    pHostname=""
	    rangeList=xrange(0,2000,2)
	    baseRouter=0
	    shvrfIP=sourceIPs
	    ipSplit=str(sourceIPs).split(".")
	    firstLP=str(ipSplit[0])+"."+str(ipSplit[1])+"."+str(ipSplit[2])+"."
	    try:
		paths=[]
		while 1:
		    rHandler=self.connect(hostname,username,password)
		    if str(hostname) in paths:
			print "conection failed"
			print paths
			print hostname
			router="->".join(paths)
			log.warning('Unable to find soure router due to last  router in chain got login failed. %s ',str(router))
			return "Unable to find source router due to last  router in chain got login failed. "+str(router)
			#return paths[-2]
		    else:
			paths.append(str(hostname))
		    if "Error" in str(rHandler):
			log.warning('Connection got failed')
			return "Connection got failed.So skipped source router finding process.Process stopped at "+hostname+" router"
		    else:
			if Next in  rangeList:
			    pHandler=rHandler
			    pHostname=hostname
		        Next=Next + 1
			if baseRouter == 0:
			    command='sh ip bgp vpnv4 all | in i'+str(firstLP)
			else:
			    command='sh ip bgp vpnv4 all '+str(sourceIPs)
			    
			output=self.runCommand(rHandler,command,hostname)
			if output:
			    if "Errorrun" in str(output):
				log.warning("Running command on Router got failed")
				return "Running command on Router got failed.So skipped source router finding process.Process stopped at "+hostname+" router"
			    else:
				if baseRouter == 0:
				    lPrefix=self.parsingShowBgpForPrefix(output,command,firstLP,sourceIPs)
				    if "ErrorParser" in str(lPrefix):
					log.warning("Parser Error.")
					return "Running command on Router got failed.So skipped source router finding process.Process stopped at "+hostname+" router"
				    elif lPrefix:    
					command="sh ip bgp vpnv4 all "+str(lPrefix)
				    else:
					command='sh ip route '+str(sourceIPs)
					output=self.runCommand(rHandler,command,hostname)
					if output:
					    cRouter=self.checkSoureRouter(output,command)
					    if "ErrorParser" in str(cRouter):
						return "Running command on Router got failed.So skipped source router finding process.Process stopped at "+hostname+" router"
					    elif "Yes" in str(cRouter):
						log.info('Source Router IP:  %s and router handle %s',str(hostname),str(rHandler))
						return hostname
					    elif "No" in str(cRouter):
						PEAddress=self.parsingShowIPRouter(output,command)
						if "ErrorParser" in str(PEAddress):
						    log.warning("Parsing error")
						    return "Running command on Router got failed.So skipped source router finding process.Process stopped at "+hostname+" router"
						elif  PEAddress:
						    hostname=PEAddress
						    continue
						else:
						    log.warning('Command output nothing.So consider current router as source router')
						    return 'Command came output nothing.So stopping source roure finding process. Process stopped at '+hostname+' router'						
					#command="sh ip bgp vpnv4 all "+str(hostname)
				    sourceIPs= lPrefix  
				    output=self.runCommand(rHandler,command,hostname)  
				    baseRouter=1
				else:
				    pass 
				cRouter=self.checkSoureRouter(output,command)
				if "ErrorParser" in str(cRouter):
				    return "Running command on Router got failed.So skipped source router finding process.Process stopped at "+hostname+" router"
				elif "Yes" in str(cRouter):
				    log.info('Source Router IP %s and router handle %s',str(hostname),str(rHandler))
				    vrfName=self.parsingVRFTable(output,command)
				    if vrfName:
					if "ErrorParser" in str(vrfName):
					    log.warning("Parser Error.")
					    return "Running command on Router got failed.So skipped source router finding process.Process stopped at "+hostname+" router"
					else:
					    command='sh ip route vrf '+str(vrfName)+' '+str(shvrfIP)
					    
					    output=self.runCommand(rHandler,command,hostname)  
					    if "Errorrun" in str(output):
						log.warning("Running command on Router got failed")
						return "Running command on Router got failed.So skipped source router finding process.Process stopped at "+hostname+" router"
					    else:
						log.info('%s Command output %s',str(command),str(output))
					    command='traceroute vrf '+str(vrfName)+' '+str(shvrfIP)+' numeric'
					    output=self.runCommand(rHandler,command,hostname)
					    if "Errorrun" in str(output):
						log.warning("Running command on Router got failed")
						return "Running command on Router got failed.So skipped source router finding process.Process stopped at "+hostname+" router"
					    else:
						log.info('%s Command output %s',str(command),str(output))
						template=open("traceroute.txtfsm")
						re_table=textfsm.TextFSM(template)
						traceroute=re_table.ParseText(output)
						print "traceroute",traceroute
						tPath=stracePath('ops.emc-corp.net','svcorionnet@emc-corp.net','$V(0r!0N3t')
						nPath=tPath.getNodeNamePath(traceroute)
						print "Npath",nPath
						rPath=tPath.getIPPath(traceroute)
						print "rpath ",rPath
				    return rPath
				elif "No" in str(cRouter):
				    PEAddress=self.parsingShowBgpAll(output,command)
				    if "ErrorParser" in str(PEAddress):
					log.warning("Parsing error")
					return "Running command on Router got failed.So skipped source router finding process.Process stopped at "+hostname+" router"
				    elif  PEAddress:
					hostname=PEAddress
				    else:
					log.warning('Command output nothing.So consider current router as source router')
					return 'Command output nothing.So stopping source roure finding process. Process stopped at '+hostname+' router'	
			else:
			    command='sh ip route '+str(sourceIPs)
			    output=self.runCommand(rHandler,command,hostname)
			    if output:
				cRouter=self.checkSoureRouter(output,command)
				if "ErrorParser" in str(cRouter):
				    return "Running command on Router got failed.So skipped source router finding process.Process stopped at "+hostname+" router"
				elif "Yes" in str(cRouter):
				    log.info('Source Router IP:  %s and router handle %s',str(hostname),str(rHandler))
				    return hostname
				elif "No" in str(cRouter):
				    PEAddress=self.parsingShowIPRouter(output,command)
				    if "ErrorParser" in str(PEAddress):
					log.warning("Parsing error")
					return "Running command on Router got failed.So skipped source router finding process.Process stopped at "+hostname+" router"
				    elif  PEAddress:
					hostname=PEAddress
				    else:
					log.warning('Command output nothing.So consider current router as source router')
					return 'Command output nothing.So stopping source roure finding process. Process stopped at '+hostname+' router'
	    except Exception as e:
		log.warning("Exception occured %s ",str(e))
		return "Exception occured .Error msg "+str(e)
		    	        

if __name__ == "__main__":
    object=SourceRouterCheck()
    object.intializeLoggerModule('PathTestingLogger.log','RRCheck')
    lastIps=object.findSourceRouter('10.10.10.70','10.10.10.102','madhan.endla','Srirama2498!')  
    #lastIps=object.findSourceRouter('10.10.10.70','212.21.51.236')
    print lastIps


