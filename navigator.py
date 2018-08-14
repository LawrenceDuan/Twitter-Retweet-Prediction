# python navigator.py -a text mentions hashtags tweetlength timeoftweet frequency retweets favorites -k 10


import argparse
import dbHandler
import textScoring
import attributeScoring
import sys
import random
import numpy
import math
import figure
import time


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


def builder(user, user_tweets, attrs, db):
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
        else: tweet_pre_clf[attr] = attributeScoring.SVR(user_tweets, attr, db)

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

    pred_score_on_text = textScoring.tweetScoring(str(tweet['text']), weighted_tweet_pre_clf['text'])
    pred_score_on_attrs = attributeScoring.tweetScoring(tweet, weighted_tweet_pre_clf)

    return pred_score_on_text, pred_score_on_attrs


def cross_validation(noofcv, user, user_tweets, db):
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
    targets = []
    predicts_on_text = []
    predicts_on_attrs = []

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
    pred_on_text_ses = []
    pred_on_attrs_ses = []

    for i in range(K):
        training = user_tweets
        training = list(filter(lambda a: a not in folds[i], training))
        testing = folds[i]

        tweet_pre_clf = builder(user, training, args.attributes, db)
        weighted_tweet_pre_clf = weighter(tweet_pre_clf)

        for tweet in testing:
            actual_score = tweet['score']
            pred_score_on_text, pred_score_on_attrs = predictor(tweet, weighted_tweet_pre_clf)

            targets.append(actual_score)
            predicts_on_text.append(pred_score_on_text)
            predicts_on_attrs.append(pred_score_on_attrs)

            baseline_ses.append(actual_score ** 2)
            pred_on_text_ses.append((actual_score - pred_score_on_text) ** 2)
            pred_on_attrs_ses.append((actual_score - pred_score_on_attrs) ** 2)

    baseline_mse = numpy.mean(baseline_ses)
    pred_on_text_mse = numpy.mean(pred_on_text_ses)
    pred_on_attrs_mse = numpy.mean(pred_on_attrs_ses)

    improvement_on_text = (baseline_mse - pred_on_text_mse) / baseline_mse * 100
    improvement_on_attrs = (baseline_mse - pred_on_attrs_mse) / baseline_mse * 100

    return improvement_on_text, improvement_on_attrs


# def evaluation(targets, predicts):
#     confusion_matrix = numpy.zeros([11,11])
#
#     normalized_targets = []
#     normalized_predicts = []
#     # Data normalisation
#     for i in range(len(targets) - 1):
#         normalized_target = int((targets[i] - min(targets)) / (max(targets) - min(targets)) * 100)
#         if normalized_target >= 0 and normalized_target <= 5:
#             normalized_targets.append(0)
#         elif normalized_target > 5 and normalized_target <= 15:
#             normalized_targets.append(10)
#         elif normalized_target > 15 and normalized_target <= 25:
#             normalized_targets.append(20)
#         elif normalized_target > 25 and normalized_target <= 35:
#             normalized_targets.append(30)
#         elif normalized_target > 35 and normalized_target <= 45:
#             normalized_targets.append(40)
#         elif normalized_target > 45 and normalized_target <= 55:
#             normalized_targets.append(50)
#         elif normalized_target > 55 and normalized_target <= 65:
#             normalized_targets.append(60)
#         elif normalized_target > 65 and normalized_target <= 75:
#             normalized_targets.append(70)
#         elif normalized_target > 75 and normalized_target <= 85:
#             normalized_targets.append(80)
#         elif normalized_target > 85 and normalized_target <= 95:
#             normalized_targets.append(90)
#         elif normalized_target > 95 and normalized_target <= 100:
#             normalized_targets.append(100)
#
#         normalized_predict = int((predicts[i] - min(predicts)) / (max(predicts) - min(predicts)) * 100)
#         if normalized_predict >= 0 and normalized_predict <= 5:
#             normalized_predicts.append(0)
#         elif normalized_predict > 5 and normalized_predict <= 15:
#             normalized_predicts.append(10)
#         elif normalized_predict > 15 and normalized_predict <= 25:
#             normalized_predicts.append(20)
#         elif normalized_predict > 25 and normalized_predict <= 35:
#             normalized_predicts.append(30)
#         elif normalized_predict > 35 and normalized_predict <= 45:
#             normalized_predicts.append(40)
#         elif normalized_predict > 45 and normalized_predict <= 55:
#             normalized_predicts.append(50)
#         elif normalized_predict > 55 and normalized_predict <= 65:
#             normalized_predicts.append(60)
#         elif normalized_predict > 65 and normalized_predict <= 75:
#             normalized_predicts.append(70)
#         elif normalized_predict > 75 and normalized_predict <= 85:
#             normalized_predicts.append(80)
#         elif normalized_predict > 85 and normalized_predict <= 95:
#             normalized_predicts.append(90)
#         elif normalized_predict > 95 and normalized_predict <= 100:
#             normalized_predicts.append(100)
#
#     # print(len(normalized_targets), len(normalized_predicts))
#
#     for i in range(len(targets) - 1):
#         print(int(normalized_targets[i]/10), int(normalized_predicts[i]/10), i)
#         confusion_matrix[int(normalized_targets[i]/10), int(normalized_predicts[i]/10)] = confusion_matrix[int(normalized_targets[i]/10), int(normalized_predicts[i]/10)] + 1
#
#     print(confusion_matrix)


if __name__ == '__main__':
    start = time.time()

    # Get commandline arguments
    parser = get_parser()
    args = parser.parse_args()

    # Connect to mongodb
    db, connection = dbHandler.connectDB()

    # users = list(db.retweetPrediction.find().distinct("username"))
    users = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21]
    # users = [19]
    improvements_on_text = []
    improvements_on_attrs = []

    for user in users:
        print("• Building classifiers and performing cross validation for user: " + str(user))
        user_tweets = list(db.retweetPrediction.find({"username": user}).sort([("date", 1)]))
        # # Build prediction classifiers for the user
        tweet_pre_clf = builder(user, user_tweets, args.attributes, db)
        #
        # # Calculate the weight of each classifier
        weighted_tweet_pre_clf = weighter(tweet_pre_clf)

        # Evaluation
        # Process k-fold cross validation
        # Split dataset into K folds
        improvement_on_text, improvement_on_attrs = cross_validation(args.noofcv, user, user_tweets, db)
        improvements_on_text.append(improvement_on_text)
        improvements_on_attrs.append(improvement_on_attrs)
        print("  Processing of " + str(user) + " finished ----- ", end="")
        end = time.time()
        print(str(end - start) + " seconds so far.")

       # evaluation(targets, predicts)

    figure.draw_figure(improvements_on_text, len(users), args.noofcv, numpy.mean(improvements_on_text))
    sys.sleep(1)
    figure.draw_figure(improvements_on_attrs, len(users), args.noofcv, numpy.mean(improvements_on_attrs))

    print(improvements_on_text, improvements_on_attrs)

    # Disconnect to mongodb
    dbHandler.closeDB(connection)

    end = time.time()
    print(str(end - start) + " in total.")