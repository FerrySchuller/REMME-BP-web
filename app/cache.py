from pprint import pprint
import sys
import json
import os
import requests
from glob import glob
from lib.josien import cmd_run, listproducers


def cache_bp_json():
    lp = listproducers()
    if lp and 'rows' in lp:
        j = False
        for row in lp['rows']:
            if row['url']:
                j = False
                url = '{}/bp.json'.format(row['url'])
                feil = 'cache/{}.json'.format(row['owner'])
                r = requests.get(url)
                if r.ok and r.json:
                    try:
                        j = r.json()
                    except:
                        print(sys.exc_info())
    
                if j:
                    with open(feil, 'w') as outfile:
                        json.dump(j, outfile)


if __name__ == '__main__':
    cache_bp_json()
