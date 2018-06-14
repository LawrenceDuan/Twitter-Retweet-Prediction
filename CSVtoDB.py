# How to run: python CSVtoDB.py (name(s) of csv file(s))

import subprocess
import sys


def mongoimport(filename):
    """ Imports a csv file at path csv_name to a mongo colection
    returns: count of the documants in the new collection
    """

    csv_path = '/Users/cheng/Documents/Dropbox/404Error/Academic/UoM/University/Academic Year/COMP66060 Masters Project/Twitter-Retweet-Prediction/' + filename

    subprocess.Popen(['mongoimport', '--db', 'tweets', '--collection', 'retweetPrediction', '--type', 'csv', '--headerline', '--file', csv_path], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)


if __name__ == '__main__':
    names = sys.argv[1:]
    for name in names:
        mongoimport(name)