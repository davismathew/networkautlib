#! /usr/bin/env python

#*--------------------------------------------------------------
#* RouterCommand.py
#*
#*--------------------------------------------------------------
#*@author:Gowdhaman Mohan

import os.path
import sys
file_path = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.path.pardir))
if file_path not in sys.path:
    sys.path.insert(0, file_path) 
import cling
import re
import jtextfsm as textfsm
from emc_utils.parseoutput_module import parseoutput

class RouterCommand:
    
    def __init__(self,routerip,command,username,password,personality='ios'):
        self.routerIP=routerip
        self.routerCommand=command
        self.username=username
        self.password=password
        self.personality=personality
#        self.intializeLoggerModule("RouterCommand","RCommand")
	
    def intializeLoggerModule(self,fileName,name):
	    log(fileName,name) 
		    
    def Login(self):
            try:
                routerHanlder=cling.Cling(hostname=self.routerIP,username= self.username,password=self.password,personality=self.personality,max_login_attempts=3,pexpect_timeout=200,pexpect_read_loop_timeout=0.5)
                routerHanlder.login()
                return routerHanlder
            except Exception as e:
                if "Authentication" in str(e):
                    msg="Error.Authentication failed"
                elif "timed-out" in str(e):
                    msg="Erro.Connection timed out error"
                elif "refused" in str(e):
                    msg="Error.Connection refused error"
                else:    
                    msg='Error.Connecting to router '+hostName+' got failed. Error msg '+str(e)
                return msg
	    
    def executeCommand(self,routerHandler):
	    output=""
            try:
                output=routerHandler.run_command(self.routerCommand)
                return output
            except Exception as e:
                if "closed" in str(e):
                    routerHandler=self.Login()
		    if "Error" in str(routerHandler):
			return "Errorrun"
                    self.executeCommand(routerHandler)
                else:
                    for i in range(0,3):
                        try:
                            output=routerHandler.executeCommand(self.routerCommand)
                            return output
                        except Exception as e:
			    if "closed" in str(e):
				pass
                return "Errorrun"
        
    def parseOutput(self,commandOutput,tempateFileName):
        try:
#           pathToFile='/etc/textfsm-templates/'+str(tempateFileName).strip()
#           log.info(" Template File Name %s . Output to be parse %s",str(tempateFileName),str(commandOutput))
#           template=open(pathToFile)
#           re_table=textfsm.TextFSM(template)
#           templateOutput=re_table.ParseText(commandOutput)    
#           log.info("Template Output %s ",str(templateOutput))
#           return templateOutput
            argument_spec=dict(platform='cisco_ios',index_file='index',template_dir='/etc/textfsm-templates',command='traceroute')

            templateOutput=parseoutput(commandOutput,argument_spec)
            return templateOutput
        except Exception as e:
            log.warning("Parsing Template Got failed.Error msg %s",str(e))
            return "ErrorTemplate Parsing Failed"

    def gencmdoutput(self):
#       cmdexec = RouterCommand(router,command,'madhan.endla','Srirama2498!')
        rHandler=self.Login()
        if "Error" in str(rHandler):
            log.warning("Connection got failed. Error msg %s",str(rHandler))
            return "conxn failed"
        else:
            commandoutput=self.executeCommand(rHandler)
            templateOutput=self.parseOutput(commandoutput,"cisco_ios_show_version.template")
            return templateOutput
	
	
if __name__ == '__main__':
     obj = RouterCommand('10.10.10.70','traceroute 10.10.10.102 source 212.21.50.254 numeric','madhan.endla','Srirama2498!')
     print obj.gencmdoutput()
#    object=RouterCommand('10.10.10.70','sh version','madhan.endla','Srirama2498!')
#    rHandler=object.Login()
#    if "Error" in str(rHandler):
#	print "Error"
#    else:
#	commandoutput=object.executeCommand(rHandler)
#	if "Errorrun" in str(commandoutput):
#	    print "Error"
#	else:
#	    templateOutput=object.parseOutput(commandoutput,"cisco_ios_show_version.template") 
#	    if "ErrorTemplate" in str(templateOutput):
#		print "Error"
#	    else:
#		print "Tamplate parsing is done"
#		print templateOutput
	
	
