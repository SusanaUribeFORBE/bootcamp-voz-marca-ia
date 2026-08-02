from src.impact_metrics import (
    MINUTOS_IA_CALENDARIO,
    MINUTOS_IA_COPY,
    MINUTOS_IA_IDEA,
    MINUTOS_MANUAL_CALENDARIO,
    MINUTOS_MANUAL_COPY,
    MINUTOS_MANUAL_IDEA,
    estimar_impacto,
)


def test_sin_contenido_no_ahorra_nada():
    impacto = estimar_impacto(n_ideas=0, n_copies=0, tiene_calendario=False)
    assert impacto.minutos_manual == 0
    assert impacto.minutos_con_ia == 0
    assert impacto.minutos_ahorrados == 0
    assert impacto.horas_ahorradas == 0


def test_calcula_ahorro_con_ideas_y_copies():
    impacto = estimar_impacto(n_ideas=6, n_copies=6, tiene_calendario=False)

    minutos_manual_esperado = 6 * MINUTOS_MANUAL_IDEA + 6 * MINUTOS_MANUAL_COPY
    minutos_ia_esperado = 6 * MINUTOS_IA_IDEA + 6 * MINUTOS_IA_COPY

    assert impacto.minutos_manual == minutos_manual_esperado
    assert impacto.minutos_con_ia == minutos_ia_esperado
    assert impacto.minutos_ahorrados == minutos_manual_esperado - minutos_ia_esperado
    assert impacto.horas_ahorradas == impacto.minutos_ahorrados / 60


def test_calendario_suma_su_propio_ahorro():
    sin_calendario = estimar_impacto(n_ideas=1, n_copies=1, tiene_calendario=False)
    con_calendario = estimar_impacto(n_ideas=1, n_copies=1, tiene_calendario=True)

    assert con_calendario.minutos_manual == sin_calendario.minutos_manual + MINUTOS_MANUAL_CALENDARIO
    assert con_calendario.minutos_con_ia == sin_calendario.minutos_con_ia + MINUTOS_IA_CALENDARIO
    assert con_calendario.minutos_ahorrados > sin_calendario.minutos_ahorrados


def test_ahorro_nunca_es_negativo():
    impacto = estimar_impacto(n_ideas=0, n_copies=0, tiene_calendario=True)
    assert impacto.minutos_ahorrados >= 0
    assert impacto.horas_ahorradas >= 0
