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
from re import search
from pprint import pprint
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

from josien import jlog, db, listproducers, get_account, remcli_get_info, remcli_get_action_swap, listvoters, po, get_block


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
        jlog.critical("{}".format(sys.exc_info()))
        sys.exit(1)


def add_db(col, slug=False, tag=False, data=False, created_at=datetime.now(timezone.utc)):
    d = {}
    d['created_at'] = created_at
    d['slug'] = slug
    d['tag'] = tag
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



def status(slaap=300):
    while True:
        # temporary for remmonsterbp
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

        url = "https://min-api.cryptocompare.com/data/price?fsym=REM&tsyms=USD&api_key={}".format(os.getenv('cryptocompare_key', False))
        r = requests.get(url)
        if r and r.ok and r.json:
            add_db(col='cache', tag='usd_rem', slug='usd_rem', data=r.json())

        lv = listvoters()
        if lv:
            add_db(col='cache', tag='guardians', slug='guardians', data=lv)

        get_info = remcli_get_info()
        if get_info:
            add_db(col='cache', tag='get_info', slug='get_info', data=get_info)
        
        swap = remcli_get_action_swap()
        if swap:
            add_db(col='cache', tag='get_swap', slug='get_swap', data=swap)

        lp = listproducers()
        d = {}
        locked_stake = 0
        if lp and 'rows' in lp:
            j = False
            for row in lp['rows']:

                d['cpu_usage_us'] = False
                cpu_usage_us = db.cache.find_one( { "tag": "rembenchmark",
                                                    "data.producer": "{}".format(row['owner'])},
                                                  { "data.cpu_usage_us": 1,
                                                    "_id": 0 },
                                                  sort=[('created_at', pymongo.DESCENDING)])
                if cpu_usage_us and 'data' in cpu_usage_us and 'cpu_usage_us' in cpu_usage_us['data']:
                    d['cpu_usage_us'] = cpu_usage_us['data']['cpu_usage_us']


                d['setprice'] = False
                setprice = db.cache.find_one( { "tag": "setprice",
                                                "data.producer": "{}".format(row['owner'])},
                                                { "data.setprice": 1,
                                                "_id": 0 },
                                                sort=[('created_at', pymongo.DESCENDING)])
                if setprice and 'data' in setprice and 'setprice' in setprice['data']:
                    d['setprice'] = setprice['data']['setprice']

                

                owner = get_account(row['owner'])
                locked_stake += int(owner['voter_info']['locked_stake'])
                d['owner'] = owner
                d['bp_json'] = False
                d['voters'] = False
                d['locked_stake_total'] = locked_stake
                if row['url']:
                    url = '{}/bp.json'.format(row['url'].rstrip('//'))
    
                    try:
                        r = requests.get(url, headers=headers, verify=False)
                    except:
                        jlog.critical("bp.json error: {}".format(sys.exc_info()))
                        r = False
                    if r and r.ok and r.json:
                        try:
                            d['bp_json'] = r.json()
                        except:
                            jlog.critical("bp.json error: {}".format(sys.exc_info()))


                if lv and 'rows' in lv and isinstance(lv['rows'], list):
                    voters = []
                    for voter in lv['rows']:
                        if isinstance(voter, dict) and 'error' not in voter.keys():
                            if row['owner'] in voter['producers']:
                                voters.append(voter['owner'])
                    d['voters'] = voters


                add_db(col='owners', tag='owners', slug='owners', data=d)

    
        jlog.info('Sleeping for: {} seconds'.format(slaap))
        sleep(slaap)


def loop_transactions(seconds=300):
    with open(os.getenv('REMME_LOG', False)) as fp:
        for line in fp:
            if not search('trxs: 0', line) and search('signed by', line):
                l = line.split()
                try:
                    dt = datetime.now() - parse(l[11])
                except:
                    dt = False
                    print(sys.exc_info())
                    jlog.critical("trxs dt {}".format(sys.exc_info()))

                if dt and dt.seconds < seconds:
                    block = l[9][1:]
                    b = get_block(block)

                    if b and b['transactions']:
                        producer = b['producer']
                        for transaction in b['transactions']:
                            if 'cpu_usage_us' in transaction and 'trx' in transaction and 'transaction' in transaction['trx'] and 'actions' in transaction['trx']['transaction'] and isinstance(transaction['trx']['transaction']['actions'], list):
                                for action in transaction['trx']['transaction']['actions']:
                                    if action['account'] == 'rembenchmark' and action['name'] == 'cpu':
                                        try:
                                            dt = parse(b['timestamp'])
                                            data = {}
                                            data['cpu_usage_us'] = transaction['cpu_usage_us']
                                            data['producer'] = producer
                                            add_db(col='cache', tag='rembenchmark', slug='rembenchmark', created_at=dt, data=data)
                                        except:
                                            print(sys.exc_info())
                                            jlog.critical("cpu_usage_us {}".format(sys.exc_info()))
                                    if action['account'] == 'rem.oracle' and action['name'] == 'setprice':
                                        try:
                                            dt = parse(b['timestamp'])
                                            data = {}
                                            data['setprice'] = dt
                                            data['producer'] = action['data']['producer']
                                            add_db(col='cache', tag='setprice', slug='setprice', created_at=dt, data=data)
                                        except:
                                            print(sys.exc_info())
                                            jlog.critical("cpu_usage_us {}".format(sys.exc_info()))



def notify(slaap=60):
    while True:
        ''' unreg not seeing blocks for slaap seconds '''
        m = ['josiendotnet', 'josientester']
        lp = listproducers()
        if lp and isinstance(lp, dict):
            if 'rows' in lp:
                for row in lp['rows']:
                    if row['is_active'] and row['owner'] in m:
                        try:
                            ldt = parse(row['last_block_time'])
                            ld = datetime.now() - ldt
                            if ld.seconds > 300:
                                msg = '{} {} Go unreg'.format(row['owner'], ld.seconds)
                                jlog.info('GO GO GO GO unreg: {}'.format(msg))
                                po(msg)
                        except:
                            print(sys.exc_info())
                            jlog.critical("unreg {}".format(sys.exc_info()))



        ''' find rembencmark cpu usages  and setprice'''
        loop_transactions(seconds=slaap)


        jlog.info('Sleeping for: {} seconds'.format(slaap))
        sleep(slaap)



def dev():
    setprice = db.cache.find_one( { "tag": "setprice",
                                    "data.producer": "{}".format('josiendotnet')},
                                    { "data.setprice": 1,
                                    "_id": 0 },
                                    sort=[('created_at', pymongo.DESCENDING)])
    pprint(setprice)
     

def main():
    if not is_running():
        jlog.info('{}'.format('Starting bot'))
        writePidFile()
        main()

        status_thread = threading.Thread(target=status, args=(), name='status')
        status_thread.start()

        notify_thread = threading.Thread(target=notify, args=(), name='notify')
        notify_thread.start()

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

    if 'fill_cache' in args:
        init()
        loop_transactions(seconds=7200)


    if 'dev' in args:
        init()
        dev()
