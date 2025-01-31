import hashlib
from flask import Flask, render_template, jsonify, request
from .database import DatabaseConnection
from flask_cors import CORS
from config import Config
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from datetime import datetime

# función para el hasheo, se utiliza en register como en login
def hash_password(password):
    """Genera un hash SHA-256 para la contraseña."""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()



def init_app():

    app = Flask(__name__)
    CORS(app)

    app.config.from_object(
        Config
    )

    #Clave secreta para JWT
    app.config['JWT_SECRET_KEY'] = 'YDveI2KRL6p_LRN0xonK6ZNlsIQKa2KuulG_NusD1JQ='
    jwt = JWTManager(app)

    @app.route('/')
    def home():
        return render_template('index.html')
    
    #partidos
    @app.route('/partidos', methods=['GET'])
    def get_partidos():
        try:
                
            query_partidos = """
                    SELECT 
                        partidos.ID,
                        partidos.lugar,
                        partidos.fecha,
                        GROUP_CONCAT(DISTINCT equipos.nombre ORDER BY equipos.ID SEPARATOR ' vs ') AS equipos
                    FROM partidos
                    JOIN participacion ON partidos.ID = participacion.ID_partido
                    JOIN equipos ON participacion.ID_equipo = equipos.ID
                    GROUP BY 
                        partidos.ID, partidos.lugar, partidos.fecha
                    ORDER BY 
                        partidos.fecha;

            """
            datos = DatabaseConnection.fetch_all(query_partidos)
            
            return jsonify(datos), 200
        except Exception as e:
            return {"msg": "Error al ver partidos", "error": str(e)}, 500


    
    # Ruta para manejar el registro
    @app.route('/register', methods=['POST'])
    def registro():
        try:
            data = request.json
            required_fields = ['nombre', 'apellido', 'email', 'paswor', 'edad', 'apodo']
            if not all(field in data for field in required_fields):
                return {"msg": "Faltan campos obligatorios."}, 400

            nombre = data['nombre']
            apellido = data['apellido']
            email = data['email']
            password = hash_password(data['paswor'])  # Hash de la contraseña
            edad = data['edad']
            apodo = data['apodo']

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

    #Login de jugadores con SHA-256
    @app.route('/login', methods=['POST'])
    def login():
        try:
            data = request.json
            if 'email' not in data or 'password' not in data:
                return {"msg": "Faltan campos obligatorios."}, 400

            email = data['email']
            password = hash_password(data['password']) 
            query = "SELECT id, paswor FROM rabonatest.jugadores WHERE email = %s"
            user_data = DatabaseConnection.fetch_one(query, (email,))

            if not user_data:
                return {"msg": "Usuario no encontrado."}, 404

            # Guardo la password obtenida en user_data
            stored_password = user_data['paswor']
            if password == stored_password: # Verificar el hash de la contraseña
                user_id = user_data['id'] #Se toma el id obtenido de la consulta, una vez verificado el hash de contraseña
                #Generar Token
                access_token = create_access_token(identity=str(user_id))
                return {"msg": "Login exitoso.","access_token": access_token, "user__id": user_id}, 200 #Mostramos id del usuario logeado por consola
            else:
                return {"msg": "Contraseña incorrecta."}, 401

        except Exception as e:
            return {"msg": "Error al iniciar sesión", "error": str(e)}, 500

    #Perfil
    @app.route('/perfil', methods=['GET'])
    @jwt_required()
    def get_perfil():
        # se obtiene el ID jugador mediante getjwtidentity
        id_jugador = get_jwt_identity()
        if id_jugador is None:
            print('No cargo el id_jugador')
            return jsonify({"msg": "No se cargo el jwt"}), 401
        try:
            #Se realiza la consulta a la base de datos seleccionando los campos necesarios para el perfil
            sql = "SELECT ID, nombre, apellido, email, edad, apodo FROM jugadores WHERE ID = %s"
            datos = DatabaseConnection.fetch_one(sql, (id_jugador,))
            if datos is None:
                return jsonify({"msg": "No se encontraron datos para el ID proporcionado"}), 422
        except Exception as e:
            return jsonify({"msg": "Error en perfil", "error": str(e)}), 500 #Se retorna el error en el perfil
        return jsonify(datos) #Se retornan los datos
    
    #Endpoint crear equipo
    @app.route('/crearEquipo', methods=['POST'])
    @jwt_required()
    def crearEquipo():
        if request.method == 'POST':
            nombre = request.json.get('nombre')
            imagen = request.json.get('img')
        
        #Aquí iria la implemtacion para extraer el ID del jugador basado en el inicio de sesion
        id_jugador = get_jwt_identity()

        query_equipo= "INSERT INTO rabonatest.equipos (nombre, escudo) VALUES (%s, %s);"
        params_equipo= (nombre, imagen)

        try:
            #insertar el equipo y obtener el ID del equipo recien creado
            id_equipo= DatabaseConnection.execute_query_and_return_id(query_equipo, params=params_equipo)
            # Insertar la relacion en la tabla intermedia 'jugador_equipo'
            query_tabla_intermedia = "INSERT INTO rabonatest.jugador_equipo (ID_equipo, ID_jugador, id_jugador_creador) VALUES (%s, %s, %s);"
            params_tabla_intermedia = (id_equipo, id_jugador, id_jugador)

            DatabaseConnection.execute_query(query_tabla_intermedia, params=params_tabla_intermedia)
            equipo_insertado = {
                "nombre": nombre,
                "escudo": imagen,
                "id_equipo": id_equipo
            }
            return jsonify(equipo_insertado), 200

        except Exception as e:
            return {"msg": "Error al registrar el equipo", "error": str(e)}, 500

    #Equipos
    @app.route('/equipos', methods=['GET'])
    @jwt_required()
    def get_equiposlist():
        id_jugador = get_jwt_identity()
        try:
            query= """SELECT e.nombre  
            FROM equipos e  
            JOIN jugador_equipo je ON e.id = je.ID_Equipo  
            WHERE je.ID_Jugador = %s"""
            equipos= DatabaseConnection.fetch_all(query, (id_jugador,))
            if not equipos:
                return jsonify({"msg": "No hay equipos registrados."}), 404
            
            #print(jsonify(equipos))
            equipos_nombre = [equipo[0] for equipo in equipos]
            return jsonify(equipos), 200
        
        except Exception as e:
            return jsonify({"msg": "Error al botener los equipos", "error": str(e)}), 500
        
    #Equipos
    @app.route('/todoslosequipos', methods=['GET'])
    def get_equipos():
        query = "SELECT ID, nombre, escudo FROM equipos"
        datos = DatabaseConnection.fetch_all(query)
        return jsonify(datos)

    #Endpoint que retorna los equipos al que pertenece el jugador
    @app.route('/equipos/jugador/<int:jugador_id>', methods=['GET'])
    def get_equipos_jugador(jugador_id):

        qry = """ 
            SELECT equipos.ID, equipos.nombre FROM equipos
            JOIN jugador_equipo ON equipos.ID = jugador_equipo.ID_equipo
            WHERE jugador_equipo.ID_jugador = %s
    
        """
        equipos = DatabaseConnection.fetch_all(qry, (jugador_id,))

        equipos_dict = [{"id": equipo[0], "nombre": equipo[1]} for equipo in equipos]

        return jsonify(equipos_dict)
    
    #Endpoint que retorna los equipos al que NO pertenece el jugador
    @app.route('/equipos-visitantes/<int:jugador_id>', methods=['GET'])
    def get_equipos_visitantes(jugador_id):

        visitantes = """ 
            SELECT DISTINCT equipos.ID, equipos.nombre FROM equipos
            JOIN jugador_equipo ON equipos.ID = jugador_equipo.ID_equipo
            WHERE jugador_equipo.ID_jugador <> %s AND jugador_equipo.id_jugador_creador <> %s
    
        """
        equipos = DatabaseConnection.fetch_all(visitantes, (jugador_id, jugador_id))

        equipos_dict = [{"id": equipo[0], "nombre": equipo[1]} for equipo in equipos]

        return jsonify(equipos_dict)
    #Endpoint que retorna los equipos al que SI pertenece el jugador y es capitan
    @app.route('/equipos-locales/<int:jugador_id>', methods=['GET'])
    def get_equipos_locales(jugador_id):

        locales = """ 
            SELECT equipos.ID, equipos.nombre FROM equipos
            JOIN jugador_equipo ON equipos.ID = jugador_equipo.ID_equipo
            WHERE jugador_equipo.id_jugador_creador = %s AND jugador_equipo.ID_jugador = %s
    
        """
        equipos = DatabaseConnection.fetch_all(locales, (jugador_id, jugador_id))

        equipos_dict = [{"id": equipo[0], "nombre": equipo[1]} for equipo in equipos]

        return jsonify(equipos_dict)
    


    #Solicitud a equipo
    @app.route('/solicitar-equipo', methods=['POST'])
    @jwt_required()
    def solicitar_equipo():
        try:
            id_jugador = get_jwt_identity()
            data = request.get_json()
            
            id_equipo = data.get('id_equipo')
            msj = data.get('mensaje')
            if not id_equipo or not msj:
                return jsonify({"Mensaje": "Datos incompletos en la solicitud"}), 400

            paramts = (id_equipo, id_jugador, msj)

            # Verificar si el jugador ya está en el equipo
            qry_verificacion = "SELECT COUNT(*) FROM jugador_equipo WHERE ID_equipo = %s AND ID_jugador = %s"
            result = DatabaseConnection.fetch_one(qry_verificacion, (id_equipo, id_jugador))
            if result['COUNT(*)'] > 0:
                return jsonify({"Mensaje": "El jugador ya es parte del equipo"}), 400

            # Insertar la solicitud en la base de datos
            qry_solicitud = "INSERT INTO rabonatest.solicitudes (id_equipo_solicitud, id_jugador_solicitud, mensaje) VALUES (%s, %s, %s)"
            DatabaseConnection.execute_query(qry_solicitud, params=paramts)


            solicitud_final = {
                "Equipo": id_equipo,
                "Jugador": id_jugador,
                "Mensaje": msj
            }
            return jsonify(solicitud_final), 200


        except Exception as e:
            return jsonify({"Mensaje": "Error al solicitar equipo", "error": str(e)}), 500
        
    #administrar solicitudes
    @app.route('/solicitudes', methods=['GET', 'POST', 'DELETE'])
    @jwt_required()
    def solicitudes():
        id_jugador = get_jwt_identity()
        try:
            if request.method == 'GET':
                qry_capitania = "SELECT ID_Equipo FROM jugador_equipo WHERE id_jugador_creador = %s AND ID_Jugador = %s"
                dato_capitania = DatabaseConnection.fetch_one(qry_capitania, (id_jugador, id_jugador))
                if dato_capitania is None:
                    return jsonify({"Mensaje":"No eres capitan de equipo"})
                
                capitan = dato_capitania['ID_Equipo']
                qry_solicitudes = "SELECT id_solicitud, id_jugador_solicitud, mensaje FROM solicitudes WHERE id_equipo_solicitud = %s"
                solicitudes = DatabaseConnection.fetch_all(qry_solicitudes, (capitan,))
                solicitudes_dict = [{"id": solicitud[0],"id_jugador_solicitud": solicitud[1], "mensaje": solicitud[2]} for solicitud in solicitudes]
                

                return jsonify({"Datos": solicitudes_dict})
            
            elif request.method == 'POST':
                
                data = request.json
                id_jugador_solicitud = data['id_jugador_solicitud'] #Solo se recolecta el id del jugador del Json enviado
                qry_id_equipo = "SELECT ID_Equipo FROM jugador_equipo WHERE id_jugador_creador = %s AND ID_Jugador = %s"
                id_equipo_dict = DatabaseConnection.fetch_one(qry_id_equipo, (id_jugador, id_jugador))
                id_equipo = id_equipo_dict['ID_Equipo'] #ID donde el jugador es capitan
                #Insertar en jugador_equipo
                inscribir = "INSERT INTO jugador_equipo (ID_Jugador, ID_Equipo, id_jugador_creador) VALUES (%s, %s, %s)"
                DatabaseConnection.execute_query(inscribir, (id_jugador_solicitud, id_equipo, id_jugador))
                
                #Eliminar la solicitud de la tabla solicitudes
                eliminar_solicitud = "DELETE FROM solicitudes WHERE id_jugador_solicitud = %s AND id_equipo_solicitud = %s"
                DatabaseConnection.execute_query(eliminar_solicitud, (id_jugador_solicitud, id_equipo))
                
                
                return jsonify({'Mensaje': 'Solicitud del jugador aceptada con exito'})
            elif request.method == 'DELETE':
                data = request.json
                id_solicitud = data.get('id_solicitud')
                qry_delete = "DELETE FROM solicitudes WHERE (id_solicitud = %s)"

                DatabaseConnection.execute_query(qry_delete, (id_solicitud,))

                return jsonify({'Mensaje': 'Solicitud eliminada con exito'})
        except Exception as e:
            return jsonify({"Mensaje": str(e)}),500
        
    #crear enfrentamiento
    @app.route("/crearEnfrentamiento", methods=["POST"])
    @jwt_required()
    def crearEnfrentamiento():
        try:
            current_user = get_jwt_identity()
            data = request.get_json()
            print("los datos son:", data)
            lugar = data.get("lugar")
            fecha_str = data.get("fecha")
            equipo_local_nombre = data.get("equipo_local_nombre")
            equipo_visitante_nombre = data.get("equipo_visitante_nombre")

            # Convertir la fecha en formato string a un objeto datetime
            if fecha_str:
                fecha = datetime.strptime(fecha_str, "%Y-%m-%dT%H:%M")  # Formato de fecha "YYYY-MM-DDTHH:mm"
            else:
                fecha = None

            print("Fecha procesada:", fecha)
            db = DatabaseConnection()
            # Aquí va el procesamiento de los datos, como guardar en la base de datos
            query_local = "SELECT ID FROM equipos WHERE nombre = %s"
            local_result = db.fetch_one(query_local, (equipo_local_nombre,))

            query_visitante = "SELECT id FROM equipos WHERE nombre = %s"
            visitante_result = db.fetch_one(query_visitante, (equipo_visitante_nombre,))

            print(local_result)
            print(visitante_result)

            
            # Validar que ambos equipos existen
            if not local_result:
                return {"msg": f"El equipo local '{equipo_local_nombre}' no existe."}, 400
            if not visitante_result:
                return {"msg": f"El equipo visitante '{equipo_visitante_nombre}' no existe."}, 400

            local_id = local_result.get('ID') or local_result.get('id')
            visitante_id = visitante_result.get('ID') or visitante_result.get('id')

            # Verificar si el jugador pertenece al equipo mediante la consulta visitante id con la consulta seleccionando el equipo donde pertenece
            query_verificacion_visita = "SELECT ID FROM jugador_equipo WHERE ID_Jugador = %s AND ID_Equipo = %s"
            verificacion_result = db.fetch_one(query_verificacion_visita, (current_user, visitante_id))
            print(verificacion_result)
            if verificacion_result is not None:
                return {"msg":"No puedes enfrentarte en un mismo partido"}, 403
            
             # Crear el partido
            query_partido = """
            INSERT INTO partidos (lugar, fecha)
            VALUES (%s, %s)
            """
            params_partido = (lugar, fecha)

            partido_id = db.execute_query_and_return_id(query_partido, params=params_partido)

            # Agregar equipos al partido
            query_participacion = """
            INSERT INTO participacion (ID_partido, ID_equipo)
            VALUES (%s, %s)
            """
            
            params_local= (partido_id, local_id)
            params_visitante= (partido_id, visitante_id)

            db.execute_query(query_participacion, params_local)
            db.execute_query(query_participacion, params_visitante)


            return jsonify({"msg": "Datos recibidos correctamente"}), 200
        except Exception as e:
            print("Error al procesar la solicitud:", str(e))
            return {"msg": "Error al procesar los datos"}, 500

    @app.route("/crearPartidoAbierto", methods=["POST"])
    @jwt_required()
    def CrearPartidoAbierto():
        try:
            current_user = get_jwt_identity()  # Obtiene el ID del usuario autenticado
            data = request.get_json()

            lugar = data.get("lugar")
            fecha_str = data.get("fecha")
            equipo_local_nombre = data.get("equipo_local_nombre")

            # Convertir la fecha en formato string a un objeto datetime
            if fecha_str:
                fecha = datetime.strptime(fecha_str, "%Y-%m-%dT%H:%M")  # Formato de fecha "YYYY-MM-DDTHH:mm"
            else:
                fecha = None

            db = DatabaseConnection()


            # Obtener el ID del equipo local
            query_local = "SELECT ID FROM equipos WHERE nombre = %s"
            local_result = db.fetch_one(query_local, (equipo_local_nombre,))

            if not local_result:
                return {"msg": f"El equipo local '{equipo_local_nombre}' no existe."}, 400

            local_id = local_result.get('ID')
            visitante_id = None  # Deja el visitante vacío (bacante)

            # Crear el partido
            query_partido = """
            INSERT INTO partidos (lugar, fecha)
            VALUES (%s, %s)
            """
            params_partido = (lugar, fecha)

            partido_id = db.execute_query_and_return_id(query_partido, params=params_partido)

            # Agregar solo el equipo local al partido
            query_participacion = """
            INSERT INTO participacion (ID_partido, ID_equipo)
            VALUES (%s, %s)
            """
            
            params_local = (partido_id, local_id)
            db.execute_query(query_participacion, params_local)

            # No agregamos el visitante ahora, dejamos el campo vacío
            if visitante_id:
                params_visitante = (partido_id, visitante_id)
                db.execute_query(query_participacion, params_visitante)

            return jsonify({"msg": "Datos recibidos correctamente"}), 200

        except Exception as e:
            print("Error al procesar la solicitud:", str(e))
            return {"msg": "Error al procesar los datos"}, 500

    @app.route("/partidosSinVisitante", methods=["GET"])
    @jwt_required()
    def partidosSinVisitante():
        try:
            db = DatabaseConnection()
            query = """
            SELECT p.ID, p.lugar, p.fecha
            FROM partidos p
            LEFT JOIN participacion pa ON p.ID = pa.ID_partido
            GROUP BY p.ID
            HAVING COUNT(pa.ID_equipo) = 1
            """
            partidos = db.fetch_all(query)

            if partidos is None:
                return jsonify([]), 200  # Si no hay partidos, devuelve lista vacía

            # Convierte los resultados a diccionarios
            lista_partidos = [{"ID": p[0], "lugar": p[1], "fecha": str(p[2])} for p in partidos]

            return jsonify(lista_partidos), 200
        except Exception as e:
            print("Error:", e)
            return jsonify({"msg": "Error al obtener partidos"}), 500


        
    @app.route("/registrarVisitante/<int:partido_id>", methods=["POST"])
    @jwt_required()
    def registrarVisitante(partido_id):
        try:
            current_user = get_jwt_identity()  # Obtiene el ID del usuario autenticado
            print(request.get_json())
            data = request.get_json()
            
            equipo_visitante_nombre = data.get("equipo_visitante_nombre")

            db = DatabaseConnection()

            # Obtener el ID del equipo visitante
            query_visitante = "SELECT ID FROM equipos WHERE nombre = %s"
            visitante_result = db.fetch_one(query_visitante, (equipo_visitante_nombre,))

            if not visitante_result:
                return {"msg": f"El equipo '{equipo_visitante_nombre}' no existe."}, 400

            visitante_id = visitante_result.get('ID')

            # Verificar si ya está registrado el visitante en el partido
            query_check = """
            SELECT * FROM participacion 
            WHERE ID_partido = %s AND ID_equipo = %s
            """
            existing_participation = db.fetch_one(query_check, (partido_id, visitante_id))

            if existing_participation:
                return {"msg": "Este equipo ya está registrado como visitante en el partido."}, 400

            # Agregar el equipo visitante al partido
            query_participacion = """
            INSERT INTO participacion (ID_partido, ID_equipo)
            VALUES (%s, %s)
            """
            params_visitante = (partido_id, visitante_id)
            db.execute_query(query_participacion, params_visitante)
            
            return jsonify({"msg": "Equipo visitante registrado correctamente"}), 200

        except Exception as e:
            print("Error al registrar el visitante:", str(e))
            return {"msg": "Error al registrar el equipo visitante"}, 500

    @app.route('/enviar-reporte', methods=['POST'])
    def enviar_reporte():
        try:
            # Obtener los datos del reporte desde el frontend
            data = request.get_json()
            equipo_reportado = data.get('equipo_reportado')
            comentario = data.get('comentario')

            if not equipo_reportado or not comentario:
                return jsonify({'error': 'Faltan datos obligatorios'}), 400

            # Conectar a la base de datos
            db = DatabaseConnection

            # Insertar el reporte en la base de datos
            query = "INSERT INTO reportes (equipo_reportado, comentario) VALUES (%s, %s)"
            db.execute_query((equipo_reportado, comentario))

            return jsonify({'message': 'Reporte enviado correctamente'}), 200

        except Exception as e:
            return jsonify({'error': str(e)}), 500
        
    @app.route('/reportes', methods=['GET'])
    def get_reportes():
        query = "SELECT ID, ID_partido, comentario FROM reportes"
        datos = DatabaseConnection.fetch_all(query)
        return jsonify(datos)

    return app