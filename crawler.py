# How to run: python crawler.py (name(s) of twitter account(s))

import sys
import codecs
import htmlHandler


def crawler(name):
    '''
    Crawling tweet information by pretending a human who is surfing through a website.
    :param name: name of the twitter account to be crawled
    :return: void
    '''
    userName = name

    csvName = userName + ".csv"
    csv = codecs.open(csvName, "w+", "utf-8")

    # Write headers to csv file first
    csv.write('username;date;tweetid;authorid;text;retweets;favorites;mentions;hashtags;permalink;geo')
    print("•Start crawling " + userName + "'s tweets!")

    htmlHandler.HtmlHandler().getTweets(userName, csv)

    csv.close()
    print(' File: ', end='')
    print('csv file generated "%s".' % csvName)
    print('--------------------------------------------------')


if __name__ == '__main__':

    if len(sys.argv[1:]) == 0:
        print('Names required.')
    else:
        name_list = sys.argv[1:]

        for name in name_list:
            crawler(name)