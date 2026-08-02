"""Persistencia en archivos locales: data/<slug-negocio>/*.json.

Sin base de datos por diseño (MVP de un solo negocio a la vez, ver
docs/decisiones.md): JSON es suficiente, versionable en git y fácil de
inspeccionar a mano.
"""
from __future__ import annotations

import json
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def business_dir(slug: str) -> Path:
    d = DATA_DIR / slug
    d.mkdir(parents=True, exist_ok=True)
    return d


def save_json(slug: str, filename: str, data) -> Path:
    path = business_dir(slug) / filename
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def load_json(slug: str, filename: str, default=None):
    path = business_dir(slug) / filename
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def list_businesses() -> list[str]:
    if not DATA_DIR.exists():
        return []
    return sorted(p.name for p in DATA_DIR.iterdir() if p.is_dir())


def save_profile(profile) -> Path:
    return save_json(profile.slug, "perfil.json", profile.to_dict())


def load_profile(slug: str):
    from .brand_profile import BrandProfile

    data = load_json(slug, "perfil.json")
    if data is None:
        return None
    return BrandProfile.from_dict(data)


def save_ideas(slug: str, ideas: list[dict]) -> Path:
    return save_json(slug, "ideas.json", ideas)


def load_ideas(slug: str) -> list[dict]:
    return load_json(slug, "ideas.json", default=[])


def save_copies(slug: str, copies: list[dict]) -> Path:
    return save_json(slug, "copies.json", copies)


def load_copies(slug: str) -> list[dict]:
    return load_json(slug, "copies.json", default=[])
