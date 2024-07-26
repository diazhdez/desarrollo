from flask import current_app


def get_user(email):
    db = current_app.get_db_connection()  # Obtener la conexión a la base de datos
    user = db['users'].find_one({'email': email})
    return user


def get_admin(email):
    db = current_app.get_db_connection()  # Obtener la conexión a la base de datos
    admin = db['admin'].find_one({'email': email})
    return admin


def get_sub(email):
    db = current_app.get_db_connection()  # Obtener la conexión a la base de datos
    sub = db['subordinados'].find_one({'email': email})
    return sub


def sub_has_completed_info(sub_id):
    db = current_app.get_db_connection()  # Obtener la conexión a la base de datos
    info = db['info']
    return info.find_one({'sub_id': str(sub_id)}) is not None
