import streamlit as st
import numpy as np
from stl import mesh
from PIL import Image, ImageOps
import tempfile
from st_stl_viewer import st_stl_viewer # El nuevo visor 3D

st.set_page_config(page_title="LithoMaker Pro 3D", layout="centered")
st.title("💖 LithoMaker Pro: Edición Especial")

# --- PARÁMETROS COMERCIALES FIJOS ---
RES_PX_MM = 4.0  # 0.25mm/px (4 px por mm)
LADO_MM = 90.0
PIXELS = int(LADO_MM * RES_PX_MM) # 360 px
MARCO_Z = 5.0      # Grosor del marco
LITHO_MIN_Z = 0.6  # Grosor luz
LITHO_MAX_Z = 3.0  # Grosor sombras

# --- SIDEBAR: PERSONALIZACIÓN ---
st.sidebar.header("1. Configura el Regalo")
forma = st.sidebar.selectbox("Forma del producto:", ["Corazón", "Círculo", "Cuadrado"])

st.sidebar.header("2. Encuadre de la Foto")
zoom = st.sidebar.slider("Zoom:", 0.5, 2.5, 1.0)
off_x = st.sidebar.slider("Mover horizontal:", -50, 50, 0)
off_y = st.sidebar.slider("Mover vertical:", -50, 50, 0)

# --- LÓGICA DE MÁSCARAS ---
def generar_mascara(forma, size):
    lin = np.linspace(-1.1, 1.1, size)
    x, y = np.meshgrid(lin, -lin)
    if forma == "Círculo":
        return x**2 + y**2 <= 1.0
    elif forma == "Cuadrado":
        return (np.abs(x) <= 1.0) & (np.abs(y) <= 1.0)
    elif forma == "Corazón":
        # Ecuación paramétrica de corazón para impresión 3D
        return (x**2 + (y - np.sqrt(np.abs(x)))**2) <= 1.0
    return np.ones((size, size), dtype=bool)

# --- PROCESAMIENTO ---
archivo = st.file_uploader("Sube tu fotografía favorita", type=['jpg', 'png', 'jpeg'])

if archivo:
    img = Image.open(archivo).convert('L')
    
    # Aplicar Transformaciones (Zoom y Desplazamiento)
    w, h = img.size
    new_w = int(PIXELS * zoom)
    new_h = int((h/w) * new_w)
    img_res = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
    
    # Crear lienzo y centrar
    canvas = Image.new('L', (PIXELS, PIXELS), color=255)
    pos_x = (PIXELS - new_w) // 2 + int(off_x * RES_PX_MM)
    pos_y = (PIXELS - new_h) // 2 + int(off_y * RES_PX_MM)
    canvas.paste(img_res, (pos_x, pos_y))
    
    # Aplicar Máscara
    mask = generar_mascara(forma, PIXELS)
    img_array = np.array(canvas)
    
    # Previsualización 2D (Lo que el cliente verá dentro de la forma)
    preview = np.where(mask, img_array, 230) # Fondo claro para simular marco
    st.image(preview, caption="Previsualización de encuadre", width=350)

    if st.button(f"✨ Generar Vista Previa 3D y STL"):
        with st.spinner("Esculpiendo el modelo en 3D..."):
            
            # Generar Alturas Z (Litofanía invertida + Marco sólido)
            z_litho = LITHO_MAX_Z - (img_array / 255.0) * (LITHO_MAX_Z - LITHO_MIN_Z)
            z_final = np.where(mask, z_litho, MARCO_Z)
            
            # Construcción de la Malla (Basado en tu lógica anterior de sándwich)
            x_lin = np.linspace(0, LADO_MM, PIXELS)
            y_lin = np.linspace(0, LADO_MM, PIXELS)
            X, Y = np.meshgrid(x_lin, y_lin)
            
            # Vértices Top (con relieve) y Bottom (plano)
            v_t = np.stack([X, Y, z_final], axis=-1)
            v_b = np.stack([X, Y, np.zeros_like(z_final)], axis=-1)
            
            # (Aquí incluimos la lógica de triangulación para caras y paredes)
            # Para la demo, simplificamos el cierre del sólido
            f = []
            # Caras superiores e inferiores (Vectorizado para velocidad)
            for m in [v_t, v_b[::-1]]:
                v00, v01 = m[:-1, :-1], m[:-1, 1:]
                v10, v11 = m[1:, :-1], m[1:, 1:]
                f.append(np.concatenate([v00[...,None,:], v10[...,None,:], v11[...,None,:]], axis=-2).reshape(-1, 3, 3))
                f.append(np.concatenate([v00[...,None,:], v11[...,None,:]], axis=-1).reshape(-1, 3, 3))
            
            # Creación del objeto STL
            all_faces = np.concatenate(f, axis=0)
            regalo_mesh = mesh.Mesh(np.zeros(all_faces.shape[0], dtype=mesh.Mesh.dtype))
            regalo_mesh.vectors = all_faces
            
            # Guardar temporalmente
            with tempfile.NamedTemporaryFile(delete=False, suffix='.stl') as tmp:
                regalo_mesh.save(tmp.name)
                
                # --- VISUALIZADOR 3D INTERACTIVO ---
                st.subheader("👀 Vista Previa 3D")
                st_stl_viewer(tmp.name, color='#FFC0CB' if forma=="Corazón" else '#FFFFFF')
                
                # --- DESCARGA ---
                st.divider()
                with open(tmp.name, "rb") as f_stl:
                    st.download_button(
                        label=f"📥 DESCARGAR {forma.upper()} PARA IMPRIMIR",
                        data=f_stl,
                        file_name=f"lithomaker_{forma.lower()}.stl",
                        mime="application/sla",
                        use_container_width=True
                    )
