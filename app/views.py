from flask import render_template, jsonify
import os
import json
from datetime import datetime, timedelta
from pathlib import Path
import requests
from pprint import pprint
from app.app import app


# lets encrypt once for domain validation
#@app.route("/.well-known/acme-challenge/<key>")
#def letsencrypt():
#    return "<key>.<xo>"


@app.route('/')
def index():
   return render_template( 'index.html' )


@app.route('/dev')
def dev():
    data = {}
    return render_template( 'dev.html', d=data )


@app.route('/_ohlc/<int:days>')
@app.route('/_ohlc')
def graph_status(days=1, coin='app/rem'):

    if Path(coin).exists():
        p = Path(coin)
        file_time = datetime.fromtimestamp(p.stat().st_mtime) + timedelta(minutes=60)
        file_to_old_time = datetime.today()
        if (file_time < file_to_old_time):

            params = { 'fsym': 'REM',
                       'tsym': 'USDT',
                       'limit': 2000,
                       'api_key': os.getenv('cryptocompare_key')   }
            r = requests.get('https://min-api.cryptocompare.com/data/v2/histoday', params=params)
 
            if r.ok and r.json:
                print('new file')
                p.write_text(r.text)

  
    with open('app/rem') as j:
        data = json.load(j)
        l = []
        if 'Data' in data and 'Data' in data['Data']:
            for ohlc in data['Data']['Data']:
                if ohlc['open'] is not 0:
                    time = ohlc['time'] * 1000
                    l.append([time, ohlc['open'], ohlc['high'], ohlc['low'], ohlc['close'], ohlc['volumefrom']])

    pprint(l)
    return jsonify(l)

@app.route('/bp.json')
def bp():
    data =  { "producer_account_name": "dvvcjmkvkpsq",
              "org": {
                "candidate_name": "",
                "website": "https://josien.net",
                "code_of_conduct":"",
                "ownership_disclosure":"",
                "email":"",
                "branding":{
                  "logo_256":"",
                  "logo_1024":"",
                  "logo_svg":""
                },
                "location": {
                  "name": "",
                  "country": "",
                  "latitude": 0,
                  "longitude": 0
                },
                "social": {
                  "steemit": "ferryschuller",
                  "twitter": "josien_net",
                  "youtube": "",
                  "facebook": "josien.net",
                  "github": "FerrySchuller",
                  "reddit": "josien_net",
                  "keybase": "",
                  "telegram": "JosienNet",
                  "wechat":""
                }
              },
              "nodes": [
                { 
                  "location": {
                    "name": "",
                    "country": "Netherlands",
                    "latitude": 52.3667,
                    "longitude": 4.8945
                  },
                  "node_type": "producer",
                  "p2p_endpoint": "",
                  "bnet_endpoint": "",
                  "api_endpoint": "",
                  "ssl_endpoint": ""
                },
                {
                  "location": {
                    "name": "",
                    "country": "",
                    "latitude": 0,
                    "longitude": 0
                  },
                  "node_type":"seed",
                  "p2p_endpoint": "",
                  "bnet_endpoint": "",
                  "api_endpoint": "",
                  "ssl_endpoint": ""
                }
              ]
            }

    return jsonify(data)
