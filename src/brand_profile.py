"""Modelo del perfil de voz de marca.

El perfil es la pieza central del sistema: todo texto generado (ideas,
copies) se ancla a este perfil para mantener una voz de marca consistente
entre canales y en el tiempo.
"""
from __future__ import annotations

import re
import unicodedata
from dataclasses import asdict, dataclass, field


def slugify(texto: str) -> str:
    texto = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode("ascii")
    texto = texto.lower().strip()
    texto = re.sub(r"[^a-z0-9]+", "-", texto)
    return texto.strip("-")


@dataclass
class Canal:
    """Un canal de publicación con su frecuencia deseada."""

    nombre: str  # ej. "Instagram", "WhatsApp", "Blog"
    frecuencia_semana: float  # veces por semana; usar fracciones para <1x/semana (ej. 0.25 = 1x/mes)


@dataclass
class BrandProfile:
    nombre_negocio: str
    descripcion_corta: str
    tono: list[str] = field(default_factory=list)
    valores: list[str] = field(default_factory=list)
    publico_objetivo: str = ""
    diferenciadores: list[str] = field(default_factory=list)
    canales: list[Canal] = field(default_factory=list)
    restricciones: list[str] = field(default_factory=list)
    ejemplos_frases: list[str] = field(default_factory=list)
    logo_path: str = ""
    color_marca: str = "#8B4A2B"

    @property
    def slug(self) -> str:
        return slugify(self.nombre_negocio)

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "BrandProfile":
        data = dict(data)
        canales_raw = data.get("canales", []) or []
        data["canales"] = [
            c if isinstance(c, Canal) else Canal(**c) for c in canales_raw
        ]
        campos_validos = {f for f in cls.__dataclass_fields__}
        data = {k: v for k, v in data.items() if k in campos_validos}
        return cls(**data)
