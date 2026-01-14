import streamlit as st
import numpy as np
from stl import mesh
from PIL import Image, ImageOps
import tempfile

# Configuración de página
st.set_page_config(page_title="LithoMaker Beta", page_icon="🕯️", layout="centered")
st.title("🕯️ LithoMaker Beta")
st.write("Sube una foto y obtén tu litofanía sólida lista para imprimir.")

# --- BARRA LATERAL ---
st.sidebar.header("Ajustes")
ancho = st.sidebar.slider("Ancho (mm):", 50, 150, 100)
min_grosor = st.sidebar.slider("Grosor mínimo (mm):", 0.6, 1.2, 0.6) # Partes claras (luz pasa)
max_grosor = st.sidebar.slider("Grosor máximo (mm):", 2.0, 5.0, 3.0) # Partes oscuras (luz bloqueada)
invertir = st.sidebar.checkbox("Invertir (Modo Litofanía)", value=True)

# --- FUNCIÓN MATEMÁTICA AVANZADA (VOLUMEN CERRADO) ---
def generar_mesh_solido(image, width_mm, min_th, max_th, inverted):
    # 1. Procesar Imagen
    img = image.convert('L')
    if inverted: 
        img = ImageOps.invert(img)
    
    # Calcular dimensiones
    ratio = img.height / img.width
    height_mm = width_mm * ratio
    
    # Resolución: 5 píxeles por mm es suficiente para litofanías rápidas
    pixels_w = int(width_mm * 5)
    pixels_h = int(height_mm * 5)
    img = img.resize((pixels_w, pixels_h), Image.Resampling.LANCZOS)
    
    # 2. Crear Nube de Puntos (Top - Relieve)
    data = np.array(img)
    # Mapear 0-255 a min_th-max_th
    z_top = min_th + (data / 255.0) * (max_th - min_th)
    
    # Malla XY
    x_lin = np.linspace(0, width_mm, pixels_w)
    y_lin = np.linspace(0, height_mm, pixels_h)
    X, Y = np.meshgrid(x_lin, y_lin)
    Y = np.flipud(Y) # Corregir orientación
    
    # 3. Definir Vértices
    # Top (Relieve)
    vertices_top = np.zeros((pixels_h, pixels_w, 3))
    vertices_top[:,:,0], vertices_top[:,:,1], vertices_top[:,:,2] = X, Y, z_top
    
    # Bottom (Plano en Z=0)
    vertices_bottom = np.zeros((pixels_h, pixels_w, 3))
    vertices_bottom[:,:,0], vertices_bottom[:,:,1], vertices_bottom[:,:,2] = X, Y, 0

    # 4. Generar Caras (Triangulación)
    faces = []

    # A) CARA SUPERIOR (Relieve)
    v00 = vertices_top[:-1, :-1]; v01 = vertices_top[:-1, 1:]
    v10 = vertices_top[1:, :-1]; v11 = vertices_top[1:, 1:]
    
    f1 = np.concatenate([v00[...,None,:], v10[...,None,:], v11[...,None,:]], axis=-2)
    f2 = np.concatenate([v00[...,None,:], v11[...,None,:], v01[...,None,:]], axis=-2)
    faces.append(f1.reshape(-1, 3, 3))
    faces.append(f2.reshape(-1, 3, 3))

    # B) CARA INFERIOR (Plana - Invertimos orden para normales hacia abajo)
    b00 = vertices_bottom[:-1, :-1]; b01 = vertices_bottom[:-1, 1:]
    b10 = vertices_bottom[1:, :-1]; b11 = vertices_bottom[1:, 1:]
    
    f3 = np.concatenate([b00[...,None,:], b11[...,None,:], b10[...,None,:]], axis=-2)
    f4 = np.concatenate([b00[...,None,:], b01[...,None,:], b11[...,None,:]], axis=-2)
    faces.append(f3.reshape(-1, 3, 3))
    faces.append(f4.reshape(-1, 3, 3))

    # C) PAREDES (Cerrar el volumen)
    # Función auxiliar para coser bordes
    def crear_pared(borde_top, borde_btm):
        # borde_top y borde_btm son arrays (N, 3)
        n = len(borde_top) - 1
        
        t0 = borde_top[:-1]; t1 = borde_top[1:]
        b0 = borde_btm[:-1]; b1 = borde_btm[1:]
        
        # Triángulo 1: Top0 -> Btm0 -> Top1
        w1 = np.stack([t0, b0, t1], axis=1)
        # Triángulo 2: Btm0 -> Btm1 -> Top1
        w2 = np.stack([b0, b1, t1], axis=1)
        
        return np.concatenate([w1, w2], axis=0)

    # Pared Norte (Índice 0)
    faces.append(crear_pared(vertices_top[0,:], vertices_bottom[0,:]))
    # Pared Sur (Índice -1) - Invertimos orden para normales correctas
    faces.append(crear_pared(vertices_bottom[-1,:], vertices_top[-1,:]))
    # Pared Oeste (Columna 0) - Invertimos orden
    faces.append(crear_pared(vertices_bottom[:,0], vertices_top[:,0]))
    # Pared Este (Columna -1)
    faces.append(crear_pared(vertices_top[:,-1], vertices_bottom[:,-1]))

    # 5. Unir todo
    all_faces = np.concatenate(faces, axis=0)
    malla = mesh.Mesh(np.zeros(all_faces.shape[0], dtype=mesh.Mesh.dtype))
    malla.vectors = all_faces
    
    return malla

# --- INTERFAZ ---
archivo = st.file_uploader("Cargar imagen", type=['jpg', 'png', 'jpeg'])

if archivo:
    image = Image.open(archivo)
    col1, col2 = st.columns(2)
    with col1:
        st.image(image, caption="Imagen Original", use_container_width=True)
    
    with col2:
        st.info("💡 Tip: Para litofanías, imprime con 100% de relleno (infill).")
        if st.button("🚀 Crear Litofanía Sólida"):
            with st.spinner("Generando volumen cerrado..."):
                malla = generar_mesh_solido(image, ancho, min_grosor, max_grosor, invertir)
                
                # Guardar en memoria temporal
                with tempfile.NamedTemporaryFile(delete=False, suffix='.stl') as tmp:
                    malla.save(tmp.name)
                    
                    with open(tmp.name, "rb") as f:
                        st.download_button(
                            label="📥 DESCARGAR STL",
                            data=f,
                            file_name="litofania_solida.stl",
                            mime="application/sla",
                            use_container_width=True
                        )
                st.success("¡Modelo generado! Ahora es un sólido plano por detrás.")


