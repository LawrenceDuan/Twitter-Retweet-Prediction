# How to run: python attributeScoring.py


import numpy
import sklearn.svm
import dbHandler
import datetime


def attrValue(tweet, attr):
    '''
    Get the value of the attribute of the tweet
    :param tweet: the tweet to be processed
    :param attr: the attribute to be considered
    :return: the value of the attribute
    '''
    if attr == 'mentions':
        return len(tweet['mentions'].split(' '))
    elif attr == 'hashtags':
        return len(tweet['hashtags'].split(' '))
    elif attr == 'tweetlength':
        return len(str(tweet['text']).split(' '))
    elif attr == 'timeoftweet':
        time = datetime.datetime.strptime(tweet['date'], "%Y-%m-%d %H:%M")
        return time.hour * 3600 + time.minute * 60 + time.second
    elif attr == 'frequency':
        return tweet['frequency']
    elif attr == 'retweets':
        return tweet['retweets']
    elif attr == 'favorites':
        return tweet['favorites']


def SVR(user_tweets, attr):
    '''
    Creating SVR models that required.
    :param user_tweets: the tweets to be processed
    :param attr: the attribute to be considered
    :return: SVR model
    '''
    SVR = {}
    x_train, y_train = trainingPrep(user_tweets, attr)

    # Creating SVR classifier
    clf = sklearn.svm.SVR(C=1e3, gamma=5e-10, kernel='rbf')
    y_pred = clf.fit(x_train, y_train).predict(x_train)

    # Creating SVR model
    SVR['clf'] = (x_train, y_pred)
    SVR['std'] = numpy.std(y_pred)

    return SVR


def trainingPrep(user_tweets, attr):
    '''
    Helper function for preparing training data.
    :param user_tweets: tweets to be processed
    :param attr: the attribute to be processed
    :return: prepared training data
    '''
    attrValue_score_tuples = []

    for tweet in user_tweets:
        attrValue_score_tuples.append((attrValue(tweet, attr), tweet['score']))

    attrValue_score_tuples = sorted(attrValue_score_tuples, reverse=False, key=lambda elem: elem[0])

    # Creating training data
    x_train = []
    y_train = []

    for tuple in attrValue_score_tuples:
        x_train.append([tuple[0]])
        y_train.append(tuple[1])

    return numpy.array(x_train), numpy.array(y_train)


def tweetScoring(tweet, weighted_tweet_pre_clf):
    '''
    Calculate tweet scoring based on tweet's attributes
    :param tweet: the tweet to be processed
    :param weighted_tweet_pre_clf: the clfs
    :return: the calculated score
    '''
    score = 0

    for k, v in weighted_tweet_pre_clf.items():
        if k != 'text' and k is not 'user':
            attr_value = weighted_tweet_pre_clf[k]['clf'][0]
            pre_tweet_score = weighted_tweet_pre_clf[k]['clf'][1]

            xp = []
            for x in attr_value:
                xp.append(x[0])
            fp = list(pre_tweet_score)

            unweighted_score = numpy.interp(attrValue(tweet, k), xp, fp)
            weighted_score = unweighted_score * weighted_tweet_pre_clf[k]['weight']
            score = score + weighted_score

    return score


if __name__ == "__main__":
    # Connect to mongodb
    db, connection = dbHandler.connectDB()
    user_tweets = list(db.myCollection.find())

    test = SVR(user_tweets, 'retweets')

    print(test)

    # Disconnect to mongodb
    dbHandler.closeDB(connection)