#!/bin/sh
# get the start date and time
start_datetime=$(date '+%m_%d_%Y_%H_%M_%S')
echo "${start_datetime} - starting spider"
#cd /home/markanthonyvale/dev/media_meter/news-extractor/venv/bin/activate# prevent click, which pipenv relies on, from freaking out to due to lack of locale info https://click.palletsprojects.com/en/7.x/python3/
#export LC_ALL=en_US.utf-8# run the spider
#$PIPENV run scrapy crawl multi_subject_spider -a debug='True' &> "logs/log_${start_datetime}.txt"# get the end date and time
cd /home/markanthonyvale/dev/media_meter/news-extractor/ && . venv/bin/activate
python3 scraper.py
end_datetime=$(date '+%m_%d_%Y_%H_%M_%S')
echo "${end_datetime} - spider finished successfully"
