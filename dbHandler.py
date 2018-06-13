import pymongo


def connectDB():
    connection = pymongo.MongoClient('mongodb://127.0.0.1:27017')
    db = connection['tweets']

    return db, connection


def closeDB(client):
    client.close()