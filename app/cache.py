from pprint import pprint
import sys
import json
import os
import requests
from lib.josien import listproducers, get_account, remcli_get_info


def cache_owner():
    lp = listproducers()
    d = {}
    if lp and 'rows' in lp:
        j = False
        for row in lp['rows']:
            owner = get_account(row['owner'])
            d['owner'] = owner
            d['bp.json'] = False
            feil = 'cache/{}.json'.format(row['owner'])
            if row['url']:
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


def dev():
    i = remcli_get_info()
    owner = get_account('josiendotnet')
    if i:
        pprint(owner['head_block_num'])
        pprint(i['fork_db_head_block_num'])
    
    

if __name__ == '__main__':
    #dev()
    cache_owner()

