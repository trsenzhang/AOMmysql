# -*- coding: utf-8 -*-
"""
Created on Mon May 20 15:08:17 2019

@author: mzhang
"""
import paramiko

class Trans(object):
    
    def __init__(self,logger,hostname,port,username,password):
        self.logger = logger
        self.hostname = hostname
        self.port = port
        self.username = username
        self.password = password
          
    def sendSoft(self,localpath,remotepath):
        try:
            t=paramiko.Transport(self.hostname,self.port)
            t.connect(username=self.username,password=self.password)
            try:
                sftp=paramiko.SFTPClient.from_transport(t)
                sftp.put(localpath,remotepath)
                t.close()
                self.logger.info("send soft success")
            except Exception as e:
                self.logger.error("sendSoft failed. %s" % str(e))
        except Exception as e:
            self.logger.error("connect error. %s " % str(e))
                
