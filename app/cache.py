from pprint import pprint
import sys
import json
import os
import requests
from lib.josien import listproducers, get_account, remcli_get_info


def cache_owner():
    lp = listproducers()
    d = {}
    locked_stake = 0
    if lp and 'rows' in lp:
        j = False
        for row in lp['rows']:
            owner = get_account(row['owner'])
            locked_stake += int(owner['voter_info']['locked_stake'])
            d['owner'] = owner
            d['bp.json'] = False
            d['locked_stake_total'] = locked_stake
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

def human_readable(v):
    v = '{:0,.0f}'.format(float(v)).split(',')
    print(v)
    if len(v) == 4:
        return('{} M'.format(v[0]))
    if len(v) == 5:
        return('{} B'.format(v[0]))
    if len(v) == 6:
        return('{} T'.format(v[0]))

    return False

def dev():
    lp = listproducers()
    i = remcli_get_info()
    owner = get_account('remproducer1')
    for row in lp['rows']:
        print(human_readable(row['total_votes']))
    
    

if __name__ == '__main__':
    #dev()
    cache_owner()

