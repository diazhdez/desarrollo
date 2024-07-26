from flask import Blueprint, render_template

errors = Blueprint('errors', __name__)


# Ruta para manejar páginas no encontradas
@errors.app_errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404
