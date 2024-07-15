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


# Ruta para empezar el cuestionario
@sub_routes.route('/subordinado/cuestionario/', methods=['GET'])
def cuestionario():
    if 'email' in session:
        email = session['email']
        # Función para obtener datos del subordinado desde MongoDB
        sub = get_sub(email)
        if sub:
            factores = []
            # Asegúrate de que user_id sea un string
            user_id = str(sub['user_id'])  # Obtener el user_id del usuario

            factores = db['factores'].find({'user_id': user_id})

            return render_template('cuestionario.html', factores=factores)
        else:
            return redirect(url_for('session.login'))
    else:
        return redirect(url_for('session.login'))


# Ruta para responder los items
@sub_routes.route('/subordinado/cuestionario/<factor_id>/items', methods=['GET'])
def cuestionario_items(factor_id):
    if 'email' in session:
        email = session['email']
        sub = get_sub(email)
        if sub:
            factor = db['factores'].find_one(
                {'_id': ObjectId(factor_id), 'user_id': str(sub['user_id'])})
            if factor:
                items = factor.get('items', [])
                return render_template('sub_items.html', factor=factor, items=items)
            else:
                flash("Factor no encontrado o no tienes permiso para verlo.")
                return redirect(url_for('sub.cuestionario'))
        else:
            return redirect(url_for('session.login'))
    else:
        return redirect(url_for('session.login'))


@sub_routes.route('/subordinado/cuestionario/<factor_id>/submit', methods=['POST'])
def submit_responses(factor_id):
    if 'email' in session:
        email = session['email']
        sub = get_sub(email)
        if sub:
            # Crear un documento de respuesta
            responses = []
            for key, value in request.form.items():
                if value:
                    item_index = key.split('_')[1]
                    responses.append({
                        "item_id": item_index,
                        "response": int(value)
                    })
            
            # Insertar respuestas en la colección de respuestas
            db['respuestas'].insert_one({
                "subordinado_id": sub['_id'],
                "factor_id": ObjectId(factor_id),
                "responses": responses
            })

            flash("Respuestas enviadas exitosamente.")
            return redirect(url_for('sub.cuestionario'))
        else:
            return redirect(url_for('session.login'))
    else:
        return redirect(url_for('session.login'))
