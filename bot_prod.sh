#!/bin/bash

case $1 in
   start)
      /prod/REMME-BP-web/env/bin/python /prod/REMME-BP-web/app/bot.py monit &
      ;;
    stop)  
      kill `cat /prod/REMME-BP-web/bot.pid` 
      ;;
    restart)
      kill `cat /prod/REMME-BP-web/bot.pid` 
      sleep 1
      /prod/REMME-BP-web/env/bin/python /prod/REMME-BP-web/app/bot.py monit &
      ;;
    *)  
      echo "usage: bot.sh {start|stop}" ;;
esac
exit 0

