"""
Core module - Generación de modelos 3D STL desde imágenes raster
Litografía traslúcida con contorno estructural

Este módulo implementa un pipeline completo para convertir una imagen raster
en un modelo STL sólido (watertight), combinando:
- Relieve tipo litografía (heightmap)
- Marco estructural definido por un contorno rojo
- Paredes laterales continuas (vectoriales) para evitar efecto escalera
"""

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from stl import mesh
import io
import tempfile
import os

from core import mesh_to_stl_bytes


# ============================================================
# PARÁMETROS DE INGENIERÍA (dimensiones físicas y resolución)
# ============================================================

LADO_MM = 90.0        # Tamaño físico total del modelo en X/Y (mm)
PIXELS = 600          # Resolución de trabajo (más alto = más detalle)
RES_PX_MM = 5.0      # Resolución efectiva (píxeles por mm)

# --- Litografía (frente / relieve) ---
BASE_Z = 0.4          # Espesor mínimo de la pieza
LITHO_MIN_Z = 0.6     # Relieve mínimo (zonas claras)
LITHO_MAX_Z = 3.0     # Relieve máximo (zonas oscuras)

# --- Marco estructural ---
MARCO_Z = 5.0         # Altura total del marco
MARCO_MM = 4.6        # Ancho físico del marco


# ============================================================
# UTILIDADES DE PROCESAMIENTO DE MÁSCARAS
# ============================================================

def erode(mask: np.ndarray, iterations: int) -> np.ndarray:
    """
    Erosión binaria simple con vecindad 4.
    Se usa para:
    - Definir el borde interior del marco
    - Evitar huecos y problemas topológicos
    """
    result = mask.copy()
    for _ in range(iterations):
        result = (
            result &
            np.roll(result, 1, 0) &
            np.roll(result, -1, 0) &
            np.roll(result, 1, 1) &
            np.roll(result, -1, 1)
        )
    return result


# ============================================================
# GENERACIÓN DE TOPO + BASE DESDE HEIGHTMAP
# ============================================================

def generar_stl_manifold(z_grid: np.ndarray, mask: np.ndarray) -> np.ndarray:
    """
    Genera las caras superiores (relieve) y la base plana del modelo.
    Aún crea paredes laterales por píxel, que luego se reemplazan.
    """
    filas, cols = z_grid.shape

    x_lin = np.linspace(0, LADO_MM, cols)
    y_lin = np.linspace(0, LADO_MM, filas)
    X, Y = np.meshgrid(x_lin, y_lin)
    Y = np.flipud(Y)

    faces = []
    valid_pixels = np.argwhere(mask)

    for i, j in valid_pixels:
        if i >= filas - 1 or j >= cols - 1:
            continue

        z0, z1 = z_grid[i, j], z_grid[i, j + 1]
        z2, z3 = z_grid[i + 1, j], z_grid[i + 1, j + 1]

        x0, y0 = X[i, j], Y[i, j]
        x1, y1 = X[i, j + 1], Y[i, j + 1]
        x2, y2 = X[i + 1, j], Y[i + 1, j]
        x3, y3 = X[i + 1, j + 1], Y[i + 1, j + 1]

        vt0 = [x0, y0, z0]
        vt1 = [x1, y1, z1]
        vt2 = [x2, y2, z2]
        vt3 = [x3, y3, z3]

        vb0 = [x0, y0, 0]
        vb1 = [x1, y1, 0]
        vb2 = [x2, y2, 0]
        vb3 = [x3, y3, 0]

        # Cara superior (relieve)
        faces.append([vt0, vt2, vt3])
        faces.append([vt0, vt3, vt1])

        # Cara inferior (base)
        faces.append([vb0, vb3, vb2])
        faces.append([vb0, vb1, vb3])

        # Paredes voxelizadas (se mantienen pero luego se sustituyen)
        if i == 0 or not mask[i - 1, j]:
            faces.append([vt0, vt1, vb1])
            faces.append([vt0, vb1, vb0])

        if i == filas - 2 or not mask[i + 1, j]:
            faces.append([vt2, vb3, vt3])
            faces.append([vt2, vb2, vb3])

        if j == 0 or not mask[i, j - 1]:
            faces.append([vt0, vb2, vt2])
            faces.append([vt0, vb0, vb2])

        if j == cols - 2 or not mask[i, j + 1]:
            faces.append([vt1, vt3, vb3])
            faces.append([vt1, vb3, vb1])

    return np.array(faces)

# ============================================================
# FUNCIÓN PRINCIPAL
# ============================================================

def generar_modelo_3d(imagen_bytes: bytes) -> bytes:
    """
    Pipeline principal:
    - Detecta contorno rojo
    - Rellena interior
    - Genera relieve (litografía)
    - Construye marco estructural
    - Genera STL watertight
    """

    # --- Cargar imagen ---
    img = Image.open(io.BytesIO(imagen_bytes)).convert("RGB")
    img = img.resize((PIXELS, PIXELS), Image.Resampling.LANCZOS)
    rgb = np.array(img)

    # --- Detectar contorno rojo ---
    red = (
        (rgb[..., 0] > 200) &
        (rgb[..., 1] < 60) &
        (rgb[..., 2] < 60)
    )

    if not np.any(red):
        raise ValueError("No se detectó borde rojo")

     # --- Rellenar interior ---
    from scipy.ndimage import binary_fill_holes
    interior = binary_fill_holes(red)

    # --- Litofanía desde gris ---
    gray = (
        0.299 * rgb[..., 0] +
        0.587 * rgb[..., 1] +
        0.114 * rgb[..., 2]
    )

    relieve = LITHO_MIN_Z + (1 - gray / 255.0) * (LITHO_MAX_Z - LITHO_MIN_Z)

    # --- Mapa Z final ---
    z = np.zeros_like(relieve, dtype=float)
    z[interior] = BASE_Z + relieve[interior]
    z[red] = MARCO_Z

    mask = z > 0

    faces = generar_stl_manifold(z, mask)

    m = mesh.Mesh(np.zeros(faces.shape[0], dtype=mesh.Mesh.dtype))
    m.vectors = faces

    return mesh_to_stl_bytes(m)
