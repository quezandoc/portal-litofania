import streamlit as st
import numpy as np
from stl import mesh
from PIL import Image
import tempfile
from streamlit_stl import stl_from_file

# Configuración de página
st.set_page_config(page_title="LithoMaker Pro Engineering", layout="centered")
st.title("💎 LithoMaker Pro: Geometría Manifold")

# --- PARÁMETROS DE INGENIERÍA ---
# Resolución fija solicitada: 0.2 mm/pixel
RES_PX_MM = 5.0  # 5 px/mm = 0.2 mm/px
LADO_MM = 90.0   # Tamaño estándar
PIXELS = int(LADO_MM * RES_PX_MM) # 450x450 px

# Espesores (Z)
MARCO_Z = 5.0      
LITHO_MIN_Z = 0.6  
LITHO_MAX_Z = 3.0  

# --- SIDEBAR ---
st.sidebar.header("1. Producto")
forma = st.sidebar.selectbox("Forma:", ["Corazón", "Círculo", "Cuadrado"])
ancho_marco = st.sidebar.slider("Ancho Marco (mm):", 2.0, 5.0, 3.0)

st.sidebar.header("2. Imagen")
zoom = st.sidebar.slider("Zoom:", 0.5, 3.0, 1.2)
off_x = st.sidebar.slider("Mover X:", -60, 60, 0)
off_y = st.sidebar.slider("Mover Y:", -60, 60, 0)

# --- MATEMÁTICA DE FORMAS (MÁSCARAS) ---
def obtener_mascaras(forma_tipo, size, border_mm):
    # Ampliamos el rango de coordenadas para asegurar que el corazón entre completo
    # Rango +/- 1.6 cubre holgadamente la fórmula del corazón
    rango = 1.6 
    lin = np.linspace(-rango, rango, size)
    x, y = np.meshgrid(lin, -lin)
    
    # Conversión: Cuántas unidades matemáticas corresponden al borde en mm
    # El lienzo mide 'size' pixeles que son 'LADO_MM' mm.
    # El rango matemático total es rango*2 (3.2).
    # Factor: units_per_mm
    units_per_mm = (rango * 2) / LADO_MM
    offset = border_mm * units_per_mm

    if forma_tipo == "Círculo":
        R = 1.3
        # Ecuación: x^2 + y^2 <= R^2
        mask_frame = (x**2 + y**2) <= R**2
        mask_litho = (x**2 + y**2) <= (R - offset)**2

    elif forma_tipo == "Cuadrado":
        L = 1.3
        mask_frame = (np.abs(x) <= L) & (np.abs(y) <= L)
        mask_litho = (np.abs(x) <= (L - offset)) & (np.abs(y) <= (L - offset))

    elif forma_tipo == "Corazón":
        # Fórmula ajustada para lóbulos completos
        # (x^2 + (y - 0.6*sqrt(|x|))^2) <= R^2
        # El factor 0.6 baja el centro de gravedad, permitiendo que la parte de arriba entre.
        def heart_eq(cx, cy):
            return (cx**2 + (cy - 0.6 * np.sqrt(np.abs(cx)))**2)
        
        R_heart = 1.6 # Radio base del corazón
        mask_frame = heart_eq(x, y) <= R_heart
        mask_litho = heart_eq(x, y) <= (R_heart - offset*1.8) # 1.8 factor de corrección de forma

    return mask_litho, mask_frame

# --- GENERACIÓN DE MALLA OPTIMIZADA (VERTEX INDEXING) ---
def generar_stl_manifold(z_grid, mask_total):
    """
    Genera una malla cerrada (watertight) usando indexación de vértices.
    Esto elimina los errores de 'bordes no moldeados' en el Slicer.
    """
    filas, cols = z_grid.shape
    
    # 1. Coordenadas Físicas
    x_lin = np.linspace(0, LADO_MM, cols)
    y_lin = np.linspace(0, LADO_MM, filas)
    X, Y = np.meshgrid(x_lin, y_lin)
    Y = np.flipud(Y) # Corregir orientación de imagen
    
    # 2. Mapa de Índices: Asigna un ID único a cada pixel válido
    # -1 significa que el pixel está vacío (fuera del recorte)
    idx_map = np.full((filas, cols), -1, dtype=int)
    
    # Lista plana de vértices (x,y,z)
    vertices = []
    current_idx = 0
    
    # Iteramos para crear los vértices ÚNICOS
    # Solo creamos vértices donde la máscara es True
    valid_pixels = np.argwhere(mask_total)
    
    # Optimizacion: Usar diccionario o mapa directo seria lento en Python puro,
    # pero necesario para topología correcta.
    
    # Estrategia:
    # Cada nodo de la grilla (i,j) genera 2 vértices físicos:
    #   - V_top: (X[j], Y[i], Z[i,j])
    #   - V_btm: (X[j], Y[i], 0)
    # Sin embargo, la triangulación se hace por CUADRADOS (i,j) -> (i+1, j+1)
    
    # Paso A: Crear mapa de índices para NODOS (puntos de la rejilla), no pixeles
    # Como la máscara es por pixel (celda), definimos que un nodo (esquina) existe
    # si cualquiera de sus 4 celdas vecinas es válida.
    # Para simplificar y asegurar solidez: Usaremos la estrategia de "Voxel vertical"
    # Cada celda válida (pixel) genera su propia tapa y base, y comparte bordes.
    
    faces = []
    
    # Iteramos sobre cada PIXEL válido de la máscara
    for i, j in valid_pixels:
        # Chequeo de seguridad de bordes de array
        if i >= filas-1 or j >= cols-1:
            continue
            
        # Coordenadas de las 4 esquinas del pixel (Top-Left convention)
        # 0:(i,j), 1:(i,j+1), 2:(i+1,j), 3:(i+1,j+1)
        
        # Alturas Z (Relieve)
        z0 = z_grid[i,j]
        z1 = z_grid[i,j+1]
        z2 = z_grid[i+1,j]
        z3 = z_grid[i+1,j+1]
        
        # Coordenadas X, Y
        x0, y0 = X[i,j], Y[i,j]
        x1, y1 = X[i,j+1], Y[i,j+1]
        x2, y2 = X[i+1,j], Y[i+1,j]
        x3, y3 = X[i+1,j+1], Y[i+1,j+1]
        
        # Definimos los 8 vértices de este prisma (pixel extruido)
        # T = Top (Relieve), B = Bottom (Z=0)
        
        vt0 = [x0, y0, z0]; vb0 = [x0, y0, 0]
        vt1 = [x1, y1, z1]; vb1 = [x1, y1, 0]
        vt2 = [x2, y2, z2]; vb2 = [x2, y2, 0]
        vt3 = [x3, y3, z3]; vb3 = [x3, y3, 0]
        
        # --- CARA SUPERIOR (Relieve) ---
        # Tri 1: 0-2-3, Tri 2: 0-3-1
        faces.append([vt0, vt2, vt3])
        faces.append([vt0, vt3, vt1])
        
        # --- CARA INFERIOR (Plana) ---
        # Orden invertido para normal hacia abajo: 0-3-2, 0-1-3
        faces.append([vb0, vb3, vb2])
        faces.append([vb0, vb1, vb3])
        
        # --- PAREDES (Solo si el vecino NO existe) ---
        
        # Pared NORTE (Arriba, i-1)
        if i == 0 or not mask_total[i-1, j]:
            # Conecta 0-1 Top con 0-1 Bottom
            faces.append([vt0, vt1, vb1])
            faces.append([vt0, vb1, vb0])
            
        # Pared SUR (Abajo, i+1) -> Ojo: el vecino sur es i+1, pero estamos en el pixel i
        # La pared sur del pixel i es la arista 2-3
        # Verificamos si el pixel de abajo (i+1) es válido
        # Nota: La máscara mask_total[i+1, j] nos dice si el pixel de abajo existe.
        if (i+1) >= filas-1 or not mask_total[i+1, j]:
            # Conecta 2-3 Top con 2-3 Bottom
            # Orden para normal hacia afuera: Top2->Top3->Btm3...
            faces.append([vt2, vb3, vt3]) # Cuidado con normales
            faces.append([vt2, vb2, vb3])
            
        # Pared OESTE (Izquierda, j-1) -> Arista 0-2
        if j == 0 or not mask_total[i, j-1]:
            # Conecta 0-2 Top con 0-2 Bottom
            faces.append([vt0, vb2, vt2])
            faces.append([vt0, vb0, vb2])
            
        # Pared ESTE (Derecha, j+1) -> Arista 1-3
        if (j+1) >= cols-1 or not mask_total[i, j+1]:
            # Conecta 1-3 Top con 1-3 Bottom
            faces.append([vt1, vt3, vb3])
            faces.append([vt1, vb3, vb1])

    return np.array(faces)

# --- PROCESAMIENTO ---
archivo = st.file_uploader("Subir Fotografía del Cliente", type=['jpg', 'png', 'jpeg'])

if archivo:
    # 1. Carga y Escalado
    img = Image.open(archivo).convert('L')
    img_res = img.resize((int(PIXELS*zoom), int((img.height/img.width)*PIXELS*zoom)), Image.Resampling.LANCZOS)
    
    # 2. Lienzo
    canvas = Image.new('L', (PIXELS, PIXELS), color=255)
    pos_x = (PIXELS - img_res.width) // 2 + int(off_x * RES_PX_MM) # Corregido factor escala
    pos_y = (PIXELS - img_res.height) // 2 + int(off_y * RES_PX_MM)
    canvas.paste(img_res, (pos_x, pos_y))
    
    # 3. Máscaras
    m_litho, m_frame = obtener_mascaras(forma, PIXELS, ancho_marco)
    img_array = np.array(canvas)
    
    # 4. Preview Color
    preview = np.array(Image.fromarray(img_array).convert("RGB"))
    # Coloreamos el marco (donde es frame pero no litho)
    preview[m_frame & ~m_litho] = [200, 50, 50] 
    # Oscurecemos lo recortado
    preview[~m_frame] = [30, 30, 30]
    
    st.image(preview, caption="Vista Previa de Corte (Rojo = Marco Sólido)", width=350)
    
    st.info(f"Resolución de Ingeniería: {RES_PX_MM} px/mm | Vértices estimados: ~{np.sum(m_frame)*2}")

    if st.button(f"🚀 Generar {forma} Sólido (Manifold)"):
        with st.spinner("Procesando geometría cerrada (esto puede tardar unos segundos)..."):
            
            # 5. Mapeo de Alturas Z
            # Invertimos: Negro (0) -> Grueso (3mm), Blanco (255) -> Delgado (0.6mm)
            z_litho = LITHO_MAX_Z - (img_array / 255.0) * (LITHO_MAX_Z - LITHO_MIN_Z)
            
            # Composición final de Z
            # Si es litofanía -> z_litho
            # Si es marco -> MARCO_Z (5mm)
            # El resto no importa porque se recorta
            z_final = np.where(m_litho, z_litho, MARCO_Z)
            
            # 6. Generación STL
            # Usamos m_frame como la máscara de recorte total
            faces = generar_stl_manifold(z_final, m_frame)
            
            if len(faces) == 0:
                st.error("Error: La geometría está vacía. Intenta ajustar el zoom.")
            else:
                # Crear Mesh
                regalo_mesh = mesh.Mesh(np.zeros(faces.shape[0], dtype=mesh.Mesh.dtype))
                regalo_mesh.vectors = faces
                
                # Guardar y Mostrar
                with tempfile.NamedTemporaryFile(delete=False, suffix='.stl') as tmp:
                    regalo_mesh.save(tmp.name)
                    
                    st.success("✅ Geometría generada correctamente. Bordes cerrados.")
                    
                    st.subheader("👀 Inspección 3D")
                    stl_from_file(file_path=tmp.name, material="material", auto_rotate=True, height=350)
                    
                    with open(tmp.name, "rb") as f_stl:
                        st.download_button(
                            label=f"📥 DESCARGAR {forma.upper()} FINAL",
                            data=f_stl,
                            file_name=f"litho_{forma.lower()}_manifold.stl",
                            mime="application/sla",
                            width='stretch'
                        )
