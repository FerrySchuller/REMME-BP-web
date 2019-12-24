import requests
import socket;
import sys


def port_open(host, port, timeout=3):
    s = socket.socket( socket.AF_INET, 
                       socket.SOCK_STREAM )
    s.settimeout(timeout)
    try:
        s.connect((host, int(port)))
        s.shutdown(socket.SHUT_RDWR)
        return True
    except:
        return False
    finally:
        s.close()

    return False


def main():
    url = "https://remchain.remme.io/v1/chain/get_producers"
    
    payload = '{ "json" : true }'
    headers = { 'accept': "application/json",
                'content-type': "application/json" }
    
    r = requests.post(url, data=payload, headers=headers)
    if r and r.ok and r.json:
        o = r.json()
        if o and 'rows' in o:
            for row in o['rows']:
                url = '{}/bp.json'.format(row['url'])
                bp_json = requests.get(url)
                bp = False
                if bp_json and bp_json.ok and bp_json.json:
                    try:
                        bp = bp_json.json()
                    except:
                        pass
                        #print(sys.exc_info())
                if bp and 'nodes' in bp:
                    for node in bp['nodes']:
                        if 'p2p_endpoint' in node and node['p2p_endpoint']:
                            n = node['p2p_endpoint'].split(":")
                            if len(n) == 2:
                                if port_open(n[0], n[1]):
                                    print('p2p-peer-address = {}'.format(node['p2p_endpoint']))


if __name__ == '__main__':
    main()
