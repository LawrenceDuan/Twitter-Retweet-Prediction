import dbHandler

if __name__ == '__main__':
    # Connect to mongodb
    db, connection = dbHandler.connectDB()

    # Show which users' tweets in the db
    print("• Users that the db contains: ", end='')
    twitter_users = list(db.retweetPrediction.find().distinct("username"))
    print(twitter_users)

    # Disconnect to mongodb
    dbHandler.closeDB(connection)