"""
@Author: Bill DeRose
"""
import collections
import urllib

import spacy
import tweepy
import xx_ent_wiki_sm

consumer_key = "T2qKisNsBJHSlspryWHNKCPjK"
consumer_secret = "fAbd4tyaS5RfpZ0cRQHuCiMz60QroA0myCd57qKUGnp0oW1zA9"
access_token_key = "14439310-WRG0hzdRnWAlDY7ZyR53iHzGfH5z5A9IF0g0jZHRy"
access_token_secret = "irsyuzLztIZdxBXKOkZC2UcoJhBPfFVLgk0SryI9h8xTu"

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token_key, access_token_secret)
api = tweepy.API(auth)

nlp = xx_ent_wiki_sm.load()
search_term = urllib.parse.quote_plus('paternity list mlb')
tweet_cursor = tweepy.Cursor(api.search, q=search_term, result_type="recent")
counts = collections.Counter()

def entity_is_person(entity):
    return entity.label_ == 'PER'

for tweet in tweet_cursor.items():
    document = nlp(tweet.text)
    for entity in document.ents:
        if entity_is_person(entity):
            counts[entity.text.lower()] += 1

counts.most_common(10)
