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
from log import log
import jtextfsm as textfsm

class RouterCommand:
    
    def __init__(self,routerip,command,username,password,personality='ios'):
        self.routerIP=routerip
        self.routerCommand=command
        self.username=username
        self.password=password
        self.personality=personality
	
    def intializeLoggerModule(self,fileName,name):
	    log(fileName,name) 
		    
    def Login(self):
            try:
		log.info("Login to %s router ",str(self.routerIP))
                routerHanlder=cling.Cling(hostname=self.routerIP,username= self.username,password=self.password,personality=self.personality,max_login_attempts=3,pexpect_timeout=200,pexpect_read_loop_timeout=0.5)
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
	    
    def executeCommand(self,routerHandler):
	    output=""
            try:
                output=routerHandler.run_command(self.routerCommand)
		log.info("%s Command output %s ",str(self.routerCommand),str(output))
                return output
            except Exception as e:
                if "closed" in str(e):
                    log.warning('Connection got closed. Error msg %s',str(e))
                    routerHandler=self.Login()
		    if "Error" in str(routerHandler):
			log.warning('Connection got closed')
			return "Errorrun"
                    self.executeCommand(routerHandler)
                else:
                    for i in range(0,3):
                        try:
                            output=routerHandler.executeCommand(self.routerCommand)
                            return output
                        except Exception as e:
			    if "closed" in str(e):
				log.warning('Connection got closed. Error msg %s',str(e))
                log.warning("Exception occured while executing %s command on  router . Error message %s",str(self.routerCommand),str(e))
                return "Errorrun"
        
    def parseOutput(self,commandOutput,tempateFileName):
	try:
	    pathToFile='/etc/textfsm-templates/'+str(tempateFileName).strip()
	    log.info(" Template File Name %s . Output to be parse %s",str(tempateFileName),str(commandOutput))
	    template=open(pathToFile)
	    re_table=textfsm.TextFSM(template)
	    templateOutput=re_table.ParseText(commandOutput)	
	    log.info("Template Output %s ",str(templateOutput))
	    return templateOutput
	except Exception as e:
	    log.warning("Parsing Template Got failed.Error msg %s",str(e))
	    return "ErrorTemplate Parsing Failed"
	
	
if __name__ == '__main__':
    object=RouterCommand('10.10.10.70','sh version','madhan.endla','Srirama2498!')
    object.intializeLoggerModule("RouterCOmmand","RCommand")
    rHandler=object.Login()
    if "Error" in str(rHandler):
	log.warning("Connection got failed. Error msg %s",str(rHandler))
    else:
	commandoutput=object.executeCommand(rHandler)
	if "Errorrun" in str(commandoutput):
	    log.warning("Command %s Execution got failed ",str(commandoutput))
	else:
	    templateOutput=object.parseOutput(commandoutput,"cisco_ios_show_version.template") 
	    if "ErrorTemplate" in str(templateOutput):
		log.warning("Template %s parsing got failed ",str(templateOutput))
	    else:
		log.info('Template Parsing Done')
	
	
