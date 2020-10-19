import pandas as pd


def get_all_resources(db):

    query = 'select * from Resources'
    db.engine.execute(query)
    db_result = db.engine.execute(query)
    r = get_dict_from_result(db_result)
    return r


def get_fitlered_resources(db, filter_on, filter_val):
    query = "select * from Resources where {} = {}".format(
        filter_on, "'" + filter_val + "'")
    db.engine.execute(query)
    db_result = db.engine.execute(query)
    r = get_dict_from_result(db_result)
    return r


def get_dict_from_result(db_result):
    d, a = {}, []
    for rowproxy in db_result:
        # rowproxy.items() returns an array like [(key0, value0), (key1, value1)]
        for column, value in rowproxy.items():
            # build up the dictionary
            d = {**d, **{column: value}}
        a.append(d)
    return a
