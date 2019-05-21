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

def initMysqlEnvVar():
    try:
        with open('/etc/profile','a') as fl:
            fl.write('export PATH=$PATH;/usr/local/mysql/bin'+'\n')
        os.system('source /etc/profile')
        print("1")
    except Exception as e:
        print(str(e))
        

def mkDATADir():
    """
        统一标准，将其所有数据文件data3306/data目录下,3306端口是可以变化的
    """
    if os.path.exists('/data/mysql/mysql%s/data' % port):
        print('mysql%s\/data directory already install' % port)
        sys.exit(1)
    else:
        try:
            os.makedirs('/data/mysql/mysql%s/data' % port)
            os.makedirs('/data/mysql/mysql%s/tmp' % port)
            os.makedirs('/data/mysql/mysql%s/logs' % port)
            print("1")
        except Exception as e:
            print("mkDATADir failed. %s" % str(e))

def unzipMysqlInstallPackage():
    """
        将tar包解压至base dirctory目录下
    """
    _instalpk='/usr/local/%s' % SOFT_NAME
    if not os.path.exists(_instalpk):
        print("mysql install package %s is not exists" % _instalpk )
        sys.exit(1)
    else:
        try:
            os.system('tar -xvf %s' % _instalpk)
            os.system('mv /usr/local/%s /usr/local/mysql' % SOFT_NAME[:-7])
        except Exception as e:
            print(str(e))
            
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
                print("mysql datadir privilege is wrong.")
                sys.exit(1)
            if not(os.stat(MYSQL_DATA_DIR+'mysql%s/data' %(port)).st_uid == mysql_uid and os.stat(MYSQL_DATA_DIR+'mysql%s/data' %(port)).st_gid == mysql_gid):
                print("mysql datadir sub directory data privileges is wrong")
                sys.exit(1)
            if not(os.stat(MYSQL_DATA_DIR+'mysql%s/logs' %(port)).st_uid == mysql_uid and os.stat(MYSQL_DATA_DIR+'mysql%s/logs' %(port)).st_gid == mysql_gid):
                print("mysql datadir sub directory logs privileges is wrong")
                sys.exit(1)
            if not(os.stat(MYSQL_DATA_DIR+'mysql%s/tmp' %(port)).st_uid == mysql_uid and os.stat(MYSQL_DATA_DIR+'mysql%s/logs' %(port)).st_gid == mysql_gid):
                print("mysql datadir sub directory tmp privileges is wrong")


if __name__ == '__main__':
    if(sys.argv[1]=='mkdatadir'):
        mkDATADir()
    elif(sys.argv[1]=='unzipm'):
        unzipMysqlInstallPackage()
    elif(sys.argv[1]=='addusergroup'):
        checkSetMysqlOwnerGroup()
    elif(sys.argv[1]=='initenv'):
        initMysqlEnvVar()
    else:
        print('not_param')