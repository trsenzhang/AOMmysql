# -*- coding: utf-8 -*-
"""
Created on Mon May 20 15:08:17 2019

@author: mzhang
"""
import paramiko

class OptRemote(object):
    
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
                self.logger.error("sendSoft exec failed. %s" % str(e))
        except Exception as e:
            self.logger.error(" func sendSoft connect error. %s " % str(e))
                
    
    def execRmotecmd(self,excmd):
        try:
            t = paramiko.SSHClient()
            t.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            t.connect(self.hostname,self.port,self.username,self.password)
            try:
                stdin,stdout,stderr=t.exec_command(excmd) #python --version
                return(stdout.read())
                t.close()
            except Exception as e:
                self.logger.error("func execRmotecmd exec error. %s " % str(e))
        except Exception as e:
            self.logger.error("func execRmotecmd connect error. %s " % str(e))
        