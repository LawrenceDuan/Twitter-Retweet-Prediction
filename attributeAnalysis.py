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


def SVR(user_tweets, attr):
    x_train, y_train = trainingPrep(user_tweets, attr)

    clf = sklearn.svm.SVR(C=1e3, gamma=5e-10, kernel='rbf')
    y_pred = clf.fit(x_train, y_train).predict(x_train)




def trainingPrep(user_tweets, attr):

    attrValue_score_tuples = []

    for tweet in user_tweets:
        attrValue_score_tuples.append((attrValue(tweet, attr), tweet['score']))

    attrValue_score_tuples = sorted(attrValue_score_tuples, reverse=False, key=lambda elem: elem[0])

    x_train = []
    y_train = []

    for tuple in attrValue_score_tuples:
        x_train.append([tuple[0]])
        y_train.append(tuple[1])

    return numpy.array(x_train), numpy.array(y_train)


if __name__ == "__main__":
    db, connection = dbHandler.connectDB()
    user_tweets = list(db.myCollection.find())

    test = trainingPrep(user_tweets, 'retweets')

    print(test[0][1])

    dbHandler.closeDB(connection)