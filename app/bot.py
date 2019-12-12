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
from pprint import pprint
import requests
from josien import jlog, db, listproducers, get_account


def init(stdout=True):
    ''' check mandetory vars from .env '''
    global pid_file
    global db
    global jlog
    log_file = os.getenv('LOG_FILE', False)
    jlog = jlog(stdout=stdout, feil=log_file)
    db = db()
    try:
        pid_file = os.getenv('PID_FILE')
    except:
        print(sys.exc_info())
        sys.exit(1)


def add_db(col, slug=False, tag=False, data=False):
    d = {}
    d['created_at'] = datetime.now(timezone.utc)
    d['slug'] = slug
    d['tag'] = tag
    d['data'] = data
    try:
        ref = db[col].insert_one(d)
    except:
        jlog.critical("{}".format(sys.exc_info()))

    jlog.info( "col:{}".format(col))



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



def status():
    while True:

        lp = listproducers()
        d = {}
        locked_stake = 0
        if lp and 'rows' in lp:
            j = False
            for row in lp['rows']:
                owner = get_account(row['owner'])
                locked_stake += int(owner['voter_info']['locked_stake'])
                d['owner'] = owner
                d['bp_json'] = False
                d['locked_stake_total'] = locked_stake
                if row['url']:
                    url = '{}/bp.json'.format(row['url'])
    
                    r = requests.get(url)
                    if r.ok and r.json:
                        try:
                            d['bp_json'] = r.json()
                        except:
                            print(sys.exc_info())

                add_db(col='owners', tag='cache', slug='cache', data=d)
    
        sleep(600)


def dev():
    #print(add_db('col', 'slug', 'tag', 'data'))
    print('dev')


def main():
    if not is_running():
        jlog.info('{}'.format('Starting bot'))
        writePidFile()
        main()

        status_thread = threading.Thread(target=status, args=(), name='status')
        status_thread.start()

    else:
        jlog.info("allready running".format())


if __name__ == '__main__':
    args = sys.argv[1:]
    if len(args) == 0:
        init()
        main()

    if 'monit' in args:
        init(stdout=False)
        main()


    if 'dev' in args:
        init()
        dev()
