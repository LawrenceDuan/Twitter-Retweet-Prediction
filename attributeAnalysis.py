import numpy
import sklearn.svm
import dbHandler
import datetime


def attrValue(tweet, attr):
    if attr == 'mentions':
        return len(tweet['mentions'].split(' '))
    elif attr == 'hashtags':
        return len(tweet['hashtags'].split(' '))
    elif attr == 'tweetlength':
        return len(tweet['text'].split(' '))
    elif attr == 'timeoftweet':
        time = datetime.datetime.strptime(tweet['date'], "%Y-%m-%d %H:%M")
        return time.hour * 3600 + time.minute * 60 + time.second
    elif attr == 'frequency':
        return tweet['frequency']
    elif attr == 'retweets':
        return tweet['retweets']
    elif attr == 'favorites':
        return tweet['favorites']


def model(tweets, attr):
    tuples = []
    


if __name__ == "__main__":
    db, connection = dbHandler.connectDB()
    user_tweets = list(db.myCollection.find())

    for tweet in user_tweets:
        test = attributeValue(tweet, attribute='tweetlength')

        print(str(test)+'---'+tweet['text'])

    dbHandler.closeDB(connection)