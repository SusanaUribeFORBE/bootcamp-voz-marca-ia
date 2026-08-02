"""Generación de piezas gráficas simples (plantilla, sin IA de imágenes).

Combina el color de marca, el logo (opcional) y un título en una imagen
cuadrada de 1080x1080 pensada para redes sociales. Todo se hace con Pillow
sobre una plantilla fija — no hay generación de imágenes con IA.
"""
from __future__ import annotations

import io
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from src.brand_profile import BrandProfile

CANVAS_SIZE = 1080
MARGIN = 60
LOGO_MAX_SIZE = 220
FONT_SIZE = 64
DEFAULT_COLOR = "#8B4A2B"


def _hex_to_rgb(color_hex: str) -> tuple[int, int, int]:
    color_hex = (color_hex or "").strip().lstrip("#")
    if len(color_hex) != 6:
        color_hex = DEFAULT_COLOR.lstrip("#")
    try:
        return tuple(int(color_hex[i : i + 2], 16) for i in (0, 2, 4))  # type: ignore[return-value]
    except ValueError:
        return tuple(int(DEFAULT_COLOR.lstrip("#")[i : i + 2], 16) for i in (0, 2, 4))  # type: ignore[return-value]


def _texto_legible(fondo_rgb: tuple[int, int, int]) -> tuple[int, int, int]:
    r, g, b = fondo_rgb
    luminancia = 0.299 * r + 0.587 * g + 0.114 * b
    return (20, 20, 20) if luminancia > 150 else (245, 245, 245)


def _envolver_texto(
    draw: ImageDraw.ImageDraw, texto: str, font: ImageFont.FreeTypeFont, ancho_max: int
) -> list[str]:
    palabras = texto.split()
    if not palabras:
        return [""]
    lineas: list[str] = []
    linea_actual = palabras[0]
    for palabra in palabras[1:]:
        candidata = f"{linea_actual} {palabra}"
        if draw.textlength(candidata, font=font) <= ancho_max:
            linea_actual = candidata
        else:
            lineas.append(linea_actual)
            linea_actual = palabra
    lineas.append(linea_actual)
    return lineas


def _pegar_logo(imagen: Image.Image, logo_path: str) -> None:
    if not logo_path:
        return
    ruta = Path(logo_path)
    if not ruta.exists():
        return
    try:
        logo = Image.open(ruta)
        logo.load()
        logo = logo.convert("RGBA")
        ratio = min(LOGO_MAX_SIZE / logo.width, LOGO_MAX_SIZE / logo.height, 1.0)
        nuevo_tamano = (max(1, int(logo.width * ratio)), max(1, int(logo.height * ratio)))
        logo = logo.resize(nuevo_tamano, Image.LANCZOS)
        x = CANVAS_SIZE - MARGIN - logo.width
        y = CANVAS_SIZE - MARGIN - logo.height
        imagen.paste(logo, (x, y), mask=logo)
    except Exception:
        return


def generate_graphic(perfil: BrandProfile, titulo: str) -> bytes:
    """Genera una pieza gráfica cuadrada (1080x1080) en memoria y retorna sus bytes PNG.

    Nunca lanza excepción por un logo faltante o inválido: en ese caso la
    pieza se genera igual, sin logo.
    """
    fondo_rgb = _hex_to_rgb(perfil.color_marca)
    imagen = Image.new("RGB", (CANVAS_SIZE, CANVAS_SIZE), fondo_rgb)
    draw = ImageDraw.Draw(imagen)

    color_texto = _texto_legible(fondo_rgb)
    font = ImageFont.load_default(size=FONT_SIZE)

    ancho_max_texto = CANVAS_SIZE - 2 * MARGIN
    lineas = _envolver_texto(draw, titulo or "", font, ancho_max_texto)

    alto_linea = int(FONT_SIZE * 1.3)
    alto_total_texto = alto_linea * len(lineas)
    y = (CANVAS_SIZE // 2 - alto_total_texto) // 2 + MARGIN

    for linea in lineas:
        ancho_linea = draw.textlength(linea, font=font)
        x = (CANVAS_SIZE - ancho_linea) / 2
        draw.text((x, y), linea, font=font, fill=color_texto)
        y += alto_linea

    _pegar_logo(imagen, perfil.logo_path)

    buffer = io.BytesIO()
    imagen.save(buffer, format="PNG")
    return buffer.getvalue()
