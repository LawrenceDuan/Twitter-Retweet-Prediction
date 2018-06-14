import dbHandler
import functions
import datetime


def scoring(db):

    twitter_users = list(db.retweetPrediction.find().distinct("username"))

    for user in twitter_users:
        user_tweets = list(db.retweetPrediction.find({"username":user}).sort([("date",1)]))

        if "score" in user_tweets[0]:
            print (user + "'s tweets has been scored before.")
        else:
            if len(user_tweets) < 100:
                db.retweetPrediction.remove({"username": user})
                print (user + "was removed from database as the number of related tweets is less than 100")
                break

            time_retweets_tuples = []
            for tweet in user_tweets:
                tweet['timeFloat'] = functions.time_to_float(datetime.datetime.strptime(tweet['date'], '%Y-%m-%d %H:%M'))
                time_retweets_tuples.append((tweet['timeFloat'], tweet['retweets']))

            m, b = functions.theilsen(time_retweets_tuples)

            i = 0
            for tweet in user_tweets:
                tweet['timeFloat'] = functions.time_to_float(datetime.datetime.strptime(tweet['date'], '%Y-%m-%d %H:%M'))
                if i > 0:
                    tweet['timeSinceLastTweet'] = tweet['timeFloat'] - user_tweets[i - 1]['timeFloat']
                i += 1
                tweet['normal'] = m * tweet['timeFloat'] + b
                try:
                    tweet['score'] = ((tweet['retweets'] - tweet['normal']) / tweet['normal']) * 100
                    db.retweetPrediction.save(tweet)
                except:
                    db.retweetPrediction.remove({"username": user})
                    print ("Removed " + user + " from database")
                    break

            print ("Saved scores for " + user)


if __name__ == '__main__':
    db, connection = dbHandler.connectDB()
    scoring(db)
    dbHandler.closeDB(connection)