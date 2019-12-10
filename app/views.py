from flask import render_template, jsonify, flash, url_for
import os, sys
import json
from datetime import datetime, timedelta
from pathlib import Path
import requests
from pprint import pprint
from app.lib.josien import track_event, jlog, cmd_run, listproducers, get_remswap, get_account, remcli_get_info
from app.app import app


log_file = os.getenv('LOG_FILE', False)
jlog = jlog(stdout=True, feil=log_file)


# lets encrypt once for domain validation
# certbot certonly --manual
#@app.route("/.well-known/acme-challenge/<key>")
#def letsencrypt():
#    return "<key>.<xo>"


def gen_social(feil):
    if os.path.exists(feil):
        with open(feil) as json_file:
            f = json.load(json_file)
            if 'bp.json' in f and f['bp.json']:
                 o = '<div><ul class="social-network">'
                 for k,v in f['bp.json']['org']['social'].items():
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


def gen_votes(feil):
    if os.path.exists(feil):
        with open(feil) as json_file:
            f = json.load(json_file)
            if 'owner' in f and f['owner']:
                o = ''
                for producer in f['owner']['voter_info']['producers']:
                    o += '{}&nbsp;'.format(producer)
                return(o)
    return('')

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
    i = remcli_get_info()
    if i:
        producing = i['head_block_producer']

    d = False
    lp = listproducers()

    if lp and isinstance(lp, dict):
        d = {}
        d['data'] = []
        if 'rows' in lp:
            rows = sorted(lp['rows'], key=lambda k: (float(k['total_votes'])), reverse=True)
            r = 1
            for row in rows:
                i = {}
                i['position'] = '{}'.format(r)
                r += 1
                if row['owner'] == producing:
                    i['owner'] = '<a href={0}>{1}&nbsp;&nbsp;<i class="fas fa-sync fa-spin fa-1x"></i></a>'.format(url_for('owner', owner=row['owner']), row['owner'])
                else:
                    i['owner'] = '<a href={0}>{1}</a>'.format(url_for('owner', owner=row['owner']), row['owner'])
                i['total_votes'] = '{:0,.0f}'.format(float(row['total_votes']))
                i['social'] = gen_social('app/cache/{}.json'.format(row['owner']))
                i['url'] = '<a href="{0}" target="_blank" >{0}<!-- <i class="fas fa-globe"></i> --></a>'.format(row['url'])
                i['votes'] = gen_votes('app/cache/{}.json'.format(row['owner']))
                i['is_active'] = '<i class="fa fa-check"></i>' if row['is_active'] == 1 else 'x'
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
                  "p2p_endpoint": "",
                  "bnet_endpoint": "",
                  "api_endpoint": "",
                  "ssl_endpoint": ""
                },
              ]
            }

    return jsonify(data)


if __name__ == '__main__':
    pass
