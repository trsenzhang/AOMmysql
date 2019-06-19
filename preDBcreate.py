#/usr/bin/python



import sys
import os
import optparse
import pymysql
import platform
from util.record_logging import RecordLog

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

DEFINE_string('source_pwd', 'null', 'Manage source database mysql password')
DEFINE_string('target_pwd', 'null', 'Manage target database mysql password')

DEFINE_string('db_host', '127.0.0.1', 'source and target database host ip address')



def ShowUsage():
    parser.print_help()
    
def ParseArgs(argv):
    usage = sys.modules["__main__"].__doc__
    parser.set_usage(usage)
    unused_flags, new_argv = parser.parse_args(args=argv, values=FLAGS)
    return new_argv

def get_conn(flag):
    
    if flag == 'source':
        return pymysql.connect(host=FLAGS.db_host, port=int(FLAGS.source_port), user=FLAGS.source_user,passwd=FLAGS.source_pwd)
    elif flag == 'target':
        return pymysql.connect(host=FLAGS.db_host, port=int(FLAGS.target_port), user=FLAGS.target_user,passwd=FLAGS.target_pwd)
    else:
        exit(1)
        
def stop_slave(flag):
    conn = get_conn(flag)
    sql = "stop slave"
    cursor = conn.cursor()
    cursor.execute(sql)
    cursor.close()
    conn.close()

def start_slave(flag):
    conn = get_conn(flag)
    sql = "start slave"
    cursor = conn.cursor()
    cursor.execute(sql)
    cursor.close()
    conn.close()

def reset_slave():
    conn = get_conn('target')
    sql = "reset slave all"
    cursor = conn.cursor()
    cursor.execute(sql)
    cursor.close()
    conn.close()

def stop_mysql(name,user,pwd):
    logger.info("stop mysql intance.")
    os_cmd="%s/bin/mysqladmin -u%s-p%s -S/tmp/%s shutdown" % (FLAGS.db_base,user,pwd,name)
    try:
        result=os.popen(os_cmd).readlines()
        print(result)
    except Exception as e:
        logger.info(str(e))
    logger.info("stop mysql intance end.")

def umount_dev(name,s1):
    logger.info("umount %s .") % s1
    os_cmd1 = "fuser -k %s" % name
    os_cmd2 = "umount %s" % name
    try:
        for i in os_cmd1,os_cmd2:
            result = os.popen(i).readlines()
            print(result)
    except Exception as e:
        logger.info(str(e))
    logger.info("umount %s end.") % s1
    
def create_snap(name):
    logger.info("create snap mysqllvsnap") 
    os_cmd = "lvcreate -L 200G -s -n mysqllvsnap %s" % name
    
    try:
        result = os.popen(os_cmd).readlines()
        print(result)
    except Exception as e:
        logger.info(str(e))
    logger.info("create snap mysqllvsnap end.")
    
def start_mysql(name ,s1):
    logger.info("starting %s mysql db.") % s1 
    os_cmd="%s/bin/mysqld --defaults-file=/conf/%s &" % (FLAGS.db_base,name)
    try:
        result = os.popen(os_cmd).readlines()
        print(result)
    except Exception as e:
        logger.info(str(e))
    logger.info("starting %s mysql db end.") % s1

def mount_snap_dev(name,s1):
    logger.info("mount %s .") % s1
    os_cmd = "mount %s /snap_data/" % name
    try:
        result = os.popen(os_cmd).readlrebooines()
        print(result)
    except Exception as e:
        logger.info(str(e))
    logger.info("mount %s end.") % s1

def remove_snap_dev():
    logger.info("remove snap ")
    os_cmd = "lvremove /dev/mapper/vg_mysql-mysqllvsnap"
    try:
        result = os.popen(os_cmd).readlines()
        print(result)
    except Exception as e:
        logger.info(str(e))
    logger("remove snap end.")
    
def main():
    pass
    

if __name__ == '__main__':
        
        
        logger = RecordLog('preDBcreate').log()
        
        if(platform.system()=='Linux'):
            logger.info('The platform check pass.')
            new_argv = ParseArgs(sys.argv[1:])
            print(new_argv)
            print(FLAGS)
        else:
            logger.info('The ENV is not linux,waiting coding')
            
        
