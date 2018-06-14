import sys
import getopt
import codecs
import htmlHandler


def crawler(name):

    userName = name
    try:
        outputFileName = userName + ".csv"
        outputFile = codecs.open(outputFileName, "w+", "utf-8")
        outputFile.write('username;date;retweets;favorites;text;geo;mentions;hashtags;id;permalink')
        print("•Start crawling " + userName + "'s tweets!")

        def receiveBuffer(tweets):
            for t in tweets:
                outputFile.write(('\n%s;%s;%d;%d;"%s";%s;%s;%s;"%s";%s' % (t.username,
                                                                           t.date.strftime("%Y-%m-%d %H:%M"),
                                                                           t.retweets,
                                                                           t.favorites,
                                                                           t.text,
                                                                           t.geo,
                                                                           t.mentions,
                                                                           t.hashtags,
                                                                           t.id,
                                                                           t.permalink)))
            outputFile.flush()
            print(len(tweets), end='')
            print(" tweets crawled and saved.")

        htmlHandler.HtmlHandler().getTweets(userName, receiveBuffer)

    except:
        print('Error occurred, please re-run!')
    finally:
        outputFile.close()
        print('Output file generated "%s".' % outputFileName)
        print('--------------------------------------------------')


if __name__ == '__main__':

    # optlist, args = getopt.getopt(sys.argv[1:], "", (
    # "username=", "near=", "within=", "since=", "until=", "querysearch=", "toptweets", "maxtweets=", "output="))
    # for opt, arg in optlist:
    #     if opt == '--username':
    #         userName = arg

    if len(sys.argv[1:]) == 0:
        print('Names required.')
    else:
        name_list = sys.argv[1:]

        for name in name_list:
            crawler(name)