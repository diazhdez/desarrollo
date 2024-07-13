import database.database as dbase

db = dbase.dbConnection()


def get_user(email):
    user = db['users'].find_one({'email': email})
    return user


def get_admin(email):
    admin = db['admin'].find_one({'email': email})
    return admin


def get_sub(email):
    sub = db['subordinados'].find_one({'email': email})
    return sub