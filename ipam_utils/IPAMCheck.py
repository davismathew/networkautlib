#! /usr/bin/env python

#*--------------------------------------------------------------
#* IPAMCheck.py
#*
#*--------------------------------------------------------------
#*@author:Gowdhaman Mohan

import os.path
import sys
file_path = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.path.pardir))
if file_path not in sys.path:
    sys.path.insert(0, file_path) 
from multiprocessing.dummy import Pool as ThreadPool
import cling
import re
from netaddr import IPAddress,IPNetwork
from log import log
from DBCode import DB
import ipcalc

class IPAMCheck:
    
        def __init__(self):
            self.username,self.password="madhan.endla","Srirama2498!"
	    self.db=DB()
	    
	def intializeLoggerModule(self,fileName,name):
	    log(fileName,name)      
	    
        def connect(self,hostName,username="madhan.endla",password="Srirama2498!"):
            try:
		log.info("Login to %s router ",str(hostName))
                routerHanlder=cling.Cling(hostname=hostName,username=username,password=password,personality='ios',max_login_attempts=3,pexpect_timeout=200,pexpect_read_loop_timeout=0.5)
                routerHanlder.login()
                return routerHanlder
            except Exception as e:
                if "Authentication" in str(e):
                    msg="Error.Authentication failed"
                    log.warning('Authentication error. %s',str(e))
                elif "timed-out" in str(e):
                    msg="Erro.Connection timed out error"
                    log.warning('Connection timed out error. %s',str(e))
                elif "refused" in str(e):
                    msg="Error.Connection refused error"
                    log.warning('Connection refused  error. %s',str(e))
                else:    
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
		   # return "Errorrun"
                    routerHandler=self.connect(hostName,"fallback","De7lc3-S!!")
		    if "Error" in str(routerHandler):
			log.warning('Connection got closed.So skipping source roter operation')
		 	return "Errorrun"
		    try:
			output=routerHandler.run_command(command)
			log.info("%s Command output %s ",str(command),str(output))
			return output
		    except Exception as e:	
			if "closed" in str(e):
			    log.warning('Connection got closed. Error msg %s',str(e))
			return "Errorrun"		        
                else:
		    print "came to else part"
                    for i in range(0,3):
                        try:
                            output=routerHandler.run_command(command)
                            return output
                        except Exception as e:
			    if "closed" in str(e):
				log.warning('Connection got closed. Error msg %s',str(e))
				#routerHandler=self.connect(hostName)
				if "Error" in str(routerHandler):
				    log.warning('Connection got closed.So skipping source router finding operations')
				return "Errorrun"	
				
                               
                log.warning("Exception occured while executing %s command on %s router . Error message %s",str(command),str(hostName),str(e))
                return "Errorrun"
        
        def parsingShowIPRouter(self,output,fullIP):
            try:
                if output:
                    peAddress=""
                    match=re.match(r'.*Routing\s+entry\s+for\s+(\d+\.\d+\.\d+\.\d+/\d+)\s*.*',str(output),re.DOTALL)
                    if match:
                        peAddress=match.group(1)
			ip=str(peAddress).split('/')
			if str(ip[0]).strip() == str(fullIP):
			    return "Exact",fullIP
			else:
			    return "Not",peAddress
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
                        
        def parsingShowBgpForPrefix(self,output,command,threeoctect,sourceIPs,subnetIPs,mask = 'No'):
            try:
                if output:
                    longestPrefixAddress=""
		    list1=str(output).split('\r\n')
		    first=0
		    for line in list1:
			match=re.match(r'.\s*(>i|i|)((\d+\.\d+\.\d+\.)\d+\/(\d+)).*',str(line),re.M|re.I|re.DOTALL)
			if match:
			    matchip=match.group(3)
			    if str(mask).strip == "Yes".strip():
				if str(subnetIPs).strip() == str(match.group(2)).strip():
				    longestPrefixAddress=str(match.group(2))
			    else:
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
	
	def getSubnet(self,subnet):
	    try:
		match=re.match(r'(\d+\.\d+\.\d+\.\d+)\/(\d+)',str(subnet),re.M|re.I|re.DOTALL)
		if match:
		    mask=match.group(2)
		    if int(mask) == 32:
			return subnet,str(match.group(1))
		    else:
			sID=ipcalc.Network(str(subnet))
			subnet=str(sID.network())+"/"+str(mask)
			return subnet,str(sID.network())
		else:
		    return subnet+"/32",subnet
	    except Exception as e:
		log.info('Erro Occured on getSubnetModule')
		    
		
	def checkOnRouterandIPAM(self,hostname,sourceIPs):
	    subnetIP,subnet=self.getSubnet(sourceIPs)
	    ipmaskSplit=str(subnetIP).split("/")
	    shvrfIP=str(ipmaskSplit[0])
	    ipSplit=str(ipmaskSplit[0]).split(".")
	    firstLP=str(ipSplit[0])+"."+str(ipSplit[1])+"."+str(ipSplit[2])+"."	 
	    fullIP=str(ipSplit[0])+"."+str(ipSplit[1])+"."+str(ipSplit[2])+"."+str(ipSplit[3])
	    if int(ipmaskSplit[1]) == 32 :
		routerCheck=self.checkIPAMIP(hostname,subnetIP,firstLP,fullIP,"Yes")
	    else:
		routerCheck=self.checkIPAMIP(hostname,subnetIP,firstLP,fullIP,"No")
	    ipamCheck=self.db.selectRecord(fullIP,str(ipmaskSplit[1]))
	    if ipamCheck == -1:
		log.info("%s and IPAM processing got failed ",str(routerCheck))
		return " "+routerCheck+".\n IPAM check got failed"
	    elif ipamCheck:
		log.info("%s and also available on New IPAM ",str(routerCheck))
		print routerCheck+" and also available on New IPAM"
		if "exact" in str(routerCheck).strip():
		    return " "+routerCheck+".\n Avilable in  IPAM"
		return " "+routerCheck+"\n Avilable in  IPAM"
	    else:
		ipamCheck=self.db.selectRecord(fullIP,str(ipmaskSplit[1]),1)
		if ipamCheck == -1:
		    log.info("%s and IPAM processing got failed ",str(routerCheck))
		    return " "+routerCheck+".\n IPAM check got failed"	
		elif ipamCheck:
		    ip=""
		    mask=""
		    for values in ipamCheck:
			ip=str(values[0])
			mask=str(values[1])
		    return " "+routerCheck+".\n No exact match and displaying Matching subnet "+str(ip)+"/"+str(mask)+" in IPAM"
		else:
		    log.info("%s and not on New IPAM ",str(routerCheck))
		    print " "+routerCheck+".\n not on New IPAM"
		    return " "+routerCheck+".\n not in IPAM"
	    
	    
        def checkIPAMIP(self,hostname,sourceIPs,firstLP,fullIP,mask):
	    Next=0
	    Previous=0
	    pHandler=""
	    pHostname=""
	    rangeList=xrange(0,2000,2)
	    baseRouter=0
	    ipvrf=sourceIPs
	    skipFirst=0
	    try:
		paths=[]
		vrfExact='No'
		while 1:
		    rHandler=self.connect(hostname)
		    if str(hostname) in paths:
			#skipFirst=1
			return "Process got failed.Error message "+str(rHandler)
			#return ipvrf+" on default VRF routing table"
		    else:
			paths.append(str(hostname))
			#if len(paths) == 1:
			 #   return -1
			#else:
			 #   pass
		    if "Error" in str(rHandler):
			log.warning('Connection got failed')
		    else:
			if Next in  rangeList:
			    pHandler=rHandler
			    pHostname=hostname
		        Next=Next + 1
			if baseRouter == 0:
			    command='sh ip bgp vpnv4 all | in '+str(firstLP)
			else:
			    command='sh ip bgp vpnv4 all '+str(sourceIPs)
			    
			output=self.runCommand(rHandler,command,hostname)
			if output:
			    if "Errorrun" in str(output):
				log.warning("Running command on Router got failed")
				return "Finding vrf Process got failed due to connection closed issue. Login to "+str(hostname)+" router got failed"
			    else:
				if baseRouter == 0:
				    lPrefix=self.parsingShowBgpForPrefix(output,command,firstLP,fullIP,sourceIPs,mask)
				    if "ErrorParser" in str(lPrefix):
					log.warning("Parser Error.")
				    elif lPrefix:    
					command="sh ip bgp vpnv4 all "+str(lPrefix)
				    else:
					command='sh ip route '+str(fullIP)
					output=self.runCommand(rHandler,command,hostname)
					if output:
					    exact,subnetip=self.parsingShowIPRouter(output,fullIP)
					    if "Not" in str(exact):
						log.info("%s is  on Global routing table.But there is no exact match , match subnet is %s",str(ipvrf),str(subnetip))
						return " No exact match, match subnet is "+subnetip+". "+subnetip
					    else:
						log.info("%s is  on Global routing table",str(ipvrf))
						return  ipvrf+" is  on Global routing table"
					else:
					    return ipvrf+" is free"					
					#command="sh ip bgp vpnv4 all "+str(hostname)
				    if str(lPrefix).strip() == str(ipvrf).strip():
					vrfExact='Yes'
				    sourceIPs= lPrefix  
				    output=self.runCommand(rHandler,command,hostname)  
				    baseRouter=1
				else:
				    pass 
				cRouter=self.checkSoureRouter(output,command)
				if "ErrorParser" in str(cRouter):
				    log.info("%s IP present on default VRF Routing Table",str(ipvrf))
				    return ipvrf+" is  on VRF table"
				elif "Yes" in str(cRouter):
				    log.info('Source Router IP %s and router handle %s',str(hostname),str(rHandler))
				    vrfName=self.parsingVRFTable(output,command)
				    if vrfName:
					if "ErrorParser" in str(vrfName):
					    log.info("%s IP on default VRF Routing Table",str(ipvrf))
					    if str(vrfExact) == 'Yes':
						return "Match on Default Routing Table."
					    return  " No exact Match on defaiulf VRF table. Match subnet is "+str(lPrefix)
					else:
					    log.info("%s IP  on %s VRF Routing Table",str(ipvrf),str(vrfName))
					    if str(vrfExact) == 'Yes':
						return "Match  on "+str(vrfName)+" vrf routing table."						    
					    return  " No exact match  on "+str(vrfName)+" vrf routing table.Match subnet is "+str(lPrefix)	
				    return rHandler
				elif "No" in str(cRouter):
				    PEAddress=self.parsingShowBgpAll(output,command)
				    if "ErrorParser" in str(PEAddress):
					log.info("%s IP  on default VRF Routing Table",str(ipvrf))
					return  ipvrf+" is  on default VRF routing table"
				    elif  PEAddress:
					hostname=PEAddress
				    else:
					log.info("%s IP  on default VRF Routing Table",str(ipvrf))
					if str(vrfExact) == 'Yes':
						return "Match on Default Routing Table."
					return  " No exact Match on defaulf VRF table. Match subnet is "+str(lPrefix)					
					#return  ipvrf+" is  on default VRF routing table."
					#return rHandler	
			else:
			    command='sh ip route '+str(fullIP)
			    output=self.runCommand(rHandler,command,hostname)
			    if output:
				exact,subnetip=self.parsingShowIPRouter(output,fullIP)
				if "Not" in str(exact):
				    log.info("%s is  on Global routing table.But there is no exact match , match subnet is %s",str(ipvrf),str(subnetip))
				    return " No exact match on Global routing table, match subnet is "+subnetip
				else:
				    log.info("%s is  on Global routing table",str(ipvrf))
				    return  ipvrf+" is  on Global routing table"
			    else:
				return ipvrf+" is free"
	    except Exception as e:
		log.warning("Exception occured %s ",str(e))
		    	        

if __name__ == "__main__":
    object=IPAMCheck()
    object.intializeLoggerModule('IPAMCheck.log','IPAMCheck')
    lastIps=object.checkOnRouterandIPAM('10.10.10.70','172.16.23.0/29') 
    #lastIps=object.checkOnRouterandIPAM('10.10.10.70','212.21.51.236')
    #lastIps=object.subnetCheckonRouter()
    print lastIps
