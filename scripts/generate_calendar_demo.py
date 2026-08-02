"""Genera el calendario de publicación de ejemplo para 'fonda-dona-pola' a
partir de los copies ya guardados, y lo exporta a
data/fonda-dona-pola/calendario.ics.

No llama a la API de Claude: el algoritmo de calendario es determinista
(ver src/calendar_builder.py y docs/decisiones.md, decisión #5).

Uso:
    python scripts/generate_calendar_demo.py
"""
from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.stdout.reconfigure(encoding="utf-8")

from src import storage
from src.calendar_builder import build_calendar, export_ics

SLUG = "fonda-dona-pola"


def main() -> None:
    perfil = storage.load_profile(SLUG)
    copies = storage.load_copies(SLUG)

    calendario = build_calendar(copies, perfil, start_date=date.today())

    for entrada in calendario:
        print(f"{entrada['fecha']}  [{entrada['canal']}]  {entrada['idea_titulo']}")

    ics_path = storage.business_dir(SLUG) / "calendario.ics"
    export_ics(calendario, ics_path)
    storage.save_json(SLUG, "calendario.json", calendario)

    print(f"\n{len(calendario)} publicaciones agendadas.")
    print(f"Calendario guardado en: {ics_path}")


if __name__ == "__main__":
    main()
