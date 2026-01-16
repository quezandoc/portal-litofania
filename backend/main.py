"""
FastAPI backend para LithoMaker Pro
Frontend-driven: recibe imagen final y genera STL
"""

from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import io
import logging

from core import generar_modelo_3d

# -----------------------
# Configuración logging
# -----------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("lithomaker")

# -----------------------
# App FastAPI
# -----------------------
app = FastAPI(
    title="LithoMaker Pro API",
    description="API para generar modelos STL desde imágenes raster",
    version="2.0.0",
)

# -----------------------
# CORS
# -----------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ajusta en producción
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------
# Health check
# -----------------------
@app.get("/health")
async def health_check():
    return {"status": "ok"}

# -----------------------
# Generar STL
# -----------------------
@app.post("/api/generate-3d/")
async def generate_3d(file: UploadFile = File(...)):
    """
    Genera un STL a partir de una imagen FINAL enviada por el frontend.

    - Negro = vacío
    - Blanco / gris = relieve
    """

    if file.content_type not in ("image/png", "image/jpeg"):
        return {"detail": "Solo se aceptan imágenes PNG o JPG"}

    try:
        image_bytes = await file.read()
        logger.info("Generando STL desde imagen raster")

        stl_bytes = generar_modelo_3d(image_bytes)

        logger.info(f"STL generado ({len(stl_bytes)} bytes)")

        return StreamingResponse(
            io.BytesIO(stl_bytes),
            media_type="application/sla",
            headers={
                "Content-Disposition": "attachment; filename=litho.stl"
            },
        )

    except ValueError as e:
        logger.warning(f"Error de validación: {e}")
        return {"detail": str(e)}

    except Exception as e:
        logger.exception("Error inesperado generando STL")
        return {"detail": "Error interno al generar el modelo"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
