
#import os.path
import sys
#file_path = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.path.pardir))
#if file_path not in sys.path:
#    sys.path.insert(0, file_path) 
import requests
import json
import base64
import getpass
#import requests.packages.urllib3
#requests.packages.urllib3.disable_warnings()

"""
 This class used to fetch node name of given IPAddress
"""

class Orion:

    """
      INPUT : URL -- Orion server Address
              username -- Orion Server UserName
	      password -- Orion Server Password
	      nodeIPaddress -- Given IPAddress 
    """
    def __init__(self,URL,username,password,nodeIPaddress):
	    self.baseUrl = "https://"+URL+":17778/SolarWinds/InformationService/v3/Json/Query?query=SELECT+n.Caption+,+n.IPAddress+FROM+Orion.Nodes+n+WHERE+n.IPAddress+=+\'"+nodeIPaddress+"\'"	    
	    self.credentials = (username, password)

    """
     This method used to get the data from Orion server and return the results as JSON format.
    """
    def _req(self):
	    return requests.request("GET",self.baseUrl,
	                          verify = False,
	                          auth = self.credentials,
	                          headers = {'Content-Type' : 'application/json'})
    def  query(self):
	    return self._req()
	
    """
      INPUT : result -- retrieved data [list]
              NodeIPAddress -- Entered IPAddress
      OUTPUT : return NodeNames as list	      
	      
    """
    def getResults(self,result,NodeIPAddress):
	NodeNames=[]
	for i in result:
	    if NodeIPAddress.strip() == i['IPAddress'].strip():
		NodeNames.append(str(i['Caption']))
		#print NodeNames
	return NodeNames
    
if __name__== "__main__":
        serverURL=raw_input('Enter the Orion server URL :')
	UserName=raw_input('Enter the UserName :')
	Password=getpass.getpass('Password :')
	NodeIPAddress=raw_input('Enter the Node IPAddress :')
	swis = Orion(serverURL,UserName,Password,NodeIPAddress)
	out=swis.query().json()
	list=out['results']
	result=swis.getResults(list,NodeIPAddress)
	print "\n\n\n\n"
	print "Orion Server Name : ",serverURL
	print "Entered IPAddress : ",NodeIPAddress
	for i in result:
	    print "Node Name : ",i




