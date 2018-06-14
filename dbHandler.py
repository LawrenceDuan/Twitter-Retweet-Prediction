import pymongo


def connectDB():
    '''
    Connect to mongodb database
    :return: selected database db and the client connection
    '''
    connection = pymongo.MongoClient('mongodb://127.0.0.1:27017')
    db = connection['tweets']

    return db, connection


def closeDB(client):
    '''
    Disconnect to mongodb database
    :param client: the client need to be disconnected
    :return: void
    '''
    client.close()