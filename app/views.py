from flask import render_template, jsonify
from app.app import app


# lets encrypt once for domain validation
#@app.route("/.well-known/acme-challenge/<key>")
#def letsencrypt():
#    return "<key>.<xo>"


@app.route('/')
def index():
   return render_template( 'index.html' )

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
