# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup

import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
import requests
import datetime
from daddyzone.items import DaddyzoneItem

import urllib
import logging

thepage = requests.get("https://www.baseballmusings.com/cgi-bin/ChooseSplitBatter.py")

class TransactionsSpider(CrawlSpider):
    name = 'transactions'
    start_urls = [ 
        'http://m.mlb.com/nyy/roster/transactions',
        'http://m.mlb.com/bos/roster/transactions',
        'http://m.mlb.com/tb/roster/transactions',
        'http://m.mlb.com/tor/roster/transactions',
        'http://m.mlb.com/bal/roster/transactions',
        'http://m.mlb.com/min/roster/transactions',
        'http://m.mlb.com/cle/roster/transactions',
        'http://m.mlb.com/cws/roster/transactions',
        'http://m.mlb.com/kc/roster/transactions',
        'http://m.mlb.com/det/roster/transactions',
        'http://m.mlb.com/hou/roster/transactions',
        'http://m.mlb.com/oak/roster/transactions',
        'http://m.mlb.com/laa/roster/transactions',
        'http://m.mlb.com/tex/roster/transactions',
        'http://m.mlb.com/sea/roster/transactions',
        'http://m.mlb.com/atl/roster/transactions',
        'http://m.mlb.com/was/roster/transactions',
        'http://m.mlb.com/phi/roster/transactions',
        'http://m.mlb.com/nym/roster/transactions',
        'http://m.mlb.com/mia/roster/transactions',
        'http://m.mlb.com/stl/roster/transactions',
        'http://m.mlb.com/chc/roster/transactions',
        'http://m.mlb.com/mil/roster/transactions',
        'http://m.mlb.com/cin/roster/transactions',
        'http://m.mlb.com/pit/roster/transactions',
        'http://m.mlb.com/lad/roster/transactions',
        'http://m.mlb.com/sf/roster/transactions',
        'http://m.mlb.com/ari/roster/transactions',
        'http://m.mlb.com/sd/roster/transactions',
        'http://m.mlb.com/col/roster/transactions',
    ]
    custom_settings = {
        'FEED_FORMAT': 'csv',
        'FEED_URI': 'stats.csv'
    }

    rules = (
        Rule(
            LinkExtractor(allow=(r'.*/roster/transactions/\d{4}/\d{2}')),
            callback="parse_item",
            follow=True
        ),
    )

    def splits_generator(self, dt):
        start_date = datetime.datetime.strptime(dt, "%m/%d/%y")
        for delta in [-90, -60, -30, -14, -7, 7, 14, 30, 60, 90]:
            end_date = start_date + datetime.timedelta(days=delta)
            if end_date <= datetime.datetime.now():
                yield delta, {
                    'EndDate': max(start_date, end_date).strftime("%m/%d/%Y"),
                    'StartDate': min(start_date, end_date).strftime("%m/%d/%Y"),
                    'PlayedFor': 0,
                    'GameType': 'all',
                    'PlayedVs': 0,
                    'Park': 0
                }

    def parse_item(self, response):
        self.logger.info('Processing..' + response.url)
        soup = BeautifulSoup(response.body, 'html.parser')
        roster = soup.select('table.roster-transactions')
        if not roster:
            return
        for row in roster[0].tbody.findAll('tr'):
            item = DaddyzoneItem()
            date = row.findAll('td')[0].contents
            transaction = row.findAll('td')[1]
            to_paternity_list = any([ 'from the paternity list' in e for e in transaction.contents])
            if to_paternity_list:

                item['date'] = date[0]
                item['player'] = transaction.find('a').contents[0]
                names = item['player'].split()
                logging.info("Adding {0} to the daddy list".format(item["player"]))

                thepage = requests.get("https://www.baseballmusings.com/cgi-bin/PlayerFind.py?{0}".format(urllib.parse.urlencode({ "passedname": item['player'].lower()})))
                soup = BeautifulSoup(thepage.content, "html.parser")
                player_links = soup.find_all('a', string="Batting Splits", href=True)
                if len(player_links) != 1:
                    msg = """
                        Did not find an exact daddy match for {0}...skipping... 
                        Usually this means the player is a pitcher with no batting stats. 
                        We should update the crawler to log pitching stats in this case.
                    """.format(item['player'])
                    logging.info(msg)
                    return
                item['splits'] = []
                for delta, split in self.splits_generator(item['date']):
                    split_uri = "{base_uri}&{rest}".format(
                        base_uri=player_links[0]['href'],
                        rest=urllib.parse.urlencode(split)
                    )
                    splits = requests.get(split_uri)
                    soup = BeautifulSoup(splits.content, "html.parser")

                    overall_rows = soup.findAll("table", {"class" : "dbd"})[0].findAll('tr')
                    if not overall_rows:
                        logging.info("""
                            Could not find any data for {0} over the split:\n
                            {1}
                            Usually this means the player is a pitcher with no batting stats 
                            over this time range. We should update the crawler to log pitching
                            stats in this case.
                        """.format(item["player"], split))
                        return
                    stat_names = overall_rows[0].findAll('th')[1:]  
                    stats = overall_rows[1].findAll('td')[1:]
                    split_line = {
                        'player': item['player'],
                        'days_until_daddy': delta,
                        'daddy_date': item['date'],
                    }
                    for name, stat in zip(stat_names, stats):
                        split_line[name.text] = stat.text
                    item['splits'].append(split_line)
                    yield split_line