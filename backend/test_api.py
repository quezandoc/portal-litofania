"""
Script de prueba para la API
"""
import requests
from pathlib import Path

# URL del servidor
API_URL = "http://localhost:8000"

def test_health():
    """Verificar que el servidor está disponible."""
    print("🔍 Verificando salud del servidor...")
    response = requests.get(f"{API_URL}/health")
    print(f"✅ Status: {response.status_code}")
    print(f"Response: {response.json()}\n")


def test_generate_model(image_path: str):
    """Generar un modelo 3D de prueba."""
    print(f"🔧 Generando modelo 3D desde {image_path}...")
    
    if not Path(image_path).exists():
        print(f"❌ Archivo no encontrado: {image_path}")
        return
    
    with open(image_path, "rb") as f:
        files = {"file": f}
        data = {
            "shape": "Corazón",
            "zoom": 1.2,
            "frame_width": 3.0,
            "offset_x": 0,
            "offset_y": 0,
        }
        
        response = requests.post(f"{API_URL}/api/generate-3d/", files=files, data=data)
        
        if response.status_code == 200:
            print(f"✅ Modelo generado exitosamente")
            print(f"Tamaño: {len(response.content)} bytes\n")
            
            # Guardar archivo
            output_file = "test_model.stl"
            with open(output_file, "wb") as out:
                out.write(response.content)
            print(f"💾 Archivo guardado como {output_file}")
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")


if __name__ == "__main__":
    print("=" * 50)
    print("LithoMaker Pro - API Test")
    print("=" * 50 + "\n")
    
    # Test 1: Health check
    test_health()
    
    # Test 2: Generar modelo (necesitas una imagen de prueba)
    # test_generate_model("test_image.jpg")
    
    print("✅ Pruebas completadas")
