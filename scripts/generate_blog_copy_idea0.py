"""Genera el copy de Blog para la idea 0 ("Así nace su bandeja paisa frente a
sus ojos") de 'fonda-dona-pola', y lo agrega a copies.json.

La idea 0 ya tiene copy de Instagram y WhatsApp (ver
scripts/generate_copies_demo.py); este script completa el trío para poder
mostrar en docs/guion-demo.md una comparación real de los 3 canales para la
misma idea, en vez de comparar ideas distintas.

Uso:
    python scripts/generate_blog_copy_idea0.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.stdout.reconfigure(encoding="utf-8")

from dotenv import load_dotenv

load_dotenv()

from src import storage
from src.ai_engine import generate_copy, validate_copy

SLUG = "fonda-dona-pola"


def main() -> None:
    perfil = storage.load_profile(SLUG)
    ideas = storage.load_ideas(SLUG)
    idea0 = ideas[0]

    copy = generate_copy(perfil, idea0, "Blog")
    copy = validate_copy(perfil, copy)

    copies = storage.load_copies(SLUG)
    copies.append(copy)
    storage.save_copies(SLUG, copies)

    marca = "✓" if copy.get("consistente") else "⚠️"
    print(f"--- [{copy['canal']}] {copy['idea_titulo']} ---")
    print(copy["texto"])
    print(f"\n{marca} {copy.get('motivo', '')}")


if __name__ == "__main__":
    main()
