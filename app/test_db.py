from database import DatabaseConnection

# Prueba la conexión
connection = DatabaseConnection.get_connection()

if connection:
    print("✅ Conexión exitosa a MySQL en Railway")
    DatabaseConnection.close_connection()
else:
    print("❌ Error al conectar a MySQL")
