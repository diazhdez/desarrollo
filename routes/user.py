from flask import Blueprint, render_template, url_for, redirect, flash, session, request, jsonify

from functions.functions import get_user

from bson import ObjectId

from bson.errors import InvalidId

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
@user_routes.route('/add/factors/', methods=['POST'])
def add_factors():
    if 'email' in session:
        email = session['email']
        # Función para obtener datos del usuario desde MongoDB
        user = get_user(email)
        if user:
            if request.method == 'POST':
                # Línea de depuración para ver el contenido del formulario
                print(request.form)
                factors = db['factores']
                # Obtener la lista de nombres de factores
                names = request.form.getlist('names[]')
                user_id = str(user['_id'])  # Obtener el user_id del usuario
                duplicated_factors = []

                for name in names:
                    if name.strip():  # Asegurarse de que el nombre no esté vacío
                        existing_factor = factors.find_one({'name': name, 'user_id': user_id})
                        if existing_factor is None:
                            factors.insert_one(
                                {'name': name, 'user_id': user_id})
                        else:
                            duplicated_factors.append(name)

                if duplicated_factors:
                    flash(f'Los siguientes factores ya existen: {", ".join(duplicated_factors)}', 'danger')
                else:
                    flash('Se agregaron los factores correctamente', 'info')

                # Redirigir a la sección específica de la página
                return redirect(url_for('user.user') + '#opciones')
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
            user_id = str(user['_id'])  # Asegúrate de que user_id sea un string

            if request.method == 'POST':
                search_query = request.form.get('search_query')
                factores = db['factores'].find({
                    '$or': [
                        {'name': {'$regex': search_query, '$options': 'i'}},
                    ]
                })
            else:
                factores = db['factores'].find({'user_id': user_id})

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
    

@user_routes.route('/get_user_factors', methods=['GET'])
def get_user_factors():
    if 'email' in session:
        email = session['email']
        user = get_user(email)
        if user:
            user_id = str(user['_id'])
            factors = list(db['factores'].find({'user_id': user_id}, {'name': 1}))
            # Convertir ObjectId a cadena
            for factor in factors:
                factor['_id'] = str(factor['_id'])
            return jsonify({'factors': factors})
        else:
            return jsonify({'error': 'Usuario no encontrado'}), 404
    else:
        return jsonify({'error': 'No autorizado'}), 401


# Ruta para agregar items
@user_routes.route('/add/items/', methods=['POST'])
def add_items():
    if 'email' in session:
        email = session['email']
        user = get_user(email)
        if user:
            if request.method == 'POST':
                print(request.form)
                factor_id = request.form.get('factor_id')
                names = request.form.getlist('names[]')
                duplicated_items = []

                if not factor_id or factor_id == 'undefined':
                    flash('Debe seleccionar un factor', 'danger')
                    return redirect(url_for('user.user') + '#opciones')

                try:
                    factor = db['factores'].find_one({'_id': ObjectId(factor_id), 'user_id': str(user['_id'])})
                except InvalidId:
                    flash('Factor ID no válido', 'danger')
                    return redirect(url_for('user.user') + '#opciones')

                if not factor:
                    flash('El factor seleccionado no existe o no pertenece al usuario', 'danger')
                    return redirect(url_for('user.user') + '#opciones')

                for name in names:
                    if name.strip():
                        existing_item = db['factores'].find_one(
                            {'_id': ObjectId(factor_id), 'items.name': name}
                        )
                        if existing_item is None:
                            db['factores'].update_one(
                                {'_id': ObjectId(factor_id)},
                                {'$push': {'items': {'name': name}}}
                            )
                        else:
                            duplicated_items.append(name)

                if duplicated_items:
                    flash(f'Los siguientes items ya existen en el factor: {", ".join(duplicated_items)}', 'danger')
                else:
                    flash('Se agregaron los items correctamente', 'info')

                return redirect(url_for('user.user') + '#opciones')
        else:
            return redirect(url_for('session.login'))
    else:
        return redirect(url_for('session.login'))