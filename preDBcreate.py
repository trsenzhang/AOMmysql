#/usr/bin/python



import sys
import os
import optparse
import pymysql
import platform
from util.record_logging import RecordLog
import time

global logger


FLAGS = optparse.Values()
parser = optparse.OptionParser()


def DEFINE_string(name, default, description, short_name=None):
    if default is not None and default != '':
        description = "%s (default: %s)" % (description, default)
    args = [ "--%s" % name ]
    if short_name is not None:
        args.insert(0, "-%s" % short_name)

    parser.add_option(type="string", help=description, *args)
    parser.set_default(name, default)
    setattr(FLAGS, name, default)

def DEFINE_integer(name, default, description, short_name=None):
    if default is not None and default != '':
        description = "%s (default: %s)" % (description, default)
    args = [ "--%s" % name ]
    if short_name is not None:
        args.insert(0, "-%s" % short_name)

    parser.add_option(type="int", help=description, *args)
    parser.set_default(name, default)
    setattr(FLAGS, name, default)

DEFINE_integer('source_port', '3306', 'source database mysql port')
DEFINE_integer('target_port', '3307', 'target database mysql port')

DEFINE_string('db_base','/usr/local/mysql','mysql soft directory')

DEFINE_string('source_user', 'root', 'Manage source database mysql account')
DEFINE_string('target_user', 'root', 'Manage target database mysql account')

DEFINE_string('source_pwd','null','Manage source database mysql password')
DEFINE_string('target_pwd','null','Manage target database mysql password')

DEFINE_string('source_dev','/dev/mapper/vg_mysql-lv_mysql','source db dev.')
DEFINE_string('snap_dev','/dev/mapper/vg_mysql-mysqllvsnap','snap db dev.')


DEFINE_string('db_host','127.0.0.1','source and target database host ip address')


MYSQL_SHOW_SLAVE_STATUS  = 'SHOW SLAVE STATUS;'


def ShowUsage():
    parser.print_help()
    
def ParseArgs(argv):
    usage = sys.modules["__main__"].__doc__
    parser.set_usage(usage)
    unused_flags, new_argv = parser.parse_args(args=argv, values=FLAGS)
    return new_argv

def get_conn(flag):
    
    if flag == 'source':
        try:
            return pymysql.connect(host=FLAGS.db_host, port=int(FLAGS.source_port), user=FLAGS.source_user,passwd=FLAGS.source_pwd)
        except Exception as e:
            print(str(e))
    elif flag == 'target':
        try:
            return pymysql.connect(host=FLAGS.db_host, port=int(FLAGS.target_port), user=FLAGS.target_user,passwd=FLAGS.target_pwd)
        except Exception as e:
            print(str(e))
    else:
        exit(1)
        
def get_slave_status(flag):
    conn = get_conn(flag)
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute(MYSQL_SHOW_SLAVE_STATUS)
    result = cursor.fetchone()
    return result

      
def stop_slave(flag):
    conn = get_conn(flag)
    sql = "stop slave;"
    cursor = conn.cursor()
    cursor.execute(sql)
    cursor.close()
    conn.close()

def start_slave(flag):
    conn = get_conn(flag)
    sql = "start slave;"
    cursor = conn.cursor()
    cursor.execute(sql)
    cursor.close()
    conn.close()

def reset_slave():
    conn = get_conn('target')
    sql = "reset slave all;"
    cursor = conn.cursor()
    cursor.execute(sql)
    cursor.close()
    conn.close()

def stop_mysql(socket,user,pwd):
    logger.info("stop mysql intance.")
    os_cmd="%s/bin/mysqladmin -u%s -p%s -S/tmp/%s.sock shutdown" % (FLAGS.db_base,user,pwd,socket)
    try:
        os.popen(os_cmd).readlines()
    except Exception as e:
        logger.error(str(e))
    logger.info("stop mysql intance end.")

def umount_dev(group_name):
    logger.info("umount %s ." % group_name) 
    os_cmd1 = "fuser -k %s" % group_name
    os_cmd2 = "umount %s" % group_name
    try:
        for i in os_cmd1,os_cmd2:
            result = os.popen(i).readlines()
            print(result)
    except Exception as e:
        logger.error(str(e))
    logger.info("umount %s end." % group_name) 
    
def create_snap(size,group_name):
    logger.info("create snap mysqllvsnap") 
    os_cmd = "lvcreate -L %sG -s -n mysqllvsnap %s" % (int(size),group_name)
    
    try:
        result = os.popen(os_cmd).readlines()
        print(result)
    except Exception as e:
        logger.info(str(e))
    logger.info("create snap mysqllvsnap end.")
    
def start_mysql(cfg ,s1):
    logger.info("starting %s mysql db."  % s1 )
    os_cmd="%s/bin/mysqld --defaults-file=/conf/%s &" % (FLAGS.db_base,cfg)
    try:
        result = os.popen(os_cmd).readlines()
        print(result)
    except Exception as e:
        logger.info(str(e))
    logger.info("starting %s mysql db end." % s1) 

def mount_dev(group_name,dir_name):
    logger.info("mount %s ." % group_name)
    os_cmd = "mount %s /%s/" % (group_name,dir_name)
    try:
        result = os.popen(os_cmd).readlines()
        print(result)
    except Exception as e:
        logger.info(str(e))
    logger.info("mount %s end." % group_name) 

def remove_snap_dev():
    logger.info("remove snap ")
    os_cmd = "echo 'y'|lvremove %s" % FLAGS.snap_dev
    try:
        result = os.popen(os_cmd).readlines()
        print(result)
    except Exception as e:
        logger.info(str(e))
    logger.info("remove snap end.")
    
def main():
    #close source db and slave thread
    #mysql.sock   
    #mysql3307.sock
    
    if str(os.popen("ps -ef |grep 'my.cnf'|grep -v grep|wc -l").read()) == '1\n':
        logger.info("close source db.")
        stop_slave('source')
        
        stop_mysql('mysql',FLAGS.source_user,FLAGS.source_pwd)
        
        logger.info('waiting mysqld stop.')
        time.sleep(10)
        logger.info('mysqld stop finished.')
        
        logger.info("finished close source db.")
    else:
        logger.info("The source db not running.")
    #source_dev snap_dev
    try:
        umount_dev(FLAGS.source_dev)
    except Exception as e:
        logger.error(str(e))
        
    #remove history snap dev

    if str(os.popen("lvs |grep 'mysqllvsnap' |wc -l").read()) == '0\n':
        logger.info("Not snapshot group, you not remove snapshot group.")
    else:
        logger.info("The history snapshot group already exists.")
        if str(os.popen("ps -ef |grep 'my_snap.cnf'|grep -v grep|wc -l").read()) == '1\n':
            logger.info("close target db.")
            stop_mysql('mysql3307',FLAGS.target_user,FLAGS.target_pwd)
            time.sleep(10)
            logger.info("finished close target db instance.")
        else:
            logger.info("the target db not running.")
        #
        #
        #
        umount_dev(FLAGS.snap_dev)
        remove_snap_dev()
        logger.info("The history snapshot group was remove.")
    
    #create snap dev and mount 
    #/dev/mapper/vg_mysql-lv_mysql  /dev/mapper/vg_mysql-mysqllvsnap
    #
    create_snap(1,FLAGS.source_dev)
    
    mount_dev(FLAGS.snap_dev,"snap_data")
    
    mount_dev(FLAGS.source_dev,"data")
    
    #start source db and start slave
    start_mysql('my.cnf','source')
    
    logger.info('waiting mysqld start.stop')
    time.sleep(30)
    logger.info('mysqld start finished.')
    
    
    gss = get_slave_status('source')
    if gss is not None:
        
        start_slave('source')
        logger.info('starting source db slave thread finished')
    else:
        logger.info('Not slave thread.')
    
    
    if gss is not None:
    #start target db and reset slave
        r = get_slave_status('source')
        if (r['Slave_IO_Running'] == "Yes" and r['Slave_SQL_Running'] == "Yes"):
            #start snap db
            start_mysql('my_snap.cnf','target')
            time.sleep(10)
            gss2 = get_slave_status('target')
            if gss2 is not None:
                stop_slave('target')
                reset_slave()
            logger.info('starting snap db finished.')
        else:
            logger.info("The source db IO or SQL is not running.")
            sys.exit(0)
    
    else:
        logger.info('starting snap db.')
        start_mysql('my_snap.cnf','target')
        time.sleep(10)
        gss2 = get_slave_status('target')
        if gss2 is not None:
            stop_slave('target')
            reset_slave()
        logger.info('starting snap db finished.')       
        
    if gss is not None:
        start_slave('source')            
    

if __name__ == '__main__':
        
        
        logger = RecordLog('preDBcreate').log()
        
        if(platform.system()=='Linux'):
            
            logger.info('The platform check pass.')
            new_argv = ParseArgs(sys.argv[1:])
            logger.info (FLAGS)
            main()
        else:
            logger.info('The ENV is not linux,waiting coding')
            
        
