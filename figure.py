from matplotlib import pyplot as plt
import matplotlib
matplotlib.use('TkAgg')
from time import gmtime, strftime
import dbHandler
import numpy as np
import matplotlib.dates as mdates
import datetime

def draw_figure(improvements, a, b, c):
    plt.title("Retweet Prediction Performance")
    plt.xlabel("Improvement over baseline in percentage (%)")
    plt.ylabel("Number of users")
    plt.hist(improvements)
    plt.figtext(0.64, 0.85, 'No. of users: ', fontsize=8)
    plt.figtext(0.76, 0.85, a, fontsize=8)
    plt.figtext(0.64, 0.83, 'No. of folds: ', fontsize=8)
    plt.figtext(0.76, 0.83, b, fontsize=8)
    plt.figtext(0.64, 0.81, 'Average improvements: ', fontsize=8)
    plt.figtext(0.70, 0.79, c, fontsize=8)



    current_time = strftime("%Y%m%d %H%M%S", gmtime())


    plt.savefig("performance " + current_time + ".png")
    print("Picture 'performance " + current_time + ".png' saved")

    plt.clf()


if __name__ == '__main__':
    # Connect to mongodb
    db, connection = dbHandler.connectDB()

    users = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21]

    for user in users:
        user_tweets = list(db.retweetPrediction.find({"username": user}).sort([("date", 1)]))

        normalNumberofRetweets = []
        normalNumberofRetweetsHUBER = []
        retweets = []
        date = []
        for tweet in user_tweets:
            normalNumberofRetweets.append(tweet['normalNumberofRetweets'])
            normalNumberofRetweetsHUBER.append(tweet['normalNumberofRetweetsHUBER'])
            retweets.append(tweet['retweets'])
            date.append(datetime.datetime.strptime(tweet['date'], '%Y-%m-%d %H:%M'))

        normalNumberofRetweets = np.array(normalNumberofRetweets)
        normalNumberofRetweetsHUBER = np.array(normalNumberofRetweetsHUBER)
        retweets = np.array(retweets)
        date = np.array(date)

        fig = plt.figure()
        ax1 = fig.add_subplot(1, 1, 1)
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
        ax1.plot(date, retweets, 'g.',fillstyle='none')
        ax1.plot(date, normalNumberofRetweets, 'r.', label='Theil-Sen', markersize=2.0)
        ax1.plot(date, normalNumberofRetweetsHUBER, 'b.', label='Huber Loss', markersize=2.0)
        ax1.legend(loc='best', frameon=False)
        plt.title('User ' + str(user))
        plt.xlabel('date')
        plt.ylabel('Number of Retweets')
        fig.autofmt_xdate(rotation=45)
        # pylab.show()
        # manager = plt.get_current_fig_manager()
        # manager.frame.Maximize(True)
        plt.tight_layout()
        plt.savefig(str(user) + ".png")
        plt.clf()

    # Disconnect to mongodb
    dbHandler.closeDB(connection)