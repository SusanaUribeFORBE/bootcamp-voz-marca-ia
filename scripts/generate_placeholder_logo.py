"""Genera un logo placeholder genérico para el negocio de ejemplo Fonda Doña Pola.

No es el logo de ninguna marca real: es un ícono simple (un plato con
cubiertos estilizado) dibujado con formas geométricas básicas de Pillow, solo
para poder demostrar la función de piezas gráficas con un logo cargado.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PIL import Image, ImageDraw

from src import storage

SLUG = "fonda-dona-pola"
TAMANO = 400
COLOR_MARCA = "#8B4A2B"


def _generar_icono() -> Image.Image:
    imagen = Image.new("RGBA", (TAMANO, TAMANO), (0, 0, 0, 0))
    draw = ImageDraw.Draw(imagen)

    centro = TAMANO // 2
    radio_plato = int(TAMANO * 0.42)
    color_plato = (245, 238, 224, 255)
    color_borde = (139, 74, 43, 255)

    draw.ellipse(
        (centro - radio_plato, centro - radio_plato, centro + radio_plato, centro + radio_plato),
        fill=color_plato,
        outline=color_borde,
        width=10,
    )
    radio_interno = int(radio_plato * 0.62)
    draw.ellipse(
        (
            centro - radio_interno,
            centro - radio_interno,
            centro + radio_interno,
            centro + radio_interno,
        ),
        outline=color_borde,
        width=4,
    )

    ancho_cubierto = 14
    alto_tenedor = int(TAMANO * 0.7)
    x_tenedor = int(TAMANO * 0.14)
    y_top = int(TAMANO * 0.15)
    draw.rectangle(
        (x_tenedor, y_top, x_tenedor + ancho_cubierto, y_top + alto_tenedor),
        fill=color_borde,
    )
    for i in range(3):
        dx = x_tenedor - 10 + i * 10
        draw.rectangle((dx, y_top, dx + 6, y_top + 40), fill=color_borde)

    x_cuchillo = int(TAMANO * 0.82)
    draw.rectangle(
        (x_cuchillo, y_top, x_cuchillo + ancho_cubierto, y_top + alto_tenedor),
        fill=color_borde,
    )
    draw.polygon(
        [
            (x_cuchillo, y_top),
            (x_cuchillo + ancho_cubierto, y_top),
            (x_cuchillo + ancho_cubierto, y_top + 50),
            (x_cuchillo, y_top + 70),
        ],
        fill=color_borde,
    )

    return imagen


def main() -> None:
    icono = _generar_icono()
    ruta_logo = storage.business_dir(SLUG) / "logo.png"
    icono.save(ruta_logo, format="PNG")
    print(f"Logo placeholder generado en: {ruta_logo}")

    perfil = storage.load_profile(SLUG)
    if perfil is None:
        print(f"No se encontró un perfil guardado para '{SLUG}'; no se actualizó el perfil.")
        return

    perfil.logo_path = str(ruta_logo)
    if not perfil.color_marca or perfil.color_marca == "#8B4A2B":
        perfil.color_marca = COLOR_MARCA
    storage.save_profile(perfil)
    print(f"Perfil de '{SLUG}' actualizado con logo_path y color_marca.")


if __name__ == "__main__":
    main()
