#!/bin/sh

cd /webapp/app/biqu

while :
do
    echo "start"
    scrapy crawl biqu
    scrapy crawl index -s CONCURRENT_REQUESTS=1
    sleep 3
done
