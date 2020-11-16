def get_all_resources(db):
    query = 'select * from Resources'
    db.engine.execute(query)
    db_result = db.engine.execute(query)
    r = get_dict_from_result(db_result)
    return r

def get_all_classes(db):
    query = 'select * from ClassSchedule'
    db.engine.execute(query)
    db_result = db.engine.execute(query)
    r = get_dict_from_result(db_result)
    return r


def get_all_classes(db):
    query = 'select * from ClassSchedule where EnrollmentCap > 0'
    db.engine.execute(query)
    db_result = db.engine.execute(query)
    r = get_dict_from_result(db_result)
    return r
    


def get_filtered_classes(db, filter_on, filter_val):
    """
    Takes in db engine, column to filter on, value to filter to
    (select * from resources where filter_on = 'filter_val')
    """
    query = "select * from ClassSchedule where {} = {} AND EnrollmentCap > 0".format(
        filter_on, "'" + filter_val + "'")
    db.engine.execute(query)
    db_result = db.engine.execute(query)
    r = get_dict_from_result(db_result)
    return r

def no_where_get_filtered_data(db, select, table):
    query = "select {} from {}".format(
        select, table)
    db.engine.execute(query)
    db_result = db.engine.execute(query)
    r = get_dict_from_result(db_result)
    return r

def get_filtered_data(db, select, table, where):
    query = "select {} from {} where {}".format(
        select, table, where)
    db.engine.execute(query)
    db_result = db.engine.execute(query)
    r = get_dict_from_result(db_result)
    return r


# Returns a list of dictionaries where each dictionary is {field:value} pairs for one row.
def get_dict_from_result(db_result):
    """
    Returns a list of dictionaries where each dictionary is {field:value} pairs for one row.
    """
    d, a = {}, []
    for rowproxy in db_result:
        # rowproxy.items() returns an array like [(field0, value0), (field1, value1)]
        for column, value in rowproxy.items():
            # build up the dictionary
            d = {**d, **{column: value}}
        a.append(d)
    return a