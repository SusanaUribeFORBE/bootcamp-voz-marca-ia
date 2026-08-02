"""Construcción del calendario de publicación sostenible.

Reglas de diseño (ver docs/decisiones.md):
- La frecuencia deseada por canal viene del perfil de marca
  (`Canal.frecuencia_semana`).
- Nunca se agenda más de una pieza el mismo día, sin importar el canal:
  el objetivo es que una sola persona pueda ejecutar el calendario sin
  saturarse.
- El algoritmo es determinista y no depende de la API de IA, por lo que es
  fácil de testear (ver tests/test_calendar_builder.py).
"""
from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path

from icalendar import Calendar, Event

from .brand_profile import BrandProfile

DEFAULT_FRECUENCIA_SEMANA = 1.0


def _intervalo_dias(frecuencia_semana: float) -> int:
    if frecuencia_semana <= 0:
        frecuencia_semana = DEFAULT_FRECUENCIA_SEMANA
    return max(1, round(7 / frecuencia_semana))


def _frecuencias_por_canal(perfil: BrandProfile) -> dict[str, float]:
    return {c.nombre.strip().lower(): c.frecuencia_semana for c in perfil.canales}


def build_calendar(
    copies: list[dict],
    perfil: BrandProfile,
    start_date: date | None = None,
) -> list[dict]:
    """Asigna una fecha a cada copy respetando la frecuencia por canal y
    evitando más de una pieza por día."""
    if start_date is None:
        start_date = date.today()

    frecuencias = _frecuencias_por_canal(perfil)

    por_canal: dict[str, list[dict]] = {}
    for copy in copies:
        canal = (copy.get("canal") or "").strip()
        por_canal.setdefault(canal, []).append(copy)

    ocupado: set[date] = set()
    entradas: list[dict] = []

    for canal, piezas in por_canal.items():
        frecuencia = frecuencias.get(canal.lower(), DEFAULT_FRECUENCIA_SEMANA)
        intervalo = _intervalo_dias(frecuencia)
        fecha = start_date
        for pieza in piezas:
            while fecha in ocupado:
                fecha += timedelta(days=1)
            ocupado.add(fecha)
            entradas.append(
                {
                    "fecha": fecha.isoformat(),
                    "canal": canal,
                    "idea_titulo": pieza.get("idea_titulo", ""),
                    "texto": pieza.get("texto", ""),
                    "estado": "planeado",
                }
            )
            fecha += timedelta(days=intervalo)

    entradas.sort(key=lambda e: e["fecha"])
    return entradas


def _build_ical(calendario: list[dict]) -> Calendar:
    cal = Calendar()
    cal.add("prodid", "-//Voz de Marca IA//bootcamp//ES")
    cal.add("version", "2.0")

    for entrada in calendario:
        evento = Event()
        titulo = entrada.get("idea_titulo") or "Publicación"
        evento.add("summary", f"[{entrada['canal']}] {titulo}")
        evento.add("description", entrada.get("texto", ""))
        dia = date.fromisoformat(entrada["fecha"])
        evento.add("dtstart", dia)
        evento.add("dtend", dia + timedelta(days=1))
        cal.add_component(evento)

    return cal


def to_ics_bytes(calendario: list[dict]) -> bytes:
    return _build_ical(calendario).to_ical()


def export_ics(calendario: list[dict], path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(to_ics_bytes(calendario))
    return path
