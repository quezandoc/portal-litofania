@echo off
REM Script para ejecutar el backend en Windows

echo 🚀 LithoMaker Pro - Backend API
echo ================================

REM Verificar si existe virtual env
if not exist "venv" (
    echo 📦 Creando entorno virtual...
    python -m venv venv
)

REM Activar virtual env
call venv\Scripts\activate.bat

REM Instalar dependencias
echo 📚 Instalando dependencias...
pip install -q -r requirements.txt

REM Ejecutar servidor
echo ✅ Iniciando servidor en http://localhost:8000
echo 📖 Documentación en http://localhost:8000/docs
echo.

uvicorn main:app --reload --port 8000
