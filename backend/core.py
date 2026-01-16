"""
Core module - Generación de modelos 3D STL desde imágenes raster
Litografía traslúcida con contorno estructural
"""

import numpy as np
from PIL import Image
from stl import mesh
import io
import tempfile
import os

# --- PARÁMETROS DE INGENIERÍA ---
LADO_MM = 90.0
PIXELS = 900

# Litografía (traslúcido)
BASE_Z = 0.4  
LITHO_MIN_Z = 0.6  
LITHO_MAX_Z = 3.0

# Marco
MARCO_Z = 5.0
MARCO_MM = 4.6

def smooth_mask(mask: np.ndarray, radius: int = 2) -> np.ndarray:
    """Suavizado simple por promedio local."""
    acc = np.zeros_like(mask, dtype=float)
    count = 0

    for dx in range(-radius, radius + 1):
        for dy in range(-radius, radius + 1):
            acc += np.roll(np.roll(mask, dx, axis=0), dy, axis=1)
            count += 1

    return acc / count


def erode(mask: np.ndarray, iterations: int) -> np.ndarray:
    """Erosión simple 4-neighbors (determinista, sin scipy)."""
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


def generar_stl_manifold(z_grid: np.ndarray, mask: np.ndarray) -> np.ndarray:
    """Genera malla STL cerrada (watertight)."""
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

        # Top
        faces.append([vt0, vt2, vt3])
        faces.append([vt0, vt3, vt1])

        # Bottom
        faces.append([vb0, vb3, vb2])
        faces.append([vb0, vb1, vb3])

        # Walls
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

def generar_modelo_3d(imagen_bytes: bytes) -> bytes:
    """
    Versión sencilla y correcta:
    - Rojo -> contorno / marco estructural
    - Interior (dentro del rojo) -> relleno sólido con relieve según gris
    - Fuera del rojo -> vacío
    """

    # 1. Leer / redimensionar
    img = Image.open(io.BytesIO(imagen_bytes)).convert("RGB")
    img = img.resize((PIXELS, PIXELS), Image.Resampling.LANCZOS)
    img_rgb = np.array(img)

    # 2. Detectar contorno rojo (boolean)
    red_mask = (
        (img_rgb[:, :, 0] > 200) &
        (img_rgb[:, :, 1] < 60) &
        (img_rgb[:, :, 2] < 60)
    ).astype(bool)

    red_float = smooth_mask(red_mask.astype(float), radius=2)
    red_smooth = red_float > 0.4

    if not np.any(red_smooth):
        raise ValueError("No se detectó contorno rojo")

    # --- Helper: flood-fill exterior para rellenar interior del contorno ---
    from collections import deque

    def fill_inside_border(border: np.ndarray) -> np.ndarray:
        h, w = border.shape
        exterior = np.zeros_like(border, dtype=bool)
        q = deque()

        # añadir todos los píxeles de la periferia que no sean borde
        for x in range(h):
            if not border[x, 0]:
                q.append((x, 0))
            if not border[x, w - 1]:
                q.append((x, w - 1))
        for y in range(w):
            if not border[0, y]:
                q.append((0, y))
            if not border[h - 1, y]:
                q.append((h - 1, y))

        # BFS para marcar exterior (no cruza el borde)
        while q:
            i, j = q.popleft()
            if i < 0 or j < 0 or i >= h or j >= w:
                continue
            if exterior[i, j] or border[i, j]:
                continue
            exterior[i, j] = True
            q.append((i + 1, j))
            q.append((i - 1, j))
            q.append((i, j + 1))
            q.append((i, j - 1))

        # interior = no-exterior y no-border
        interior = (~exterior) & (~border)
        return interior

    # 3. Rellenar interior a partir del contorno rojo
    inner_filled = fill_inside_border(red_smooth)
    shape_mask = red_smooth | inner_filled    # todo lo que tendrá material
    frame_mask = red_smooth.copy()            # el rojo será la banda visible del marco

    # 4. Gris para relieve (luminancia) y mapa de profundidad
    gray = (
        0.299 * img_rgb[:, :, 0] +
        0.587 * img_rgb[:, :, 1] +
        0.114 * img_rgb[:, :, 2]
    ).astype(np.uint8)

    # invertimos: negro -> más grosor, blanco -> menos
    depth = 1.0 - (gray / 255.0)
    relieve = LITHO_MIN_Z + depth * (LITHO_MAX_Z - LITHO_MIN_Z)

    # 5. Construir el marco físico (opcional: erosionar el rojo para crear anillo)
    px_per_mm = PIXELS / LADO_MM
    marco_px = max(1, int(MARCO_MM * px_per_mm))

    # Usamos la erode original (actúa sobre border/red_smooth)
    inner_border = erode(red_smooth, marco_px)
    frame_mask = red_smooth & ~inner_border
    inner_mask = inner_filled   # el interior relleno

    # 6. Alturas finales: interior = base + relieve, marco = MARCO_Z
    z_final = np.zeros_like(relieve, dtype=float)
    z_final[inner_mask] = BASE_Z + relieve[inner_mask]
    z_final[frame_mask] = MARCO_Z

    # 7. Generar STL sobre la máscara derivada del heightmap (firme)
    solid_mask = z_final > 0
    faces = generar_stl_manifold(z_final, solid_mask)

    if faces.size == 0:
        raise ValueError("La geometría resultante está vacía (ajusta parámetros o la imagen).")

    modelo_mesh = mesh.Mesh(np.zeros(faces.shape[0], dtype=mesh.Mesh.dtype))
    modelo_mesh.vectors = faces

    # 8. Guardar temporal y devolver bytes
    with tempfile.NamedTemporaryFile(suffix=".stl", delete=False) as tmp:
        path = tmp.name

    try:
        modelo_mesh.save(path)
        with open(path, "rb") as f:
            return f.read()
    finally:
        if os.path.exists(path):
            os.remove(path)
