import os, sys
import subprocess
import logging
import logging.handlers
import requests

GA_TRACKING_ID = os.getenv('GA_TRACKING_ID', False)


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
    process.wait()
    data, err = process.communicate()
    if process.returncode is 0:
        return data.decode('utf-8')
    else:
        print("Error:", err)
    return ""

