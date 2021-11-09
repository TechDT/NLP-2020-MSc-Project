from pandas_datareader.data import DataReader
from swanalytics_logger import get_sw_logger
swanalytics_logger = get_sw_logger()

from datetime import datetime
from datetime import timedelta
from dotenv import load_dotenv
load_dotenv()
from ast import literal_eval

import tweepy
import json
import os
import time


# read events.json 
def read_events():
    with open("events.json", "r") as read_file:
        return json.load(read_file)


# handle rate-limit of TwitterAPI
def limit_handler(cursor):
    # this is the response in the message that Twitter uses if account limit reached
    account_exceed = "Request exceeds account’s current package request limits"

    while True:
        try:
            yield cursor.next()
        except tweepy.RateLimitError as b:
            swanalytics_logger.exception("Rate limit hit: ")
            time.sleep(15 * 60)
        except tweepy.TweepError as e:
            d = literal_eval(e.reason)
            if account_exceed in d["message"]:
                swanalytics_logger.exception("Monthly rate limit reached:")
                break
            elif e.response is not None:
                if hasattr(e.response, 'status_code'):
                    if e.response.status_code == 420 or e.response.status_code == 429:
                        swanalytics_logger.exception("Rate limit hit: ")
                        time.sleep(15 * 60)
            else:
                swanalytics_logger.exception("Break cause of exception:")
                break
        except StopIteration:
            break


# get Twitter and stock data based on events.json and store 
# them in separate files based on the event dates
def get_twitter_stock_data(events):
    API_KEY = os.getenv("TWITTER_API_KEY")
    API_SECRET = os.getenv("TWITTER_API_SECRET")
    ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
    ACCESS_TOKEN_SECRET = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
    TWITTER_APP_ENV = os.getenv("TWITTER_APP_ENV")

    auth = tweepy.OAuthHandler(API_KEY, API_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    api = tweepy.API(auth)

    for event in events["events"]:
        swanalytics_logger.info(f"[{event['start_date']} to {event['end_date']}] {event['title']}")
        
        stock_price = DataReader(events["stock"], "yahoo", event["start_date"], event["end_date"])
        stock_price.to_csv("stocks/" + event["start_date"] + "_" + event["end_date"] + ".csv")
        swanalytics_logger.info("Stock data received")

        # prepare query string
        # see: https://developer.twitter.com/en/docs/tweets/rules-and-filtering/guides/using-premium-operators
        query_string = "("
        for i in range (0, len(event["hashtags"])):
            if i == len(event["hashtags"]) - 1:
                query_string += event["hashtags"][i]
            else:
                query_string += event["hashtags"][i] + " OR "
        query_string += ") lang:en"

        # twitter premium API expects date to be in format 'yyyyMMddHHmm'
        start_datetime = event["start_date"].replace("-", "") + "0000"
        end_datetime = event["start_date"].replace("-", "") + "2359"

        tweets = { "tweets": [] }
        start_dateobj = datetime.strptime(event["start_date"], '%Y-%m-%d').date()
        end_dateobj = datetime.strptime(event["end_date"], '%Y-%m-%d').date()

        # iterate each day and get max tweets as event["max_tweets_per_day"]
        while True:
            # tweepy docs: https://github.com/tweepy/tweepy/blob/premium-search/docs/api.rst - premium API does not support 'lang'
            for items in limit_handler(tweepy.Cursor(api.search_full_archive, environment_name=TWITTER_APP_ENV, query=query_string, fromDate=start_datetime, toDate=end_datetime).items(event["max_tweets_per_day"])):
                tweets["tweets"].append(items._json)
            
            # Move to netxt day
            start_dateobj = start_dateobj + timedelta(days=1)
            start_datetime = start_dateobj.strftime("%Y-%m-%d").replace("-", "") + "0000"
            end_datetime = start_dateobj.strftime("%Y-%m-%d").replace("-", "") + "2359"
            
            # if the day is the next day of our end_date break
            if(start_dateobj > end_dateobj):
                break
    
        swanalytics_logger.info(f"Tweets fetched: {str(len(tweets['tweets']))}")

        # got all event data - write them to file
        if len(tweets["tweets"]) > 0:
            filename = event["start_date"] + "_" + event["end_date"] + ".json"
            with open("tweets/" + filename, 'w') as outfile:
                json.dump(tweets, outfile, ensure_ascii=True, indent=4)


def main():
    swanalytics_logger.info("Started receiving Twitter & Stock data")
    events = read_events()
    get_twitter_stock_data(events)


if __name__ == "__main__":
    main()