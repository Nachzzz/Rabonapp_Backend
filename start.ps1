# Script PowerShell para inicializar el entorno de desarrollo
# Ejecutar desde la raíz del proyecto en PowerShell (ejecutar como usuario):
#   Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass; .\start.ps1

# 1) Crear y activar venv
if (-not (Test-Path -Path .venv)) {
    python -m venv .venv
}

Write-Host "Activando entorno virtual .venv"
.\.venv\Scripts\Activate.ps1

# 2) Actualizar pip e instalar dependencias
Write-Host "Instalando dependencias..."
python -m pip install --upgrade pip
pip install -r requirements.txt

Write-Host "Instalación completada. Crear un archivo .env con las variables de DB y (opcional) JWT_SECRET_KEY si no existe."

Write-Host "Para ejecutar la app: python run.py"
