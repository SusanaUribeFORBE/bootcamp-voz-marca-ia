"""Regenera una pieza gráfica de ejemplo para Fonda Doña Pola.

Usa el perfil real guardado (color de marca + logo) y un título con tildes y
ñ, para confirmar visualmente que el degradado, el overlay, el logo y la
fuente (Montserrat bundleada, con fallback) se ven bien juntos.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src import storage
from src.graphic_generator import generate_graphic

SLUG = "fonda-dona-pola"
TITULO_MUESTRA = "Así nace su bandeja paisa, señor(a) — sazón de la Fonda Doña Pola"
RUTA_SALIDA = Path(__file__).resolve().parent.parent / "data" / SLUG / "muestra_pieza_grafica.png"


def main() -> None:
    perfil = storage.load_profile(SLUG)
    if perfil is None:
        print(f"No se encontró un perfil guardado para '{SLUG}'.")
        return

    imagen_bytes = generate_graphic(perfil, TITULO_MUESTRA)
    RUTA_SALIDA.write_bytes(imagen_bytes)
    print(f"Pieza de ejemplo regenerada en: {RUTA_SALIDA}")
    print(f"color_marca usado: {perfil.color_marca}  logo_path usado: {perfil.logo_path}")


if __name__ == "__main__":
    main()
