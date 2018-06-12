import urllib.request
import urllib.parse
import urllib.error
import urllib.request
import urllib.error
import urllib.parse
import json
import re
import datetime
import sys
import http.cookiejar
from pyquery import PyQuery


class HtmlHandler:

    def __init__(self):
        pass

    @staticmethod
    def getJsonReponse(userName, refreshCursor, cookieJar, proxy):
        urlGetData = ' from:' + userName
        url = "https://twitter.com/i/search/timeline?f=tweets&q=" + urllib.parse.quote(urlGetData) + "&src=typd&" + '' + "max_position=" + refreshCursor

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
    def getTweets(userName, receiveBuffer=None, bufferLength=100, proxy=None):
        refreshCursor = ''

        results = []
        resultsAux = []
        cookieJar = http.cookiejar.CookieJar()

        active = True

        while active:
            jsonTweet = HtmlHandler.getJsonReponse(userName, refreshCursor, cookieJar, proxy)
            if len(jsonTweet['items_html'].strip()) == 0:
                break

            refreshCursor = jsonTweet['min_position']
            tweets = PyQuery(jsonTweet['items_html'])
            # Remove incomplete tweets withheld by Twitter Guidelines
            tweets.remove('div.withheld-tweet')
            tweets = tweets('div.js-stream-tweet')

            if len(tweets) == 0:
                break

            for tweetHTML in tweets:
                tweetPQ = PyQuery(tweetHTML)
                tweet = Tweet()

                usernameTweet = tweetPQ("span.username.js-action-profile-name b").text()
                txt = re.sub(r"\s+", " ", tweetPQ("p.js-tweet-text").text().replace('# ', '#').replace('@ ', '@'))
                retweets = int(tweetPQ("span.ProfileTweet-action--retweet span.ProfileTweet-actionCount").attr(
                    "data-tweet-stat-count").replace(",", ""))
                favorites = int(tweetPQ("span.ProfileTweet-action--favorite span.ProfileTweet-actionCount").attr(
                    "data-tweet-stat-count").replace(",", ""))
                dateSec = int(tweetPQ("small.time span.js-short-timestamp").attr("data-time"))
                id = tweetPQ.attr("data-tweet-id")
                permalink = tweetPQ.attr("data-permalink-path")
                user_id = int(tweetPQ("a.js-user-profile-link").attr("data-user-id"))
                geo = ''
                geoSpan = tweetPQ('span.Tweet-geo')
                if len(geoSpan) > 0:
                    geo = geoSpan.attr('title')
                urls = []
                for link in tweetPQ("a"):
                    try:
                        urls.append((link.attrib["data-expanded-url"]))
                    except KeyError:
                        pass

                tweet.id = id
                tweet.permalink = 'https://twitter.com' + permalink
                tweet.username = usernameTweet
                tweet.text = txt
                tweet.date = datetime.datetime.fromtimestamp(dateSec)
                tweet.formatted_date = datetime.datetime.fromtimestamp(dateSec).strftime("%a %b %d %X +0000 %Y")
                tweet.retweets = retweets
                tweet.favorites = favorites
                tweet.mentions = " ".join(re.compile('(@\\w*)').findall(tweet.text))
                tweet.hashtags = " ".join(re.compile('(#\\w*)').findall(tweet.text))
                tweet.geo = geo
                tweet.urls = ",".join(urls)
                tweet.author_id = user_id

                results.append(tweet)
                resultsAux.append(tweet)

                if receiveBuffer and len(resultsAux) >= bufferLength:
                    receiveBuffer(resultsAux)
                    resultsAux = []

        if receiveBuffer and len(resultsAux) > 0:
            receiveBuffer(resultsAux)

        return results


class Tweet:

    def __init__(self):
        pass
