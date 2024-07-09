from pymongo import MongoClient

import certifi

import os

MONGO_URI = os.environ.get('MONGO_URI')

ca = certifi.where()


def dbConnection():
    try:
        client = MongoClient(MONGO_URI, tlsCAFile=ca)
        db = client["desarrollo"]
    except ConnectionError:
        print('Error de conexión con la BD')
    return db
