# python navigator.py -u taylorswift13 -a text mentions hashtags tweetlength timeoftweet frequency retweets favorites


import argparse
import dbHandler
import textScoring
import attributeScoring
import sys
import random
import numpy
import math
import figure


def get_parser():
    '''
    Get command line input arguments
    :return: parser
    '''
    # Get parser for command line arguments.
    parser = argparse.ArgumentParser(description="Text Scoring")
    parser.add_argument("-a",
                        "--attrs",
                        nargs='+',
                        dest="attributes")
    parser.add_argument("-k",
                        dest="noofcv")
    return parser


def builder(user, user_tweets, attrs):
    '''
    Build clfs for the user.
    :param user: the name of the user
    :param user_tweets: the tweets of the user
    :param attrs: the attributes to be considered
    :return: the clfs for the user
    '''
    tweet_pre_clf = {}
    tweet_pre_clf['user'] = user

    # Build clf for both text content and attribute content
    for attr in attrs:
        if attr == 'text': tweet_pre_clf[attr] = textScoring.createWordDictionary(user, user_tweets)
        else: tweet_pre_clf[attr] = attributeScoring.SVR(user_tweets, attr)

    return tweet_pre_clf


def weighter(tweet_pre_clf):
    '''
    Calculate the weight of each classifier
    :param tweet_pre_clf: each prediction classifier
    :return: weighted prediction classifier
    '''

    total_weight = 0

    # Calculate the total weight available for the user
    for k, v in tweet_pre_clf.items():
        if k != 'text' and k is not 'user':
            total_weight = total_weight + v['std']

    # Calculate each clf's weight among all the clfs
    for k, v in tweet_pre_clf.items():
        if k != 'text' and k is not 'user':
            v['weight'] = v['std'] / total_weight

    weighted_tweet_pre_clf = tweet_pre_clf

    return weighted_tweet_pre_clf


def predictor(tweet, weighted_tweet_pre_clf):
    '''
    A predictor that using a score to represent the success of a tweet
    :param tweet: the tweet to be tested
    :param weighted_tweet_pre_clf: weighted tweet prediction classifiers
    :return: weighted tweet prediction classifiers
    '''
    pred_score = 0

    text_score = textScoring.tweetScoring(str(tweet['text']), weighted_tweet_pre_clf['text'])
    attrs_score = attributeScoring.tweetScoring(tweet, weighted_tweet_pre_clf)

    pred_score = text_score + attrs_score

    return pred_score


def cross_validation(noofcv, user, user_tweets):
    '''
    K-fold cross validation function
    :param noofcv: number of fold
    :param user: the user being processed
    :param user_tweets: the tweets to be processed
    :return: improvement value
    '''
    K = int(noofcv)
    base = numpy.random.permutation(user_tweets)
    folds = []
    outputs = []
    for i in range(K):
        folds.append([])
    foldSize = math.ceil(len(user_tweets) / K);
    index_to_delete = list(range(foldSize))
    for i in range(K - 1):
        folds[i] = base[0:foldSize]
        base = numpy.delete(base, index_to_delete)
    folds[K - 1] = base

    # Create training and testing set during each iteration
    # Then using training set to train clfs, using testing and trained clfs to get prediction
    # Finally compare prediction with the actual score

    baseline_ses = []
    pred_ses = []

    for i in range(K):
        training = user_tweets
        training = list(filter(lambda a: a not in folds[i], training))
        testing = folds[i]

        tweet_pre_clf = builder(user, training, args.attributes)
        weighted_tweet_pre_clf = weighter(tweet_pre_clf)

        for tweet in testing:
            actual_score = tweet['score']
            pred_score = predictor(tweet, weighted_tweet_pre_clf)

            baseline_ses.append(actual_score ** 2)
            pred_ses.append((actual_score - pred_score) ** 2)

    baseline_mse = numpy.mean(baseline_ses)
    pred_mse = numpy.mean(pred_ses)

    improvement = abs(baseline_mse - pred_mse) / baseline_mse * 100

    return improvement


def evaluation():



if __name__ == '__main__':
    # Get commandline arguments
    parser = get_parser()
    args = parser.parse_args()

    # Connect to mongodb
    db, connection = dbHandler.connectDB()

    users = list(db.retweetPrediction.find().distinct("username"))
    # users = ["taylorswift13"]
    improvements = []
    for user in users:
        print("• Building classifiers and performing cross validation for user: " + user)
        user_tweets = list(db.retweetPrediction.find({"username": user}).sort([("date", 1)]))
        # # Build prediction classifiers for the user
        # tweet_pre_clf = builder(args.user, user_tweets, args.attributes)
        #
        # # Calculate the weight of each classifier
        # weighted_tweet_pre_clf = weighter(tweet_pre_clf)

        # Evaluation
        # Process k-fold cross validation
        # Split dataset into K folds
        improvement = cross_validation(args.noofcv, user, user_tweets)
        improvements.append(improvement)
        print("  Processing of " + user + " finished")

    figure.draw_figure(improvements, len(users), args.noofcv, numpy.mean(improvements))

    # Disconnect to mongodb
    dbHandler.closeDB(connection)