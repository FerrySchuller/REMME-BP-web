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
from statistics import mean
import randomcolor
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


def random_color():
    rand_color = randomcolor.RandomColor()
    return(rand_color.generate(luminosity="dark")[0])


def get_actions(seconds=60):
    dt = (datetime.now() - timedelta(seconds=seconds))
    logs = db.logs.find({"time": {"$gt": dt}}).sort([("time", pymongo.ASCENDING)])
    for log in logs:
        msg = log['msg'].split()
        if len(msg) == 24:
            d = {}
            block = msg[9].replace('#', '')
            produced_on = parse(msg[11])
            block_owner = msg[14]
            #d['trxs'] = msg[16].replace(',', '')
            b = get_block(block)
            if b and b['transactions'] and isinstance(b['transactions'], list):
                for transaction in b['transactions']:
                    for action in transaction['trx']['transaction']['actions']:
                        '''
                        if action['account'] == 'rembenchmark' and action['name'] == 'cpu':
                            o = db.producers.find_one( { "name": "{}".format(block_owner) })
                            if o:
                                data = o
                                data['cpu_usage_us'] = transaction['cpu_usage_us']
                                data['cpu_usage_us_dt'] = produced_on

                                db_info = {}
                                db_info['cpu_usage_us'] = transaction['cpu_usage_us']
                                db_info['cpu_usage_us_dt'] = produced_on

                                add_db(col='cache', tag='cpu_usage_us', slug='cpu_usage_us', owner=block_owner, data=db_info)
                                ref = db.producers.update({"name": '{}'.format(block_owner)}, {"$set": data}, upsert=True)
                        '''
                        if action['account'] == 'rem.oracle' and action['name'] == 'setprice':
                            o = db.producers.find_one( { "name": "{}".format(action['data']['producer']) })
                            if o:
                                data = o
                                data['updated_at'] = datetime.now(timezone.utc)
                                data['setprice'] = produced_on
                                ref = db.producers.update({"name": '{}'.format(action['data']['producer'])}, {"$set": data}, upsert=True)


def notify(slaap=300):
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


        jlog.info('Sleeping for: {} seconds'.format(slaap))
        sleep(slaap)



def producers_fast(slaap=20):
    while True:
        actions_seconds = slaap + 60
        get_actions(actions_seconds)
        lv = listvoters()
        lp = listproducers()
        position = 0

        if lp and 'rows' in lp:
            swaps = remcli_get_action_swap()
            swap_it = []
            if swaps and 'rows' in swaps:
                for swap in swaps['rows']:
                    swap_it = swap_it + swap['provided_approvals']
        
            rows = sorted(lp['rows'], key=lambda k: (float(k['total_votes'])), reverse=True)
            for p in rows:
                health = []

                o = db.producers.find_one( { "name": "{}".format(p['owner']) })
                if o:
                    data = o
                    data['updated_at'] = datetime.now(timezone.utc)
                    data['health'] = []
                else:
                    ''' init producer '''
                    data = {}
                    data['name'] = p['owner']
                    data['position'] = 99
                    data['producer'] = p
                    data['slug'] = 'producers'
                    data['tag'] = 'producers'
                    data['cpu_usage_us'] = ''
                    data['social'] = ''
                    data['bp_json'] = ''
                    data['bp_json_url'] = ''
                    data['health'] = []
                    data['color'] = random_color()
                    data['created_at'] = datetime.now(timezone.utc)

    
                usage = db.cpu_usage_us.find( { "producer": "{}".format(p['owner']) } )
                dt = (datetime.now() - timedelta(seconds=3600))
                if usage:
                    l = []
                    for use in usage:
                        for cpu in use['data']:
                            if cpu['timestamp'] > dt:
                                l.append(cpu['cpu_usage_us'])


                    if l:
                        try:
                            data['cpu_usage_us'] = mean(l)
                        except:
                            jlog.critical("cpu_usage_us error: {} {}".format(p['name'], sys.exc_info()))





                data['producer'] = p

                if p['is_active'] == 1:
                    position += 1
                    data['position'] = position
                else:
                    health.append({'title':'Not Active'})
                    data['position'] = 99

    
                if p['owner'] in swap_it:
                    data['swaps'] = True
                else:
                    data['swaps'] = False
                    health.append({'title':'Not swapping'})

                owner = get_account(p['owner'])
                data['owner'] = owner
    
                voters = []
                data['voters'] = []
                if lv and 'rows' in lv and isinstance(lv['rows'], list):
                    for voter in lv['rows']:
                        if isinstance(voter, dict) and 'error' not in voter.keys():
                            if p['owner'] in voter['producers']:
                                voters.append(voter['owner'])
                                data['voters'] = voters
    
                data['voters_count'] = len(voters)

                data['health'] = health
                ref = db.producers.update({"name": '{}'.format(p['owner'])}, {"$set": data}, upsert=True)

        jlog.info('Sleeping for: {} seconds'.format(slaap))
        sleep(slaap)


def producers_slow(slaap=300):
    while True:

        url = "https://min-api.cryptocompare.com/data/price?fsym=REM&tsyms=USD&api_key={}".format(os.getenv('cryptocompare_key', False))
        r = requests.get(url)
        if r and r.ok and r.json:
            add_db(col='cache', tag='usd_rem', slug='usd_rem', data=r.json())


        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
        #producers = db.producers.find({"name":"josiendotnet"}).limit(100)
        producers = db.producers.find().limit(100)
        if producers:
            for p in producers:
                if 'producer' in p and 'url' in p['producer']:
                    if p['producer']['url']:
                        url = '{}/bp.json'.format(p['producer']['url'].rstrip('//'))
                        data = p
                        data['updated_at'] = datetime.now(timezone.utc)
                        data['bp_json'] = False
                        data['bp_json_url'] = ''
                        health = data['health']
                 
    
                        r = False
                        try:
                            r = requests.get(url, headers=headers, verify=False)
                        except:
                            jlog.critical("bp.json error: {} {}".format(sys.exc_info(), p['name']))

                        if r and r.ok and r.json:
                            try:
                                data['bp_json'] = r.json()
                                data['bp_json_url'] = url
                            except:
                                jlog.critical("bp.json error: {} {}".format(p['name'], sys.exc_info()))

                        if not data['bp_json']:
                            health.append({'title':'No bp.json'})

                        if data['bp_json']:
                            bp_json = r.json()
                            if 'org' in bp_json and 'social' in bp_json['org'] and isinstance(bp_json['org']['social'], dict):
                                o = '<div><ul class="social-network">'
                                for k,v in bp_json['org']['social'].items():
                                    if v:
                                        if k == 'facebook':
                                            o += '<li><a data-toggle="tooltip" data-placement="top" data-html="true" title="{0}" target="_blank" href="https://facebook.com/{1}""><i class="fab fa-{0}"></i></a></li>'.format(k,v)
                                        if k == 'twitter':
                                            o += '<li><a data-toggle="tooltip" data-placement="top" data-html="true" target="_blank" href="https://twitter.com/{1}" title="{0}"><i class="fab fa-{0}"></i></a></li>'.format(k,v)
                                        if k == 'telegram':
                                            o += '<li><a data-toggle="tooltip" data-placement="top" data-html="true" target="_blank" href="https://t.me/{1}" title="{0}"><i class="fab fa-{0}"></i></a></li>'.format(k,v)
                                        if k == 'reddit':
                                            o += '<li><a data-toggle="tooltip" data-placement="top" data-html="true" target="_blank" href="https://reddit.com/user/{1}" title="{0}"><i class="fab fa-{0}"></i></a></li>'.format(k,v)
                                        if k == 'github':
                                            o += '<li><a data-toggle="tooltip" data-placement="top" data-html="true" target="_blank" href="https://github.com/{1}" title="{0}"><i class="fab fa-{0}"></i></a></li>'.format(k,v)
                                        if k == 'linkedin':
                                            o += '<li><a data-toggle="tooltip" data-placement="top" data-html="true" target="_blank" href="https://linkedin.com/in/{1}" title="{0}"><i class="fab fa-{0}"></i></a></li>'.format(k,v)

                
                                o += '</ul></div>'
                                data['social'] = o
                         
    
                        data['health'] = health
                        ref = db.producers.update({"name": '{}'.format(p['name'])}, {"$set": data}, upsert=True)

        jlog.info('Sleeping for: {} seconds'.format(slaap))
        sleep(slaap)

     
def cpu_usage_us(slaap=10):
    while True:
        trxs = False
        bl = db.cpu_usage_us.find().limit(400)
        blocks = []
        start = 168517 # first benchmark block
        if bl:
            for row in bl:
                for cpu in row['data'] :
                    blocks.append(cpu['block'])
            if blocks:
                start = max(blocks) + 1
    
        i = remcli_get_info()
        stop = i['last_irreversible_block_num']
    
        for block in range(start, stop):
            b = get_block(block)
            try:
                timestamp = parse(b['timestamp'])
            except:
                timestamp = False
                jlog.critical('timestamp ERROR: {}'.format(sys.exc_info()))
            if timestamp:
                d = db.cpu_usage_us.find_one( { "producer": "{}".format(b['producer']) })
            if timestamp and b['transactions']:
                for transaction in b['transactions']:
                    if isinstance(transaction['trx'], dict):
                        for action in transaction['trx']['transaction']['actions']:
                            if 'account' in action and 'name' in action and action['account'] == 'rembenchmark' and action['name'] == 'cpu':
                                trxs = True
                                cpu_usage_us = transaction['cpu_usage_us']
                                if d and not list(filter(lambda xo: xo['block'] == block, d['data'])):
                                    d['data'].append( {"timestamp": timestamp, "cpu_usage_us": cpu_usage_us, "block": block})
                                else:
                                    d = {}
                                    d['producer'] = b['producer']
                                    d['data'] = []
                                    d['data'].append( {"timestamp": timestamp, "cpu_usage_us": cpu_usage_us, "block": block})
        
                                ref = db.cpu_usage_us.update({"producer": '{}'.format(b['producer'])}, {"$set": d}, upsert=True)
                                jlog.info('{} {} {}'.format(block, timestamp, ref))
        if not trxs:
            jlog.info('Sleeping for: {} seconds'.format(slaap))
            sleep(slaap)


def trxs(slaap):
    while True:
        dt = (datetime.now() - timedelta(seconds=slaap))
        y = 0
        logs  = db.logs.find( {"time": { "$gt": dt } } )
        if logs:
            for log in logs:
                msg = log['msg'].split()
                if len(msg) == 24:
                    try:
                        produced_on = parse(msg[11])
                        y += int(msg[16].replace(',', ''))
                    except:
                        jlog.critical('trxs ERROR: {}'.format(sys.exc_info()))
                else:
                    jlog.warning('trxs WARN len(msg) not 24: {}'.format(msg))
    
        t = datetime.now()
        d = { 't': t, 'y': y }
        add_db('trxs', slug='trxs', tag=slaap, data=d)

        jlog.info('Sleeping trxs for: {} seconds'.format(slaap))
        sleep(slaap)

        

def roundTime(dt=None, roundTo=60):
   if dt == None : dt = datetime.datetime.now()
   seconds = (dt.replace(tzinfo=None) - dt.min).seconds
   rounding = (seconds+roundTo/2) // roundTo * roundTo
   r = dt + timedelta(0,rounding-seconds,-dt.microsecond)
   return(r.timestamp() * 1000)
   #return dt + timedelta(0,rounding-seconds,-dt.microsecond)
   #return dt + timedelta(0,rounding-seconds,-dt.microsecond)


def pruning(slaap=3600):
    while True:
        dt = (datetime.now() - timedelta(days=1))
        trxs  = db.trxs.find( { "$and": [ {"created_at": { "$lt": dt } },
                                          {"tag": 5 } ] } )
    
        for trx in trxs:
            _id = trx['_id']
            p = db.trxs.remove({"_id": _id})
            jlog.info('pruning {} {}'.format(_id, p))


        transactions  = db.transactions.find( { "$and": [ {"created_at": { "$lt": dt } },
                                                          {"tag": 'transactions' } ] } )
    
        for transaction in transactions:
            _id = transaction['_id']
            p = db.transactions.remove({"_id": _id})
            jlog.info('pruning {} {}'.format(_id, p))


        jlog.info('Pruning sleeping for: {} seconds'.format(slaap))
        sleep(slaap)




def transactions(slaap=2):
    while True:
        last = db.transactions.find_one( { "tag": 'transactions' }, { "_id": 0, "created_at": 0 },sort=([('created_at', pymongo.DESCENDING)]))
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
            if b['transactions']:
                for t in b['transactions']:
                    try:
                        for action in t['trx']['transaction']['actions']:
                            print('x0', action)
                            d = {}
                            d['account'] = action['account']
                            d['id'] = b['id']
                            d['producer'] = b['producer']
                            d['block_num'] = b['block_num']
                            d['timestamp'] = parse(b['timestamp'])
                            d['cpu_usage_us'] = t['cpu_usage_us']
                            add_db(col='transactions', slug='transactions', tag='transactions', data=d, owner=False, block=b['block_num'])
                    except:
                        jlog.critical("{}".format(sys.exc_info()))


        jlog.info('Transacions sleeping for: {} seconds'.format(slaap))
        sleep(slaap)


def dev(slaap=2):
    dt = (datetime.now() - timedelta(minutes=1))
    transactions  = db.transactions.find( { "$and": [ {"created_at": { "$lt": dt } },
                                          {"tag": 'transactions' } ] } )

    for transaction in transactions:
        _id = transaction['_id']
        p = db.transactions.remove({"_id": _id})
        print(p)


def dev1(roundTo=3600, seconds=86400):
    dt = (datetime.now() - timedelta(seconds=seconds))
    producers = db.producers.find({}, {"name": 1, "position": 1, "_id": 0}).limit(30)
    resp = []
    if producers:
        for p in producers:
            if p['position'] < 22:

                chart = {}
                chart['backgroundColor'] = 'xx'
                chart['borderColor'] = 'xx'
                chart['fill'] = 'false'
                chart['label'] = p['name']
                chart['data'] = []


                cpu_usage = db.cpu_usage_us.find_one( { "producer": "{}".format(p['name']) },
                                                { "_id": 0, "data.block": 0, },sort=([('time', pymongo.DESCENDING)]))
            
                l = []
                low = []
                if cpu_usage:
                    for data in cpu_usage['data']:
                        if data['timestamp']> dt:
                            y = data['cpu_usage_us'] / 10000
                            t = roundTime(data['timestamp'], roundTo=roundTo)
                            d = {}
                            d['t'] = t
                            d['y'] = y
                            low.append(t)
                            l.append(d)
            
                low = min(low)
                ty = []
                data = []
                for xo in l:
                    if xo['t'] == low:
                        ty.append(xo['y'])
                    else:
                        low = xo['t']
                        d = {}
                        try:
                            av = "{:.4f}".format(sum(ty) / len(ty))
                            d = {}
                            d['t'] = xo['t']
                            d['y'] = av
                            chart['data'].append(d)
                        except:
                            pass
                        ty = []

                resp.append(chart)
    pprint(resp)

#        try:
#            av = sum(ly) / len(ly)
#            print(xo['t'], av)
#        except:
#            pass



def main():
    if not is_running():
        jlog.info('{}'.format('Starting bot'))
        writePidFile()
        main()

        producers_fast_thread = threading.Thread(target=producers_fast, args=(), name='producers_fast')
        producers_fast_thread.start()

        producers_slow_thread = threading.Thread(target=producers_slow, args=(), name='producers_slow')
        producers_slow_thread.start()

        pruning_thread = threading.Thread(target=pruning, args=(), name='pruning')
        pruning_thread.start()


        trxs5_thread = threading.Thread(target=trxs, args=[5], name='trxs')
        trxs5_thread.start()

        trxs300_thread = threading.Thread(target=trxs, args=[300], name='trxs')
        trxs300_thread.start()

        trxs3600 = threading.Thread(target=trxs, args=[3600], name='trxs')
        trxs3600.start()

        trxs86400 = threading.Thread(target=trxs, args=[86400], name='trxs')
        trxs86400.start()

        cpu_usage_us_thread = threading.Thread(target=cpu_usage_us, args=(), name='cpu_usage_us')
        cpu_usage_us_thread.start()

        transactions_thread = threading.Thread(target=transactions, args=(), name='transactions')
        transactions_thread.start()



        #notify_thread = threading.Thread(target=notify, args=(), name='notify')
        #notify_thread.start()
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

    if 'pruning' in args:
        init()
        pruning()


    if 'dev' in args:
        init()
        dev()

    if 'dev1' in args:
        init()
        dev1()
