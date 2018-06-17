import argparse
import dbHandler
import numpy
import re


def get_parser():
    '''
    Get command line input arguments
    :return: parser
    '''
    # Get parser for command line arguments.
    parser = argparse.ArgumentParser(description="Text Scoring")
    parser.add_argument("-u",
                        "--user",
                        dest="user")
    parser.add_argument("-t",
                        "--tweet",
                        dest="tweet")
    return parser


def createWordDictionary(user, user_tweets):
    scoreCollection, dictionary = {}

    for tweet in user_tweets:
        for word in wordsin(tweet['text']):
            if word in scoreCollection: scoreCollection[word].append(tweet['score'])
            else: scoreCollection[word] = [tweet['score']]

    for word in scoreCollection:
        dictionary[word] = word
        dictionary[word] = numpy.mean(scoreCollection[word])

    print("•" + user + "'s dictionary created!")

    descending_sorted_dictionary = sorted(dictionary.items(), reverse=True, key=lambda elem: elem[1])

    return descending_sorted_dictionary


def wordsin(tweet):
    nonPicTexts = []
    texts = tweet.split(' ')

    for word in texts:
        pureCharacters = re.sub('[^A-Za-z0-9]+', '', word.lower())

        if pureCharacters[:4] != 'http': nonPicTexts.append(pureCharacters)

    return nonPicTexts


def tweetScoring(tweet, dictionary):
    scoreList = []

    for word in wordsin(tweet):
        if word in dictionary: scoreList.append(dictionary[word])
        else: scoreList.append(0)

    if scoreList == []: score = 0
    else: score = numpy.mean(scoreList)

    return score


if __name__ == "__main__":
    # Get commandline arguments
    parser = get_parser()
    args = parser.parse_args()

    # Connect to mongodb
    db, connection = dbHandler.connectDB()

    # Get users's tweets for text scoring
    users = list(db.retweetPrediction.find().distinct("username"))
    for user in users:
        user_tweets = list(db.retweetPrediction.find({"username": user}).sort([("date", 1)]))

        # Create word dictionary for the user
        descending_sorted_dictionary = createWordDictionary(user, user_tweets)

        # Calculating a new tweet's score
        score = tweetScoring(args.tweet, descending_sorted_dictionary)

        print 

    # Disconnect to mongodb
    dbHandler.closeDB(connection)