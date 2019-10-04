# REMME-BP-web
REMME Block Producer by josien.net


'''
  apt install python3-pip python3-dev build-essential libssl-dev libffi-dev python3-setuptools nginx
  root@remme0:/prod# git clone https://github.com/FerrySchuller/REMME-BP-web.git
  root@remme0:/prod# cd REMME-BP-web/
  root@remme0:/prod/REMME-BP-web# python3 -m venv env
  root@remme0:/prod/REMME-BP-web# . env/bin/activate
  (env) root@remme0:/prod/REMME-BP-web# pip install --upgrade pip
  (env) root@remme0:/prod/REMME-BP-web# pip install -r requirements.txt
'''


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



  systemctl start josien.net
  systemctl status josien.net
  systemctl enable josien.net


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
          uwsgi_pass unix:/prod/REMME-BP-web/web.sock;
          add_header Content-Security-Policy "img-src * 'self' data: blob: https:; default-src 'self' https://*.googleapis.com https://*.googletagmanager.com https://*.google-analytics.com https://s.ytimg.com https://www.youtube.com https://josien.net https://*.googleapis.com https://*.gstatic.com https://*.w.org data: 'unsafe-inline' 'unsafe-eval';" always;
  add_header X-Xss-Protection "1; mode=block" always;
          add_header X-Frame-Options "SAMEORIGIN" always;
          add_header X-Content-Type-Options "nosniff" always;
          add_header Access-Control-Allow-Origin "https://josien.net";
          add_header Referrer-Policy "origin-when-cross-origin" always;
          add_header Strict-Transport-Security "max-age=31536000; includeSubdomains; preload";
      }
  }

  ln -s /etc/nginx/sites-available/josien.net /etc/nginx/sites-enabled/josien.net
