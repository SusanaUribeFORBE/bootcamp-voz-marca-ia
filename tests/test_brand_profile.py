from src.brand_profile import BrandProfile


def test_from_dict_con_perfil_antiguo_sin_logo_ni_color_usa_defaults():
    """Perfiles guardados en disco antes de agregar logo_path/color_marca
    a BrandProfile deben seguir cargando, con los valores por defecto."""
    perfil_antiguo = {
        "nombre_negocio": "Fonda Doña Pola",
        "descripcion_corta": "Restaurante de comida antioqueña.",
        "tono": ["cercano"],
        "valores": ["Ingredientes locales"],
        "publico_objetivo": "Adultos en Medellín",
        "diferenciadores": ["Bandeja paisa"],
        "canales": [{"nombre": "Instagram", "frecuencia_semana": 3}],
        "restricciones": ["No groserías"],
        "ejemplos_frases": ["Aquí la sazón no se apura"],
    }

    perfil = BrandProfile.from_dict(perfil_antiguo)

    assert perfil.nombre_negocio == "Fonda Doña Pola"
    assert perfil.logo_path == ""
    assert perfil.color_marca == "#8B4A2B"


def test_from_dict_con_perfil_nuevo_respeta_logo_y_color_guardados():
    perfil_nuevo = {
        "nombre_negocio": "Fonda Doña Pola",
        "descripcion_corta": "Restaurante de comida antioqueña.",
        "logo_path": "data/fonda-dona-pola/logo.png",
        "color_marca": "#123456",
    }

    perfil = BrandProfile.from_dict(perfil_nuevo)

    assert perfil.logo_path == "data/fonda-dona-pola/logo.png"
    assert perfil.color_marca == "#123456"


def test_from_dict_ignora_claves_desconocidas():
    perfil = BrandProfile.from_dict(
        {
            "nombre_negocio": "Fonda Doña Pola",
            "descripcion_corta": "Restaurante de comida antioqueña.",
            "campo_que_ya_no_existe": "algo",
        }
    )

    assert perfil.nombre_negocio == "Fonda Doña Pola"
