# -*- coding: utf-8 -*-
"""
Created on Mon May 20 15:08:17 2019

@author: mzhang
"""
import paramiko

class Trans(object):
    
    def __init__(self,logger,localpath,remotepath):
        self.logger = logger
        self.localpath = localpath
        self.remotepath = remotepath
          
    def sendSoft(self,hostname,port,username,password):
        try:
            t=paramiko.Transport(hostname,port)
            t.connect(username=username,password=password)
            try:
                sftp=paramiko.SFTPClient.from_transport(t)
                sftp.put(self.localpath,self.remotepath)
                t.close()
                self.logger.info("send soft success")
            except Exception as e:
                self.logger.error("sendSoft failed. %s" % str(e))
        except Exception as e:
            self.logger.error("connect error. %s " % str(e))
                

