import pandas

def mongoimport(db, csv_path):
    """ Imports a csv file at path csv_name to a mongo colection
    returns: count of the documants in the new collection
    """

    db.segment.drop()

    data = pandas.read_csv(csv_path)
    header = ["username", "date", "retweets", "favorites", "text", "geo", "mentions", "hashtags", "id", "permalink"]

    for each in data:
        row = {}
        for field in header:
            row[field] = each[field]

        db.segment.insert(row)

    # coll = db[coll_name]
    #
    # payload = json.loads(data.to_json(orient='records'))
    # coll.remove()
    # coll.insert(payload)
    # return coll.count()