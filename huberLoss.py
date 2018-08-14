

import dbHandler
import gc
import numpy as np


# def huber_loss(m, b, x, y, dy, c=2):
#     y_fit = m * x + b
#     t = abs((y - y_fit) / dy)
#     flag = t > c
#     return np.sum((~flag) * (0.5 * t ** 2) - (flag) * c * (0.5 * c - t), -1)


def huber_loss(e, d):
    return (abs(e) <= d) * e ** 2 / 2 + (e > d) * d * (abs(e) - d / 2)


def scoring(db):
    '''
    Perform scoring on each tweet of each user in database
    :param db: the database to be processed
    :return: void
    '''
    twitter_users = list(db.retweetPrediction.find().distinct("username"))

    for user in twitter_users:
        print("•Start scoring for " + str(user))
        user_tweets = np.array(list(db.retweetPrediction.find({"username":user}).sort([("date", 1)])))

        if "normalNumberofRetweetsHUBER" in user_tweets[0]:
            print(str(user) + "'s tweets has been scored before.")
        else:
            for tweet in user_tweets:
                tweet['normalNumberofRetweetsHUBER'] = huber_loss(tweet['refTime'], tweet['TSslope'])
                db.retweetPrediction.save(tweet)
            print("Saved scores for " + str(user))


if __name__ == '__main__':
    db, connection = dbHandler.connectDB()
    gc.collect()
    scoring(db)
    dbHandler.closeDB(connection)