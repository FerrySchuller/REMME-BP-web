#!/bin/bash

case $1 in
   start)
      /prod/apps/remme/REMME-BP-web/env/bin/python /prod/apps/remme/REMME-BP-web/app/bot.py monit &
      ;;
    stop)  
      kill `cat /prod/apps/remme/REMME-BP-web/bot.pid` ;;
    *)  
      echo "usage: bot.sh {start|stop}" ;;
esac
exit 0

