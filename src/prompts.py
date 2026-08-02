"""Construcción de prompts a partir del perfil de marca.

Este módulo es el punto único donde el `BrandProfile` se traduce a lenguaje
natural para el modelo. Si el perfil cambia, todo lo que se genere después
(ideas y copies) hereda automáticamente la nueva voz — es el mecanismo que
garantiza consistencia entre canales y en el tiempo.
"""
from __future__ import annotations

from .brand_profile import BrandProfile

# Reglas de formato conocidas por canal. Si el usuario define un canal que no
# está aquí, se usa una guía genérica (ver `_reglas_canal`).
REGLAS_CANAL = {
    "instagram": (
        "- Formato: caption corto (máx. 5-6 líneas), lenguaje visual, "
        "pensado para acompañar una foto o reel.\n"
        "- Incluye 1 llamado a la acción (CTA) claro al final.\n"
        "- Incluye 3 a 6 hashtags relevantes y locales (Medellín/Antioquia) al final, "
        "en una línea aparte.\n"
        "- Puede usar emojis con moderación, coherentes con el tono de marca."
    ),
    "whatsapp": (
        "- Formato: mensaje conversacional, como si el dueño del negocio le "
        "escribiera directo a un cliente o a una lista de difusión.\n"
        "- Corto (máx. 3-4 líneas), sin hashtags.\n"
        "- Cercano y personal, puede incluir 1 emoji si el tono de marca lo permite.\n"
        "- Debe dejar claro qué acción tomar (ej. responder, reservar, pedir)."
    ),
    "blog": (
        "- Formato: artículo corto (300-500 palabras) con un título llamativo "
        "y 2-4 subtítulos (H2).\n"
        "- Tono más desarrollado que en redes, pero sin perder la voz de marca.\n"
        "- Cierra con una conclusión breve y una invitación a visitar o contactar "
        "el negocio."
    ),
}

REGLA_GENERICA = (
    "- No hay una regla de formato predefinida para este canal: usa buen juicio "
    "editorial, prioriza que la pieza sea publicable tal cual, y adapta la "
    "longitud a lo que sea razonable para ese canal."
)


def _reglas_canal(canal: str) -> str:
    return REGLAS_CANAL.get(canal.strip().lower(), REGLA_GENERICA)


def build_system_prompt(perfil: BrandProfile) -> str:
    """Serializa el perfil de marca a un system prompt reutilizable."""
    tono = ", ".join(perfil.tono) or "sin definir"
    valores = "\n".join(f"- {v}" for v in perfil.valores) or "- (sin definir)"
    diferenciadores = "\n".join(f"- {d}" for d in perfil.diferenciadores) or "- (sin definir)"
    restricciones = "\n".join(f"- {r}" for r in perfil.restricciones) or "- (sin restricciones adicionales)"
    ejemplos = "\n".join(f'- "{e}"' for e in perfil.ejemplos_frases) or "- (sin ejemplos)"

    return f"""Eres el redactor de marketing de "{perfil.nombre_negocio}", una pyme colombiana.

DESCRIPCIÓN DEL NEGOCIO
{perfil.descripcion_corta}

PÚBLICO OBJETIVO
{perfil.publico_objetivo or "sin definir"}

TONO DE VOZ (aplica siempre, en todos los canales)
{tono}

VALORES DE MARCA
{valores}

DIFERENCIADORES (qué los hace únicos frente a la competencia)
{diferenciadores}

RESTRICCIONES — NUNCA hagas esto
{restricciones}

EJEMPLOS DE FRASES QUE SÍ SUENAN A ESTA MARCA (úsalas como referencia de estilo, no las copies literalmente)
{ejemplos}

REGLAS GENERALES
- Escribe siempre en español de Colombia, natural, sin sonar a traducción.
- Mantén la voz de marca consistente sin importar el canal: lo que cambia es
  el formato y la longitud, no la personalidad de la marca.
- Nunca inventes datos concretos (precios, direcciones, horarios, promociones)
  que no te hayan dado explícitamente; si hace falta un dato así, usa un
  placeholder entre corchetes, ej. [precio] o [horario].
- Cuando se te pida una salida en JSON, responde ÚNICAMENTE con JSON válido,
  sin texto adicional antes ni después, sin bloques de código markdown."""


def build_ideas_prompt(perfil: BrandProfile, cantidad: int, temporada: str | None = None) -> str:
    canales = ", ".join(c.nombre for c in perfil.canales) or "redes sociales en general"
    contexto_temporada = f"\nContexto/temporada a considerar: {temporada}." if temporada else ""

    return f"""Genera {cantidad} ideas de contenido de marketing para este negocio,
pensadas para publicarse en estos canales: {canales}.{contexto_temporada}

Cada idea debe tener un ángulo distinto (no repitas el mismo tema con otras
palabras). Varía entre ideas que muestren producto, ideas que muestren la
historia/valores de la marca, e ideas que inviten a la acción (venta directa).

Responde en JSON con esta forma exacta:
{{
  "ideas": [
    {{
      "titulo": "string corto, 5-10 palabras",
      "angulo": "1-2 frases explicando de qué trata y por qué encaja con la marca",
      "canal_sugerido": "uno de: {canales}",
      "objetivo": "uno de: awareness, venta, engagement"
    }}
  ]
}}"""


def build_copy_prompt(perfil: BrandProfile, idea: dict, canal: str) -> str:
    reglas = _reglas_canal(canal)

    return f"""Escribe el copy final para publicar, basado en esta idea:

Título de la idea: {idea.get("titulo", "")}
Ángulo: {idea.get("angulo", "")}
Objetivo: {idea.get("objetivo", "")}

Canal de destino: {canal}

REGLAS DE FORMATO PARA ESTE CANAL
{reglas}

Responde en JSON con esta forma exacta:
{{
  "canal": "{canal}",
  "texto": "el copy completo, listo para publicar, incluyendo saltos de línea con \\n donde corresponda"
}}"""


def build_ideas_validation_prompt(ideas: list[dict]) -> str:
    """Pide evaluar todas las ideas del lote en una sola llamada."""
    ideas_texto = "\n".join(
        f"{i}. Título: {idea.get('titulo', '')} | Ángulo: {idea.get('angulo', '')} | "
        f"Objetivo: {idea.get('objetivo', '')}"
        for i, idea in enumerate(ideas)
    )

    return f"""Evalúa si cada una de estas ideas de contenido respeta el tono, los
valores y, sobre todo, las restricciones de la marca definidos arriba en tu
system prompt.

IDEAS A EVALUAR
{ideas_texto}

Para cada idea, decide si es consistente con la marca (true) o si se desvía
de alguna forma (false) — por ejemplo, si viola una restricción, usa un tono
que no corresponde, o no encaja con los valores/diferenciadores del negocio.

Responde en JSON con esta forma exacta:
{{
  "resultados": [
    {{"indice": 0, "consistente": true, "motivo": "1 frase corta explicando por qué"}}
  ]
}}

Incluye un resultado por cada idea, en el mismo orden (índice 0 a {len(ideas) - 1})."""


def build_copy_validation_prompt(copy: dict) -> str:
    """Evalúa un solo copy ya redactado contra el perfil de marca."""
    return f"""Evalúa si este copy respeta el tono, los valores y, sobre todo, las
restricciones de la marca definidos arriba en tu system prompt.

CANAL: {copy.get("canal", "")}
TEXTO A EVALUAR:
{copy.get("texto", "")}

Decide si es consistente con la marca (true) o si se desvía de alguna forma
(false) — por ejemplo, si viola una restricción, usa un tono que no
corresponde, o no encaja con los valores/diferenciadores del negocio.

Responde en JSON con esta forma exacta:
{{
  "consistente": true,
  "motivo": "1 frase corta explicando por qué"
}}"""
