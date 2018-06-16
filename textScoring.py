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

    return dictionary


def wordsin(tweet):
    nonPicTexts = []
    texts = tweet.split(' ')

    for word in texts:
        pureCharacters = re.sub('[^A-Za-z0-9]+', '', word.lower())

        if pureCharacters[:4] != 'http': nonPicTexts.append(pureCharacters)

    return nonPicTexts


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
        dictionary = createWordDictionary(user, user_tweets)

    # Disconnect to mongodb
    dbHandler.closeDB(connection)