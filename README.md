# LithoMaker Pro - Full Stack

Aplicación web para generar modelos 3D (litofanías) a partir de imágenes. 

**Frontend**: Svelte + Shadcn/ui
**Backend**: FastAPI + uvicorn

```
portal-litofania/
├── frontend/          # Aplicación Svelte
│   ├── src/
│   ├── package.json
│   └── ...
├── backend/           # API FastAPI
│   ├── main.py       # Aplicación principal
│   ├── core.py       # Lógica de generación
│   ├── requirements.txt
│   └── ...
├── docker-compose.yml # Orquestación de servicios
└── README.md
```

## Ejecución Rápida

### Opción 1: Modo Desarrollo (Recomendado)

#### Backend
```bash
cd backend
chmod +x run.sh      # En Linux/Mac
./run.sh             # En Linux/Mac
# O en Windows
run.bat
```

El backend estará en: **http://localhost:8000**
Documentación API: **http://localhost:8000/docs**

#### Frontend (en otra terminal)
```bash
cd frontend
npm install          # Solo primera vez
npm run dev
```

El frontend estará en: **http://localhost:5173**

### Opción 2: Con Docker Compose

```bash
docker-compose up
```

Frontend: http://localhost:5173
Backend: http://localhost:8000

## Estructura

### Backend
- `main.py` - Aplicación FastAPI con endpoints
- `core.py` - Lógica de generación de modelos 3D
- `requirements.txt` - Dependencias Python
- `test_api.py` - Script de prueba

### Frontend  
- `/src/routes/+page.svelte` - Página principal
- `/src/lib/api.ts` - Cliente HTTP para la API
- `/src/lib/components/` - Componentes reutilizables

## API Endpoints

### GET /health
Verifica que el servidor está disponible.

### POST /api/generate-3d/
Genera un modelo 3D a partir de una imagen.

**Parámetros:**
- `file` (File): Imagen JPG o PNG
- `shape` (string): "Corazón", "Círculo" o "Cuadrado"
- `zoom` (float): 0.5 - 3.0
- `frame_width` (float): 2.0 - 5.0 mm
- `offset_x` (int): -60 a 60 píxeles
- `offset_y` (int): -60 a 60 píxeles

**Respuesta:** Archivo STL binario

## Tecnologías

### Frontend
- **Svelte 5** - Framework reactivo
- **SvelteKit** - Meta-framework para SSR/SSG
- **Shadcn/ui** - Componentes UI basados en bits-ui
- **Tailwind CSS** - Estilos utility-first
- **Lucide Icons** - Iconografía

### Backend
- **FastAPI** - Framework web moderno y rápido
- **Uvicorn** - Servidor ASGI
- **NumPy** - Cálculos numéricos
- **Pillow** - Procesamiento de imágenes
- **NumPy-STL** - Generación de archivos STL

## Desarrollo

### Instalación de dependencias

Backend:
```bash
cd backend
pip install -r requirements.txt
```

Frontend:
```bash
cd frontend
npm install
```

### Variables de entorno

Backend (`backend/.env`):
```
HOST=0.0.0.0
PORT=8000
RELOAD=true
```

Frontend (`frontend/.env`):
```
VITE_API_URL=http://localhost:8000
```

## Scripts útiles

### Backend
```bash
# Desarrollo con recarga automática
uvicorn main:app --reload --port 8000

# Producción
uvicorn main:app --host 0.0.0.0 --port 8000

# Con Gunicorn (producción)
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app
```

### Frontend
```bash
# Desarrollo
npm run dev

# Build de producción
npm run build

# Preview de build
npm run preview

# Linting
npm run lint
```

## Troubleshooting

### Backend no conecta
- Verificar que está corriendo en `http://localhost:8000`
- Revisar CORS en `main.py`
- Comprobar firewall

### Frontend no carga datos
- Verificar URL de API en `.env`
- Abrir DevTools para ver errores de red
- Comprobar que el backend está disponible

### Error "Cannot find module"
- Backend: `pip install -r requirements.txt`
- Frontend: `npm install`

## Licencia

Privado

## Autor

Desarrollado con ❤️
