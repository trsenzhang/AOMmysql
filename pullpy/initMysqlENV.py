# -*- coding: utf-8 -*-
"""
Created on Mon May 20 16:42:12 2019

@author: mzhang
"""

import os
import sys
import re
import pwd
from record_logging import RecordLog

MYSQL_DATA_DIR = '/data/mysql/'
MYSQL_BASE_DIR = '/usr/local/mysql/'
MYSQL_CNF_DIR = '/etc/'
MYSQL_BACK_DIR = '/data/backup/mysql/'
port=3306
SOFT_NAME='mysql-5.7.24-linux-glibc2.12-x86_64.tar.gz'

global logger


def initMysqlEnvVar():
    try:
        with open('/etc/profile','a') as fl:
            fl.write('export PATH=$PATH;/usr/local/mysql/bin'+'\n')
        os.system('source /etc/profile')
    except Exception as e:
        logger.error(str(e))
        

def mkDATADir():
    """
        统一标准，将其所有数据文件data3306/data目录下,3306端口是可以变化的
    """
    if os.path.exists('/data/mysql/mysql%s/data' % port):
        logger.info('mysql%s\/data directory already install' % port)
        sys.exit(1)
    else:
        try:
            os.makedirs('/data/mysql/mysql%s/data' % port)
            os.makedirs('/data/mysql/mysql%s/tmp' % port)
            os.makedirs('/data/mysql/mysql%s/logs' % port)
        except Exception as e:
            logger.error("mkDATADir failed. %s" % str(e))

def unzipMysqlInstallPackage():
    """
        将tar包解压至base dirctory目录下
    """
    _instalpk='/usr/local/%s' % SOFT_NAME
    os.system('tar -xvf %s -C /usr/local' % _instalpk)
    os.system('mv /usr/local/%s /usr/local/mysql' % SOFT_NAME[:-7])
            
def checkSetMysqlOwnerGroup():
            with open('/etc/passwd','r') as fl:
                for ln in fl:
                    semysql = re.search(r'mysql',ln,re.I)
            
            if semysql:
                os.system('chown -R mysql.mysql %s' % MYSQL_DATA_DIR)
                os.system('chown -R mysql.mysql %s' % MYSQL_BASE_DIR)
            else:
                os.system('groupadd mysql')
                os.system('useradd -g mysql -d /usr/local/mysql -s /sbin/nologin -MN mysql')
                os.system('chown -R mysql.mysql %s' % MYSQL_DATA_DIR)
                os.system('chown -R mysql.mysql %s' % MYSQL_BASE_DIR)
            
            list=[]
            for i in pwd.getpwnam('mysql'):
                list.append[i]
            mysql_uid=list[2]
            mysql_gid=list[3]
            
            if not(os.stat(MYSQL_DATA_DIR).st_uid == mysql_uid and os.stat(MYSQL_DATA_DIR).st_gid == mysql_gid):
                logger.info("mysql datadir privilege is wrong.")
                sys.exit(1)
            if not(os.stat(MYSQL_DATA_DIR+'mysql%s/data' %(port)).st_uid == mysql_uid and os.stat(MYSQL_DATA_DIR+'mysql%s/data' %(port)).st_gid == mysql_gid):
                logger.info("mysql datadir sub directory data privileges is wrong")
                sys.exit(1)
            if not(os.stat(MYSQL_DATA_DIR+'mysql%s/logs' %(port)).st_uid == mysql_uid and os.stat(MYSQL_DATA_DIR+'mysql%s/logs' %(port)).st_gid == mysql_gid):
                logger.info("mysql datadir sub directory logs privileges is wrong")
                sys.exit(1)
            if not(os.stat(MYSQL_DATA_DIR+'mysql%s/tmp' %(port)).st_uid == mysql_uid and os.stat(MYSQL_DATA_DIR+'mysql%s/logs' %(port)).st_gid == mysql_gid):
                logger.info("mysql datadir sub directory tmp privileges is wrong")


if __name__ == '__main__':
    logger = RecordLog('initMysqlENV').log()
    if(sys.argv[1]=='mkdatadir'):
        mkDATADir()
    elif(sys.argv[1]=='unzipm'):
        unzipMysqlInstallPackage()
    elif(sys.argv[1]=='addusergroup'):
        checkSetMysqlOwnerGroup()
    elif(sys.argv[1]=='initenv'):
        initMysqlEnvVar()
    else:
        logger.info('not_param')