#!/bin/bash

case $1 in
   start)
      /prod/REMME-BP-web/env/bin/python /prod/REMME-BP-web/app/bot.py monit &
      ;;
    stop)  
      kill `cat /var/tmp/bot.pid` ;;
    *)  
      echo "usage: bot.sh {start|stop}" ;;
esac
exit 0

