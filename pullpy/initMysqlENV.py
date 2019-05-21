# -*- coding: utf-8 -*-
"""
Created on Mon May 20 16:42:12 2019

@author: mzhang
"""

import os
import sys
import re
import pwd


MYSQL_DATA_DIR = '/data/mysql/'
MYSQL_BASE_DIR = '/usr/local/mysql/'
MYSQL_CNF_DIR = '/etc/'
MYSQL_BACK_DIR = '/data/backup/mysql/'
port=3306
SOFT_NAME='mysql-5.7.24-linux-glibc2.12-x86_64.tar.gz'
SOFT_NAME_FILE='mysql-5.7.24-linux-glibc2.12-x86_64'

def initMysqlEnvVar():
    try:
        with open('/etc/profile','a') as fl:
            fl.write('export PATH=$PATH;/usr/local/mysql/bin'+'\n')
        os.system('source /etc/profile')
        return("1")
    except Exception as e:
        return(str(e))
        

def mkDATADir():
    """
        统一标准，将其所有数据文件data3306/data目录下,3306端口是可以变化的
    """
    if os.path.exists('/data/mysql/mysql%s/data' % port):
        return('mysql%s\/data directory already install' % port)
        sys.exit(1)
    else:
        try:
            os.makedirs('/data/mysql/mysql%s/{data,tmp,logs}' % port)
            return(1)
        except Exception as e:
            return("mkDATADir failed. %s" % str(e))

def unzipMsoft():
    if os.path.exits('/usr/local/mysql'):
        return('The mysql base dirctory is exists.')
        sys.exit(1)
    else:
        try:
            os.system('tar -xvf /usr/local/%s' % SOFT_NAME)
            os.system('mv /usr/local/%s /usr/local/mysql' % SOFT_NAME_FILE)
            return(1)
        except Exception as e:
            return("unzipMsoft. %s" % str(e))
            
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
                return("mysql datadir privilege is wrong.")
                sys.exit(1)
            if not(os.stat(MYSQL_DATA_DIR+'mysql%s/data' %(port)).st_uid == mysql_uid and os.stat(MYSQL_DATA_DIR+'mysql%s/data' %(port)).st_gid == mysql_gid):
                return("mysql datadir sub directory data privileges is wrong")
                sys.exit(1)
            if not(os.stat(MYSQL_DATA_DIR+'mysql%s/logs' %(port)).st_uid == mysql_uid and os.stat(MYSQL_DATA_DIR+'mysql%s/logs' %(port)).st_gid == mysql_gid):
                return("mysql datadir sub directory logs privileges is wrong")
                sys.exit(1)
            if not(os.stat(MYSQL_DATA_DIR+'mysql%s/tmp' %(port)).st_uid == mysql_uid and os.stat(MYSQL_DATA_DIR+'mysql%s/logs' %(port)).st_gid == mysql_gid):
                return("mysql datadir sub directory tmp privileges is wrong")


if __name__ == '__main__':
    if(sys.argv[1]=='mkdatadir'):
        mkDATADir()
    elif(sys.argv[1]=='unzipm'):
        unzipMsoft()
    elif(sys.argv[1]=='addusergroup'):
        checkSetMysqlOwnerGroup()
    elif(sys.argv[1]=='initenv'):
        initMysqlEnvVar()
    else:
        print('not_param')