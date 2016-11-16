#! /usr/bin/env python

# *------------------------------------------------------------------
# * DBCode.py  
# *
# 
# *------------------------------------------------------------------
# *@author:Gowdhaman Mohan

"""
 Importing required packages for this Apps
"""
import os.path
import sys
file_path = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.path.pardir))
if file_path not in sys.path:
    sys.path.insert(0, file_path)
import sqlalchemy.pool as pool
import mysql.connector
import datetime

def getconn():
    c = mysql.connector.connect(host='200.12.221.72',user='phpipam', password='EMCMTNip@mDB',database='phpipam')
    return c

class DB:
    dbConnectionPool = None

    def __init__(self):
        try:
            DB.dbConnectionPool = pool.QueuePool(getconn, max_overflow=20, pool_size=15,echo=True)
        except mysql.connector.Error as err:
            log.error('MySql Error: Exception occured due to Database doesnt exists or MySql Credentials error %s',str(err))

    def getConnection(self):
                    try:
                        conn = DB.dbConnectionPool.connect()
                        return conn
                    except mysql.connector.Error as err:
                        log.error('300000: MySql Error: Exception occured due to Database doesnt exists or MySql Credentials error %s',str(err))
                        return None
    
    def selectRecord(self,value,mask,skip=0):
        try:
            if skip == 0:
                SqlSelectQuery = "select INET_NTOA(subnet) from subnets where INET_NTOA(subnet)=\'"+str(value)+"\' and mask=\'"+str(mask)+"\'"
                print SqlSelectQuery
            else:
                SqlSelectQuery = "select INET_NTOA(subnet),mask from subnets where INET_NTOA(subnet)=\'"+str(value)+"\' ORDER BY mask DESC limit 1"
            connecTion = self.getConnection()
            lockQuery = " LOCK TABLES subnets READ"
            releaseLocks = " UNLOCK TABLES"
            returnVal = []
            if connecTion:
                try:
                    cursor = connecTion.cursor()
                    cursor.execute(lockQuery)
                    cursor.execute(SqlSelectQuery)
                    for (val) in cursor:
                        returnVal.append(val)
                    cursor.execute(releaseLocks)
                    connecTion.commit()
                    cursor.close()
                    return returnVal
                except Exception as err:
                    cursor.execute(releaseLocks)
                    cursor.close()
                    return -1
                    #raise Exception(err)
            else:
                print("300000: Error while connecting to MySql")  
                return -1
        except Exception as e:
            print str(e)
   

if __name__ == '__main__':
    db=DB()
    print db.selectRecord('172.23.13.0','32',1)
                                










