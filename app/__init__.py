import hashlib
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from config import Config
from .database import DatabaseConnection

# función para el hasheo, se utiliza en register como en login
def hash_password(password):
    """Genera un hash SHA-256 para la contraseña."""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()


def init_app():
    """Crea y configura la app Flask."""
    app = Flask(__name__, static_folder=Config.STATIC_FOLDER, template_folder=Config.TEMPLATE_FOLDER)
    CORS(app)
    app.config.from_object(Config)

    # Obtener jugadores
    @app.route('/', methods=['GET'])
    def get_jugadores():
        query = "SELECT nombre, apellido, email FROM jugadores"
        datos = DatabaseConnection.fetch_all(query)
        return jsonify(datos)

    @app.route('/register.html')
    def register():
        return render_template('register.html')

    # registramos jugadores con SHA-256
    @app.route('/register', methods=['POST'])
    def registro():
        try:
            data = request.json
            required_fields = ['name', 'surname', 'email', 'password', 'age', 'nickname']
            if not all(field in data for field in required_fields):
                return {"msg": "Faltan campos obligatorios."}, 400

            nombre = data['name']
            apellido = data['surname']
            email = data['email']
            password = hash_password(data['password'])  # Hash de la contraseña
            edad = data['age']
            apodo = data['nickname']

            query = """
                INSERT INTO rabonatest.jugadores (nombre, apellido, email, paswor, edad, apodo)
                VALUES (%s, %s, %s, %s, %s, %s);
            """
            params = (nombre, apellido, email, password, edad, apodo)
            DatabaseConnection.execute_query(query, params=params)

            usuario_insertado = {
                "Nombre": nombre,
                "Apellido": apellido,
                "Email": email,
                "Edad": edad,
                "Apodo": apodo
            }
            return jsonify(usuario_insertado), 200

        except Exception as e:
            return {"msg": "Error al registrar el cliente", "error": str(e)}, 500

    # Login de jugadores con SHA-256
    @app.route('/login', methods=['POST'])
    def login():
        try:
            data = request.json
            if 'email' not in data or 'password' not in data:
                return {"msg": "Faltan campos obligatorios."}, 400

            email = data['email']
            password = hash_password(data['password'])  # Hash de la contraseña ingresada
            query = "SELECT id, paswor FROM rabonatest.jugadores WHERE email = %s"
            user_data = DatabaseConnection.fetch_one(query, (email,))

            if not user_data:
                return {"msg": "Usuario no encontrado."}, 404

            # Guardo la password obtenida en user_data
            stored_password = user_data['paswor']
            if password == stored_password: # Verificar el hash de la contraseña
                user_id = user_data['id'] #Se toma el id obtenido de la consulta, una vez verificado el hash de contraseña
                return {"msg": "Login exitoso.", "user_id": user_id}, 200 #Mostramos id del usuario logeado por consola
            else:
                return {"msg": "Contraseña incorrecta."}, 401

        except Exception as e:
            return {"msg": "Error al iniciar sesión", "error": str(e)}, 500

    @app.route('/register_equipo.html')
    def register_equipos():
        return render_template('register_equipo.html')

    # Crear equipo
    @app.route('/crearEquipo', methods=['POST'])
    def crearEquipo():
        try:
            data = request.json
            if 'name' not in data or 'img' not in data:
                return {"msg": "Faltan campos obligatorios."}, 400

            nombre = data['name']
            imagen = data['img']
            query = "INSERT INTO rabonatest.equipos (nombre, escudo) VALUES (%s, %s);"
            params = (nombre, imagen)
            DatabaseConnection.execute_query(query, params=params)

            equipo_insertado = {
                "nombre": nombre,
                "escudo": imagen
            }
            return jsonify(equipo_insertado), 200

        except Exception as e:
            return {"msg": "Error al registrar el equipo", "error": str(e)}, 500

    return app


app = init_app()



# import bcrypt
# from flask import Flask, render_template, request, jsonify
# from flask_cors import CORS
# from config import Config
# from .database import DatabaseConnection
# from werkzeug.exceptions import BadRequest

# def init_app():
#     """Crea y configura la app Flask"""

#     app = Flask(__name__, static_folder = Config.STATIC_FOLDER, template_folder=Config.TEMPLATE_FOLDER)
#     CORS(app)
#     app.config.from_object(Config)

#     # Consulta
    
#     @app.route('/', methods=['GET'])
#     def get_jugadores():
#         query = "SELECT nombre, apellido, email FROM jugadores"
#         datos = DatabaseConnection.fetch_all(query)
#         return jsonify(datos)
    
#     @app.route('/register.html')
#     def register():
#         return render_template('register.html')

#     # Ruta para manejar el registro
#     @app.route('/register', methods=['POST'])
#     def registro():
#         if request.method == 'POST':
#             nombre = request.json.get('name')
#             apellido = request.json.get('surname')
#             email = request.json.get('email')
#             password = request.json.get('password')
#             edad = request.json.get('age')
#             apodo = request.json.get('nickname')

#         query= "INSERT INTO rabonatest.jugadores (nombre, apellido, email, paswor, edad, apodo) VALUES (%s, %s, %s, %s, %s, %s);"
#         params= (nombre, apellido, email, password, edad, apodo)

#         try:
#             DatabaseConnection.execute_query(query, params=params)
#             #construir el objeto json con los datos del jugador
#             usuario_insertado = {
#                 "Nombre": nombre,
#                 "Apellido": apellido,
#                 "Email": email,
#                 "paswor": password,
#                 "Edad": edad,
#                 "Apodo": apodo
#             }
#             return jsonify(usuario_insertado), 200

#         except Exception as e:
#             # Detallar el error para ayudar con la depuración
#             return {"msg": "Error al registrar el cliente", "error": str(e)}, 500
        
#     # Login de jugadores
#     @app.route('/login', methods=['POST'])
#     def login():
#         try:
#             data = request.json
#             if 'email' not in data or 'password' not in data:
#                 return {"msg": "Faltan campos obligatorios."}, 400

#             email = data['email']
#             password = data['password']
#             query = "SELECT paswor FROM rabonatest.jugadores WHERE email = %s"
#             user_data = DatabaseConnection.fetch_one(query, (email,))

#             if not user_data:
#                 return {"msg": "Usuario no encontrado."}, 404

#             # Verificar la contraseña directamente
#             if password == user_data['paswor']:
#                 return {"msg": "Login exitoso."}, 200
#             else:
#                 return {"msg": "Contraseña incorrecta."}, 401

#         except Exception as e:
#             return {"msg": "Error al iniciar sesión", "error": str(e)}, 500


#     @app.route('/register_equipo.html')
#     def register_equipos():
#         return render_template('register_equipo.html')

#     @app.route('/crearEquipo', methods=['POST'])
#     def crearEquipo():
#         if request.method == 'POST':
#             nombre = request.form['name']
#             imagen = request.form['img']
    
#         query= "INSERT INTO rabonatest.equipos (nombre, escudo) VALUES (%s, %s);"
#         params= (nombre, imagen)

#         try:
#             DatabaseConnection.execute_query(query, params=params)
#             equipo_insertado = {
#                 "nombre": nombre,
#                 "escudo": imagen
#             }
#             return jsonify(equipo_insertado), 200
    
#         except Exception as e:
#             return {"msg": "Error al registrar el equipo", "error": str(e)}, 500

#     return app

# app = init_app()