# -*- coding: utf-8 -*-
"""
Created on Wed Feb 27 09:36:12 2019

@author: mzhang
"""

import logging
import  os
import datetime
import platform
"""
    日志模块，将按日期的格式方式
"""
class RecordLog(object):
    __total = 0
    
    def __init__(self,logname):
        if not os.path.exists('%s/%s' %(os.getcwd(),'log')):
            os.makedirs('%s/%s' % (os.getcwd(),'log'))
        self.logname = logname
        if RecordLog.__total != 0:
            raise Exception('You can only create one instanse')
    
    def log(self):
        fdate=datetime.datetime.now().strftime('%Y-%m-%d') + '.log'
        log_filename = '%s-%s' % (self.logname,fdate)
        logger = logging.getLogger('logger')
        logger.handlers = []
        logger.setLevel(logging.INFO)
        fmt_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        formatter = logging.Formatter('%(asctime)s : %(levelname)s : %(message)s',fmt_date)
        if(platform.system()=='Windows'):
            path_to_log_directory='%s\%s' % (os.getcwd(),'log')
        elif(platform.system()=='Linux'):
            path_to_log_directory='%s/%s' % (os.getcwd(),'log')
        
        fh = logging.FileHandler(filename=os.path.join(path_to_log_directory, log_filename))
        fh.setLevel(logging.INFO)
        fh.setFormatter(formatter)
        logger.addHandler(fh)
        
        return logger


    
    