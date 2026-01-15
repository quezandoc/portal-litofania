"""
FastAPI backend para LithoMaker Pro
"""
from fastapi import FastAPI, File, UploadFile, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import io
import logging

from core import generar_modelo_3d

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Crear app FastAPI
app = FastAPI(
    title="LithoMaker Pro API",
    description="API para generar modelos 3D a partir de imágenes",
    version="1.0.0",
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """Verificar que la API está disponible."""
    return {"status": "ok"}


@app.post("/api/generate-3d/")
async def generate_3d(
    file: UploadFile = File(...),
    shape: str = Query("Corazón", description="Forma: Corazón, Círculo, Cuadrado"),
    zoom: float = Query(1.2, ge=0.5, le=3.0, description="Factor de zoom"),
    frame_width: float = Query(3.0, ge=2.0, le=5.0, description="Ancho del marco en mm"),
    offset_x: int = Query(0, ge=-60, le=60, description="Desplazamiento X"),
    offset_y: int = Query(0, ge=-60, le=60, description="Desplazamiento Y"),
):
    """
    Genera un modelo 3D STL a partir de una imagen.
    
    - **file**: Archivo de imagen (JPG, PNG, JPEG)
    - **shape**: Forma del modelo (Corazón, Círculo, Cuadrado)
    - **zoom**: Factor de zoom (0.5 - 3.0)
    - **frame_width**: Ancho del marco en mm (2.0 - 5.0)
    - **offset_x**: Desplazamiento horizontal en píxeles (-60 a 60)
    - **offset_y**: Desplazamiento vertical en píxeles (-60 a 60)
    """
    try:
        # Validar tipo de archivo
        if file.content_type not in ["image/jpeg", "image/png"]:
            return {"detail": "Solo se aceptan archivos JPG o PNG"}

        # Leer contenido del archivo
        contents = await file.read()

        logger.info(
            f"Generando modelo: forma={shape}, zoom={zoom}, frame_width={frame_width}"
        )

        # Generar modelo
        stl_bytes = generar_modelo_3d(
            imagen_bytes=contents,
            forma=shape,
            zoom=zoom,
            frame_width=frame_width,
            offset_x=offset_x,
            offset_y=offset_y,
        )

        logger.info(f"Modelo generado exitosamente. Tamaño: {len(stl_bytes)} bytes")

        # Retornar archivo STL
        return StreamingResponse(
            io.BytesIO(stl_bytes),
            media_type="application/sla",
            headers={
                "Content-Disposition": f"attachment; filename=litho_{shape.lower()}_manifold.stl"
            },
        )

    except ValueError as e:
        logger.error(f"Error de validación: {str(e)}")
        return {"detail": str(e)}
    except Exception as e:
        logger.error(f"Error inesperado: {str(e)}")
        return {"detail": f"Error al generar el modelo: {str(e)}"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
