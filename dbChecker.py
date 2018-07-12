import dbHandler


def checker():
    # Connect to mongodb
    db, connection = dbHandler.connectDB()

    # Show which users' tweets in the db
    print("• Users that the db contains: ")
    twitter_users = list(db.retweetPrediction.find().distinct("username"))
    twitter_users.sort()

    print(twitter_users, end=' -- ')
    print(len(twitter_users))

    # Disconnect to mongodb
    dbHandler.closeDB(connection)


if __name__ == '__main__':
    checker()