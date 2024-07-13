from flask import Blueprint, render_template, url_for, redirect, flash, session, request

from functions.functions import get_sub

from bson import ObjectId

import database.database as dbase

db = dbase.dbConnection()

sub_routes = Blueprint('sub', __name__)


# Ruta para inicio de subordinados
@sub_routes.route('/subordinado/')
def sub():
    if 'email' in session:
        email = session['email']
        # Función para obtener datos del subordinado desde MongoDB
        sub = get_sub(email)
        if sub:
            return render_template('subordinado.html', sub=sub)
        else:
            return redirect(url_for('session.login'))
    else:
        return redirect(url_for('session.login'))


# Metodo para actualizar subordinados
@sub_routes.route('/update/subordinado/', methods=['POST'])
def update_sub():
    if 'email' in session:
        email = session['email']
        # Función para obtener datos del subordinado desde MongoDB
        sub = get_sub(email)
        if sub:
            if request.method == 'POST':
                print(request.form)
                sub_id = request.form.get('sub_id')
                genero = request.form.get('genero')
                age = request.form.get('age')
                antiguedad = request.form.get('antiguedad')

                subs = db['subordinados']
                subs.update_one(
                    {'_id': ObjectId(sub_id)},
                    {'$set': {
                        'genero': genero,
                        'age': age,
                        'antiguedad': antiguedad
                    }}
                )

            flash('Datos actualizados correctamente.')
            return redirect(url_for('sub.sub') + '#opcionesSub')
        else:
            return redirect(url_for('session.login'))
    else:
        return redirect(url_for('session.login'))
