## SWAnalytics - The Social Web (Vrije Universiteit)
SWAnalytics is a tool that helps data-analysts to understand if there is any correlation between various events related with stock prices and user tweets (from Twitter). The tool can be configured through a file, events.json. In that file an analyst should provide:
- The name of the stock price
- X number of events where each one has
  - A title
  - A start date
  - An end date
  - A number of hashtags 
  - The maximum number of tweets to search (for each day of the event)

The tool treats each event as a separate entity. For each one retrieves 1) the relevant Twitter data and 2) the relevant stock price from Yahoo Finance. After an automated data processing, the tool performs sentiment analysis using Vader in order to determine the positivity, negativity or neutrality of a tweet, and topic analysis using LDA to automatically extract meaning from texts by identifying recurrent themes or topics. Finally, it builds and exposes a web-app with one page for each event where each one includes various interactive graphs.

### Use case scenario
One of the most shorted stock this fiscal year on the market is [Tesla](https://www.tesla.com). At the end of January its short interest had reached 18% of its total available shares to trade. Controversial to 
this high volume of short positions, Tesla’s stock has been rising ever since its lowest stock price since 2014, on the 3rd of June 2019 with a close of $178.97. 
Before this time period Tesla had followed a sharp downward trend. Some of it could be explained by Elon Musk’s bad business attitude of announcing over optimistic 
false information on tweeter to take Tesla private. In addition financial reports (quarterly reports to be more exact) during different time 
periods and the loss of key personnel have more strongly influenced the movement of the stock price in 2019.

In the beginning of 2020 we see a financial chart of the company that follows an increasing parabolic trend ever since the 3rd of June 2019. With controversial topics like 
the release and presentation of Tesla’s cyber truck, during this period Tesla has had to face many bluders and experienced great success on the stock market. 
This research aims to look at the sentiment of Tesla followers on [Twitter](https://twitter.com) during important events/announcements made by the company or its CEO and find a relationship between 
Twitter sentiment and the state of the investors interest (expressed in the stock price) in the following 3 trading days. 

In this research we are interested in the following events:
- <strong>24th of July 2019</strong>: Tesla suffers its worst day of the year after brutal earnings report and loss of technology chief.
- <strong>21st of November 2019</strong>: Tesla unveils its new cyber truck.
- <strong>4th of February 2020</strong>: Tesla reaches its highest stock price till date of $962.86.

### Demo
https://thzois.com/swanalytics

### Requirements
- Install [Docker](https://docs.docker.com/install/) and [Docker Compose](https://docs.docker.com/compose/install/)

<strong>Note</strong>: in Docker we are using the branch "premium-search" from [tweepy](https://github.com/tweepy/tweepy) repository. In a future release that branch will be merged into master. Hence, building the container will fail at the point of installing 'tweepy'. You will have to change the corresponding line in the Dockefile.

### Run the application
- Run 'docker-compose up -d --build' inside the main directory
- Open your browser and navigate to localhost:8080

In case you would like to skip the part of gathering, cleaning and sentiment analysis of the data because e.g: you have already done that, you need to set 'DATA_ANALYSIS=false' in docker-compose.yml. The application produces a 'swanalytics.log' in order to inform you about the various data-processing events.
