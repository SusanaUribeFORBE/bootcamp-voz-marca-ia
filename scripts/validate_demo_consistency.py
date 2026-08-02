"""Re-valida las ideas y copies ya guardados de 'fonda-dona-pola' contra el
perfil de marca, y los re-guarda con los campos `consistente`/`motivo`.

Existe para que la demo ya muestre las señales ✓/⚠️ de consistencia de marca
sin depender de generar contenido nuevo en vivo (ver docs/decisiones.md).

Uso:
    python scripts/validate_demo_consistency.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.stdout.reconfigure(encoding="utf-8")

from dotenv import load_dotenv

load_dotenv()

from src import storage
from src.ai_engine import validate_copy, validate_ideas

SLUG = "fonda-dona-pola"


def main() -> None:
    perfil = storage.load_profile(SLUG)

    ideas = storage.load_ideas(SLUG)
    ideas_validadas = validate_ideas(perfil, ideas)
    storage.save_ideas(SLUG, ideas_validadas)
    for i, idea in enumerate(ideas_validadas):
        marca = "✓" if idea.get("consistente") else "⚠️"
        print(f"{marca} idea {i}: {idea.get('titulo', '')} — {idea.get('motivo', '')}")

    copies = storage.load_copies(SLUG)
    copies_validados = [validate_copy(perfil, copy) for copy in copies]
    storage.save_copies(SLUG, copies_validados)
    for copy in copies_validados:
        marca = "✓" if copy.get("consistente") else "⚠️"
        print(f"{marca} [{copy.get('canal')}] {copy.get('idea_titulo')} — {copy.get('motivo', '')}")

    print(f"\n{len(ideas_validadas)} ideas y {len(copies_validados)} copies re-validados.")


if __name__ == "__main__":
    main()
