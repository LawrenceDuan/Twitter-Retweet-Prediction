import json
import re
import datetime
import sys
import http.cookiejar
from pyquery import PyQuery
import urllib.request
import urllib.parse
import urllib.error
import urllib.request
import urllib.error
import urllib.parse


class HtmlHandler:

    def __init__(self):
        pass

    @staticmethod
    def writeToCSV(tweets, csv):
        '''
        Writing tweet information into the csv file
        :param tweets: the extracted tweets
        :param csv: the csv file to be written in
        :return: void
        '''
        for tweet in tweets:
            csv.write(('\n%s;%s;"%s";%d;"%s";%d;%d;%s;%s;%s;%s' % (tweet.username,
                                                                tweet.date.strftime("%Y-%m-%d %H:%M"),
                                                                tweet.tweetid,
                                                                tweet.authorid,
                                                                tweet.text,
                                                                tweet.retweets,
                                                                tweet.favorites,
                                                                tweet.mentions,
                                                                tweet.hashtags,
                                                                tweet.permalink,
                                                                tweet.geo)))
        csv.flush()
        print('\n Summary: ', end='')
        print(len(tweets), end='')
        print(" tweets crawled and saved.")


    @staticmethod
    def getJsonReponse(userName, e_cursor, cookieJar, proxy):
        '''
        Pretend to be a human who is reading through twitter.com. Then extract back html page information into json.
        :param userName: name of the twitter account
        :param e_cursor: current cursor position on web page
        :param cookieJar: reading cookie on twitter.com
        :param proxy: web proxy
        :return: json of current twitter page
        '''
        urlGetData = ' from:' + userName
        url = "https://twitter.com/i/search/timeline?f=tweets&q=" + urllib.parse.quote(urlGetData) + "&src=typd&" + '' + "max_position=" + e_cursor

        headers = [
            ('Host', "twitter.com"),
            ('User-Agent', "Mozilla/5.0 (Windows NT 6.1; Win64; x64)"),
            ('Accept', "application/json, text/javascript, */*; q=0.01"),
            ('Accept-Language', "de,en-US;q=0.7,en;q=0.3"),
            ('X-Requested-With', "XMLHttpRequest"),
            ('Referer', url),
            ('Connection', "keep-alive")
        ]

        if proxy: opener = urllib.request.build_opener(urllib.request.ProxyHandler({'http': proxy, 'https': proxy}), urllib.request.HTTPCookieProcessor(cookieJar))
        else:
            opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookieJar))
        opener.addheaders = headers

        try:
            response = opener.open(url)
            jsonTweet = json.loads(response.read().decode())
        except:
            sys.exit()
            return

        return jsonTweet

    @staticmethod
    def getTweets(userName, csv, proxy=None):
        '''
        Get tweet information from twitter.com
        :param userName: the name of twitter account
        :param csv: the file to written in
        :param proxy: proxy of web
        :return: void
        '''
        e_cursor = ''
        e_cursor_previous = 'none'

        extractedFormattedTweetInfo = []
        cookieJar = http.cookiejar.CookieJar()

        while e_cursor != e_cursor_previous :
            # Pretend to be a human reading a html page and extract current page back in json
            jsonTweet = HtmlHandler.getJsonReponse(userName, e_cursor, cookieJar, proxy)
            if len(jsonTweet['items_html'].strip()) == 0:
                break

            # Control the cursor on the html
            e_cursor_previous = e_cursor
            e_cursor = jsonTweet['min_position']
            tweets = PyQuery(jsonTweet['items_html'])

            tweets.remove('div.withheld-tweet')
            tweets = tweets('div.js-stream-tweet')

            if len(tweets) == 0:
                break

            for tweetPiece in tweets:
                tweetPQ = PyQuery(tweetPiece)
                tweet = Tweet()

                # Filter correspoding information from html
                tweet.username = userName
                tweet.date = datetime.datetime.fromtimestamp(int(tweetPQ("small.time span.js-short-timestamp").attr("data-time")))
                tweet.tweetid = tweetPQ.attr("data-tweet-id")
                tweet.authorid = int(tweetPQ("a.js-user-profile-link").attr("data-user-id"))
                tweet.text = re.sub(r"\s+", " ", tweetPQ("p.js-tweet-text").text().replace('# ', '#').replace('@ ', '@'))
                tweet.retweets = int(tweetPQ("span.ProfileTweet-action--retweet span.ProfileTweet-actionCount").attr("data-tweet-stat-count").replace(",", ""))
                tweet.favorites = int(tweetPQ("span.ProfileTweet-action--favorite span.ProfileTweet-actionCount").attr("data-tweet-stat-count").replace(",", ""))
                tweet.mentions = " ".join(re.compile('(@\\w*)').findall(tweet.text))
                tweet.hashtags = " ".join(re.compile('(#\\w*)').findall(tweet.text))
                tweet.permalink = 'https://twitter.com' + tweetPQ.attr("data-permalink-path")
                if len(tweetPQ('span.Tweet-geo')) > 0:
                    tweet.geo = tweetPQ('span.Tweet-geo').attr('title')
                else:
                    tweet.geo = ''

                extractedFormattedTweetInfo.append(tweet)
                print(" Progress: ", end='')
                print(len(extractedFormattedTweetInfo), end='')
                print(" tweets extracted from html.", end='\r')

        # Write what extracted form html page into csv file
        HtmlHandler.writeToCSV(extractedFormattedTweetInfo, csv)


class Tweet:
    def __init__(self):
        pass