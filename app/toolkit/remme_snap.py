import requests
from pprint import pprint


url = "http://127.0.0.1:8888/v1/producer/create_snapshot"

payload = '{ "json" : true }'
#headers = { 'accept': "application/json",
#            'content-type': "application/json" }

headers = { 'content-type': 'application/x-www-form-urlencoded; charset=UTF-8' }
r = requests.post(url, data=payload, headers=headers)
pprint(vars(r))
