#!/bin/bash
# Script para ejecutar el backend

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}🚀 LithoMaker Pro - Backend API${NC}"
echo "================================"

# Verificar si existe virtual env
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}📦 Creando entorno virtual...${NC}"
    python -m venv venv
fi

# Activar virtual env
source venv/bin/activate

# Instalar dependencias
echo -e "${YELLOW}📚 Instalando dependencias...${NC}"
pip install -q -r requirements.txt

# Ejecutar servidor
echo -e "${GREEN}✅ Iniciando servidor en http://localhost:8000${NC}"
echo -e "${GREEN}📖 Documentación en http://localhost:8000/docs${NC}"
echo ""

uvicorn main:app --reload --port 8000
