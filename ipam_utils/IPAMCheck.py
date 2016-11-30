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
import ipaddr
from DBCode import DB
import ipcalc

class IPAMCheck:
    
        def __init__(self):
	    self.db=DB()
	       
	    
        def connect(self,hostName,username,password,attempt=1):
            try:
		#log.info("Login to %s router ",str(hostName))
                routerHanlder=cling.Cling(hostname=hostName,username=username,password=password,personality='ios',max_login_attempts=3,pexpect_timeout=200,pexpect_read_loop_timeout=0.5)
                routerHanlder.login()
                return routerHanlder
            except Exception as e:
                if "Authentication" in str(e):
		    if attempt == 1:
			routerHandler=self.connect(hostName,"fallback","De7lc3-S!!",2)
                    msg="Error.Authentication failed"
                    #log.warning('Authentication error. %s',str(e))
                elif "timed-out" in str(e):
		    if attempt == 1:
			routerHandler=self.connect(hostName,"fallback","De7lc3-S!!",2)		    
                    msg="Erro.Connection timed out error"
                    #log.warning('Connection timed out error. %s',str(e))
                elif "refused" in str(e):
		    if attempt == 1:
			routerHandler=self.connect(hostName,"fallback","De7lc3-S!!",2)		    
                    msg="Error.Connection refused error"
                    #log.warning('Connection refused  error. %s',str(e))
                else:    
		    if attempt == 1:
			routerHandler=self.connect(hostName,"fallback","De7lc3-S!!",2)		    
		    #routerHandler=self.connect(hostName,"fallback","De7lc3-S!!")
                    msg='Error.Connecting to router '+hostName+' got failed. Error msg '+str(e)
                    #log.warning('Connecting to router got error. %s',str(e))
		    
                return msg
        
        def runCommand(self,routerHandler,command,hostName):
	    output=""
            try:
                output=routerHandler.run_command(command)
		#log.info("%s Command output %s ",str(command),str(output))
		print output
                return output
            except Exception as e:
                if "closed" in str(e):
                 #   log.warning('Connection got closed. Error msg %s',str(e))
		   # return "Errorrun"
                    routerHandler=self.connect(hostName,"fallback","De7lc3-S!!")
		    if "Error" in str(routerHandler):
			#log.warning('Connection got closed.So skipping source roter operation')
		 	return "Errorrun"
		    try:
			output=routerHandler.run_command(command)
			#log.info("%s Command output %s ",str(command),str(output))
			return output
		    except Exception as e:	
			if "closed" in str(e):
			 #   log.warning('Connection got closed. Error msg %s',str(e))
			    return "Errorrun"		        
                else:
		    print "came to else part"
                    for i in range(0,3):
                        try:
                            output=routerHandler.run_command(command)
                            return output
                        except Exception as e:
			    if "closed" in str(e):
			#	log.warning('Connection got closed. Error msg %s',str(e))
				#routerHandler=self.connect(hostName)
				if "Error" in str(routerHandler):
				    pass
			#	    log.warning('Connection got closed.So skipping source router finding operations')
				return "Errorrun"	
				
                               
                #log.warning("Exception occured while executing %s command on %s router . Error message %s",str(command),str(hostName),str(e))
                return ""
        
        def parsingShowIPRouter(self,output,fullIP):
            try:
                if output:
                    peAddress=""
		   # log.info(" parsing output ")
                    match=re.match(r'.*Routing\s+entry\s+for\s+(\d+\.\d+\.\d+\.\d+\/\d+)\s*.*',str(output),re.DOTALL)
                    if match:
                        peAddress=match.group(1)
			ip=str(peAddress).split('/')
			if str(peAddress).strip() == str(fullIP):
			    return "Exact",fullIP
			else:
			    return "Not",peAddress
                    return peAddress,""
            except Exception as e:
                    #log.warning('Exception occured while parsing \'%s\' command output : %s',str(command),str(output))
                    return "",""
        
        def parsingShowBgpAll(self,output,command):
            try:
                if output:
                    peAdress=""
                    match=re.match(r'.*\s*from\s+(\d+\.\d+\.\d+\.\d+)\s*.*best.*',str(output),re.DOTALL)
                    if match:
                        peAdress=match.group(1)
                    return peAdress
            except Exception as e:
                    #log.warning('Exception occured while parsing \'%s\' command output : %s',str(command),str(output))
		    return ""    
                        
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
                    #log.warning('Exception occured while parsing \'%s\' command output : %s',str(command),str(output))
		    return ""
        
        def parsingVRFTable(self,output,command):
	    try:
		if output:
		    vrfName=""
		    match=re.match(r'.*table\s+(.*)\).*Advertised.*',str(output),re.M|re.I|re.DOTALL)
		    if match:
			vrfName=match.group(1)
		    return vrfName
	    except Exception as e:
		#log.warning('Exception occured while parsing \'%s\' command output : %s',str(command),str(output))
		return ""	
	    
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
                 #       log.warning('Exception occured while parsing \'%s\' command output : %s',str(command),str(output))
                        return ""
	
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
		#log.info('Erro Occured on getSubnetModule')
		return "Error",str(e)
		    
	def matchNearestSubnet(self,subnets,subnetIP):
	    try:
		first=0
		ip=""
		mask=""
		macthSubnets=""
		n1=ipaddr.IPNetwork(str(subnetIP).strip())
		for i in subnets:
		    matchSubnet=str(i[0]).strip()+"/"+str(i[1]).strip()
		    n2=ipaddr.IPNetwork(str(matchSubnet).strip())
		    if  n1.overlaps(n2):
			if first == 0:
			    ip=i[0]
			    mask=i[1]
			    macthSubnets=str(ip)+"/"+str(mask)
			    first=1
			else:
			    if int(mask) < int(i[1]):
				ip=i[0]
				mask=i[1]
				macthSubnets=str(ip)+"/"+str(mask)
				first=1
				
		return macthSubnets		
	    except Exception as e:
		return "Error  "+str(e)
	    
	def checkOnRouterandIPAM(self,hostname,sourceIPs,username,password):
	    try:
		subnetIP,subnet=self.getSubnet(sourceIPs)
		if "Error" in str(subnetIP):
		    #log.warning(" Error occured suring subnetting process.Error msg ",str(subnet))
		    return "Error occured during subnetting process.Error msg "+str(subnet)
		ipmaskSplit=str(subnetIP).split("/")
		shvrfIP=str(ipmaskSplit[0])
		ipSplit=str(ipmaskSplit[0]).split(".")
		firstLP=str(ipSplit[0])+"."+str(ipSplit[1])+"."+str(ipSplit[2])+"."	 
		fullIP=str(ipSplit[0])+"."+str(ipSplit[1])+"."+str(ipSplit[2])+"."+str(ipSplit[3])
		if int(ipmaskSplit[1]) == 32 :
		    routerCheck=self.checkIPAMIP(hostname,subnetIP,firstLP,fullIP,"Yes",username,password)
		else:
		    routerCheck=self.checkIPAMIP(hostname,subnetIP,firstLP,fullIP,"No",username,password)
		ipamCheck=self.db.selectRecord(fullIP,str(ipmaskSplit[1]))
		if ipamCheck == -1:
		    #log.info("%s and IPAM processing got failed ",str(routerCheck))
		    return " "+routerCheck+".\n IPAM check got failed"
		elif ipamCheck:
		    #log.info("%s and also available on New IPAM ",str(routerCheck))
		    print routerCheck+" and also available on New IPAM"
		    if "exact" in str(routerCheck).strip():
			return " "+routerCheck+".\n Avilable in  IPAM"
		    return " "+routerCheck+"\n Avilable in  IPAM"
		else:
		    ipamCheck=self.db.selectRecord(fullIP,str(ipmaskSplit[1]),1)
		    if ipamCheck == -1:
		     #   log.info("%s and IPAM processing got failed ",str(routerCheck))
			return " "+routerCheck+".\n IPAM check got failed"	
		    elif ipamCheck:
			ip=""
			mask=""
			for values in ipamCheck:
			    ip=str(values[0])
			    mask=str(values[1])
			return " "+routerCheck+".\n No Exact Match found, nearest matching subnet in IPAM is"+str(ip)+"/"+str(mask)
		    else:
		      #  log.info("%s and not on New IPAM ",str(routerCheck))
			ipamCheck=self.db.selectRecord(firstLP,str(ipmaskSplit[1]),2)
			if ipamCheck == -1:
			    return ""+str(routerCheck)+"\n IPAM check got failed "
			elif ipamCheck:
			    check=self.matchNearestSubnet(ipamCheck,subnetIP)
			    if "Error" in str(check):
				return ""+str(routerCheck)+"\n IPAM check got failed "
			    elif check:
				return ""+str(routerCheck)+".\n No Exact Match found, nearest matching subnet in IPAM is"+str(check)
			    else:
				print " "+routerCheck+".\n not on New IPAM"
				return " "+routerCheck+".\n not in IPAM"
	    except Exception as e:
		return str(e)
	    
        def checkIPAMIP(self,hostname,sourceIPs,firstLP,fullIP,mask,username,password):
	    Next=0
	    Previous=0
	    pHandler=""
	    pHostname=""
	    rangeList=xrange(0,2000,2)
	    baseRouter=0
	    ipvrf=sourceIPs
	    skipFirst=0
	    attempt=0
	    try:
		paths=[]
		vrfExact='No'
		while 1:
		    rHandler=self.connect(hostname,username,password)
		    if str(hostname) in paths:
			return "Process got failed.Error message "+str(rHandler)
		    else:
			paths.append(str(hostname))
		    if "Error" in str(rHandler):
		#	log.warning('Connection got failed')
			return "Login to router got failed. Router IP "+str(hostname)
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
		#		log.warning("Running command on Router got failed")
				return "Finding vrf Process got failed due to connection closed issue. Login to "+str(hostname)+" router got failed"
			    else:
				if baseRouter == 0:
				    lPrefix=self.parsingShowBgpForPrefix(output,command,firstLP,fullIP,sourceIPs,mask)
				    if "ErrorParser" in str(lPrefix):
					#log.warning("Parser Error.")
					pass
				    elif lPrefix:    
					command="sh ip bgp vpnv4 all "+str(lPrefix)
				    else:
					command='sh ip route '+str(fullIP)
					output=self.runCommand(rHandler,command,hostname)
					if output:
					    exact,subnetip=self.parsingShowIPRouter(output,ipvrf)
					    if "Not" in str(exact):
						#log.info("%s is  on Global routing table.But there is no exact match , match subnet is %s",str(ipvrf),str(subnetip))
						return " No Exact Match Found, nearest matching subnet is "+subnetip+" in global routing table"
					    else:
						#log.info("%s is  on Global routing table",str(ipvrf))
						if exact:
						    return  ipvrf+" is  on Global routing table"
						else:
						    return ipvrf+" is free"
					else:
					    return ipvrf+" is free"					
				    if str(lPrefix).strip() == str(ipvrf).strip():
					vrfExact='Yes'
				    sourceIPs= lPrefix  
				    output=self.runCommand(rHandler,command,hostname)  
				    baseRouter=1
				else:
				    pass 
				cRouter=self.checkSoureRouter(output,command)
				if "ErrorParser" in str(cRouter):
				    #log.info("%s IP present on default VRF Routing Table",str(ipvrf))
				    return ipvrf+" is  on VRF table"
				elif "Yes" in str(cRouter):
				    #log.info('Source Router IP %s and router handle %s',str(hostname),str(rHandler))
				    vrfName=self.parsingVRFTable(output,command)
				    if vrfName:
					if "ErrorParser" in str(vrfName):
					#    log.info("%s IP on default VRF Routing Table",str(ipvrf))
					    if str(vrfExact) == 'Yes':
						return "Match on Default Routing Table."
					    return  " No Exact Match on defaiulf VRF table, nearest matching subnet is "+str(lPrefix)+" in routing table"
					else:
					 #   log.info("%s IP  on %s VRF Routing Table",str(ipvrf),str(vrfName))
					    if str(vrfExact) == 'Yes':
						return "Match  on "+str(vrfName)+" vrf routing table."						    
					    return  " No Exact Match  on "+str(vrfName)+" vrf routing table, nearest  matching subnet is "+str(lPrefix)+" in routing table"	
				    return rHandler
				elif "No" in str(cRouter):
				    PEAddress=self.parsingShowBgpAll(output,command)
				    if "ErrorParser" in str(PEAddress):
					#log.info("%s IP  on default VRF Routing Table",str(ipvrf))
					return  ipvrf+" is  on default VRF routing table"
				    elif  PEAddress:
					hostname=PEAddress
				    else:
					#log.info("%s IP  on default VRF Routing Table",str(ipvrf))
					if str(vrfExact) == 'Yes':
						return "Match on Default Routing Table."
					return  " No Exact Match on defaulf VRF table, nearest matching subnet is "+str(lPrefix)+" in routing table"						
			else:
			    command='sh ip route '+str(fullIP)
			    output=self.runCommand(rHandler,command,hostname)
			    if output:
				exact,subnetip=self.parsingShowIPRouter(output,ipvrf)
				if "Not" in str(exact):
				    #log.info("%s is  on Global routing table.But there is no exact match , match subnet is %s",str(ipvrf),str(subnetip))
				    return " No Exact Match on Global routing table, nearest matching subnet is "+subnetip+" in routing table"
				else:
				    #log.info("%s is  on Global routing table",str(ipvrf))
				    if exact:
					return  ipvrf+" is  on Global routing table"
				    else:
					return ipvrf+" is free"
					
			    else:
				return ipvrf+" is free"
	    except Exception as e:
		print "error",str(e)
		pass
		#log.warning("Exception occured %s ",str(e))
		    	        

if __name__ == "__main__":
    object=IPAMCheck()
    #object.intializeLoggerModule('IPAMCheck.log','IPAMCheck')
    lastIps=object.checkOnRouterandIPAM('10.10.10.70','10.10.10.244','','') 
    print lastIps
