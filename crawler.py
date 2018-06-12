import sys
import getopt
import datetime
import codecs
import htmlHandler

def crawler(argv):

    if len(argv) == 0:
        print('Parameters required.')
        return

    userName = ''
    try:
        optlist, args = getopt.getopt(argv, "", ("username=", "near=", "within=", "since=", "until=", "querysearch=", "toptweets", "maxtweets=", "output="))
        for opt, arg in optlist:
            if opt == '--username':
                userName = arg

        # tweetCriteria = got.manager.TweetCriteria()
        outputFileName = "outpu_got.csv"

        outputFile = codecs.open(outputFileName, "w+", "utf-8")

        outputFile.write('username;date;retweets;favorites;text;geo;mentions;hashtags;id;permalink')

        print('Searching...\n')

        def receiveBuffer(tweets):
            for t in tweets:
                outputFile.write(('\n%s;%s;%d;%d;"%s";%s;%s;%s;"%s";%s' % (
                t.username, t.date.strftime("%Y-%m-%d %H:%M"), t.retweets, t.favorites, t.text, t.geo, t.mentions,
                t.hashtags, t.id, t.permalink)))
            outputFile.flush()
            print('More %d saved on file...\n' % len(tweets))

        htmlHandler.HtmlHandler().getTweets(userName, receiveBuffer)

    except:
        print('Arguments parser error, try -h' + arg)
    finally:
        outputFile.close()
        print('Done. Output file generated "%s".' % outputFileName)


if __name__ == '__main__':
    crawler(sys.argv[1:])