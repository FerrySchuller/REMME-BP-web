# REMME-BP-web
REMME Block Producer Flask / Mongodb app by josien.net

Live site: https://josien.net

Dependencies, the code and virtual environment.

```
apt install python3-pip python3-dev build-essential libssl-dev libffi-dev python3-setuptools nginx mongodb monit python3-venv certbot rsyslog-mongodb git
root@remme0:/prod# git clone https://github.com/FerrySchuller/REMME-BP-web.git
root@remme0:/prod# cd REMME-BP-web/
root@remme0:/prod/REMME-BP-web# python3 -m venv env
root@remme0:/prod/REMME-BP-web# . env/bin/activate
(env) root@remme0:/prod/REMME-BP-web# pip install --upgrade pip
(env) root@remme0:/prod/REMME-BP-web# pip install -r requirements.txt
```

remnode systemd file

```
# cat /etc/systemd/system/remnode.service
[Unit]
Description=remnode
After=network.target mongod.service
RequiresMountsFor=/prod
[Service]
SyslogFacility=local0
User=root
Group=root
ExecStart=/usr/bin/remnode --config-dir /prod/bp/config/ --data-dir /prod/bp/data/
[Install]
WantedBy=multi-user.target

systemctl start remnode
systemctl enable remnode
systemctl status remnode
```


rsyslog config for caching blocks with transactions:
```
$:/etc/rsyslog.d# cat /etc/rsyslog.d/remme.conf
module(load="ommongodb")

if (not re_match($msg, ".*trxs: 0.*")) and (re_match($msg, ".*signed by.*")) then {
    local0.info action( type="ommongodb"
                        server="localhost"
                        db="josien_remme"
                        collection="logs" )
}
```


mongo pruning settings:

```
mongo josien_remme --eval "printjson(db.logs.createIndex( { "time": 1 }, { expireAfterSeconds: 43200 } ))"
```

systemd config:

```
cat /etc/systemd/system/josien.net.service

[Unit]
Description=uWSGI josien.net
After=network.target
  
[Service]
User=root
Group=www-data
WorkingDirectory=/prod/REMME-BP-web
Environment="PATH=/prod/REMME-BP-web/env/bin"
ExecStart=/prod/REMME-BP-web/env/bin/uwsgi --ini web.ini

[Install]
WantedBy=multi-user.target

# systemctl start josien.net
# systemctl status josien.net
# systemctl enable josien.net

```

monit config:

```
cat /etc/monit/conf.d/bot 
check process bot with pidfile /prod/REMME-BP-web/bot.pid
start program = "/prod/REMME-BP-web/bot_prod.sh start" as uid "root" and gid "root" with timeout 60 seconds
stop program = "/prod/REMME-BP-web/bot_prod.sh stop"
```

nginx config:

```
root@remme0:~# vi /etc/nginx/sites-available/josien.net

server {
    listen [::]:80;
    listen 80;
    server_name josien.net;
    # redirect http to https www
    return 301 https://josien.net$request_uri;
}

server {
    listen [::]:443 ssl http2;
    listen 443 ssl http2;
    server_name josien.net;
    ssl_certificate /etc/letsencrypt/live/josien.net/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/josien.net/privkey.pem;
    location = /favicon.ico {
        access_log off;
        log_not_found off;
    }
    location / {
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
        include uwsgi_params;
        uwsgi_ignore_client_abort on;
        uwsgi_pass unix:/prod/REMME-BP-web/web.sock;
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header Access-Control-Allow-Origin "https://josien.net";
        add_header Referrer-Policy "origin-when-cross-origin" always;
        add_header Strict-Transport-Security "max-age=31536000; includeSubdomains; preload";
    }
}


# ln -s /etc/nginx/sites-available/josien.net /etc/nginx/sites-enabled/josien.net
# systemctl status nginx
# systemctl restart nginx
```
