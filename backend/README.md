# LithoMaker Pro - Backend API

Backend FastAPI para generar modelos 3D (archivos STL) a partir de imágenes.

## Instalación

```bash
# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

## Ejecutar el servidor

```bash
# Método 1: Usando uvicorn directamente
uvicorn main:app --reload --port 8000

# Método 2: Desde Python
python main.py
```

El servidor estará disponible en `http://localhost:8000`

## Documentación API

Una vez que el servidor esté corriendo, puedes acceder a:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Endpoints

### Health Check
```
GET /health
```
Verifica que el servidor está disponible.

### Generar Modelo 3D
```
POST /api/generate-3d/
```

**Parámetros:**
- `file` (File): Imagen JPG o PNG
- `shape` (string): "Corazón", "Círculo" o "Cuadrado"
- `zoom` (float): Factor de zoom (0.5 - 3.0)
- `frame_width` (float): Ancho del marco en mm (2.0 - 5.0)
- `offset_x` (int): Desplazamiento X en píxeles (-60 a 60)
- `offset_y` (int): Desplazamiento Y en píxeles (-60 a 60)

**Respuesta:**
- Archivo STL binario descargable

## Estructura del proyecto

```
backend/
├── main.py           # Aplicación FastAPI
├── core.py          # Lógica de generación de modelos
├── requirements.txt # Dependencias
└── README.md       # Este archivo
```

## Variables de entorno

Puedes configurar el puerto y el host:

```bash
# Puerto personalizado
uvicorn main:app --host 0.0.0.0 --port 8080

# Solo localhost
uvicorn main:app --host 127.0.0.1 --port 8000
```

## Desarrollo

Para desarrollo con recarga automática:

```bash
uvicorn main:app --reload --port 8000
```

La flag `--reload` reinicia el servidor cuando hay cambios en los archivos.
