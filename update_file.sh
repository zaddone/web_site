#!/usr/bin/expect
cd /data/web/user_center_git/user_center
spawn git pull hdj@wwwhuodongjia.oicp.net:/home/xiaorizigit/user_center.git
expect "hdj@wwwhuodongjia.oicp.net's password:"
send "88888888\r"
interact
spawn sudo service uwsgi restart
send "Hdfgy$%&2975!2\r"
interact