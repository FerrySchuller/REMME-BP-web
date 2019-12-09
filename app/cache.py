from pprint import pprint
import sys
import json
import os
import requests
from lib.josien import listproducers, get_account


def cache_owner():
    lp = listproducers()
    d = {}
    if lp and 'rows' in lp:
        j = False
        for row in lp['rows']:
            d['owner'] = get_account(row['owner'])
            feil = 'cache/{}.json'.format(row['owner'])
            if row['url']:
                d['bp.json'] = False
                url = '{}/bp.json'.format(row['url'])
                feil = 'cache/{}.json'.format(row['owner'])

                r = requests.get(url)
                if r.ok and r.json:
                    try:
                        d['bp.json'] = r.json()
                    except:
                        print(sys.exc_info())
    
            with open(feil, 'w') as outfile:
                json.dump(d, outfile)



if __name__ == '__main__':
    #dev()
    cache_owner()

