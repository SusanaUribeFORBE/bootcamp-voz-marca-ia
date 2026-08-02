from datetime import date

from src.brand_profile import BrandProfile, Canal
from src.calendar_builder import build_calendar, export_ics


def _perfil_ejemplo() -> BrandProfile:
    return BrandProfile(
        nombre_negocio="Fonda Doña Pola",
        descripcion_corta="Restaurante de comida antioqueña en Medellín.",
        canales=[
            Canal(nombre="Instagram", frecuencia_semana=3),
            Canal(nombre="WhatsApp", frecuencia_semana=1),
            Canal(nombre="Blog", frecuencia_semana=0.25),
        ],
    )


def _copies(canal: str, cantidad: int) -> list[dict]:
    return [
        {"idea_titulo": f"Idea {i}", "canal": canal, "texto": f"Texto {i}"}
        for i in range(cantidad)
    ]


def test_build_calendar_asigna_una_fecha_por_pieza():
    perfil = _perfil_ejemplo()
    copies = _copies("Instagram", 5) + _copies("WhatsApp", 2) + _copies("Blog", 1)

    calendario = build_calendar(copies, perfil, start_date=date(2026, 8, 3))

    assert len(calendario) == len(copies)
    for entrada in calendario:
        assert entrada["estado"] == "planeado"
        assert entrada["fecha"]
        assert entrada["canal"]


def test_build_calendar_nunca_repite_fecha():
    perfil = _perfil_ejemplo()
    copies = _copies("Instagram", 6) + _copies("WhatsApp", 4) + _copies("Blog", 2)

    calendario = build_calendar(copies, perfil, start_date=date(2026, 8, 3))

    fechas = [e["fecha"] for e in calendario]
    assert len(fechas) == len(set(fechas))


def test_build_calendar_queda_ordenado_por_fecha():
    perfil = _perfil_ejemplo()
    copies = _copies("Instagram", 4) + _copies("WhatsApp", 3)

    calendario = build_calendar(copies, perfil, start_date=date(2026, 8, 3))

    fechas = [date.fromisoformat(e["fecha"]) for e in calendario]
    assert fechas == sorted(fechas)


def test_build_calendar_respeta_frecuencia_aproximada_instagram():
    # 3x/semana => intervalo ideal de ~2-3 días entre piezas del mismo canal.
    perfil = _perfil_ejemplo()
    copies = _copies("Instagram", 4)

    calendario = build_calendar(copies, perfil, start_date=date(2026, 8, 3))
    fechas = sorted(date.fromisoformat(e["fecha"]) for e in calendario)

    for anterior, actual in zip(fechas, fechas[1:]):
        assert 1 <= (actual - anterior).days <= 3


def test_canal_sin_frecuencia_definida_usa_default_sin_fallar():
    perfil = _perfil_ejemplo()
    copies = _copies("TikTok", 2)  # canal no está en perfil.canales

    calendario = build_calendar(copies, perfil, start_date=date(2026, 8, 3))

    assert len(calendario) == 2


def test_export_ics_genera_un_evento_por_pieza(tmp_path):
    perfil = _perfil_ejemplo()
    copies = _copies("Instagram", 3)
    calendario = build_calendar(copies, perfil, start_date=date(2026, 8, 3))

    destino = tmp_path / "calendario.ics"
    export_ics(calendario, destino)

    contenido = destino.read_text(encoding="utf-8")
    assert contenido.count("BEGIN:VEVENT") == 3
    assert "Idea 0" in contenido
