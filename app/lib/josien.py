import os, sys, json
import subprocess
import logging
import logging.handlers
import requests
from chump import Application as Pushover
from pymongo import MongoClient


GA_TRACKING_ID = os.getenv('GA_TRACKING_ID', False)


def db():
    c = MongoClient(connect=False)
    db = c[os.getenv('DB_NAME')]
    return db


def track_event(category, action, label=None, value=0):
    data = {
        'v': '1',
        'tid': GA_TRACKING_ID,
        'cid': '555',
        't': 'event',
        'ec': category,
        'ea': action,
        'el': label,
        'ev': value }
    response = requests.post( 'https://www.google-analytics.com/collect', data=data)
    response.raise_for_status()


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


def cmd_run(cmd):
    process = subprocess.Popen( cmd, shell=True, stdout=subprocess.PIPE)
    #process.wait()
    data, err = process.communicate()
    if process.returncode is 0:
        return data.decode('utf-8')
    else:
        print("Error:", err)
    return ""


def listvoters():
    o = cmd_run('/usr/bin/remcli system listvoters --json -l 1000')
    j = False
    if o:
        try:
            j = json.loads(o)
        except:
            print(sys.exc_info())

    return j


def listproducers():
    o = cmd_run('/usr/bin/remcli system listproducers --json -l 100')
    j = False
    if o:
        try:
            j = json.loads(o)
        except:
            print(sys.exc_info())

    return j

def get_remswap():
    o = cmd_run('/usr/bin/remcli get actions rem.swap --json')
    j = False
    if o:
        try:
            j = json.loads(o)
        except:
            print(sys.exc_info())

    return j

def get_block(block):
    o = cmd_run('/usr/bin/remcli get block {}'.format(block))
    j = False
    if o:
        try:
            j = json.loads(o)
        except:
            print(sys.exc_info())

    return j


def get_account(account):
    o = cmd_run('/usr/bin/remcli get account {0} --json'.format(account))
    j = False
    if o:
        try:
            j = json.loads(o)
        except:
            print(sys.exc_info())

    return j


def remcli_get_info():
    o = cmd_run('/usr/bin/remcli get info')
    j = False
    if o:
        try:
            j = json.loads(o)
        except:
            print(sys.exc_info())

    return j


def remcli_get_action_swap():
    o = cmd_run('/usr/bin/remcli get table rem.swap rem.swap swaps -r -l 3')
    j = False
    if o:
        try:
            j = json.loads(o)
        except:
            print(sys.exc_info())

    return j


def po(msg):
    app = Pushover(os.getenv('PUSHOVER_APP', False))
    if app.is_authenticated == True:
        user = app.get_user(os.getenv('PUSHOVER_USER', False))
        if user.is_authenticated == True:
            message = user.send_message(msg)
            return True

    return False



def human_readable(v):
    try:
        v = '{:0,.0f}'.format(float(v)).split(',')
        if len(v) == 2:
            return('{} k'.format(v[0]))
        if len(v) == 3:
            return('{} M'.format(v[0]))
        if len(v) == 4:
            return('{} G'.format(v[0]))
        if len(v) == 5:
            return('{} T'.format(v[0]))
        if len(v) == 6:
            return('{} P'.format(v[0]))
        if len(v) == 7:
            return('{} E'.format(v[0]))
    except:
        print(sys.exc_info())

    return False
