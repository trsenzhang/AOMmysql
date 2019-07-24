#/usr/bin/python



import sys
import os
import re
import optparse
import pymysql
import platform
from util.record_logging import RecordLog

global logger


MYSQL_SHOW_SLAVE_STATUS  = 'SHOW SLAVE STATUS;'

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

DEFINE_integer('port', '3306', 'The slave port')
DEFINE_string('user', 'root', 'replication user')
DEFINE_string('password', 'root', 'prelication user passwod')
DEFINE_string('host', '127.0.0.1', 'slave ip address')


def ShowUsage():
    parser.print_help()
    
def ParseArgs(argv):
    usage = sys.modules["__main__"].__doc__
    parser.set_usage(usage)
    unused_flags, new_argv = parser.parse_args(args=argv, values=FLAGS)
    return new_argv

def get_conn():
    return pymysql.connect(host=FLAGS.host, port=int(FLAGS.port), user=FLAGS.user,passwd=FLAGS.password)


def get_slave_status(conn):
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute(MYSQL_SHOW_SLAVE_STATUS)
    result = cursor.fetchone()
    return result


def main():
    try:
        conn = get_conn()
    except Exception as e:
        logger.info('Can\'t connect to mysql %s:%s ' %(FLAGS.host,FLAGS.port))
        sys.exit(0)
    
    r = get_slave_status(conn)
    if (r['Slave_IO_Running'] == "Yes" and r['Slave_SQL_Running'] == "Yes"):
        if('gtid is true'):
            if(r['Master_Log_File'] == r['Relay_Master_Log_File'] and r['Read_Master_Log_Pos'] == r['Exec_Master_Log_Pos'] and r['Retrieved_Gtid_Set'] == r['Executed_Gtid_Set']):
                pass
            else:
                print("the replication delay.")
        else:
            if(r['Master_Log_File'] == r['Relay_Master_Log_File'] and r['Read_Master_Log_Pos'] == r['Exec_Master_Log_Pos']):
                pass
            else:
                print("the replication delay.")
    
    else:
        print("%s of %s slave thread stop." % (r['Master_Host'],FLAGS.host))
        
if __name__ == '__main__':
        logger = RecordLog('repl_monitor').log()
        
        if(platform.system()=='Linux'):
            logger.info('The platform check pass.')
            new_argv = ParseArgs(sys.argv[1:])
            main()
        else:
            logger.info('The ENV is not linux,waiting coding')
            
        
