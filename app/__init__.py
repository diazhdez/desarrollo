from flask import Flask, g
from pymongo import MongoClient
from config import Config
import certifi


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Configuración de la conexión a la base de datos usando la URL
    ca = certifi.where()

    def get_db_connection():
        if 'db' not in g:
            try:
                client = MongoClient(Config.MONGO_URI, tlsCAFile=ca)
                g.db = client["desarrollo"]
            except Exception as e:
                print(f"Error de conexión con la base de datos: {e}")
                g.db = None
        return g.db

    @app.teardown_appcontext
    def close_db_connection(exception):
        db = g.pop('db', None)
        if db is not None:
            try:
                client = db.client  # Obtener el cliente de MongoDB desde la conexión
                client.close()
            except Exception as e:
                print(f"Error al cerrar la conexión con la base de datos: {e}")

    app.get_db_connection = get_db_connection

    with app.app_context():
        # Importa y registra los Blueprints
        from app.routes.main import main_routes
        from app.routes.session import session_routes
        from app.routes.admin import admin_routes
        from app.routes.user import user_routes
        from app.routes.sub import sub_routes
        from app.routes.errors import errors

        app.register_blueprint(main_routes)
        app.register_blueprint(session_routes)
        app.register_blueprint(admin_routes)
        app.register_blueprint(user_routes)
        app.register_blueprint(sub_routes)
        app.register_blueprint(errors)

    return app
