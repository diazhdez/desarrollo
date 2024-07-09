from flask import Blueprint, render_template, url_for, redirect, flash, session, request

from functions.functions import get_user

from bson import ObjectId

import database.database as dbase

db = dbase.dbConnection()

user_routes = Blueprint('user', __name__)


# Ruta para inicio de usuarios
@user_routes.route('/user/')
def user():
    if 'email' in session:
        email = session['email']
        # Función para obtener datos del usuario desde MongoDB
        user = get_user(email)
        if user:
            return render_template('user.html', user=user)
        else:
            return redirect(url_for('session.login'))
    else:
        return redirect(url_for('session.login'))


# Ruta para agregar factores
@user_routes.route('/add/factor/', methods=['POST', 'GET'])
def add_factor():
    if 'email' in session:
        email = session['email']
        # Función para obtener datos del usuario desde MongoDB
        user = get_user(email)
        if user:
            if request.method == 'POST':
                factor = db['factores']
                existing_factor = factor.find_one(
                    {'name': request.form['name']})
                name = request.form['name']

                if existing_factor is None:
                    factor.insert_one({
                        'name': name,

                    })
                    flash('Se agregó el factor correctamente')
                    return redirect(url_for('user.user'))

                flash('Este factor ya existe')
                return redirect(url_for('user.user'))
        else:
            return redirect(url_for('session.login'))
    else:
        return redirect(url_for('session.login'))


# Ruta para ver factores
@user_routes.route('/user/factores/', methods=['POST', 'GET'])
def factores():
    if 'email' in session:
        email = session['email']
        # Función para obtener datos del usuario desde MongoDB
        user = get_user(email)
        if user:
            factores = []
            if request.method == 'POST':
                search_query = request.form.get('search_query')
                factores = db['factores'].find({
                    '$or': [
                        {'name': {'$regex': search_query, '$options': 'i'}},
                    ]
                })
            else:
                factores = db['factores'].find()
            return render_template('factores.html', factores=factores)
        else:
            return redirect(url_for('session.login'))
    else:
        return redirect(url_for('session.login'))


# Method DELETE para factores
@user_routes.route('/delete/factor/<string:factor_id>/')
def delete_factor(factor_id):
    if 'email' in session:
        email = session['email']
        # Función para obtener datos del usuario desde MongoDB
        user = get_user(email)
        if user:
            factor = db['factores']
            factor.delete_one({'_id': ObjectId(factor_id)})
            return redirect(url_for('user.factores'))
        else:
            return redirect(url_for('session.login'))
    else:
        return redirect(url_for('session.login'))


# Metodo para editar factores
@user_routes.route('/edit/factor/', methods=['POST'])
def edit_factor():
    if 'email' in session:
        email = session['email']
        # Función para obtener datos del usuario desde MongoDB
        user = get_user(email)
        if user:
            if request.method == 'POST':
                factor_id = request.form.get('factor_id')
                new_name = request.form.get('name')

                factor = db['factores']
                factor.update_one(
                    {'_id': ObjectId(factor_id)},
                    {'$set': {
                        'name': new_name,
                    }}
                )

            return redirect(url_for('user.factores'))
        else:
            return redirect(url_for('session.login'))
    else:
        return redirect(url_for('session.login'))


# Ruta para agregar items
@user_routes.route('/add/item/', methods=['POST', 'GET'])
def add_item():
    if 'email' in session:
        email = session['email']
        # Función para obtener datos del usuario desde MongoDB
        user = get_user(email)
        if user:
            if request.method == 'POST':
                item = db['items']
                existing_item = item.find_one(
                    {'name': request.form['name']})
                name = request.form['name']

                if existing_item is None:
                    item.insert_one({
                        'name': name,

                    })
                    flash('Se agregó el item correctamente')
                    return redirect(url_for('user.user'))

                flash('Este item ya existe')
                return redirect(url_for('user.user'))
        else:
            return redirect(url_for('session.login'))
    else:
        return redirect(url_for('session.login'))