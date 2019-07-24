# -*- coding: utf-8 -*-
"""
Created on Tue Jul  9 17:58:53 2019

@author: mzhang

脚本包括两部分
1.基于mysqldump的工具自动化备份
2.自动备份binlog
"""

import sys
import os
import optparse
import pymysql
import platform
from util.record_logging import RecordLog
import time


global logger


class bkBinlog(object):
    def test():
        pass

class bkLogical(object):

    def test():
        pass

class bkPyical(object):
    
    def test():
        pass
    


if __name__ == '__main__':
    
    logger = RecordLog('backup_mysql').log()
