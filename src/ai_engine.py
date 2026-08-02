"""Wrapper sobre la API de Claude (Anthropic) para generar ideas y copies.

Toda llamada al modelo se hace con el mismo `system prompt` derivado del
perfil de marca (ver prompts.py) — así se garantiza que la voz sea
consistente entre una idea y otra, y entre un canal y otro.
"""
from __future__ import annotations

import json
import os

from anthropic import Anthropic

from .brand_profile import BrandProfile
from .prompts import (
    build_copy_prompt,
    build_copy_validation_prompt,
    build_ideas_prompt,
    build_ideas_validation_prompt,
    build_system_prompt,
)

MODEL = os.environ.get("CLAUDE_MODEL", "claude-sonnet-5")
MAX_TOKENS_IDEAS = 2000
MAX_TOKENS_COPY = 1200
MAX_TOKENS_VALIDACION = 1500


class ConfiguracionError(RuntimeError):
    """La API key de Anthropic no está configurada."""


def get_client() -> Anthropic:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise ConfiguracionError(
            "No se encontró ANTHROPIC_API_KEY. Copia .env.example a .env y "
            "coloca tu API key antes de generar contenido."
        )
    return Anthropic(api_key=api_key)


def _texto_respuesta(respuesta) -> str:
    """Extrae el primer bloque de texto de la respuesta.

    Algunos modelos devuelven bloques de "thinking" antes del bloque de
    texto final, así que no se puede asumir que `content[0]` sea texto.
    """
    for bloque in respuesta.content:
        if getattr(bloque, "type", None) == "text":
            return bloque.text
    raise ValueError("La respuesta de Claude no contiene un bloque de texto.")


def _extraer_json(texto: str) -> dict:
    """Limpia posibles bloques de código markdown y parsea JSON."""
    texto = texto.strip()
    if texto.startswith("```"):
        texto = texto.split("```", 2)[1]
        if texto.startswith("json"):
            texto = texto[len("json"):]
        texto = texto.strip()
        if texto.endswith("```"):
            texto = texto[: -len("```")]
    # strict=False: permite caracteres de control (ej. saltos de línea reales)
    # dentro de los strings, porque el modelo a veces no los escapa como \n
    # en textos largos (blog).
    return json.loads(texto.strip(), strict=False)


def generate_ideas(
    perfil: BrandProfile, cantidad: int = 6, temporada: str | None = None
) -> list[dict]:
    client = get_client()
    system = build_system_prompt(perfil)
    user_prompt = build_ideas_prompt(perfil, cantidad, temporada)

    respuesta = client.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS_IDEAS,
        system=system,
        messages=[{"role": "user", "content": user_prompt}],
    )
    texto = _texto_respuesta(respuesta)
    data = _extraer_json(texto)
    return data.get("ideas", [])


def generate_copy(perfil: BrandProfile, idea: dict, canal: str) -> dict:
    client = get_client()
    system = build_system_prompt(perfil)
    user_prompt = build_copy_prompt(perfil, idea, canal)

    respuesta = client.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS_COPY,
        system=system,
        messages=[{"role": "user", "content": user_prompt}],
    )
    texto = _texto_respuesta(respuesta)
    data = _extraer_json(texto)
    return {
        "idea_titulo": idea.get("titulo", ""),
        "canal": data.get("canal", canal),
        "texto": data.get("texto", ""),
    }


def validate_ideas(perfil: BrandProfile, ideas: list[dict]) -> list[dict]:
    """Evalúa un lote de ideas contra el perfil de marca en una sola llamada.

    Si la validación falla (ej. error de red/API), no rompe el flujo
    principal: devuelve las ideas con `consistente=None` y un motivo neutro,
    para que la UI muestre un estado "no validado" en vez de un error.
    """
    try:
        client = get_client()
        system = build_system_prompt(perfil)
        user_prompt = build_ideas_validation_prompt(ideas)

        respuesta = client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS_VALIDACION,
            system=system,
            messages=[{"role": "user", "content": user_prompt}],
        )
        texto = _texto_respuesta(respuesta)
        data = _extraer_json(texto)
        resultados = {r.get("indice"): r for r in data.get("resultados", [])}
    except Exception:  # noqa: BLE001 - la validación nunca debe romper la generación
        resultados = {}

    ideas_validadas = []
    for i, idea in enumerate(ideas):
        resultado = resultados.get(i)
        idea_validada = dict(idea)
        if resultado is not None:
            idea_validada["consistente"] = resultado.get("consistente")
            idea_validada["motivo"] = resultado.get("motivo", "")
        else:
            idea_validada["consistente"] = None
            idea_validada["motivo"] = "No se pudo validar."
        ideas_validadas.append(idea_validada)
    return ideas_validadas


def validate_copy(perfil: BrandProfile, copy: dict) -> dict:
    """Evalúa un copy ya redactado contra el perfil de marca.

    Igual que `validate_ideas`, si la validación falla no rompe el flujo
    principal: devuelve el copy con `consistente=None`.
    """
    try:
        client = get_client()
        system = build_system_prompt(perfil)
        user_prompt = build_copy_validation_prompt(copy)

        respuesta = client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS_VALIDACION,
            system=system,
            messages=[{"role": "user", "content": user_prompt}],
        )
        texto = _texto_respuesta(respuesta)
        data = _extraer_json(texto)
        copy_validado = dict(copy)
        copy_validado["consistente"] = data.get("consistente")
        copy_validado["motivo"] = data.get("motivo", "")
    except Exception:  # noqa: BLE001 - la validación nunca debe romper la generación
        copy_validado = dict(copy)
        copy_validado["consistente"] = None
        copy_validado["motivo"] = "No se pudo validar."
    return copy_validado
