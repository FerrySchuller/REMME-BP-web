from flask import render_template, jsonify, flash, url_for, redirect, abort, request
import os, sys
import json
from datetime import datetime, timedelta, timezone, time
from dateutil.parser import parse
from pathlib import Path
from time import sleep
import pymongo
import random
import randomcolor
import requests
from pprint import pprint
from app.lib.josien import track_event, jlog, cmd_run, listproducers, get_account, remcli_get_info, human_readable, db, listvoters, get_block
from app.app import app

log_file = os.getenv('LOG_FILE', False)
jlog = jlog(stdout=True, feil=log_file)
db = db()

# lets encrypt once for domain validation
# certbot certonly --manual
cert_key = os.getenv('cert_key', False)
cert_handshake = os.getenv('cert_handshake', False)

@app.route("/.well-known/acme-challenge/{}".format(cert_key))
def letsencrypt():
    return "{}".format(cert_handshake)


#@app.before_request
#def before_request():
#    i = remcli_get_info()
#    if i and 'head_block_time' in i:
#        dt = parse(i['head_block_time'])
#        d = datetime.now() - dt
#        if d.seconds > 30:
#            abort(400)


def gen_health(title, fa_class='fa-times', color='tomato', text=''):
    msg = '<li><span style="color: {2};"><text data-toggle="tooltip" data-placement="top" data-html="true" title="{0}"><i class="fa {1}">{3}</i></text></span></li>'.format(title, fa_class, color, text)
    return(msg)


def gen_trxs(seconds, tag):
    dt = (datetime.now() - timedelta(seconds=seconds))
    trxs  = db.trxs.find( { "$and": [ {"created_at": { "$gt": dt } },
                                      {"tag": tag } ] }, { "_id": 0 } )
    l = []
    if trxs:
        for trx in trxs:
            t = trx['data']['t'].timestamp() * 1000
            y = trx['data']['y']
            l.append({ 't': t, 'y': y })
    return(l)


@app.route('/')
def index():
    #track_event( category='index', action='index')
    return render_template( 'index.html', trxs=gen_trxs(200, 5) )


@app.route('/offline')
def offline():
    #track_event( category='offline', action='offline')
    return render_template( 'offline.html' )


@app.route('/guardians')
def guardians():
    #track_event( category='guardians', action='guardians')
    return render_template( 'guardians.html' )


@app.route('/code_of_conduct')
def code_of_conduct():
    #track_event( category='index', action='code_of_conduct')
    return render_template( 'code_of_conduct.html' )


@app.route('/ownership_disclosure')
def ownership_disclosure():
    #track_event( category='index', action='ownership_disclosure')
    return render_template( 'ownership_disclosure.html' )


@app.route('/owner/<owner>')
def owner(owner):
    #track_event( category='index', action='owner')
    voter = False
    get_owner = db.producers.find_one( {"name": "{}".format(owner)} )
    if not get_owner:
        voter = get_account(owner)
    return render_template( 'owner.html', owner=get_owner, voter=voter  )


def random_color():
    rand_color = randomcolor.RandomColor()
    return(rand_color.generate(luminosity="dark")[0])


def gen_graph():
    graph = {}
    graph['title'] = 'CPU in ms active 21 producers'
    values = []

    producers = db.producers.find()
    if producers:
        for p in producers:
            if p['position'] < 22:
                usages = db.cache.find({"owner": "{}".format(p['name'])}).limit(1000)
                color = random_color()
                l = []
                d = {}  
                d['label'] = p['name']
                d['fill'] = "false"
                d['borderWidth'] = 1.5 
                d['pointRadius'] = 0
                d['backgroundColor'] = color
                d['borderColor'] = color

                for use in usages:
                    t = use['data']['cpu_usage_us_dt'].timestamp() * 1000
                    y = use['data']['cpu_usage_us'] / 1000
                    if y > 2:
                        d['borderColor'] = '#de4040'
                        d['backgroundColor'] = '#de4040'
                    l.append({"t": t, "y": y})
                    
                if l:
                    d['data'] = l
                    values.append(d) 


    graph['values'] = values
    return(graph)


def chart_time(dt=None, roundTo=60):
   if dt == None : dt = datetime.datetime.now()
   seconds = (dt.replace(tzinfo=None) - dt.min).seconds
   rounding = (seconds+roundTo/2) // roundTo * roundTo
   r = dt + timedelta(0,rounding-seconds,-dt.microsecond)
   return(r.timestamp() * 1000)


def cpu_usage(roundTo=7200, seconds=1209600):
    dt = (datetime.now() - timedelta(seconds=seconds))
    producers = db.producers.find({}, {"name": 1, "position": 1, "color": 1, "_id": 0}).limit(30)
    resp = []
    if producers:
        for p in producers:
            if p['position'] < 22:

                #color = random_color()
                color = p['color']
                red = '#FF2323'
                chart = {}
                chart['backgroundColor'] = color
                chart['borderColor'] = color
                chart['borderWidth'] = "1.8"
                chart['fill'] = 'false'
                chart['label'] = p['name']
                chart['data'] = []

                cpu_usage = db.cpu_usage_us.find_one( { "producer": "{}".format(p['name']) },
                                                { "_id": 0, "data.block": 0, },sort=([('time', pymongo.DESCENDING)]))

                l = []
                low = []
                if cpu_usage:
                    for data in cpu_usage['data']:
                        if data['timestamp']> dt:
                            y = data['cpu_usage_us'] / 10000
                            t = chart_time(data['timestamp'], roundTo=roundTo)
                            d = {}
                            d['t'] = t
                            d['y'] = y
                            low.append(t)
                            l.append(d)

                try:
                    low = min(low)
                except:
                    low = False
                    jlog.critical('low: {} {}'.format(p['name'], sys.exc_info()))
                ty = []
                for xo in l:
                    if low and xo['t'] == low:
                        ty.append(xo['y'])
                    else:
                        low = xo['t']
                        d = {}
                        try:
                            av = "{:.4f}".format(sum(ty) / len(ty))
                            if float(av) > 0.3:
                                chart['backgroundColor'] = red
                                chart['borderColor'] = red
                            d = {}
                            d['t'] = xo['t']
                            d['y'] = av
                            chart['data'].append(d)
                        except:
                            jlog.critical('cpu_usage ERROR: {}'.format(sys.exc_info()))
                        ty = []

                resp.append(chart)
    return (resp)


@app.route('/_trxs/<int:tag>')
def _trxs(tag):
    trx = db.trxs.find_one( { "tag": tag }, { "_id": 0, "created_at": 0 },sort=([('created_at', pymongo.DESCENDING)]))
    y = trx['data']['y']
    d = {'y': y}
    return jsonify(d)


@app.route('/charts', methods = ['POST', 'GET'])
def charts():
    cpu = False
    trxs=gen_trxs(21600, 5)
    d = {}
    d['t'] = '# Transactions on remchain, 5 seconds interval.'
    if request.method == "POST" and request.form and 'roundTo' in request.form and 'seconds' in request.form:
        roundTo = request.form['roundTo']
        seconds = request.form['seconds']
        cpu = cpu_usage(float(roundTo), float(seconds))
    else:
        cpu = cpu_usage()

    if request.method == "POST" and request.form and 'trxs' in request.form and 'seconds' in request.form and request.form['seconds'] == '300':
        try:
            d['t'] = '# Transactions on remchain, 300 seconds interval.'
            tag = int(request.form['seconds'])
            trxs = gen_trxs(172800, tag)
        except:
            jlog.critical('chart ERROR: {}'.format(sys.exc_info()))

    if request.method == "POST" and request.form and 'trxs' in request.form and 'seconds' in request.form and request.form['seconds'] == '3600':
        try:
            d['t'] = '# Transactions on remchain, 3600 seconds interval.'
            tag = int(request.form['seconds'])
            trxs = gen_trxs(172800, tag)
        except:
            jlog.critical('chart ERROR: {}'.format(sys.exc_info()))


    if request.method == "POST" and request.form and 'trxs' in request.form and 'seconds' in request.form and request.form['seconds'] == '86400':
        try:
            d['t'] = '# Transactions on remchain, 86400 seconds interval.'
            tag = int(request.form['seconds'])
            trxs = gen_trxs(172800, tag)
        except:
            jlog.critical('chart ERROR: {}'.format(sys.exc_info()))



    return render_template( 'charts.html', cpu_usage=cpu, trxs=trxs, d=d )



@app.route('/dev', methods = ['POST', 'GET'])
def dev():
    return render_template( 'dev.html' )


@app.route('/_dev')
def _dev():
    get_info = remcli_get_info()
    producing = False
    if get_info:
        producing = get_info['head_block_producer']

    lp = listproducers()
    rows = lp['rows']
    owners = db.producers.find()
    data = []
    for owner in owners:

        health = '<div><ul class="health">'
        if owner['health']:
            for issue in owner['health']:
                health += gen_health(issue['title'])


        html = '<div class="alert alert-info alert-dismissible fade show" role="alert">'
        name = owner['name'] 
        html += '<h4>{}</h4>'.format(name)
        producer = next((item for item in rows if item["owner"] == name), None)
        if producer and producing:
            d = {}

            d['punished_until'] = False
            dt = parse(producer['punished_until'])
            days = dt - datetime.now()
            if days.days > 0:
                d['punished_until'] = days.days

            if d['punished_until']:
                health += gen_health(title='punished_until {}'.format(d['punished_until']), text=' {}'.format(d['punished_until']))
                html += '<h4 class="alert-heading"><i class="fas fa-exclamation-triangle"></i> Punished for {} days.</h4>'.format(d['punished_until'])

            d['position'] = owner['position']
            d['name'] = name
            d['total_votes'] = '{:0,.0f}'.format(float(producer['total_votes']) / 10000)
            d['voters'] = owner['voters_count']
            d['social'] = owner['social']

            d['cpu_usage_us'] = False
            try:
                if owner['cpu_usage_us']:
                    cpu_usage_ms = owner['cpu_usage_us'] / 1000
                    if cpu_usage_ms > 1:
                        d['cpu_usage_us'] = "<medium class='text-warning'>{:.2f} ms</medium>".format(cpu_usage_ms)
                    if cpu_usage_ms < 1:
                        d['cpu_usage_us'] = "<medium class='text-success'>{:.2f} ms</medium>".format(cpu_usage_ms)
                    if cpu_usage_ms > 2:
                        d['cpu_usage_us'] = "<medium class='text-danger'>{:.2f} ms</medium>".format(cpu_usage_ms)
                        html += '<h4 class="alert-heading"><i class="fas fa-exclamation-triangle"></i> Slow CPU execution time.</h4>'.format()
                        health += gen_health(title='Slow CPU')
            except:
                jlog.critical('cpu_usage_us ERROR: {}'.format(sys.exc_info()))



            d['last_work_done'] = False
            ldt = parse(producer['last_block_time'])
            ld = datetime.now() - ldt

            if owner['name'] == producing:
                d['last_work_done'] = '<i class="fas fa-sync fa-spin fa-1x"></i>'
            else:
                if ld.seconds < 1800:
                    d['last_work_done'] = ("<medium class='text-success'>{:.0f}</medium>".format(ld.seconds))
                if ld.seconds > 1801:
                    d['last_work_done'] = ("<medium class='text-warning'>{:.0f} Minutes</medium>".format(ld.seconds / 60))


            if owner['bp_json_url']:
                d['bp_json'] = '<a target="_blank" href="{}"><i class="fa fa-check"></i></a>'.format(owner['bp_json_url'])
            else:
                health += gen_health(title='bp.json is missing')
                html += '<h4 class="alert-heading"><i class="fas fa-exclamation-triangle"></i> bp.json is missing.</h4>'.format()
                d['bp_json'] = ''



            d['is_active'] = ''
            if producer['is_active']:
                d['is_active'] = '<span style="display:inline-block; width:60px" class="badge badge-success">Active</span>'
            if producer['is_active'] and owner['position'] > 21:
                d['is_active'] = '<span style="display:inline-block; width:60px" class="badge badge-warning">Rotated</span>'
            if producer['is_active'] and owner['position'] > 25:
                d['is_active'] = '<span style="display:inline-block; width:60px" class="badge badge-danger">Standby</span>'
            if not producer['is_active']:
                d['is_active'] = '<span style="color: Tomato;"><i class="fa fa-times"></i></text></span>'

            #if not owner['health']:
            #    html += '<h4 class="alert-heading"><i class="far fa-thumbs-up"></i></h4>'
            #else:

            for h in owner['health']:
                html += '<h4 class="alert-heading"><i class="fas fa-exclamation-triangle"></i> {}!</h4>'.format(h['title'])

            for voter in owner['voters']:
                pass


            html += '<button type="button" class="close" data-dismiss="alert" aria-label="Close"><span aria-hidden="true">&times;</span></button>'
            html += '</div>'
            #d['dev'] = '<div data-toggle="tooltip" data-placement="top" title="dev!">dev</div>'
            d['html'] = html 

            health += '</div></ul>'
            d['health'] = health

            data.append(d)

    return jsonify(data)



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


@app.route('/_listvoters')
def _listvoters():
    price = False
    d = {}
    d['data'] = []
    lv = listvoters()
    #print(sorted(lv['rows'], key=lambda k: (float(k['last_vote_weight'])), reverse=True))
    if lv and 'rows' in lv and isinstance(lv['rows'], list):

        usd_rem = db.cache.find_one( {"tag": "usd_rem"}, sort=[('created_at', pymongo.DESCENDING)])
        if usd_rem and 'data' in usd_rem and 'USD' in usd_rem['data']:
            price = usd_rem['data']['USD']
        r = 1
        for g in lv['rows']:
            if not 'error' in g.keys():
                if (float(g['staked']) > 2500000000):
                    i = {}
                    i['pending_perstake_reward_usd'] = ''

                    try:
                        dt = parse(g['last_reassertion_time'])
                        days = datetime.now() - dt
                        i['last_reassertion_time'] = '{}'.format(days.days)
                        if days.days > 20:
                            i['last_reassertion_time'] = '<medium class="text-warning">{}</medium>'.format(days.days)
                        if days.days > 25:
                            i['last_reassertion_time'] = '<medium class="text-danger">{}</medium>'.format(days.days)
                        if days.days == 18267:
                            i['last_reassertion_time'] = ''
                    except:
                        i['last_reassertion_time'] = ''

                    i['position'] = r
                    r += 1
                    i['owner'] = '<a href={0}>{1}</a>'.format(url_for('owner', owner=g['owner']), g['owner'])

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
                        dt = parse(g['last_claim_time'])
                        days = datetime.now() - dt
                        if not days.days > 18000:
                            i['last_claim_time'] = '{}'.format(days.days)
                        else:
                            i['last_claim_time'] = '{}'.format('-')
                    except: 
                        i['last_claim_time'] = ''

       
                    try:
                        dt = parse(g['stake_lock_time'])
                        days = dt - datetime.now()
                        i['stake_lock_time'] = '{}'.format(days.days)
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

    get_info = remcli_get_info()
    producing = False
    if get_info:
        producing = get_info['head_block_producer']

    owners = db.producers.find()

    lp = listproducers()
    producers = []
    if lp and isinstance(lp, dict):
        for row in lp['rows']:
            d = {}
            d['owner'] = row['owner']
            d['last_block_time'] = row['last_block_time']
            d['is_active'] = row['is_active']
            d['punished_until'] = False
            d['total_votes'] = row['total_votes']

            try:
                dt = parse(row['punished_until'])
                days = dt - datetime.now()
                if days.days > 0:
                    d['punished_until'] = days.days
            except:
                jlog.critical('punished_until ERROR: {}'.format(sys.exc_info()))

            producers.append(d)

    if owners:
        d = {}
        d['data'] = []
        for owner in owners:

            health = '<div><ul class="health">'
            if owner['health']:
                for issue in owner['health']:
                    health += gen_health(issue['title'])

            i = {}
            i['position'] = owner['position']

            i['owner'] = '<a href={0}>{1}</a>'.format(url_for('owner', owner=owner['name']), owner['name'])

            if producers and isinstance(producers, list):
                for producer in producers:
                    if owner['name'] == producer['owner'] and producer['punished_until']:
                        health += gen_health(title='punished_until {}'.format(producer['punished_until']), text=' {}'.format(producer['punished_until']))
                    
              

            
            try:
                if producers and isinstance(producers, list):
                    for producer in producers:
                        if producer['owner'] == owner['name']:
                            total_votes = (float(producer['total_votes']) / 10000)
                            i['total_votes'] = '{:0,.0f}'.format(total_votes)
            except:
                i['total_votes'] = False


            i['voters'] = owner['voters_count']


            i['social'] = owner['social']


            i['cpu_usage_us'] = False
            try:
                if owner['cpu_usage_us']:
                    cpu_usage_ms = owner['cpu_usage_us'] / 1000
                    if cpu_usage_ms > 1:
                        i['cpu_usage_us'] = "<medium class='text-warning'>{:.2f} ms</medium>".format(cpu_usage_ms)
                    if cpu_usage_ms < 1:
                        i['cpu_usage_us'] = "<medium class='text-success'>{:.2f} ms</medium>".format(cpu_usage_ms)
                    if cpu_usage_ms > 2:
                        health += gen_health(title='Slow CPU')
                        i['cpu_usage_us'] = "<medium class='text-danger'>{:.2f} ms</medium>".format(cpu_usage_ms)
            except:
                jlog.critical('cpu_usage_us ERROR: {}'.format(sys.exc_info()))

            i['last_work_done'] = False

            if owner['name'] == producing:
                i['last_work_done'] = '<i class="fas fa-sync fa-spin fa-1x"></i>'
            else:
                try:
                    if producers and isinstance(producers, list):
                        for lbt in producers:
                            if owner['name'] == lbt['owner']:
                                ldt = parse(lbt['last_block_time'])
                                ld = datetime.now() - ldt

                                if ld.seconds < 1800:
                                    i['last_work_done'] = ("<medium class='text-success'>{:.0f}</medium>".format(ld.seconds))
                                if ld.seconds > 1801:
                                    i['last_work_done'] = ("<medium class='text-warning'>{:.0f} Minutes</medium>".format(ld.seconds / 60))
                                    health += gen_health(title='Not producing blocks for at least 30 minutes')
                                #if ld.seconds > 3600:
                                #    i['last_work_done'] = ("<medium class='text-danger'>{:.0f} Hours</medium>".format(ld.seconds / 60 / 60))

                except:
                    jlog.critical('last_work_done ERROR: {}'.format(sys.exc_info()))



            i['is_active'] = ''
            if producers and isinstance(producers, list):
                for producer in producers:
                    if owner['name'] == producer['owner']:
                        i['is_active'] = producer['is_active']
                        if producer['is_active']:
                            i['is_active'] = '<span style="display:inline-block; width:60px" class="badge badge-success">Active</span>'
                        if producer['is_active'] and owner['position'] > 21:
                            i['is_active'] = '<span style="display:inline-block; width:60px" class="badge badge-warning">Rotated</span>'
                        if producer['is_active'] and owner['position'] > 25:
                            i['is_active'] = '<span style="display:inline-block; width:60px" class="badge badge-danger">Standby</span>'
                        if not producer['is_active']:
                            i['is_active'] = '<span style="color: Tomato;"><i class="fa fa-times"></i></text></span>'


            if owner['bp_json_url']:
                i['bp_json'] = '<a target="_blank" href="{}"><i class="fa fa-check"></i></a>'.format(owner['bp_json_url'])
            else:
                health += gen_health(title='bp.json is missing')
                i['bp_json'] = ''

         
            health += '</div></ul>'
            i['health'] = health
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



@app.route('/_cpu_benchmark/<int:days>')
@app.route('/_cpu_benchmark')
def cpu_benchmark(days=1):
    data = {}
    data['title'] = 'rem'

    cpu_usage_us = [ [ 1578490398000, 2352 ], [ 1578490431000, 3352 ], 
                     [ 1578490466000, 2352 ], [ 1578490498000, 5352 ], 
                     [ 1578490531000, 1352 ], [ 1578490564000, 7352 ] ]

    josiendotnet = [ [ 1578490398000, 8350 ], [ 1578490431000, 8152 ],                                                                                                                                  [ 1578490466000, 8552 ], [ 1578490498000, 8352 ],
                     [ 1578490531000, 8350 ], [ 1578490564000, 8952 ] ]


    data['josiendotnet'] = josiendotnet
    data['cpu_usage_us'] = cpu_usage_us
    data['owners'] = { 'josiendotnet': josiendotnet, 'josientester': josiendotnet }

    return jsonify(data)


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
