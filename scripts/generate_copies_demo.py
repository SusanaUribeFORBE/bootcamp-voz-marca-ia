"""Genera copies de ejemplo para el negocio 'fonda-dona-pola' usando la API
real de Claude, y los guarda en data/fonda-dona-pola/copies.json.

Uso:
    python scripts/generate_copies_demo.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.stdout.reconfigure(encoding="utf-8")

from dotenv import load_dotenv

load_dotenv()

from src import storage
from src.ai_engine import generate_copy

SLUG = "fonda-dona-pola"


def main() -> None:
    perfil = storage.load_profile(SLUG)
    ideas = storage.load_ideas(SLUG)

    # Idea 0 en dos canales distintos, para mostrar "mismo tono, distinto
    # formato"; el resto, cada una en su canal sugerido.
    tareas = [
        (ideas[0], "Instagram"),
        (ideas[0], "WhatsApp"),
        (ideas[1], "WhatsApp"),
        (ideas[2], "Blog"),
        (ideas[4], "WhatsApp"),
        (ideas[6], "Instagram"),
    ]

    copies = []
    for idea, canal in tareas:
        copy = generate_copy(perfil, idea, canal)
        copies.append(copy)
        print(f"--- [{copy['canal']}] {copy['idea_titulo']} ---")
        print(copy["texto"])
        print()

    storage.save_copies(perfil.slug, copies)
    print(f"{len(copies)} copies guardados.")


if __name__ == "__main__":
    main()
