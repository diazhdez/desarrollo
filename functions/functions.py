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


# Función para verificar si el usuario ha completado sus datos
def sub_has_completed_info(sub_id):
    info = db['info']
    return info.find_one({'sub_id': str(sub_id)}) is not None