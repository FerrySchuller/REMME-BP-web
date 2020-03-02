#!/usr/bin/env python
from dotenv import load_dotenv
load_dotenv()
from pprint import pprint
from dateutil.parser import parse
from datetime import datetime, timedelta
from chump import Application as Pushover
import os, sys
import subprocess
import requests
import logging
import logging.handlers


'''
Create venv and install packages:

# cd /var/tmp
# mkdir auto_unreg
# cd auto_unreg
# wget https://raw.githubusercontent.com/FerrySchuller/REMME-BP-web/master/app/toolkit/unreg.py
# /var/tmp/auto_unreg$ python3 -m venv env
# /var/tmp/auto_unreg$ . env/bin/activate
# (env) /var/tmp/auto_unreg$ pip install chump requests python-dotenv python-dateutil

Cron example
*/5 * * * * /var/tmp/auto_unreg/env/bin/python /var/tmp/auto_unreg/unreg.py >> /var/tmp/unreg 2>&1

dotenv example, needed for push notification to https://pushover.net:
vi $/var/tmp/auto_unreg/.env
PUSHOVER_APP="xo"
PUSHOVER_USER="xoxoxoxo"
'''

prod = True
treshold = 1500 # seconds

if prod:
    host = 'https://remchain.remme.io'
    producer = 'josiendotnet'
    #pubkey = 'EOS7mATonnQyXoEsh8x5oUDSPM3vpLw3zM9SmVCYmkHf8Cmhhx4uY'
    pubkey = 'EOS7DTnVFPPcKZJo4uGbKwCmtyNtgqUZhWoXohxkYYW4XLRXyttUQ'
    web = 'https://josien.net'
    walletpass = '/prod/remme/walletpass'
else:
    host = 'https://testchain.remme.io'
    producer = 'josientester'
    pubkey = 'EOS8a58FJsdusyMZz3UgbRfh8pJRkqvTVLzfRjtN9Bx9yhNBP1RqK'
    web = 'https://josien.net'
    walletpass = '/prod/remme/walletpass'



def jlog(feil=False, stdout=False):
    jlog = logging.getLogger(__name__)
    jlog.setLevel(logging.DEBUG)
    formatter = logging.Formatter('jlog [%(asctime)s] %(filename)s %(module)s %(funcName)s %(levelname)s %(message)s')

    syslog = logging.handlers.SysLogHandler(address = '/dev/log')
    syslog.setFormatter(formatter)
    jlog.addHandler(syslog)

    if feil:
        feil = logging.FileHandler(feil)
        feil.setFormatter(formatter)
        jlog.addHandler(feil)

    if stdout:
        stdout = logging.StreamHandler(sys.stdout)
        stdout.setFormatter(formatter)
        jlog.addHandler(stdout)

    return jlog

jlog = jlog(stdout=True, feil='/var/tmp/unregprod.log')


def po(msg):
    PUSHOVER_APP = os.getenv('PUSHOVER_APP', False)
    PUSHOVER_USER = os.getenv('PUSHOVER_USER', False)
    if PUSHOVER_APP and PUSHOVER_USER:
        app = Pushover(PUSHOVER_APP)
        if app.is_authenticated == True:
            user = app.get_user(PUSHOVER_USER)
            if user.is_authenticated == True:
                message = user.send_message(msg)
                return True

    return False


def get_producer(producer):
    url = "{}/v1/chain/get_producers".format(host)
    
    payload = '{{"limit":"1","lower_bound":"{}","json":true}}'.format(producer)
    headers = { 'accept': "application/json", 
                'content-type': "application/json" }
    
    r = requests.post(url, data=payload, headers=headers)
    if r and r.ok and r.json:
        return r.json()
    return False


def main():
    p = get_producer(producer)
    divv = False
    if p and 'rows' in p:
        for row in p['rows']:
            if 'last_block_time' in row and 'is_active' in row:
                if row['is_active']:
                    try:
                        last_block_time = parse(row['last_block_time'])
                        dt = (datetime.now() - last_block_time)
                        divv = dt.seconds
                    except:
                        print(sys.exc_info())
                else:
                    jlog.info("{} is not is_active".format(producer))
                    jlog.info("regproducer {} with:".format(producer))
                    jlog.info("/usr/bin/remcli wallet unlock < {}".format(walletpass))
                    jlog.info("/usr/bin/remcli -u {} system regproducer {} {} {}".format(host, producer, pubkey, web))
    if divv and divv > treshold:
        unlock = subprocess.run('/usr/bin/remcli wallet unlock < {}'.format(walletpass), shell=True, 
                                check=False, stdout=subprocess.PIPE, universal_newlines=True)

        unregprod = subprocess.run('/usr/bin/remcli -u {} system unregprod {}'.format(host, producer), shell=True, 
                                    check=False, stdout=subprocess.PIPE, universal_newlines=True)

        jlog.info('{} {}'.format(unlock.stdout, unregprod.stdout))
        msg = "Going to unreg producer {} {} seconds, last_block_time exceeds {} seconds treshold.".format(producer, divv, treshold)
        jlog.warning(msg)
        po(msg)
    else:
        msg = "{} {} seconds, last_block_time does not exceeds {} seconds treshold.".format(producer, divv, treshold)
        jlog.info(msg)


if __name__ == '__main__':
    main()
    #pprint(get_producer('josiendotnet'))
