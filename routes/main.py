from flask import Blueprint, render_template

import database.database as dbase

db = dbase.dbConnection()

main_routes = Blueprint('main', __name__)


# Ruta principal
@main_routes.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')
