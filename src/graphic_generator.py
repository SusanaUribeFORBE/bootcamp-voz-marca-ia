"""Generación de piezas gráficas simples (plantilla, sin IA de imágenes).

Combina un fondo derivado del color de marca (degradado + overlay, sin
depender de fotos externas que podrían tener problemas de derechos), el logo
(opcional) y un título en una imagen cuadrada de 1080x1080 pensada para
redes sociales. Todo se hace con Pillow sobre una plantilla fija — no hay
generación de imágenes con IA.
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
OVERLAY_ALPHA = 90  # 0-255: qué tanto oscurece el degradado para resaltar el texto

_ASSETS_FONTS_DIR = Path(__file__).resolve().parent.parent / "assets" / "fonts"

# Cascada de fuentes con soporte de tildes/ñ: primero la fuente bundleada en
# el repo (funciona igual en cualquier máquina/deploy), luego equivalentes
# del sistema operativo (Windows y Linux) y, si todo falla, la fuente por
# defecto de Pillow — nunca rompe la generación de la pieza.
_FONT_CANDIDATES = [
    _ASSETS_FONTS_DIR / "Montserrat-Variable.ttf",
    Path("C:/Windows/Fonts/seguisb.ttf"),
    Path("C:/Windows/Fonts/arialbd.ttf"),
    Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
    Path("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"),
]


def _hex_to_rgb(color_hex: str) -> tuple[int, int, int]:
    color_hex = (color_hex or "").strip().lstrip("#")
    if len(color_hex) != 6:
        color_hex = DEFAULT_COLOR.lstrip("#")
    try:
        return tuple(int(color_hex[i : i + 2], 16) for i in (0, 2, 4))  # type: ignore[return-value]
    except ValueError:
        return tuple(int(DEFAULT_COLOR.lstrip("#")[i : i + 2], 16) for i in (0, 2, 4))  # type: ignore[return-value]


def _mezclar(color: tuple[int, int, int], hacia: tuple[int, int, int], factor: float) -> tuple[int, int, int]:
    """Interpola `color` hacia `hacia` un `factor` (0=color, 1=hacia)."""
    return tuple(int(c + (h - c) * factor) for c, h in zip(color, hacia))  # type: ignore[return-value]


def _texto_legible(fondo_rgb: tuple[int, int, int]) -> tuple[int, int, int]:
    r, g, b = fondo_rgb
    luminancia = 0.299 * r + 0.587 * g + 0.114 * b
    return (20, 20, 20) if luminancia > 150 else (245, 245, 245)


def _cargar_fuente(size: int) -> ImageFont.ImageFont:
    """Carga una fuente TTF con soporte de tildes/ñ, con fallback en cascada.

    Nunca lanza excepción: si la fuente bundleada y las del sistema fallan,
    cae en la fuente por defecto de Pillow (siempre disponible).
    """
    for ruta in _FONT_CANDIDATES:
        if not ruta.exists():
            continue
        try:
            fuente = ImageFont.truetype(str(ruta), size=size)
            try:
                fuente.set_variation_by_axes([700])  # negrita, si es fuente variable
            except Exception:
                pass  # fuente estática o sin eje "Weight": se usa tal cual
            return fuente
        except Exception:
            continue
    return ImageFont.load_default(size=size)


def _generar_fondo(color_marca_hex: str) -> Image.Image:
    """Degradado vertical simple a partir del color de marca (sin fotos externas)."""
    base = _hex_to_rgb(color_marca_hex)
    claro = _mezclar(base, (255, 255, 255), 0.18)
    oscuro = _mezclar(base, (0, 0, 0), 0.35)

    columna = Image.new("RGB", (1, CANVAS_SIZE))
    pixeles = columna.load()
    for y in range(CANVAS_SIZE):
        t = y / (CANVAS_SIZE - 1)
        pixeles[0, y] = _mezclar(claro, oscuro, t)
    return columna.resize((CANVAS_SIZE, CANVAS_SIZE))


def _aplicar_overlay(fondo: Image.Image, color_marca_hex: str) -> Image.Image:
    """Superpone una capa semitransparente del color de marca (oscurecido)
    sobre el degradado, para que el texto resalte sin importar qué tan claro
    sea el color de marca elegido."""
    base = _hex_to_rgb(color_marca_hex)
    oscuro_overlay = _mezclar(base, (0, 0, 0), 0.55)
    overlay = Image.new("RGBA", fondo.size, (*oscuro_overlay, OVERLAY_ALPHA))
    compuesta = Image.alpha_composite(fondo.convert("RGBA"), overlay)
    return compuesta.convert("RGB")


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

    Nunca lanza excepción por un logo faltante/inválido ni por una fuente
    faltante: en esos casos la pieza se genera igual, con los fallbacks
    correspondientes (sin logo / con la fuente por defecto de Pillow).
    """
    fondo = _generar_fondo(perfil.color_marca)
    imagen = _aplicar_overlay(fondo, perfil.color_marca)
    draw = ImageDraw.Draw(imagen)

    color_fondo_efectivo = imagen.getpixel((CANVAS_SIZE // 2, CANVAS_SIZE // 2))
    color_texto = _texto_legible(color_fondo_efectivo)
    font = _cargar_fuente(FONT_SIZE)

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
