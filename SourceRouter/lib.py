#! /usr/bin/env python

#*--------------------------------------------------------------
#* common.py
#*
#*--------------------------------------------------------------
#*@author:Gowdhaman Mohan

import os.path
import sys
file_path = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.path.pardir))
if file_path not in sys.path:
    sys.path.insert(0, file_path) 
    
class lib: 
    @staticmethod
    def getEmailList(severity):
        if severity.strip() == "sev1":
            emailList = ["shadrach.retnamony@emcconnected.com","pvijay@emc-corp.net","Gowdhaman.Mohan@emcconnected.com","important-core-notifications@mtnsat.pagerduty.com"]
        elif severity.strip() == "sev2":
            emailList = ["shadrach.retnamony@emcconnected.com","critical-core-notifications@mtnsat.pagerduty.com","Gowdhaman.Mohan@emcconnected.com","pvijay@emc-corp.net"]  
        else:
            emailList = ["pvijay@emc-corp.net","Gowdhaman.Mohan@emcconnected.com"] 
        return emailList
    
                
    @staticmethod
    def getRouterCredentials():
        username = "madhan.endla"
        password = "Srirama2498!"
        return username,password
    
           

    

