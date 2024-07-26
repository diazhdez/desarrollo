from flask import Blueprint, render_template

main_routes = Blueprint('main', __name__)


# Ruta principal
@main_routes.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')
