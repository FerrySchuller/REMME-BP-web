from flask import render_template, jsonify, flash, url_for
import os, sys
import json
from datetime import datetime, timedelta, timezone
from dateutil.parser import parse
from pathlib import Path
from time import sleep
import pymongo
import requests
from pprint import pprint
from app.lib.josien import track_event, jlog, cmd_run, listproducers, get_account, remcli_get_info, human_readable, db, listvoters
from app.app import app

log_file = os.getenv('LOG_FILE', False)
jlog = jlog(stdout=True, feil=log_file)
db = db()

# lets encrypt once for domain validation
# certbot certonly --manual
#@app.route("/.well-known/acme-challenge/<key>")
#def letsencrypt():
#    return "<key>.<xo>"


def gen_social(j):
    if j['data']['bp_json'] and 'org' in j['data']['bp_json'] and 'social' in j['data']['bp_json']['org']:
        o = '<div><ul class="social-network">'
        for k,v in j['data']['bp_json']['org']['social'].items():
            if v:
                if k == 'facebook':
                    o += '<li><a target="_blank" href="https://facebook.com/{1}" title="{0}"><i class="fab fa-{0}"></i></a></li>'.format(k,v)
                if k == 'twitter':
                    o += '<li><a target="_blank" href="https://twitter.com/{1}" title="{0}"><i class="fab fa-{0}"></i></a></li>'.format(k,v)
                if k == 'telegram':
                    o += '<li><a target="_blank" href="https://t.me/{1}" title="{0}"><i class="fab fa-{0}"></i></a></li>'.format(k,v)
                if k == 'reddit':
                    o += '<li><a target="_blank" href="https://reddit.com/user/{1}" title="{0}"><i class="fab fa-{0}"></i></a></li>'.format(k,v)
                if k == 'github':
                    o += '<li><a target="_blank" href="https://github.com/{1}" title="{0}"><i class="fab fa-{0}"></i></a></li>'.format(k,v)
                if k == 'linkedin':
                    o += '<li><a target="_blank" href="https://linkedin.com/in/{1}" title="{0}"><i class="fab fa-{0}"></i></a></li>'.format(k,v)
        o += '</ul></div>'
        return(o)
    return('')




def get_feil(feil):
    if os.path.exists(feil):
        with open(feil) as json_file:
            try:
                return(json.load(json_file))
            except:
                print(sys.exc_info())
    return False



def gen_locked_stake(feil):
    if os.path.exists(feil):
        with open(feil) as json_file:
            f = json.load(json_file)
            if 'owner' in f and f['owner']:
                o = f['owner']['voter_info']['locked_stake']
                return(o)
    return(False)



@app.route('/')
def index():
    track_event( category='index', action='test index')
    return render_template( 'index.html' )

@app.route('/guardians')
def guardians():
    track_event( category='guardians', action='guardians')
    return render_template( 'guardians.html' )


@app.route('/code_of_conduct')
def code_of_conduct():
    track_event( category='index', action='code_of_conduct')
    return render_template( 'code_of_conduct.html' )


@app.route('/ownership_disclosure')
def ownership_disclosure():
    track_event( category='index', action='ownership_disclosure')
    return render_template( 'ownership_disclosure.html' )


@app.route('/owner/<owner>')
def owner(owner):
    track_event( category='index', action='owner')
    data = get_account(owner)
    feil = get_feil('app/cache/{}.json'.format(owner))
    return render_template( 'owner.html', data=data, feil=feil )



@app.route('/dev')
def dev():
    return render_template( 'dev.html', d=data )


@app.route('/_get_account/<owner>')
def _get_account(owner):
    d = False
    owner = get_account(owner)
    
    if owner:
        d = {}
        d['data'] = []
        for k,v in owner.items():
            i = {}
            i['position'] = 0
            i['key'] = k
            i['value'] = str(v)
            d['data'].append(i)

    return jsonify(d)


def lwd(owner):
    if owner:
        lwd = db.cache.find_one({"tag": "last_work_done", "data.{}".format(owner): {"$exists": "True"}})
        if lwd and 'data' in lwd and owner in lwd['data'] and isinstance(lwd['data'][owner], datetime):
            divv = datetime.now() - lwd['data'][owner]
            if divv.seconds and divv.seconds > 86400:
                return("<medium class='text-danger'>{:.0f} Days</medium>".format(divv.seconds / 86400))
            if divv.seconds and divv.seconds > 3600:
                return("<medium class='text-warning'>{:.0f} Hours</medium>".format(divv.seconds / 3600))
            if divv.seconds:
                return("<medium class='text-success'>{}</medium>".format(divv.seconds))

    return(False)




@app.route('/_listvoters')
def _listvoters():
    price = False
    d = {}
    d['data'] = []
    lv = listvoters()
    if lv and 'rows' in lv:

        usd_rem = db.cache.find_one( {"tag": "usd_rem"}, 
                                   sort=[('created_at', pymongo.DESCENDING)])
        if usd_rem and 'data' in usd_rem and 'USD' in usd_rem['data']:
            price = usd_rem['data']['USD']
        for g in lv['rows']:
            if (float(g['staked']) > 2500000000):
                i = {}
                i['owner'] = g['owner']
                try:
                    i['staked'] = "{:0,.0f}".format((float(g['staked']) / 10000))
                except:
                    i['staked'] = ''
                    jlog.critical('STAKED FLOAT ERROR: {}'.format(sys.exc_info()))
    
    
                try:
                    i['last_vote_weight'] = "{:0,.0f}".format((float(g['last_vote_weight'])/ 10000))
                except: 
                    i['last_vote_weight'] = ''
                    jlog.critical('LAST_VOTE_WEIGHT FLOAT ERROR: {}'.format(sys.exc_info()))
    
                try:
                    dt = parse(g['stake_lock_time'])
                    days = dt - datetime.now()
                    i['stake_lock_time'] = '{} days'.format(days.days)
                    #i['stake_lock_time'] = '{:%Y-%m-%d - %H:%M:%S}'.format(dt)
                except: 
                    i['stake_lock_time'] = ''
                try:
                    remme = (g['pending_perstake_reward'] / 10000)
                    if price:
                        rem_usd = remme * price
                        i['pending_perstake_reward_usd'] = '${:.2f}'.format(rem_usd)
                        i['pending_perstake_reward'] = '{:.2f}'.format(remme)
                        #i['pending_perstake_reward'] = '{:.2f} <small class="text-muted">${:.2f}</small>'.format(remme, rem_usd)
                    else:
                        i['pending_perstake_reward'] = "REM: {:.2f}".format(remme)
                except: 
                    i['pending_perstake_reward'] = ''
    
                try:
                    i['producers'] = ' '.join(g['producers'])
                except: 
                    i['producers'] = ''
            
                d['data'].append(i)
    return jsonify(d)


@app.route('/_listproducers')
def _listproducers():
    i = remcli_get_info()
    if i:
        producing = i['head_block_producer']

    d = False
    lp = listproducers()

    if lp and isinstance(lp, dict):
        d = {}
        d['data'] = []
        if 'rows' in lp:
            r = 1
            rows = sorted(lp['rows'], key=lambda k: (float(k['total_votes'])), reverse=True)
            for row in rows:
                owner_cached = db.owners.find_one( {"tag": "owners", "data.owner.account_name": "{}".format(row['owner'])}, 
                                                   sort=[('created_at', pymongo.DESCENDING)])
                if owner_cached:
                    ''' INIT table '''
                    i = {}
                    i['position'] = False
                    i['total_votes'] = False
                    i['social'] = False
                    i['url'] = False
                    i['last_work_done'] = False
                    i['bp_json'] = ''
    
    
                    i['position'] = '{}'.format(r)
                    r += 1
    
                    i['owner'] = '<a href={0}>{1}</a>'.format(url_for('owner', owner=row['owner']), row['owner'])
    
                    try:
                        total_votes = (float(row['total_votes']) / 10000)
                        i['total_votes'] = '{:0,.0f}'.format(total_votes)
                    except:
                        jlog.critical('TOTAL VOTES ERROR: {}'.format(sys.exc_info()))
    
                    i['social'] = gen_social(owner_cached)
                    i['url'] = '<a href="{0}" target="_blank" >{0}<!-- <i class="fas fa-globe"></i> --></a>'.format(row['url'])

                    if row['owner'] == producing:
                        i['last_work_done'] = '<i class="fas fa-sync fa-spin fa-1x"></i>'
                    else:
                        i['last_work_done'] = lwd(row['owner'])

                    if owner_cached['data']['bp_json']:
                        i['bp_json'] = '<a target="_blank" href="{}/bp.json"><i class="fa fa-check"></i></a>'.format(row['url'])
                    d['data'].append(i)
    
    return jsonify(d)



@app.route('/_ohlc/<int:days>')
@app.route('/_ohlc')
def graph_status(days=1, coin='rem'):

    l = []
    def get_ohlc():
        p = Path(coin)
        params = { 'fsym': coin.upper(),
                   'tsym': 'USDT',
                   'limit': 2000,
                   'api_key': os.getenv('cryptocompare_key')   }
        r = requests.get('https://min-api.cryptocompare.com/data/v2/histoday', params=params)

        if r.ok and r.json:
            #flash( 'New OHLC data cached.', 'info' )
            p.write_text(r.text)


    if not Path(coin).exists():
        get_ohlc()

    if Path(coin).exists():
        p = Path(coin)
        file_time = datetime.fromtimestamp(p.stat().st_mtime) + timedelta(minutes=30)
        if (file_time < datetime.today()):
            get_ohlc()


    with open(coin) as j:
        data = json.load(j)
        if 'Data' in data and 'Data' in data['Data']:
            for ohlc in data['Data']['Data']:
                if ohlc['open'] is not 0:
                    time = ohlc['time'] * 1000
                    l.append([time, ohlc['open'], ohlc['high'], ohlc['low'], ohlc['close'], ohlc['volumefrom']])

    return jsonify(l)


@app.route('/bp.json')
def bp():
    data =  { "producer_account_name": "josiendotnet",
              "org": {
                "candidate_name": "josien.net",
                "website": "https://josien.net",
                "code_of_conduct":"https://josien.net/code_of_conduct",
                "ownership_disclosure":"https://josien.net/ownership_disclosure",
                "email":"ferry@josien.net",
                "branding":{
                  "logo_256":"https://josien.net/static/fav/favicon-96x96.png",
                  "logo_1024":"",
                  "logo_svg":""
                },
                "location": {
                  "name": "The Hague",
                  "country": "NL",
                  "latitude": 52.3667,
                  "longitude": 4.8945 
                },
                "social": {
                  "steemit": "ferryschuller",
                  "twitter": "josien_net",
                  "facebook": "josien.net",
                  "github": "FerrySchuller/REMME-BP-web",
                  "reddit": "josien_net",
                  "telegram": "JosienNet",
                  "linkedin": "ferryschuller",
                }
              },
              "nodes": [
                { 
                  "location": {
                    "name": "The Hague",
                    "country": "NL",
                    "latitude": 52.3667,
                    "longitude": 4.8945
                  },
                  "node_type": "producer",
                  "p2p_endpoint": "p2p.remchain.josien.net:9876",
                  "bnet_endpoint": "",
                  "api_endpoint": "",
                  "ssl_endpoint": ""
                },
              ]
            }

    return jsonify(data)


if __name__ == '__main__':
    pass
