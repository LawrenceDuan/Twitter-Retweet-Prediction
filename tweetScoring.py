import argparse
import pymongo
import functions
import datetime


def database_connection():
    connection = pymongo.MongoClient('mongodb://127.0.0.1:27017')
    db = connection['tweets']

    return db


def scoring(db):

    users = list(db.retweetPrediction.find().distinct("username"))

    for user in users:

        tweets = list(db.retweetPrediction.find({"username":user}).sort('date'))

        if "score" in tweets[0]:
            print ("Skipping over " + user)
        else:
            if len(tweets) < 50:
                db.retweetPrediction.remove({"username": user})
                print ("Removed " + user + " from database")
                break

            time_retweets_tuples = []
            for tweet in tweets:
                tweet['timeFloat'] = functions.time_to_float(datetime.datetime.strptime(tweet['date'], '%Y-%m-%d %H:%M'))
                time_retweets_tuples.append((tweet['timeFloat'], tweet['retweets']))

            m, b = functions.theilsen(time_retweets_tuples)

            i = 0
            for tweet in tweets:
                tweet['timeFloat'] = functions.time_to_float(datetime.datetime.strptime(tweet['date'], '%Y-%m-%d %H:%M'))
                if i > 0:
                    tweet['timeSinceLastTweet'] = tweet['timeFloat'] - tweets[i - 1]['timeFloat']
                i += 1
                tweet['normal'] = m * tweet['timeFloat'] + b
                try:
                    tweet['score'] = ((tweet['retweets'] - tweet['normal']) / tweet['normal']) * 100
                    db.retweetPrediction.save(tweet)
                except:
                    db.retweetPrediction.remove({"username": user})
                    print ("Removed " + user + " from database")
                    break

            print ("Saved scores for " + user)


if __name__ == '__main__':
    db = database_connection()
    scoring(db)