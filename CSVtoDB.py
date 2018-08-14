# How to run: python CSVtoDB.py (name(s) of csv file(s)) 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21
# mongoimport --db tweets --collection retweetPrediction --type csv --headerline --file 'Cristiano.csv'

import subprocess
import sys
import dbChecker


def mongoimport(filename):
    """ Imports a csv file at path csv_name to a mongo colection
    returns: count of the documants in the new collection
    """

    csv_path = '/Users/cheng/Documents/Dropbox/404Error/Academic/UoM/University/Academic Year/COMP66060 Masters Project/Twitter-Retweet-Prediction/' + filename + '.csv'

    subprocess.Popen(['mongoimport', '--db', 'tweets', '--collection', 'retweetPrediction', '--type', 'csv', '--headerline', '--file', csv_path], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)


if __name__ == '__main__':
    names = sys.argv[1:]

    dbChecker.checker()

    for name in names:
        mongoimport(name)

    dbChecker.checker()