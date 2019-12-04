from flask import render_template, jsonify, flash, url_for
import os, sys
import json
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
import requests
from pprint import pprint
from app.lib.josien import track_event, jlog, cmd_run
from app.app import app


log_file = os.getenv('LOG_FILE', False)
jlog = jlog(stdout=True, feil=log_file)


def get_account(account):
    o = cmd_run('/usr/bin/remcli get account {0} --json'.format(account))
    j = False
    if o:
        try:
            j = json.loads(o)
        except:
            print(sys.exc_info())
    
    return j


def get_remswap():
    o = cmd_run('/usr/bin/remcli --url https://testchain.remme.io get actions rem.swap --json')
    j = False
    if o:
        try:
            j = json.loads(o)
        except:
            print(sys.exc_info())

    return j



def listproducers():
    o = cmd_run('/usr/bin/remcli system listproducers --json')
    j = False
    if o:
        try:
            j = json.loads(o)
        except:  
            print(sys.exc_info())

    return j


# lets encrypt once for domain validation
# certbot certonly --manual
#@app.route("/.well-known/acme-challenge/<key>")
#def letsencrypt():
#    return "<key>.<xo>"


@app.route('/')
def index():
    track_event( category='index', action='test index')
    return render_template( 'index.html' )


@app.route('/code_of_conduct')
def code_of_conduct():
    track_event( category='index', action='code_of_conduct')
    return render_template( 'code_of_conduct.html' )


@app.route('/ownership_disclosure')
def ownership_disclosure():
    track_event( category='index', action='ownership_disclosure')
    return render_template( 'ownership_disclosure.html' )

@app.route('/producers')
def producers():
    track_event( category='index', action='Producers')
    return render_template( 'producers.html' )


@app.route('/permissions')
def permissions():
    track_event( category='index', action='Permissions')
    return render_template( 'permissions.html' )


@app.route('/remswap')
def remswap():
    track_event( category='index', action='rem.swap')
    return render_template( 'remswap.html' )


@app.route('/owner/<owner>')
def owner(owner):
    track_event( category='index', action='owner')
    data = get_account(owner)
    return render_template( 'owner.html', data=data )



@app.route('/dev')
def dev():
    return render_template( 'dev.html', d=data )


@app.route('/_get_permissions')
def get_permissions():
    lp = listproducers()
    d = {}
    d['data'] = []

    if lp and 'rows' in lp:
        for p in lp['rows']:
            owner = get_account(p['owner'])
            if 'permissions' in owner:
                for permission in owner['permissions']:
                    i = {}
                    i['position'] = 0
                    i['owner'] = '<a href={0}>{1}</a>'.format(url_for('owner', owner=p['owner']), p['owner'])
                    i['perm_name'] = permission['perm_name']
                    i['parent'] = permission['parent']
                    i['keys'] = str(permission['required_auth']['keys'])
                    d['data'].append(i)

    return jsonify(d)



@app.route('/_get_remswap')
def _get_remswap():
    d = False
    remswap = get_remswap()

    if remswap:
        d = {}
        d['data'] = []
        for k,v in remswap.items():
            if 'actions' in k:
                for i in v:
                    for k,v in i.items():
                        i = {}
                        i['position'] = 0
                        i['key'] = k
                        i['value'] = str(v)
                        d['data'].append(i)

    return jsonify(d)


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


@app.route('/_listproducers')
def _listproducers():
    d = False
    lp = listproducers()

    if lp and isinstance(lp, dict):
        d = {}
        d['data'] = []
        if 'rows' in lp:
            for row in lp['rows']:
                i = {}
                i['position'] = 0
                i['owner'] = '<a href={0}>{1}</a>'.format(url_for('owner', owner=row['owner']), row['owner'])
                i['total_votes'] = '{:0,.2f}'.format(float(row['total_votes']))
                i['url'] = '<a href="{0}" target="_blank" >{0}</a>'.format(row['url'])
                i['is_active'] = row['is_active']
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
            flash( 'New OHLC data cached.', 'info' )
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
                "email":"",
                "branding":{
                  "logo_256":"",
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
                  "p2p_endpoint": "",
                  "bnet_endpoint": "",
                  "api_endpoint": "",
                  "ssl_endpoint": ""
                },
              ]
            }

    return jsonify(data)
