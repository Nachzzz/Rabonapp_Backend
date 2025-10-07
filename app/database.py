import os
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

# Cargar variables desde un archivo .env (opcional)
load_dotenv()

class DatabaseConnection:
    _connection = None

    print("MYSQLUSER:", os.getenv("MYSQLUSER"))
    print("MYSQLPASSWORD:", os.getenv("MYSQLPASSWORD"))
    print("MYSQLHOST:", os.getenv("MYSQLHOST"))
    print("MYSQLPORT:", os.getenv("MYSQLPORT"))
    print("MYSQLDATABASE:", os.getenv("MYSQLDATABASE"))



    @classmethod
    def get_connection(cls):
        """Obtiene una conexión a la base de datos, reutilizándola si ya existe."""
        if cls._connection is None or not cls._connection.is_connected():
            try:
                cls._connection = mysql.connector.connect(
                    user=os.getenv("MYSQLUSER"),  
                    password=os.getenv("MYSQLPASSWORD"),
                    host=os.getenv("MYSQLHOST"),
                    port=os.getenv("MYSQLPORT"),
                    database=os.getenv("MYSQLDATABASE")
                )
                print("✅ Conexión exitosa a MySQL en Railway")
            except Error as e:
                print(f"❌ Error al conectar a la base de datos: {e}")
                cls._connection = None
        return cls._connection

    @classmethod
    def execute_query(cls, query, params=None):
        """Ejecuta una consulta que no devuelve resultados (INSERT, UPDATE, DELETE)."""
        try:
            connection = cls.get_connection()
            # usar cursor bufferizado para consumir resultados y evitar 'Unread result found'
            with connection.cursor(buffered=True) as cursor:
                cursor.execute(query, params)
                connection.commit()
                return cursor.rowcount
        except Error as e:
            if 'Unread result found' in str(e):
                print(f"❌ Error en execute_query: Unread result found. Asegúrate de consumir resultados antes de ejecutar nuevas consultas. Detalle: {e}")
            else:
                print(f"❌ Error en execute_query: {e}")
            return None

    @classmethod
    def execute_query_and_return_id(cls, query, params=None):
        """Ejecuta una consulta y devuelve el ID del último registro insertado."""
        try:
            connection = cls.get_connection()
            with connection.cursor(buffered=True) as cursor:
                cursor.execute(query, params)
                connection.commit()
                return cursor.lastrowid
        except Error as e:
            if 'Unread result found' in str(e):
                print(f"❌ Error en execute_query_and_return_id: Unread result found. Detalle: {e}")
            else:
                print(f"❌ Error en execute_query_and_return_id: {e}")
            return None

    @classmethod
    def fetch_one(cls, query, params=None):
        """Ejecuta una consulta y devuelve una sola fila."""
        try:
            connection = cls.get_connection()
            # dictionary=True para obtener resultados como dicts; buffered=True evita 'Unread result found'
            with connection.cursor(dictionary=True, buffered=True) as cursor:
                cursor.execute(query, params)
                result = cursor.fetchone()
                return result
        except Error as e:
            if 'Unread result found' in str(e):
                print(f"❌ Error en fetch_one: Unread result found. Asegúrate de cerrar/consumir cursores anteriores. Detalle: {e}")
            else:
                print(f"❌ Error en fetch_one: {e}")
            return None

    @classmethod
    def fetch_all(cls, query, params=None):
        """Ejecuta una consulta y devuelve todas las filas."""
        try:
            connection = cls.get_connection()
            with connection.cursor(dictionary=True, buffered=True) as cursor:
                cursor.execute(query, params)
                results = cursor.fetchall()
                return results
        except Error as e:
            if 'Unread result found' in str(e):
                print(f"❌ Error en fetch_all: Unread result found. Detalle: {e}")
            else:
                print(f"❌ Error en fetch_all: {e}")
            return None

    @classmethod
    def close_connection(cls):
        """Cierra la conexión a la base de datos."""
        if cls._connection and cls._connection.is_connected():
            cls._connection.close()
            cls._connection = None
            print("🔌 Conexión a la base de datos cerrada.")



# import os
# import mysql.connector

# class DatabaseConnection:
#     _connection = None

#     @classmethod
#     def get_connection(cls):
#         if cls._connection is None:
#             cls._connection = mysql.connector.connect(
#                 user=os.getenv("MYSQLUSER"),  # Asegúrate que coincide con Railway
#                 password=os.getenv("MYSQLPASSWORD"),
#                 host=os.getenv("MYSQLHOST"),
#                 port=os.getenv("MYSQLPORT"),
#                 database=os.getenv("MYSQLDATABASE")
#             )
#         return cls._connection



#     @classmethod
#     def execute_query(cls, query, params=None):
#         cursor = cls.get_connection().cursor()
#         cursor.execute(query, params)
#         cls._connection.commit()
#         return cursor
    
#     @classmethod
#     def execute_query_and_return_id(cls, query, params=None):
#         cursor = cls.get_connection().cursor()
#         cursor.execute(query, params)
#         cls._connection.commit()
#         return cursor.lastrowid
    
#     @classmethod
#     def fetch_one(cls, query, params=None):
#         cursor = cls.get_connection().cursor(dictionary=True)
#         cursor.execute(query, params)
#         return cursor.fetchone()

#     @classmethod
#     def fetch_all(cls, query, params=None):
#         cursor = cls.get_connection().cursor()
#         cursor.execute(query, params)
#         return cursor.fetchall()

#     @classmethod
#     def close_connection(cls):
#         if cls._connection is not None:
#             cls._connection.close()
#             cls._connection = None