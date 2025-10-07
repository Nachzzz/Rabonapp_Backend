# BackEnd_Rabonapp

Instrucciones para inicializar el backend (Windows - PowerShell)

Requisitos:
- Python 3.11 o superior
- MySQL (o acceso a una instancia remota)

Pasos rápidos:

1) Crear y activar un entorno virtual (PowerShell)

    python -m venv .venv
    .\.venv\Scripts\Activate.ps1

2) Actualizar pip e instalar dependencias

    python -m pip install --upgrade pip
    pip install -r requirements.txt

3) Variables de entorno

Crea un archivo `.env` en la raíz con las siguientes variables (ajusta valores):

    MYSQLUSER=tu_usuario
    MYSQLPASSWORD=tu_contraseña
    MYSQLHOST=127.0.0.1
    MYSQLPORT=3306
    MYSQLDATABASE=rabonatest

Opcional: cambiar `JWT_SECRET_KEY` dentro de `app/__init__.py` o leerlo desde env para producción.

4) Probar la conexión a la base de datos

    python app\test_db.py

Deberías ver `✅ Conexión exitosa a MySQL en Railway` si se conecta correctamente.

5) Ejecutar la aplicación

    python run.py

La aplicación levantará un servidor Flask en `127.0.0.1:5000` por defecto.

Notas:
- `config.py` tiene `DEBUG=True` y `SERVER_NAME=127.0.0.1:5000`.
- Recomendación: mover los secretos (JWT, credenciales) a variables de entorno.
- Para producción, usar `gunicorn` o un servicio WSGI y configurar `SERVER_NAME` y certificados.

Si quieres, puedo:
- Añadir soporte para leer `JWT_SECRET_KEY` desde `.env` y eliminar la clave dura en `app/__init__.py`.
- Crear un script PowerShell `start.ps1` que automatice los pasos.
