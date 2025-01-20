from flask import Flask, render_template, request, jsonify
from config import Config
from .database import DatabaseConnection
from werkzeug.exceptions import BadRequest

def init_app():
    """Crea y configura la app Flask"""

    app = Flask(__name__, static_folder = Config.STATIC_FOLDER, template_folder=Config.TEMPLATE_FOLDER)
    app.config.from_object(Config)

    # Consulta
    
    @app.route('/', methods=['GET'])
    def get_jugadores():
        query = "SELECT nombre, apellido, email FROM jugadores"
        datos = DatabaseConnection.fetch_all(query)
        return jsonify(datos)
    
    


    return app

app = init_app()