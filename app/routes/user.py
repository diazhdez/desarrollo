from flask import Blueprint, current_app, render_template, url_for, redirect, flash, session, request, jsonify

from app.functions.functions import get_user

from bson import ObjectId

from bson.errors import InvalidId

from random import randint

import bcrypt

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

                db = current_app.get_db_connection()  # Obtener la conexión a la base de datos

                factors = db['factores']
                # Obtener la lista de nombres de factores

                names = request.form.getlist('names[]')
                user_id = str(user['_id'])  # Obtener el user_id del usuario
                duplicated_factors = []

                for name in names:
                    if name.strip():  # Asegurarse de que el nombre no esté vacío
                        existing_factor = factors.find_one(
                            {'name': name, 'user_id': user_id})
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
            # Asegúrate de que user_id sea un string
            user_id = str(user['_id'])  # Obtener el user_id del usuario

            if request.method == 'POST':
                # Accede a las colecciones directamente desde la conexión a la base de datos
                db = current_app.db

                search_query = request.form.get('search_query')
                factores = db['factores'].find({
                    '$or': [
                        {'name': {'$regex': search_query, '$options': 'i'}},
                    ]
                })
            else:
                db = current_app.get_db_connection()  # Obtener la conexión a la base de datos

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
            db = current_app.get_db_connection()  # Obtener la conexión a la base de datos

            factor = db['factores']
            factor.delete_one({'_id': ObjectId(factor_id)})

            flash('Factor eliminado correctamente.')
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

                db = current_app.get_db_connection()  # Obtener la conexión a la base de datos

                factor = db['factores']
                factor.update_one(
                    {'_id': ObjectId(factor_id)},
                    {'$set': {
                        'name': new_name,
                    }}
                )

            flash('Factor actualizado correctamente.')
            return redirect(url_for('user.factores'))
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
            db = current_app.get_db_connection()  # Obtener la conexión a la base de datos

            user_id = str(user['_id'])  # Obtener el user_id del usuario
            factors = list(db['factores'].find(
                {'user_id': user_id}, {'name': 1})
            )

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
                factor_id = request.form.get('factor_id')
                names = request.form.getlist('names[]')
                duplicated_items = []

                if not factor_id or factor_id == 'undefined':
                    flash('Debe seleccionar un factor', 'danger')
                    return redirect(url_for('user.user') + '#opciones')

                try:
                    db = current_app.get_db_connection()  # Obtener la conexión a la base de datos
                    factor = db['factores'].find_one(
                        {'_id': ObjectId(factor_id), 'user_id': str(user['_id'])})
                except InvalidId:
                    flash('Factor ID no válido', 'danger')
                    return redirect(url_for('user.user') + '#opciones')

                if not factor:
                    flash(
                        'El factor seleccionado no existe o no pertenece al usuario', 'danger')
                    return redirect(url_for('user.user') + '#opciones')

                new_items = []
                for name in names:
                    if name.strip():
                        item_id = ObjectId()  # Generar un ID único para el ítem
                        existing_item = db['factores'].find_one(
                            {'_id': ObjectId(factor_id), 'items._id': item_id}
                        )
                        if existing_item is None:
                            new_items.append({
                                "_id": item_id,
                                "name": name
                            })
                        else:
                            duplicated_items.append(name)

                if new_items:
                    db['factores'].update_one(
                        {'_id': ObjectId(factor_id)},
                        {'$push': {'items': {'$each': new_items}}}
                    )

                if duplicated_items:
                    flash(f'Los siguientes items ya existen en el factor: {", ".join(duplicated_items)}', 'danger')
                else:
                    flash('Se agregaron los items correctamente', 'info')

                return redirect(url_for('user.user') + '#opciones')
        else:
            return redirect(url_for('session.login'))
    else:
        return redirect(url_for('session.login'))


# Ruta para visualizar items
@user_routes.route('/user/factor/<factor_id>/items', methods=['GET'])
def view_items(factor_id):
    if 'email' in session:
        email = session['email']
        user = get_user(email)
        if user:
            db = current_app.get_db_connection()  # Obtener la conexión a la base de datos

            factor = db['factores'].find_one(
                {'_id': ObjectId(factor_id), 'user_id': str(user['_id'])})
            if factor:
                items = factor.get('items', [])
                return render_template('items.html', factor=factor, items=items)
            else:
                flash("Factor no encontrado o no tienes permiso para verlo.")
                return redirect(url_for('user.factores'))
        else:
            return redirect(url_for('session.login'))
    else:
        return redirect(url_for('session.login'))


# Ruta para eliminar items
@user_routes.route('/user/factor/<factor_id>/item/<item_id>/delete', methods=['POST'])
def delete_item(factor_id, item_id):
    if 'email' in session:
        email = session['email']
        user = get_user(email)
        if user:
            db = current_app.get_db_connection()  # Obtener la conexión a la base de datos

            # Buscar el factor asociado al usuario
            factor = db['factores'].find_one(
                {'_id': ObjectId(factor_id), 'user_id': str(user['_id'])}
            )
            if factor:
                # Eliminar el ítem por su ID
                result = db['factores'].update_one(
                    {'_id': ObjectId(factor_id)},
                    {'$pull': {'items': {'_id': ObjectId(item_id)}}}
                )
                if result.modified_count > 0:
                    flash("Ítem eliminado correctamente.")
                else:
                    flash("Ítem no encontrado o no se pudo eliminar.")
                return redirect(url_for('user.view_items', factor_id=factor_id))
            else:
                flash("Factor no encontrado o no tienes permiso para eliminar ítems.")
                return redirect(url_for('user.factores'))
        else:
            return redirect(url_for('session.login'))
    else:
        return redirect(url_for('session.login'))


# Ruta para actualizar un item
@user_routes.route('/user/factor/<factor_id>/item/<item_id>/update', methods=['POST'])
def update_item(factor_id, item_id):
    if 'email' in session:
        email = session['email']
        user = get_user(email)
        if user:
            db = current_app.get_db_connection()  # Obtener la conexión a la base de datos

            factor = db['factores'].find_one(
                {'_id': ObjectId(factor_id), 'user_id': str(user['_id'])})
            if factor:
                new_name = request.form.get('new_name')
                items = factor.get('items', [])
                for item in items:
                    if str(item['_id']) == item_id:
                        item['name'] = new_name
                        break

                db['factores'].update_one(
                    {'_id': ObjectId(factor_id), 'user_id': str(user['_id'])},
                    {'$set': {'items': items}}
                )
                flash("Ítem actualizado correctamente.")
                return redirect(url_for('user.view_items', factor_id=factor_id))
            else:
                flash("Factor no encontrado o no tienes permiso para verlo.")
                return redirect(url_for('user.factores'))
        else:
            return redirect(url_for('session.login'))
    else:
        return redirect(url_for('session.login'))


# Ruta para registrar subordinados
@user_routes.route('/register/subordinado/', methods=['POST', 'GET'])
def register_sub():
    if 'email' in session:
        email = session['email']
        # Función para obtener datos del usuario desde MongoDB
        user = get_user(email)
        if user:
            if request.method == 'POST':
                # Obtener la cantidad de usuarios a registrar desde el formulario
                num_subs = int(request.form['num_subs'])
                # Contraseña predeterminada para todos los usuarios
                password = request.form['password']
                user_id = str(user['_id'])  # Obtener el user_id del asesor
                asesor = user['name']
                empresa = user['empresa']

                db = current_app.get_db_connection()  # Obtener la conexión a la base de datos

                sub = db['subordinados']

                # Generar los documentos de los usuarios
                sub_docs = []
                for _ in range(num_subs):
                    email = str(randint(100000, 999999))
                    hashpass = bcrypt.hashpw(
                        password.encode('utf-8'), bcrypt.gensalt())
                    sub_docs.append({
                        'email': email,
                        'password': hashpass,
                        'user_id': user_id,
                        'asesor': asesor,
                        'empresa': empresa
                    })

                # Insertar los documentos de los subordinados en la base de datos
                sub.insert_many(sub_docs)

                flash(f'Se registraron {num_subs} subordinados correctamente')
                return redirect(url_for('user.user') + '#opciones')
        else:
            return redirect(url_for('session.login'))

    return redirect(url_for('session.login'))


# Ruta para visualizar los subordinados
@user_routes.route('/user/listas/subordinados/', methods=['POST', 'GET'])
def subordinados():
    if 'email' in session:
        email = session['email']
        # Función para obtener datos del usuario desde MongoDB
        user = get_user(email)
        if user:
            subs = []
            # Asegúrate de que user_id sea un string
            user_id = str(user['_id'])  # Obtener el user_id del usuario

            if request.method == 'POST':
                db = current_app.get_db_connection()  # Obtener la conexión a la base de datos

                search_query = request.form.get('search_query')
                subs = db['subordinados'].find({
                    '$or': [
                        {'email': {'$regex': search_query, '$options': 'i'}},
                        {'empresa': {'$regex': search_query, '$options': 'i'}},
                        {'asesor': {'$regex': search_query, '$options': 'i'}},
                        {'genero': {'$regex': search_query, '$options': 'i'}},
                        {'age': {'$regex': search_query, '$options': 'i'}},
                        {'antiguedad': {'$regex': search_query, '$options': 'i'}},
                    ]
                })
            else:
                db = current_app.get_db_connection()  # Obtener la conexión a la base de datos

                subs = db['subordinados'].find({'user_id': user_id})

            return render_template('subs.html', subordinados=subs)
        else:
            return redirect(url_for('session.login'))
    else:
        return redirect(url_for('session.login'))


# Method DELETE para usuarios
@user_routes.route('/delete/subordinado/<string:sub_id>/')
def delete_sub(sub_id):
    if 'email' in session:
        email = session['email']
        user = get_user(email)
        if user:
            db = current_app.get_db_connection()  # Obtener la conexión a la base de datos

            sub = db['subordinados']
            info = db['info']
            answers = db['answers']
            sub.delete_one({'_id': ObjectId(sub_id)})
            info.delete_one({'sub_id': str(sub_id)})
            answers.delete_many({'subordinado_id': str(sub_id)})

            flash('Subordinado eliminado correctamente.')
            return redirect(url_for('user.subordinados'))
        else:
            return redirect(url_for('session.login'))
    else:
        return redirect(url_for('session.login'))
