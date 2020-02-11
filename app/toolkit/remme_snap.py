import requests
from dotenv import load_dotenv
load_dotenv()
from datetime import datetime, timedelta
import os, sys
import glob
from pprint import pprint


snapshot_dir = os.getenv('SNAPSHOT_DIR', False)
snapshot_symlink = os.getenv('SNAPSHOT_SYMLINK', False)

def create_snap():
    url = "http://127.0.0.1:8888/v1/producer/create_snapshot"

    payload = '{ "json" : true }'
    headers = { 'content-type': 'application/x-www-form-urlencoded; charset=UTF-8' }
    r = requests.post(url, data=payload, headers=headers)
    pprint(vars(r))


def xo():
    files = glob.glob(snapshot_dir)
    latest = max(files, key=os.path.getctime)
    
    if os.path.islink(snapshot_symlink):
        os.remove(snapshot_symlink)
    
    try:
        os.symlink(latest, snapshot_symlink)
    except:
        print(sys.exc_info())
    
    for feil in files:
        dt = datetime.now() - timedelta(days=7)
        feil_time = datetime.fromtimestamp(os.path.getmtime(feil))
        if feil_time < dt:
            os.remove(feil)


if __name__ == '__main__':
    if snapshot_dir and snapshot_symlink:
        create_snap()
        xo()
