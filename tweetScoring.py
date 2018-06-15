# How to run: python tweetScoring.py


import dbHandler
import datetime


def preprocessing(db):
    # Remove tweets which retweets and favorites are not integer
    db.retweetPrediction.remove({"retweets": {"$type": 2}})
    db.retweetPrediction.remove({"favorites": {"$type": 2}})

    # Remove users whose number of tweets is less than 100
    twitter_users = list(db.retweetPrediction.find().distinct("username"))

    for user in twitter_users:
        user_tweets = list(db.retweetPrediction.find({"username": user}))
        if len(user_tweets) < 100:
            db.retweetPrediction.remove({"username": user})
            print(user + "was removed from database as the number of related tweets is less than 100")


def scoring(db):

    twitter_users = list(db.retweetPrediction.find().distinct("username"))

    for user in twitter_users:
        user_tweets = list(db.retweetPrediction.find({"username":user}).sort([("date", 1)]))

        if "score" in user_tweets[0]:
            print(user + "'s tweets has been scored before.")
        else:

            # For this user, get his median value of theilson regression slope and error value
            time_retweets_tuples = []
            for tweet in user_tweets:
                tweet['timeFloat'] = seconds_since_20060321(datetime.datetime.strptime(tweet['date'], '%Y-%m-%d %H:%M'))
                time_retweets_tuples.append((tweet['timeFloat'], tweet['retweets']))
            median_slope, median_error = theilsen(time_retweets_tuples)

            #
            tweet_count = 0
            for tweet in user_tweets:
                if tweet_count > 0:
                    tweet['timeSinceLastTweet'] = tweet['timeFloat'] - user_tweets[tweet_count - 1]['timeFloat']
                else:
                    tweet['timeSinceLastTweet'] = 0

                # Predict normal number of retweets by this time based on theilson regression
                tweet['normal'] = median_slope * tweet['timeFloat'] + median_error

                # Calculate score for this specific tweet based on predicted normal no. of retweets and real no. of retweets
                tweet['score'] = ((tweet['retweets'] - tweet['normal']) / tweet['normal']) * 100
                db.retweetPrediction.save(tweet)

                tweet_count = tweet_count + 1

            print("Saved scores for " + user)


def theilsen(timeRetweetsPair):
    median_slope = median([slope(i, j, timeRetweetsPair) for i in range(len(timeRetweetsPair)) for j in range(i)])
    median_error = median([random_error(i, timeRetweetsPair, median_slope) for i in range(len(timeRetweetsPair))])

    return median_slope, median_error


def slope(i, j, timeRetweetsPair):
    xi, yi = timeRetweetsPair[i]
    xj, yj = timeRetweetsPair[j]
    if xi - xj:
        return (yi - yj) / (xi - xj)
    else:
        return 0


def median(L):
    L.sort()
    if len(L) & 1:
        return L[len(L)//2]
    else:
        return (L[len(L)//2] + L[len(L)//2 + 1])/2


def random_error(i, timeRetweetsPair, median_value):
    x, y = timeRetweetsPair[i]
    return y - median_value * x


def seconds_since_20060321(dt):
  import datetime
  return (dt - datetime.datetime(2006, 3, 21)).total_seconds()


if __name__ == '__main__':
    db, connection = dbHandler.connectDB()
    preprocessing(db)
    scoring(db)
    dbHandler.closeDB(connection)