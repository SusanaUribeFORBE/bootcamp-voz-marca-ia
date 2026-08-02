"""Estimación transparente del tiempo ahorrado usando la app vs. hacerlo a mano.

No es un estudio de tiempos: son supuestos declarados explícitamente (ver
docs/decisiones.md) sobre cuánto toma cada tarea a mano vs. revisar/ajustar
lo que genera la IA. La UI muestra estos mismos supuestos para que el cálculo
sea auditable, no una caja negra.
"""
from __future__ import annotations

from dataclasses import dataclass

MINUTOS_MANUAL_IDEA = 15
MINUTOS_MANUAL_COPY = 20
MINUTOS_MANUAL_CALENDARIO = 45

MINUTOS_IA_IDEA = 1
MINUTOS_IA_COPY = 2
MINUTOS_IA_CALENDARIO = 2


@dataclass
class ImpactoEstimado:
    minutos_manual: float
    minutos_con_ia: float

    @property
    def minutos_ahorrados(self) -> float:
        return max(0.0, self.minutos_manual - self.minutos_con_ia)

    @property
    def horas_ahorradas(self) -> float:
        return self.minutos_ahorrados / 60


def estimar_impacto(n_ideas: int, n_copies: int, tiene_calendario: bool) -> ImpactoEstimado:
    minutos_manual = n_ideas * MINUTOS_MANUAL_IDEA + n_copies * MINUTOS_MANUAL_COPY
    minutos_con_ia = n_ideas * MINUTOS_IA_IDEA + n_copies * MINUTOS_IA_COPY

    if tiene_calendario:
        minutos_manual += MINUTOS_MANUAL_CALENDARIO
        minutos_con_ia += MINUTOS_IA_CALENDARIO

    return ImpactoEstimado(minutos_manual=minutos_manual, minutos_con_ia=minutos_con_ia)
