import os.path
import sys
file_path = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.path.pardir))
if file_path not in sys.path:
    sys.path.insert(0, file_path) 
import itertools    
from FetchNodeName import Orion    
import json
from collections import OrderedDict

"""
 This class used to fetch traceroute info from json file and return list of unique path . 
"""
class stracePath:
    """
      Input : OrionServerURL --> URL of the Orion Server
              OrionUserName  --> Orion server User Name
	      OrionServerPassword --> OrionServerPassword 
    """
    def __init__(self,OrionServerURL,OrionUserName,OrionServerPassword):
        self.OrionServerURL=OrionServerURL
        self.OrionUserName=OrionUserName
        self.OrionServerPassword=OrionServerPassword
	self.nodeNamePath=[]
	self.ipPath=[]
	
     
    """
     This method takes IPAddress as input and return NodeName of that IPAddress 
    """
    def getNodeName(self,IPAddress):
	#Call orion class with required parameter
        swis=Orion(self.OrionServerURL,self.OrionUserName,self.OrionServerPassword,IPAddress)
	#Call query method in Orion class and returns NodeName in JSON format
	out=swis.query().json()
	list1=out['results']
	if list1:
	    pass
	else:
	    swis.getName(self.OrionServerURL,self.OrionUserName,self.OrionServerPassword,IPAddress)
	    out=swis.query().json()
	    list1=out['results']	    
	#Get correct name of node by given IPAddress 
	result=swis.getResults(list1,IPAddress)
	for i in result:
	    return i
    """
      Input :  Ansible Output file ( file should ne JSON format)
      Output : Parsed JSON output
      
    """
    def readAnsibleOutput(self,filename):
	json_data=open(filename).read()
	data = json.loads(json_data)	
	for key in data:
	    output=data[key]
        return output
    
    def getNodeNamePath(self,filename):
	if self.nodeNamePath:
	    return self.nodeNamePath
	else:
	    nodeName,ippath=self.getPath(filename)
	    return nodeName
	
    def getIPPath(self,filename):
	if self.ipPath:
	    return self.ipPath
	else:
	    nodeName,ippath=self.getPath(filename)
	    return ippath	    
    """
      This method takes parsed JSON output and fetch NodeNames for all IPAddress and returns list of paths between first to end hopnum
    """
    def getPath(self,output):
	try:
	    #out=self.readAnsibleOutput(filename)
	    traceRoutePath=OrderedDict()
	    i=0
	    list1=[]
	    Address=""
	    start=0
	    for path in output:
		index=path[0]
		index=str(index)
		Address=str(path[1])
		if index:
			if i == 0:
			    list1.append(Address)
			else:
			    traceRoutePath[index1]=list1
			    list1=[]
			    list1.append(Address)
			index1=index
			i=1
		else:
			if Address in list1:
			    pass
			else:
			    list1.append(Address)
	  		    
	    traceRoutePath[index1]=list1
	    print traceRoutePath
	    #return 1,2
	    traceNodeName=[]
	    traceIPwithNodeName=[]
	    for key in traceRoutePath:
		listOfIps=traceRoutePath[key]
		list1=[]
		list2=[]
		for ips in listOfIps:
		    nodeName=self.getNodeName(ips)
		    #print nodeName
		    if nodeName:
			list1.append(nodeName)
			list2.append(str(nodeName)+"("+str(ips)+")")
		    else:
			list1.append(ips)
			list2.append(str(ips)+"( NodeName not present in Orion server)")
		traceNodeName.append(list1)
		traceIPwithNodeName.append(list2)
	    i=1
	    listOfPath=[]
	    for tup in itertools.product(*traceNodeName):
		lt=list(tup)
		path="-->".join(lt)
		nPath="path"+str(i)+": "+path
		listOfPath.append(nPath)
		i=i+1
	    i=1
	    listOfPathwithIPS=[]
	    for tup in itertools.product(*traceIPwithNodeName):
		lt=list(tup)
		path="-->".join(lt)
		nPath="path"+str(i)+": "+path
		listOfPathwithIPS.append(nPath)
		i=i+1	    	
	    self.nodeNamePath=listOfPath
	    self.ipPath=listOfPathwithIPS
	    return listOfPath,listOfPathwithIPS
	except Exception as e:
	    print "Exception Message :- ",str(e)
		                 
	
   	       
if __name__ == "__main__":
    
    tPath=tracePath('ops.emc-corp.net','svcorionnet@emc-corp.net','$V(0r!0N3t')
    iPath=tPath.getNodeNamePath("8.json")
    rPath=tPath.getIPPath("8.json")
    #print iPath
    print "\n"
    print "\n"
    for path in iPath:
	print path 
	print "\n"
    for path in rPath:
	print "\n"
	print path
	
    


