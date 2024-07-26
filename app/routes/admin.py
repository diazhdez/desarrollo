from flask import Blueprint, current_app, render_template, url_for, redirect, flash, session, request

from app.functions.functions import get_admin

from bson import ObjectId

import bcrypt

admin_routes = Blueprint('admin', __name__)


# Ruta para el administrador
@admin_routes.route('/admin/')
def admin():
    if 'email' in session:
        email = session['email']
        # Función para obtener datos del usuario desde MongoDB
        admin = get_admin(email)
        if admin:
            return render_template('admin.html', admin=admin)
    else:
        return redirect(url_for('session.login'))


# Ruta de para registrar aspirantes y administradores
@admin_routes.route('/admin/registro/')
def registro():
    if 'email' in session:
        email = session['email']
        # Función para obtener datos del usuario desde MongoDB
        admin = get_admin(email)
        if admin:
            return render_template('registro.html')
    else:
        return redirect(url_for('session.login'))


# Ruta para registrar a los usuarios
@admin_routes.route('/register_user/', methods=['POST', 'GET'])
def register_user():
    if 'email' in session:
        email = session['email']
        # Función para obtener datos del usuario desde MongoDB
        admin = get_admin(email)
        if admin:
            if request.method == 'POST':
                db = current_app.get_db_connection()  # Obtener la conexión a la base de datos
                user = db['users']
                existing_user = user.find_one(
                    {'email': request.form['email']})
                name = request.form['name']
                email = request.form['email']
                password = request.form['password']
                empresa = request.form['empresa']
                phone = request.form['phone']

                if existing_user is None:
                    hashpass = bcrypt.hashpw(
                        password.encode('utf-8'), bcrypt.gensalt())
                    user.insert_one({
                        'name': name,
                        'email': email,
                        'password': hashpass,
                        'empresa': empresa,
                        'phone': phone
                    })
                    flash('Se registró el usuario correctamente')
                    return redirect(url_for('admin.registro'))

                flash('El correo ya está en uso')
                return redirect(url_for('admin.registro'))
        else:
            return redirect(url_for('session.login'))

    return redirect(url_for('admin.registro'))


# Ruta para registrar administradores
@admin_routes.route('/register_admin/', methods=['POST', 'GET'])
def register_admin():
    if 'email' in session:
        email = session['email']
        # Función para obtener datos del usuario desde MongoDB
        admin = get_admin(email)
        if admin:
            if request.method == 'POST':
                db = current_app.get_db_connection()  # Obtener la conexión a la base de datos
                admin = db['admin']
                existing_admin = admin.find_one(
                    {'email': request.form['email']})
                name = request.form['name']
                email = request.form['email']
                password = request.form['password']
                phone = request.form['phone']

                if existing_admin is None:
                    hashpass = bcrypt.hashpw(
                        password.encode('utf-8'), bcrypt.gensalt())
                    admin.insert_one({
                        'name': name,
                        'email': email,
                        'password': hashpass,
                        'phone': phone
                    })
                    flash('Se registró el administrador correctamente')
                    return redirect(url_for('admin.registro'))

                flash('El correo ya está en uso')
                return redirect(url_for('admin.registro'))
        else:
            return redirect(url_for('session.login'))

    return redirect(url_for('admin.registro'))


# Ruta para visualizar los gerentes
@admin_routes.route('/admin/listas/users/', methods=['POST', 'GET'])
def users():
    if 'email' in session:
        email = session['email']
        admin = get_admin(email)
        if admin:
            users = []
            if request.method == 'POST':
                search_query = request.form.get('search_query')
                db = current_app.get_db_connection()  # Obtener la conexión a la base de datos
                users = db['users'].find({
                    '$or': [
                        {'name': {'$regex': search_query, '$options': 'i'}},
                        {'email': {'$regex': search_query, '$options': 'i'}},
                        {'empresa': {'$regex': search_query, '$options': 'i'}},
                    ]
                })
            else:
                db = current_app.get_db_connection()  # Obtener la conexión a la base de datos
                users = db['users'].find()

            return render_template('users.html', users=users)
        else:
            return redirect(url_for('session.login'))
    else:
        return redirect(url_for('session.login'))


# Metodo para editar users
@admin_routes.route('/edit/user/', methods=['POST'])
def edit_user():
    if 'email' in session:
        email = session['email']
        # Función para obtener datos del usuario desde MongoDB
        admin = get_admin(email)
        if admin:
            if request.method == 'POST':
                user_id = request.form.get('user_id')
                new_name = request.form.get('name')
                new_email = request.form.get('email')
                new_empresa = request.form.get('empresa')
                new_phone = request.form.get('phone')

                db = current_app.get_db_connection()  # Obtener la conexión a la base de datos
                user = db['users']
                user.update_one(
                    {'_id': ObjectId(user_id)},
                    {'$set': {
                        'name': new_name,
                        'email': new_email,
                        'empresa': new_empresa,
                        'phone': new_phone
                    }}
                )
            flash('Asesor editado correctamente.')
            return redirect(url_for('admin.users'))
        else:
            return redirect(url_for('session.login'))
    else:
        return redirect(url_for('session.login'))


# Method DELETE para usuarios
@admin_routes.route('/deleteUser/<string:user_id>/')
def delete_user(user_id):
    if 'email' in session:
        email = session['email']
        admin = get_admin(email)
        if admin:
            # Accede a las colecciones directamente desde la conexión a la base de datos
            db = current_app.db
            users = db['users']
            factores = db['factores']
            sub = db['subordinados']
            answers = db['answers']
            info = db['info']
            users.delete_one({'_id': ObjectId(user_id)})
            factores.delete_many({'user_id': str(user_id)})
            sub.delete_many({'user_id': str(user_id)})
            answers.delete_many({'user_id': str(user_id)})
            info.delete_many({'user_id': str(user_id)})
            flash('Asesor eliminado correctamente.')
            return redirect(url_for('admin.users'))
        else:
            return redirect(url_for('session.login'))
    else:
        return redirect(url_for('session.login'))


# Ruta para visualizar los administradores
@admin_routes.route('/admin/listas/admins/')
def admins():
    if 'email' in session:
        email = session['email']
        admin = get_admin(email)
        if admin:
            # Accede a las colecciones directamente desde la conexión a la base de datos
            db = current_app.db
            admins = db['admin'].find()
            return render_template('admins.html', admins=admins)
        else:
            return redirect(url_for('session.login'))
    else:
        return redirect(url_for('session.login'))


# Method DELETE para administradores
@admin_routes.route('/deleteAdmin/<string:admin_id>/')
def delete_admin(admin_id):
    if 'email' in session:
        email = session['email']
        admin = get_admin(email)
        if admin:
            # Accede a las colecciones directamente desde la conexión a la base de datos
            db = current_app.db
            admin = db['admin']
            admin.delete_one({'_id': ObjectId(admin_id)})
            flash('Administrador eliminado correctamente.')
            return redirect(url_for('admin.admins'))
        else:
            return redirect(url_for('session.login'))
    else:
        return redirect(url_for('session.login'))
