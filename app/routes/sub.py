from flask import Blueprint, current_app, render_template, url_for, redirect, flash, session, request

from app.functions.functions import get_sub, sub_has_completed_info

from bson import ObjectId

sub_routes = Blueprint('sub', __name__)


# Ruta para inicio de subordinados
@sub_routes.route('/sub/')
def sub():
    if 'email' in session:
        email = session['email']
        # Función para obtener datos del subordinado desde MongoDB
        sub = get_sub(email)
        if sub:
            # Buscar si el subordinado ha mandado su info
            sub['has_completed_info'] = sub_has_completed_info(sub['_id'])

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
                sub_id = sub['_id']
                genero = request.form.get('genero')
                age = request.form.get('age')
                antiguedad = request.form.get('antiguedad')

                db = current_app.get_db_connection()  # Obtener la conexión a la base de datos

                subs = db['subordinados']
                info = db['info']

                subs.update_one(
                    {'_id': ObjectId(sub_id)},
                    {'$set': {
                        'genero': genero,
                        'age': age,
                        'antiguedad': antiguedad
                    }}
                )

                info.insert_one({
                    'sub_id': str(sub_id),
                    'user_id': sub['user_id']
                })

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

            db = current_app.get_db_connection()  # Obtener la conexión a la base de datos

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
            db = current_app.get_db_connection()  # Obtener la conexión a la base de datos

            factor = db['factores'].find_one(
                {'_id': ObjectId(factor_id), 'user_id': str(sub['user_id'])})
            if factor:
                # Verificar si ya ha respondido
                existing_answers = db['answers'].find_one({
                    'subordinado_id': str(sub['_id']),
                    'factor_id': str(factor_id)
                })
                if existing_answers:
                    flash("Ya has respondido este factor.")
                    return redirect(url_for('sub.cuestionario'))

                items = factor.get('items', [])
                return render_template('sub_items.html', factor=factor, items=items)
            else:
                flash("Factor no encontrado o no tienes permiso para verlo.")
                return redirect(url_for('sub.cuestionario'))
        else:
            return redirect(url_for('session.login'))
    else:
        return redirect(url_for('session.login'))


# Ruta para guardar las respuestas
@sub_routes.route('/subordinado/cuestionario/<factor_id>/submit', methods=['POST'])
def submit_answers(factor_id):
    if 'email' in session:
        email = session['email']
        sub = get_sub(email)
        if sub:
            db = current_app.get_db_connection()  # Obtener la conexión a la base de datos

            # Verificar si ya ha respondido
            existing_answers = db['answers'].find_one({
                'subordinado_id': str(sub['_id']),
                'factor_id': str(factor_id)
            })
            if existing_answers:
                flash("Ya has respondido este factor.")
                return redirect(url_for('sub.cuestionario'))

            # Crear un documento de respuesta
            answers = []
            for key, value in request.form.items():
                if value:
                    # Obtener el item_id del formulario
                    item_id = key.split('_')[1]
                    answers.append({
                        "item_id": item_id,
                        "answer": int(value)
                    })

            # Insertar respuestas en la colección de answers
            db['answers'].insert_one({
                "subordinado_id": str(sub['_id']),
                "factor_id": str(factor_id),
                "user_id": str(sub['user_id']),
                "answers": answers
            })

            flash("Respuestas enviadas exitosamente.")
            return redirect(url_for('sub.cuestionario'))
        else:
            return redirect(url_for('session.login'))
    else:
        return redirect(url_for('session.login'))
