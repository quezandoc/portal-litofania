"""
Core module - Funciones de generación de modelos 3D independientes de FastAPI
"""
import numpy as np
from PIL import Image
from stl import mesh
import io
import tempfile
import os
import base64

# --- PARÁMETROS DE INGENIERÍA ---
RES_PX_MM = 5.0  # 5 px/mm = 0.2 mm/px
LADO_MM = 90.0   # Tamaño estándar
PIXELS = int(LADO_MM * RES_PX_MM)  # 450x450 px

# Espesores (Z)
MARCO_Z = 5.0
LITHO_MIN_Z = 0.6
LITHO_MAX_Z = 3.0


def obtener_mascaras(forma_tipo: str, size: int, border_mm: float):
    """Genera máscaras de corte para las diferentes formas."""
    rango = 1.6
    lin = np.linspace(-rango, rango, size)
    x, y = np.meshgrid(lin, -lin)

    units_per_mm = (rango * 2) / LADO_MM
    offset = border_mm * units_per_mm

    if forma_tipo == "Círculo":
        R = 1.3
        mask_frame = (x**2 + y**2) <= R**2
        mask_litho = (x**2 + y**2) <= (R - offset)**2

    elif forma_tipo == "Cuadrado":
        L = 1.3
        mask_frame = (np.abs(x) <= L) & (np.abs(y) <= L)
        mask_litho = (np.abs(x) <= (L - offset)) & (np.abs(y) <= (L - offset))

    elif forma_tipo == "Corazón":
        def heart_eq(cx, cy):
            return cx**2 + (cy - 0.6 * np.sqrt(np.abs(cx)))**2

        R_heart = 1.6
        mask_frame = heart_eq(x, y) <= R_heart
        mask_litho = heart_eq(x, y) <= (R_heart - offset * 1.8)

    else:
        raise ValueError(f"Forma desconocida: {forma_tipo}")

    return mask_litho, mask_frame


def generar_stl_manifold(z_grid: np.ndarray, mask_total: np.ndarray) -> np.ndarray:
    """Genera una malla cerrada (watertight) STL."""
    filas, cols = z_grid.shape

    x_lin = np.linspace(0, LADO_MM, cols)
    y_lin = np.linspace(0, LADO_MM, filas)
    X, Y = np.meshgrid(x_lin, y_lin)
    Y = np.flipud(Y)

    faces = []
    valid_pixels = np.argwhere(mask_total)

    for i, j in valid_pixels:
        if i >= filas - 1 or j >= cols - 1:
            continue

        z0 = z_grid[i, j]
        z1 = z_grid[i, j + 1]
        z2 = z_grid[i + 1, j]
        z3 = z_grid[i + 1, j + 1]

        x0, y0 = X[i, j], Y[i, j]
        x1, y1 = X[i, j + 1], Y[i, j + 1]
        x2, y2 = X[i + 1, j], Y[i + 1, j]
        x3, y3 = X[i + 1, j + 1], Y[i + 1, j + 1]

        vt0 = [x0, y0, z0]
        vb0 = [x0, y0, 0]
        vt1 = [x1, y1, z1]
        vb1 = [x1, y1, 0]
        vt2 = [x2, y2, z2]
        vb2 = [x2, y2, 0]
        vt3 = [x3, y3, z3]
        vb3 = [x3, y3, 0]

        # Cara superior
        faces.append([vt0, vt2, vt3])
        faces.append([vt0, vt3, vt1])

        # Cara inferior
        faces.append([vb0, vb3, vb2])
        faces.append([vb0, vb1, vb3])

        # Paredes
        if i == 0 or not mask_total[i - 1, j]:
            faces.append([vt0, vt1, vb1])
            faces.append([vt0, vb1, vb0])

        if (i + 1) >= filas - 1 or not mask_total[i + 1, j]:
            faces.append([vt2, vb3, vt3])
            faces.append([vt2, vb2, vb3])

        if j == 0 or not mask_total[i, j - 1]:
            faces.append([vt0, vb2, vt2])
            faces.append([vt0, vb0, vb2])

        if (j + 1) >= cols - 1 or not mask_total[i, j + 1]:
            faces.append([vt1, vt3, vb3])
            faces.append([vt1, vb3, vb1])

    return np.array(faces)


def generar_modelo_3d(
    imagen_bytes: bytes,
    forma: str,
    zoom: float,
    frame_width: float,
    offset_x: int,
    offset_y: int,
) -> bytes:
    """
    Genera un archivo STL a partir de una imagen.
    
    Args:
        imagen_bytes: Bytes de la imagen
        forma: "Corazón", "Círculo" o "Cuadrado"
        zoom: Factor de zoom (0.5-3.0)
        frame_width: Ancho del marco en mm (2.0-5.0)
        offset_x: Desplazamiento X en píxeles (-60 a 60)
        offset_y: Desplazamiento Y en píxeles (-60 a 60)
    
    Returns:
        Bytes del archivo STL
    """
    # Cargar imagen
    img = Image.open(io.BytesIO(imagen_bytes)).convert("L")
    img_res = img.resize(
        (
            int(PIXELS * zoom),
            int((img.height / img.width) * PIXELS * zoom),
        ),
        Image.Resampling.LANCZOS,
    )

    # Crear lienzo
    canvas = Image.new("L", (PIXELS, PIXELS), color=255)
    pos_x = (PIXELS - img_res.width) // 2 + int(offset_x * RES_PX_MM)
    pos_y = (PIXELS - img_res.height) // 2 + int(offset_y * RES_PX_MM)
    canvas.paste(img_res, (pos_x, pos_y))

    # Obtener máscaras
    m_litho, m_frame = obtener_mascaras(forma, PIXELS, frame_width)
    img_array = np.array(canvas)

    # Mapear alturas Z
    z_litho = LITHO_MAX_Z - (img_array / 255.0) * (LITHO_MAX_Z - LITHO_MIN_Z)
    z_final = np.where(m_litho, z_litho, MARCO_Z)

    # Generar malla
    faces = generar_stl_manifold(z_final, m_frame)

    if len(faces) == 0:
        raise ValueError("La geometría está vacía. Intenta ajustar el zoom.")

    # Crear y guardar STL
    modelo_mesh = mesh.Mesh(np.zeros(faces.shape[0], dtype=mesh.Mesh.dtype))
    modelo_mesh.vectors = faces

    # Guardar en archivo temporal (numpy-stl requiere ruta de archivo)
    with tempfile.NamedTemporaryFile(suffix=".stl", delete=False) as tmp_file:
        tmp_path = tmp_file.name
    
    try:
        modelo_mesh.save(tmp_path)
        with open(tmp_path, "rb") as f:
            stl_bytes = f.read()
        return stl_bytes
    finally:
        # Limpiar archivo temporal
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
