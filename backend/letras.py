# ============================================================
# IMPORTS Y DEPENDENCIAS
# ============================================================
# numpy        → manejo de arrays, máscaras y vértices
# PIL          → renderizado de texto a imagen (heightmap)
# stl.mesh     → creación del STL
# mesh_to_stl  → conversión final a bytes (API / descarga)
# ============================================================

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from stl import mesh
import math

from core import mesh_to_stl_bytes


# ============================================================
# PARÁMETROS DE INGENIERÍA (ESCALA Y DIMENSIONES FÍSICAS)
# ============================================================

# Resolución global:
# 5 píxeles representan 1 mm físico
RES_PX_MM = 5.0

# Dimensiones del bloque base (mm)
BASE_ANCHO_MM = 45.0
BASE_ALTO_MM  = 20.0
BASE_Z_MM     = 90.0     # altura total del bloque

# Dimensiones del plano donde vive el texto (mm)
TEXTO_X_MM = 90.0        # alto del texto (vertical)
TEXTO_Y_MM = 45.0        # ancho del texto
TEXTO_Z_MM = 12.0         # espesor del texto (extrusión)

# Cantidad máxima de caracteres pensada para el escalado automático
MAX_CHARS = 12


# ============================================================
# CARGA DE FUENTE TIPOGRÁFICA
# ============================================================

def cargar_fuente(size_px):
    """
    Carga una fuente TrueType en tamaño píxel.
    Si falla, utiliza la fuente por defecto del sistema.
    """
    try:
        return ImageFont.truetype("./Montserrat-ExtraBold.ttf", int(size_px))
    except:
        return ImageFont.load_default()


# ============================================================
# GENERACIÓN DEL HEIGHTMAP DEL TEXTO
# ============================================================
def generar_texto_heightmap(texto: str, ancho_mm=TEXTO_X_MM, alto_mm=TEXTO_Y_MM, debug=False):

    px_w = int(ancho_mm * RES_PX_MM)
    px_h = int(alto_mm * RES_PX_MM)

    img = Image.new("L", (px_w, px_h), 0)
    draw = ImageDraw.Draw(img)

    n = max(len(texto), 1)
    FONT_BASE_PX = int(px_h * 0.8)
    scale = min(1.0, MAX_CHARS / n)
    font_size = int(FONT_BASE_PX * scale)
    font = cargar_fuente(font_size)

    # -------------------------------------------------
    # 1️⃣ MEDICIÓN CORRECTA DEL ANCHO (NO baseline)
    # -------------------------------------------------
    bbox = draw.textbbox((0, 0), texto, font=font, anchor="lt")
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]

    # Ajuste FINAL si aún se pasa del ancho
    if text_w > px_w:
        font_size = int(font_size * (px_w / text_w) * 0.98)
        font = cargar_fuente(font_size)
        bbox = draw.textbbox((0, 0), texto, font=font, anchor="lt")
        text_w = bbox[2] - bbox[0]

    # -------------------------------------------------
    # 2️⃣ POSICIONAMIENTO
    # -------------------------------------------------
    x = (px_w - text_w) // 2

    # Baseline EXACTO en el borde inferior
    baseline_y = px_h

    # -------------------------------------------------
    # 3️⃣ DIBUJO CON BASELINE REAL
    # -------------------------------------------------
    draw.text(
        (x, baseline_y),
        texto,
        fill=255,
        font=font,
        anchor="ls"
    )

    if debug:
        img.show()

    mask = np.array(img) > 128
    z = np.zeros_like(mask, dtype=float)
    z[mask] = 2.0

    return z, mask



# ============================================================
# MOVIMIENTO DE FACES
# ============================================================

def trasladar_faces(faces, dx=0, dy=0, dz=0):
    faces = faces.copy()
    faces[:, :, 0] += dx
    faces[:, :, 1] += dy
    faces[:, :, 2] += dz
    return faces


def rotar_faces(faces, eje="y", grados=90, centro=None):
    """
    Rota un array de caras STL alrededor de un eje.
    
    faces  : ndarray (N, 3, 3)
    eje    : "x", "y" o "z"
    grados : ángulo de rotación
    centro : (x, y, z) o None → rota respecto al origen
    """
    theta = math.radians(grados)
    c, s = math.cos(theta), math.sin(theta)

    if eje == "x":
        R = np.array([[1, 0, 0],
                      [0, c, -s],
                      [0, s,  c]])
    elif eje == "y":
        R = np.array([[ c, 0, s],
                      [ 0, 1, 0],
                      [-s, 0, c]])
    elif eje == "z":
        R = np.array([[c, -s, 0],
                      [s,  c, 0],
                      [0,  0, 1]])
    else:
        raise ValueError("Eje debe ser 'x', 'y' o 'z'")

    f = faces.reshape(-1, 3)

    if centro is not None:
        centro = np.array(centro)
        f = f - centro

    f = f @ R.T

    if centro is not None:
        f = f + centro

    return f.reshape(faces.shape)

def extruir_faces_x(faces, espesor_mm):
    """
    Extruye un sólido existente en el eje X,
    generando un volumen con espesor real.
    """
    f0 = faces.copy()
    f1 = faces.copy()
    f1[:, :, 0] += espesor_mm  # desplaza en X

    # Caras laterales
    laterales = []

    for a, b in zip(f0.reshape(-1, 3), f1.reshape(-1, 3)):
        laterales.append([a, b, b])
        laterales.append([a, a, b])

    return np.concatenate([f0, f1, np.array(laterales)])



# ============================================================
# HEIGHTMAP → STL MANIFOLD (SUPERFICIE CERRADA)
# ============================================================

def generar_stl_manifold(z_grid, mask):
    """
    Convierte una grilla de alturas en un STL sólido y manifold.
    """

    h, w = z_grid.shape

    ancho_mm = w / RES_PX_MM
    alto_mm = h / RES_PX_MM

    x = np.linspace(0, ancho_mm, w)
    y = np.linspace(0, alto_mm, h)
    X, Y = np.meshgrid(x, y)
    Y = np.flipud(Y)

    faces = []

    for i, j in np.argwhere(mask):
        if i >= h - 1 or j >= w - 1:
            continue

        # Alturas
        z0 = z_grid[i, j]
        z1 = z_grid[i, j + 1]
        z2 = z_grid[i + 1, j]
        z3 = z_grid[i + 1, j + 1]

        # Vértices superiores
        vt0 = [X[i, j], Y[i, j], z0]
        vt1 = [X[i, j + 1], Y[i, j + 1], z1]
        vt2 = [X[i + 1, j], Y[i + 1, j], z2]
        vt3 = [X[i + 1, j + 1], Y[i + 1, j + 1], z3]

        # Vértices inferiores
        vb0 = [X[i, j], Y[i, j], 0]
        vb1 = [X[i, j + 1], Y[i, j + 1], 0]
        vb2 = [X[i + 1, j], Y[i + 1, j], 0]
        vb3 = [X[i + 1, j + 1], Y[i + 1, j + 1], 0]

        # Superficie superior e inferior
        faces += [
            [vt0, vt2, vt3], [vt0, vt3, vt1],
            [vb0, vb3, vb2], [vb0, vb1, vb3],
        ]

        # Cierre lateral
        if i == 0 or not mask[i - 1, j]:
            faces += [[vt0, vt1, vb1], [vt0, vb1, vb0]]
        if i + 1 >= h - 1 or not mask[i + 1, j]:
            faces += [[vt2, vb3, vt3], [vt2, vb2, vb3]]
        if j == 0 or not mask[i, j - 1]:
            faces += [[vt0, vb2, vt2], [vt0, vb0, vb2]]
        if j + 1 >= w - 1 or not mask[i, j + 1]:
            faces += [[vt1, vt3, vb3], [vt1, vb3, vb1]]

    return np.array(faces)

def generar_stl_manifold_x(z_grid, mask, espesor_mm):
    """
    Genera un sólido manifold extruido en X
    usando una máscara 2D (Y,Z).
    """

    h, w = z_grid.shape

    dy = 1.0 / RES_PX_MM
    dz = 1.0 / RES_PX_MM

    y_coords = (h - np.arange(h) - 1) * dy
    z_coords = np.arange(w) * dz

    faces = []

    for i, j in np.argwhere(mask):
        if i >= h - 1 or j >= w - 1:
            continue

        y0 = y_coords[i]
        y1 = y0 + dy
        z0 = z_coords[j]
        z1 = z0 + dz

        x0 = 0.0
        x1 = espesor_mm

        # vértices
        v000 = [x0, y0, z0]
        v001 = [x1, y0, z0]
        v010 = [x0, y1, z0]
        v011 = [x1, y1, z0]
        v100 = [x0, y0, z1]
        v101 = [x1, y0, z1]
        v110 = [x0, y1, z1]
        v111 = [x1, y1, z1]

        # sólido completo (6 caras)
        faces += [
            [v000, v010, v110], [v000, v110, v100],  # X-
            [v001, v101, v111], [v001, v111, v011],  # X+
            [v000, v001, v011], [v000, v011, v010],  # Z-
            [v100, v110, v111], [v100, v111, v101],  # Z+
            [v010, v011, v111], [v010, v111, v110],  # Y+
            [v000, v100, v101], [v000, v101, v001],  # Y-
        ]

    return np.array(faces)



# ============================================================
# MODELO FINAL: BASE + TEXTO VERTICAL
# ============================================================

def generar_base_texto_stl(texto: str) -> bytes:
    """
    Genera el STL completo del bloque con texto vertical frontal.
    """
    base_w_px = int(BASE_ANCHO_MM * RES_PX_MM)   # 45 mm
    base_h_px = int(BASE_ALTO_MM  * RES_PX_MM)   # 45 mm


    # Heightmap del texto
    z_texto, mask_texto = generar_texto_heightmap(
        texto,
        TEXTO_X_MM,
        TEXTO_Y_MM,
        True
    )

    z_base = np.full((base_h_px, base_w_px), BASE_Z_MM)
    mask_base = np.ones_like(z_base, dtype=bool)


    # Bloque base macizo
    faces_base = generar_stl_manifold(z_base, mask_base)

    faces_texto = generar_stl_manifold_x(
        z_texto,
        mask_texto,
        TEXTO_Z_MM
    )

    faces_texto = rotar_faces(faces_texto, "y", 180)

    faces_texto = trasladar_faces(
        faces_texto,
        dx=BASE_ANCHO_MM,
        dy=BASE_ALTO_MM,
        dz=BASE_ANCHO_MM * 2
    )


    # Letras verticales extruidas en X
    # faces_texto = generar_texto_vertical(
    #     mask_texto,
    #     espesor_mm=TEXTO_Z_MM,
    #     x_plano=BASE_ANCHO_MM - (TEXTO_Z_MM * 2),
    #     offset_y_mm=BASE_ALTO_MM
    # )
    

    # Unión de geometrías
    faces = np.concatenate([faces_base, faces_texto])

    # Creación del STL
    m = mesh.Mesh(np.zeros(faces.shape[0], dtype=mesh.Mesh.dtype))
    m.vectors = faces

    return mesh_to_stl_bytes(m)
 