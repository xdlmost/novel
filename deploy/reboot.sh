#!/bin/sh
# arg in [reboot,boot]


boot_process(){
ID=`ps -ef | grep "$1" | grep -v "grep" | awk '{print $2}'`
if [ -z "$ID" ];then
    nohup $1 $2 > /dev/null 2>&1 &
fi
}

kill_process(){
ID=`ps -ef | grep "$1" | grep -v "grep" | awk '{print $2}'`
if [ -z "$ID" ];then
    :
else
    for id in $ID
    do
        kill -9 $id
    done
fi
}

if [ "$1" = "boot" ];then
    cd /webapp/app/biqu
    boot_process "scrapy crawl index" "-s CONCURRENT_REQUESTS=1"
    boot_process "scrapy crawl biqu"
else if [ "$1" = "reboot" ];then
    cd /webapp/app/biqu
    kill_process "scrapy crawl index " "-s CONCURRENT_REQUESTS=1"
    boot_process "scrapy crawl index " "-s CONCURRENT_REQUESTS=1"
    kill_process "scrapy crawl biqu"
    boot_process "scrapy crawl biqu"
fi
fi
