from dotenv import load_dotenv
load_dotenv()
import sys
import os
lib_dir = os.getenv('LIB_DIR')
if not lib_dir:
    sys.exit('no lib_dir in .env')
sys.path.append(os.getenv('LIB_DIR'))
import threading
import psutil
import pymongo
from time import sleep
from datetime import datetime, timedelta, timezone
from dateutil.parser import parse
from pprint import pprint
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

from josien import jlog, josiendotnet_db, listproducers, get_account, remcli_get_info, remcli_get_action_swap, listvoters, po, get_block


def init(stdout=True):
    ''' check mandetory vars from .env '''
    global pid_file
    global db
    global jlog
    log_file = os.getenv('CACHE_LOGFILE', False)
    jlog = jlog(stdout=stdout, feil=log_file)
    db = josiendotnet_db()
    try:
        pid_file = os.getenv('CACHE_PID')
    except:
        print(sys.exc_info())
        jlog.critical("{}".format(sys.exc_info()))
        sys.exit(1)


def add_db(col, slug=False, tag=False, data=False, owner=False, block=False):
    d = {}
    d['created_at'] = datetime.now()
    d['slug'] = slug
    d['tag'] = tag
    d['owner'] = owner
    d['block'] = block
    d['data'] = data
    try:
        ref = db[col].insert_one(d)
    except:
        jlog.critical("{} {}".format(tag, sys.exc_info()))

    jlog.info( "col:{} tag:{}".format(col,tag))


def writePidFile():
    pid = str(os.getpid())
    f = open(pid_file, 'w')
    f.write(pid)
    f.close()


def is_running():
    if os.path.exists(pid_file):
        with open(pid_file, 'r') as f:
            try:
                pid = int(f.read())
                if psutil.pid_exists(pid):
                    return(True)
            except BaseException:
                e = sys.exc_info()
                jlog.critical("{} {}".format(e, "PID ERROR!"))

    return(False)


def trxs(slaap=2):
    last = db.trxs.find_one( { "tag": 'trxs' }, 
                             { "_id": 0, "created_at": 0 },sort=([('created_at', pymongo.DESCENDING)]))
    pprint(last)




def trxs(slaap=2):
    while True:
        last = db.trxs.find_one( { "tag": 'trxs' },
                                 { "_id": 0, "created_at": 0 },sort=([('created_at', pymongo.DESCENDING)]))
        i = remcli_get_info()
        if i and 'head_block_num' in i:
           stop = i['head_block_num']
        if last and 'block' in last:
            start = last['block'] + 1
        else:
            start = i['head_block_num'] - 10
        blocks = []
        for block in range(start, stop):
            blocks.append(get_block(block))
        for b in blocks:
            if b['transactions'] and isinstance(b['transactions'], list):
                add_db(col='trxs', slug='trxs', tag='trxs', data=b, owner=b['producer'], block=b['block_num'])
        jlog.info('trxs sleeping for: {} seconds'.format(slaap))
        sleep(slaap)


def dev(slaap=2):
    print('dev')



def dev1(slaap=2):
    while True:
        jlog.info('Sleeping for: {} seconds'.format(slaap))
        sleep(slaap)



def main():
    if not is_running():
        jlog.info('{}'.format('Starting bot'))
        writePidFile()
        main()

        #dev1_t = threading.Thread(target=dev1, args=(), name='dev1')
        #dev1_t.start()

        trxs_t = threading.Thread(target=trxs, args=(), name='trxs')
        trxs_t.start()



if __name__ == '__main__':
    args = sys.argv[1:]
    if len(args) == 0:
        init()
        main()

    if 'monit' in args:
        init(stdout=False)
        main()

    if 'pruning' in args:
        init()
        pruning()


    if 'dev' in args:
        init()
        dev()

    if 'dev1' in args:
        init()
        dev1()
