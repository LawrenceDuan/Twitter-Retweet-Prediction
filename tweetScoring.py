# How to run: python tweetScoring.py


import dbHandler
import datetime
import gc
import numpy

def preprocessing(db):
    '''
    Processing preprocessing on data stored in mongodb
    :param db: the database to be processed
    :return: void
    '''
    # Remove tweets which retweets and favorites are not integer
    db.retweetPrediction.remove({"retweets": {"$type": 2}})
    db.retweetPrediction.remove({"favorites": {"$type": 2}})

    # Remove tweets which text is not string
    db.retweetPrediciton.remove({"text": {"$not": {"$type": 2}}})

    # Remove users whose number of tweets is less than 100
    twitter_users = list(db.retweetPrediction.find().distinct("username"))

    for user in twitter_users:
        user_tweets = list(db.retweetPrediction.find({"username": user}))
        if len(user_tweets) < 100:
            db.retweetPrediction.remove({"username": user})
            print(user + "was removed from database as the number of related tweets is less than 100")


def scoring(db):
    '''
    Perform scoring on each tweet of each user in database
    :param db: the database to be processed
    :return: void
    '''
    twitter_users = list(db.retweetPrediction.find().distinct("username"))

    for user in twitter_users:
        print("•Start scoring for " + str(user))
        user_tweets = numpy.array(list(db.retweetPrediction.find({"username":user}).sort([("date", 1)])))

        if "score" in user_tweets[0]:
            print(str(user) + "'s tweets has been scored before.")
        else:

            # For this user, get his median value of theilson regression slope and error value
            median_slope, median_error = scoring_step_1(user_tweets)
            scoring_step_2(user_tweets, median_slope, median_error)

            print("Saved scores for " + str(user))


def scoring_step_1(user_tweets):
    time_retweets_tuples = []
    for tweet in user_tweets:
        tweet['refTime'] = seconds_since_20060321(datetime.datetime.strptime(tweet['date'], '%Y-%m-%d %H:%M'))
        time_retweets_tuples.append((tweet['refTime'], tweet['retweets']))
    median_slope, median_error = theilsen(time_retweets_tuples)

    return median_slope, median_error


def scoring_step_2(user_tweets, median_slope, median_error):
    tweet_count = 0
    for tweet in user_tweets:
        tweet['TSslope'] = median_slope
        tweet['TSerror'] = median_error

        if tweet_count > 0:
            tweet['frequency'] = tweet['refTime'] - user_tweets[tweet_count - 1]['refTime']
        else:
            tweet['frequency'] = 0

        # Predict normal number of retweets by this time based on theilson regression
        tweet['normalNumberofRetweets'] = round(median_slope * tweet['refTime'] + median_error, 2)
        # print(tweet['normalNumberofRetweets'])

        # Calculate score for this specific tweet based on predicted normal no. of retweets and real no. of retweets
        if tweet['normalNumberofRetweets'] == 0.0:
            tweet['score'] = tweet['retweets']
        else:
            tweet['score'] = round(((tweet['retweets'] - tweet['normalNumberofRetweets']) / tweet['normalNumberofRetweets']) * 100, 2)

        if tweet['score'] > 0:
            tweet['success'] = 0
        else:
            tweet['success'] = 1

        db.retweetPrediction.save(tweet)

        tweet_count = tweet_count + 1

def theilsen(timeRetweetsPair):
    '''
    Implementation of theilsen algorithm
    :param timeRetweetsPair: pair data in the form of (refTime, retweets)
    :return: median slope value and median error value
    '''
    median_slope = median([slope(i, j, timeRetweetsPair) for i in range(len(timeRetweetsPair)) for j in range(i)])
    median_error = median([random_error(i, timeRetweetsPair, median_slope) for i in range(len(timeRetweetsPair))])

    return median_slope, median_error


def slope(i, j, timeRetweetsPair):
    '''
    Helper function of theilsen. Calculate slope value for a pair of value.
    :param i: iterate helper
    :param j: iterate helper
    :param timeRetweetsPair: pair data in the form of (refTime, retweets)
    :return: slope value
    '''
    xi, yi = timeRetweetsPair[i]
    xj, yj = timeRetweetsPair[j]
    if xi - xj:
        return (yi - yj) / (xi - xj)
    else:
        return 0


def median(L):
    '''
    Helper function of theilsen. Get median value of a list of values.
    :param L:
    :return:
    '''
    L.sort()
    if len(L) & 1:
        return L[len(L)//2]
    else:
        return (L[len(L)//2] + L[len(L)//2 + 1])/2


def random_error(i, timeRetweetsPair, median_value):
    '''
    Helper function of theilsen. Calculate random error value.
    :param i: iterate value
    :param timeRetweetsPair: pair data in the form of (refTime, retweets)
    :param median_value: the value of median slope
    :return: random error value
    '''
    x, y = timeRetweetsPair[i]
    return y - median_value * x


def seconds_since_20060321(dt):
    '''
    Helper function of scoring. Help calculate refTime value. The twitter is found on 21/03/2006. No twitter will older than that date.
    :param dt: date of a tweet
    :return: refTime value.
    '''
    return (dt - datetime.datetime(2006, 3, 21)).total_seconds()


if __name__ == '__main__':
    db, connection = dbHandler.connectDB()
    preprocessing(db)
    scoring(db)
    dbHandler.closeDB(connection)