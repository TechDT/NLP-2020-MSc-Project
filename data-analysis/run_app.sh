#!/bin/bash

if [ "$DATA_ANALYSIS" = "true" ]; then 
    # remove stock prices
    rm /data-analysis/stocks/*.csv

    # remove all files after cleaning, sentiment and topic_analysis plus stocks
    rm /data-analysis/tweets/*.json
    rm /data-analysis/tweets/results/*.json
    rm /data-analysis/tweets/results/topic_analysis/*.html

    # remove old logs 
    rm /data-analysis/swanalytics.log
    
    # clean web-app
    rm /web-app/event*.html
    rm /web-app/results/world/*.json
    rm /web-app/results/sentiment/*.json
    rm /web-app/results/topic_analysis/*.json

    # run the app
    python data_retrieval.py
    python clean_and_sentiment.py
    python topic_analysis.py
    python prepare_app.py
else 
    echo "Bypassing data analysis"
fi