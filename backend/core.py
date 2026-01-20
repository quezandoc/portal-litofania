import tempfile
import os
from stl.mesh import Mesh


def mesh_to_stl_bytes(modelo_mesh: Mesh) -> bytes:
    """
    Convierte un mesh STL a bytes usando archivo temporal seguro.
    """

    tmp_path = None

    try:
        with tempfile.NamedTemporaryFile(
            suffix=".stl",
            delete=False
        ) as tmp:
            tmp_path = tmp.name
            modelo_mesh.save(tmp_path)

        with open(tmp_path, "rb") as f:
            return f.read()

    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)
