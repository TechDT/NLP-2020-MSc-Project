from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from swanalytics_logger import get_sw_logger
swanalytics_logger = get_sw_logger()

from datetime import datetime

import pycountry_convert
import pycountry
import json
import re


# read events.json 
def read_events():
    with open("events.json", "r") as read_file:
        return json.load(read_file)


def search_location(location):
    country = None
    for location_part in location:
        try:
            country = pycountry.countries.search_fuzzy(location_part)
            break
        except:
            try:
                country = pycountry.countries.lookup(location_part)
                break
            except:
                continue
    return country


def clean_and_sentiment(events):
    for event in events["events"]:
        swanalytics_logger.info(f"[{event['start_date']} to {event['end_date']}] {event['title']}")
        event_file = event["start_date"] + "_" + event["end_date"] + ".json"
        with open("tweets/" + event_file, 'r') as read_file:
            # list (array) of tweets
            full_tweets = json.load(read_file)["tweets"]
            # iterrate the tweets for each event
            tweets = { "tweets": [] }

            # statistics
            total_tweets = len(full_tweets)
            total_tweets_loc = 0
            total_tweets_loc_undesc = 0
            
            for t in full_tweets:
                if t["user"]["location"] != None:
                    total_tweets_loc += 1
                    location = re.split('; |- |,', t["user"]["location"])
                    country = search_location(location)

                    if not country:
                        location = t["user"]["location"].split(' ')
                        country = search_location(location)
                        if not country:
                            total_tweets_loc_undesc += 1
                    if country:
                        try:
                            continent = \
                                pycountry_convert.convert_continent_code_to_continent_name(
                                    pycountry_convert.country_alpha2_to_continent_code(
                                        country[0].alpha_2
                                    )
                                )
                        except:
                            total_tweets_loc_undesc += 1
                            continue

                        tweet = {
                            "created_at": datetime.strptime(t["created_at"], "%a %b %d %H:%M:%S %z %Y").strftime("%Y-%m-%d %H:%M:%S"),
                            "created_at_original": t["created_at"],
                            "user_id": t["user"]["id"],
                            "user_location": {
                                'alpha_2': country[0].alpha_2,
                                'alpha_3': country[0].alpha_3,
                                'name': country[0].name,
                                'numeric': country[0].numeric,
                                'official_name': country[0].official_name if hasattr(country[0],'official_name') else None,
                                'continent': continent
                            },
                            "user_followers": t["user"]["followers_count"]
                        }

                        if "extended_tweet" in t:
                            try:
                                tweet["text"] = t["extended_tweet"]["full_text"]
                            except:
                                tweet["text"] = t["text"]
                        elif "retweeted_status" in t:
                            try:
                                tweet["text"] = t["retweeted_status"]["extended_tweet"]["full_text"]
                            except:
                                tweet["text"] = t["retweeted_status"]["text"]
                        else:
                            tweet["text"] = t["text"]

                        tweets["tweets"].append(tweet)

        tweets_per_user = {}
        for tweet in tweets["tweets"]:
            user_tweets = tweets_per_user.get(tweet["user_id"])
            if not user_tweets:
                tweets_per_user.update({tweet["user_id"]: {
                        "tweets": [tweet],
                        "is_bot": False
                    }})
            else:
                tweets_per_user.get(tweet["user_id"])["tweets"].append(tweet)
        
        # discard duplicate tweets per user
        tweets_final_list = []        
        total_tweets_dup = 0
        for user_id, user_tweets in tweets_per_user.items():
            for i in range(0, len(user_tweets['tweets'])):
                is_duplicate = False
                for j in range(i + 1, len(user_tweets['tweets'])):
                    if user_tweets['tweets'][i]['text'] == user_tweets['tweets'][j]['text']:
                        total_tweets_dup += 1
                        is_duplicate = True
                if not is_duplicate:
                    tweets_final_list.append(user_tweets['tweets'][i])

        total_tweets_to_store = len(tweets_final_list)

        # print statistics
        tweets_final = {}
        tweets_final["total_tweets"] = total_tweets
        tweets_final["tweets_with_location"] = total_tweets_loc
        tweets_final["tweets_disc_unknown_location"] = total_tweets_loc_undesc
        tweets_final["duplicate_tweets"] = total_tweets_dup
        tweets_final["tweets_stored"] = total_tweets_to_store
        tweets_final["tweets"] = tweets_final_list
        
        # write to file the cleaned data
        if total_tweets_to_store > 0:
            # perform sentiment analysis
            analyzer = SentimentIntensityAnalyzer()
            for i in range(0, total_tweets_to_store):
                td = tweets_final["tweets"][i]
                vs = analyzer.polarity_scores(td["text"])
                td["neg"] = vs["neg"]
                td["neu"] = vs["neu"]
                td["pos"] = vs["pos"]
                td["compound"] = vs["compound"]
            
            with open("tweets/results/" + event_file, 'w') as outfile:
                json.dump(tweets_final, outfile, ensure_ascii=True, indent=4)


def main():
    swanalytics_logger.info("Started data cleaning and sentiment analysis")
    events = read_events()
    clean_and_sentiment(events)


if __name__ == "__main__":
    main()
