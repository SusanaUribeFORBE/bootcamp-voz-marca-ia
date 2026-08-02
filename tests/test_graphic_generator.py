import io

from PIL import Image

from src.brand_profile import BrandProfile
from src.graphic_generator import CANVAS_SIZE, generate_graphic


def _perfil_base(**kwargs) -> BrandProfile:
    datos = dict(nombre_negocio="Fonda Doña Pola", descripcion_corta="Comida antioqueña")
    datos.update(kwargs)
    return BrandProfile(**datos)


def test_genera_pieza_sin_logo():
    perfil = _perfil_base(logo_path="")
    imagen_bytes = generate_graphic(perfil, "Bandeja paisa los domingos")

    assert isinstance(imagen_bytes, bytes)
    assert len(imagen_bytes) > 0

    imagen = Image.open(io.BytesIO(imagen_bytes))
    assert imagen.size == (CANVAS_SIZE, CANVAS_SIZE)


def test_genera_pieza_con_logo(tmp_path):
    ruta_logo = tmp_path / "logo.png"
    logo = Image.new("RGBA", (100, 100), (255, 0, 0, 255))
    logo.save(ruta_logo, format="PNG")

    perfil = _perfil_base(logo_path=str(ruta_logo))
    imagen_bytes = generate_graphic(perfil, "Sancocho los viernes")

    imagen = Image.open(io.BytesIO(imagen_bytes))
    assert imagen.size == (CANVAS_SIZE, CANVAS_SIZE)


def test_logo_inexistente_no_rompe_generacion():
    perfil = _perfil_base(logo_path="data/no-existe/logo-fantasma.png")
    imagen_bytes = generate_graphic(perfil, "Promo especial")

    imagen = Image.open(io.BytesIO(imagen_bytes))
    assert imagen.size == (CANVAS_SIZE, CANVAS_SIZE)


def test_titulo_vacio_no_rompe_generacion():
    perfil = _perfil_base()
    imagen_bytes = generate_graphic(perfil, "")

    imagen = Image.open(io.BytesIO(imagen_bytes))
    assert imagen.size == (CANVAS_SIZE, CANVAS_SIZE)
