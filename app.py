"""App Streamlit: perfil de marca -> ideas -> copies -> calendario -> .ics."""
from __future__ import annotations

import os
from datetime import date
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

from src import storage
from src.ai_engine import ConfiguracionError, generate_copy, generate_ideas, validate_copy, validate_ideas
from src.brand_profile import BrandProfile, Canal, slugify
from src.calendar_builder import build_calendar, to_ics_bytes
from src.graphic_generator import generate_graphic
from src.impact_metrics import (
    MINUTOS_IA_CALENDARIO,
    MINUTOS_IA_COPY,
    MINUTOS_IA_IDEA,
    MINUTOS_MANUAL_CALENDARIO,
    MINUTOS_MANUAL_COPY,
    MINUTOS_MANUAL_IDEA,
    estimar_impacto,
)

load_dotenv()

st.set_page_config(
    page_title="Voz de Marca IA",
    page_icon="🗣️",
    layout="wide",
    menu_items={"Get help": None, "Report a bug": None, "About": None},
)

# Oculta el menú de hamburguesa nativo y el footer "Made with Streamlit":
# están en inglés y no son traducibles vía menu_items, así que se ocultan
# por CSS para el Demo Day (ver docs/decisiones.md).
st.markdown(
    """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("🗣️ Voz de Marca IA")
st.caption(
    "Elimina el bloqueo creativo y ahorra horas a la semana: automatiza el "
    "marketing de tu negocio con contenido listo para publicar, adaptado a "
    "tus canales y fiel a tu marca."
)

if not os.environ.get("ANTHROPIC_API_KEY"):
    st.warning(
        "No se encontró `ANTHROPIC_API_KEY`. Copia `.env.example` a `.env` y "
        "coloca tu API key para poder generar contenido con IA. Aún puedes "
        "crear o editar el perfil de marca sin la key."
    )

negocios = storage.list_businesses()
opciones = ["➕ Nuevo negocio"] + negocios
seleccion = st.sidebar.selectbox("Negocio", opciones)

if "slug_actual" not in st.session_state:
    st.session_state.slug_actual = negocios[0] if negocios else None

if seleccion != "➕ Nuevo negocio":
    st.session_state.slug_actual = seleccion
elif seleccion == "➕ Nuevo negocio" and st.sidebar.button("Empezar negocio nuevo"):
    st.session_state.slug_actual = None

perfil_actual = (
    storage.load_profile(st.session_state.slug_actual) if st.session_state.slug_actual else None
)

if perfil_actual:
    n_ideas = len(storage.load_ideas(perfil_actual.slug))
    n_copies = len(storage.load_copies(perfil_actual.slug))
    tiene_calendario = (storage.business_dir(perfil_actual.slug) / "calendario.ics").exists()
    impacto = estimar_impacto(n_ideas, n_copies, tiene_calendario)

    col_m1, col_m2, col_m3 = st.columns(3)
    col_m1.metric("⏱️ Tiempo ahorrado (estimado)", f"{impacto.horas_ahorradas:.1f} h")
    col_m2.metric("💡 Ideas generadas", n_ideas)
    col_m3.metric("✍️ Copies generados", n_copies)

    with st.expander("¿Cómo se calcula esto?"):
        st.markdown(
            f"""
Es una aproximación simple y transparente, no un estudio de tiempos formal.
Se compara el tiempo típico de hacer cada tarea a mano vs. revisar/ajustar lo
que genera la IA:

| Tarea | A mano | Con IA (revisar/ajustar) |
|---|---|---|
| Idea de contenido | {MINUTOS_MANUAL_IDEA} min | {MINUTOS_IA_IDEA} min |
| Copy adaptado a un canal | {MINUTOS_MANUAL_COPY} min | {MINUTOS_IA_COPY} min |
| Calendario de publicación | {MINUTOS_MANUAL_CALENDARIO} min | {MINUTOS_IA_CALENDARIO} min |

Con {n_ideas} idea(s), {n_copies} copy(s){" y calendario generado" if tiene_calendario else ""}:
tiempo a mano ≈ {impacto.minutos_manual:.0f} min, tiempo con la app ≈
{impacto.minutos_con_ia:.0f} min.
            """
        )

tab_perfil, tab_ideas, tab_copies, tab_calendario = st.tabs(
    ["1. Perfil de marca", "2. Ideas", "3. Copies", "4. Calendario"]
)

CANALES_BASE = ["Instagram", "WhatsApp", "Blog"]

# --- 1. Perfil de marca ---------------------------------------------------
with tab_perfil:
    st.subheader("Perfil de voz de marca")
    st.caption(
        "Este perfil es la base de todo lo que se genera: entre más claro, "
        "más consistente será la voz de la marca en cada pieza."
    )

    with st.form("form_perfil"):
        nombre_negocio = st.text_input(
            "Nombre del negocio",
            value=perfil_actual.nombre_negocio if perfil_actual else "",
        )
        descripcion_corta = st.text_area(
            "Descripción corta del negocio",
            value=perfil_actual.descripcion_corta if perfil_actual else "",
        )
        tono = st.text_input(
            "Tono de voz (separado por comas)",
            value=", ".join(perfil_actual.tono) if perfil_actual else "",
            help="Ej: cercano, cálido, con humor paisa moderado",
        )
        valores = st.text_area(
            "Valores de marca (uno por línea)",
            value="\n".join(perfil_actual.valores) if perfil_actual else "",
        )
        publico_objetivo = st.text_area(
            "Público objetivo",
            value=perfil_actual.publico_objetivo if perfil_actual else "",
        )
        diferenciadores = st.text_area(
            "Diferenciadores (uno por línea)",
            value="\n".join(perfil_actual.diferenciadores) if perfil_actual else "",
        )
        restricciones = st.text_area(
            "Restricciones — qué NUNCA debe hacer el contenido (uno por línea)",
            value="\n".join(perfil_actual.restricciones) if perfil_actual else "",
        )
        ejemplos_frases = st.text_area(
            "Ejemplos de frases que sí suenan a la marca (uno por línea)",
            value="\n".join(perfil_actual.ejemplos_frases) if perfil_actual else "",
        )

        st.markdown("**Piezas gráficas**")
        col_color, col_logo = st.columns([1, 2])
        with col_color:
            color_marca = st.color_picker(
                "Color de marca",
                value=perfil_actual.color_marca if perfil_actual else "#8B4A2B",
            )
        with col_logo:
            logo_subido = st.file_uploader(
                "Logo (opcional, PNG o JPG)", type=["png", "jpg", "jpeg"]
            )
            if perfil_actual and perfil_actual.logo_path and not logo_subido:
                st.caption(f"Logo actual: `{perfil_actual.logo_path}`")

        st.markdown("**Canales y frecuencia deseada (veces por semana)**")
        valores_default = {c.nombre: c.frecuencia_semana for c in perfil_actual.canales} if perfil_actual else {
            "Instagram": 3.0,
            "WhatsApp": 1.0,
            "Blog": 0.25,
        }
        columnas = st.columns(len(CANALES_BASE))
        nuevos_canales: list[Canal] = []
        for col, nombre_canal in zip(columnas, CANALES_BASE):
            with col:
                freq = st.number_input(
                    f"{nombre_canal} (x/semana)",
                    min_value=0.0,
                    value=float(valores_default.get(nombre_canal, 0.0)),
                    step=0.25,
                )
                if freq > 0:
                    nuevos_canales.append(Canal(nombre_canal, freq))

        guardar = st.form_submit_button("Guardar perfil")

    if guardar:
        if not nombre_negocio.strip():
            st.error("El nombre del negocio es obligatorio.")
        else:
            slug_nuevo = slugify(nombre_negocio.strip())
            logo_path = perfil_actual.logo_path if perfil_actual else ""
            if logo_subido is not None:
                extension = Path(logo_subido.name).suffix or ".png"
                ruta_logo = storage.business_dir(slug_nuevo) / f"logo{extension}"
                ruta_logo.write_bytes(logo_subido.getvalue())
                logo_path = str(ruta_logo)

            perfil = BrandProfile(
                nombre_negocio=nombre_negocio.strip(),
                descripcion_corta=descripcion_corta.strip(),
                tono=[t.strip() for t in tono.split(",") if t.strip()],
                valores=[v.strip() for v in valores.splitlines() if v.strip()],
                publico_objetivo=publico_objetivo.strip(),
                diferenciadores=[d.strip() for d in diferenciadores.splitlines() if d.strip()],
                canales=nuevos_canales,
                restricciones=[r.strip() for r in restricciones.splitlines() if r.strip()],
                ejemplos_frases=[e.strip() for e in ejemplos_frases.splitlines() if e.strip()],
                logo_path=logo_path,
                color_marca=color_marca,
            )
            storage.save_profile(perfil)
            st.session_state.slug_actual = perfil.slug
            st.success(f"Perfil guardado: {perfil.nombre_negocio} (`{perfil.slug}`)")
            st.rerun()

# --- 2. Ideas ---------------------------------------------------------------
with tab_ideas:
    if not st.session_state.slug_actual:
        st.info("Primero crea y guarda un perfil de marca en la pestaña 1.")
    else:
        perfil = storage.load_profile(st.session_state.slug_actual)
        st.subheader(f"Ideas de contenido — {perfil.nombre_negocio}")

        col_a, col_b = st.columns([1, 2])
        with col_a:
            cantidad = st.number_input("Cantidad de ideas", min_value=1, max_value=20, value=6)
            temporada = st.text_input(
                "Temporada/contexto (opcional)", placeholder="Ej: diciembre, día de la madre"
            )
            if st.button("✨ Generar ideas"):
                try:
                    with st.spinner("Generando ideas con Claude..."):
                        ideas = generate_ideas(perfil, cantidad=int(cantidad), temporada=temporada or None)
                    with st.spinner("Verificando consistencia con la marca..."):
                        ideas = validate_ideas(perfil, ideas)
                    storage.save_ideas(perfil.slug, ideas)
                    st.success(f"{len(ideas)} ideas generadas y guardadas.")
                    st.rerun()
                except ConfiguracionError as e:
                    st.error(str(e))
                except Exception as e:  # noqa: BLE001 - mostrar cualquier error de la API al usuario
                    st.error(f"Error generando ideas: {e}")

        ideas_guardadas = storage.load_ideas(perfil.slug)
        if ideas_guardadas:
            st.markdown("### Ideas actuales")
            for i, idea in enumerate(ideas_guardadas):
                with st.expander(f"{i + 1}. {idea.get('titulo', '(sin título)')}"):
                    st.write(f"**Ángulo:** {idea.get('angulo', '')}")
                    st.write(f"**Canal sugerido:** {idea.get('canal_sugerido', '')}")
                    st.write(f"**Objetivo:** {idea.get('objetivo', '')}")
                    consistente = idea.get("consistente")
                    if consistente is True:
                        st.success("✓ Consistente con la marca")
                    elif consistente is False:
                        st.warning(f"⚠️ Revisar: {idea.get('motivo', '')}")
        else:
            st.info("Aún no hay ideas generadas para este negocio.")

# --- 3. Copies ---------------------------------------------------------------
with tab_copies:
    if not st.session_state.slug_actual:
        st.info("Primero crea un perfil y genera ideas.")
    else:
        perfil = storage.load_profile(st.session_state.slug_actual)
        ideas_guardadas = storage.load_ideas(perfil.slug)
        if not ideas_guardadas:
            st.info("Primero genera ideas en la pestaña 2.")
        else:
            st.subheader(f"Copies por canal — {perfil.nombre_negocio}")
            canales_disponibles = [c.nombre for c in perfil.canales] or CANALES_BASE

            titulos = [idea.get("titulo", f"Idea {i}") for i, idea in enumerate(ideas_guardadas)]
            idx_seleccion = st.selectbox(
                "Elige una idea", range(len(titulos)), format_func=lambda i: titulos[i]
            )
            idea_elegida = ideas_guardadas[idx_seleccion]

            canal_sugerido = idea_elegida.get("canal_sugerido")
            canales_elegidos = st.multiselect(
                "Canales para los que quieres generar copy",
                canales_disponibles,
                default=[canal_sugerido] if canal_sugerido in canales_disponibles else [],
            )

            if st.button("✍️ Generar copy(s)"):
                if not canales_elegidos:
                    st.warning("Elige al menos un canal.")
                else:
                    try:
                        copies_existentes = storage.load_copies(perfil.slug)
                        with st.spinner("Redactando copies..."):
                            for canal in canales_elegidos:
                                nuevo = generate_copy(perfil, idea_elegida, canal)
                                nuevo = validate_copy(perfil, nuevo)
                                copies_existentes.append(nuevo)
                        storage.save_copies(perfil.slug, copies_existentes)
                        st.success("Copy(s) generado(s) y guardado(s).")
                        st.rerun()
                    except ConfiguracionError as e:
                        st.error(str(e))
                    except Exception as e:  # noqa: BLE001
                        st.error(f"Error generando copy: {e}")

            copies_guardadas = storage.load_copies(perfil.slug)
            if copies_guardadas:
                st.markdown("### Copies generados")
                for i, copy in enumerate(copies_guardadas):
                    with st.expander(f"[{copy.get('canal')}] {copy.get('idea_titulo')}"):
                        st.text_area("Texto", value=copy.get("texto", ""), key=f"copy_{i}", height=150)
                        consistente = copy.get("consistente")
                        if consistente is True:
                            st.success("✓ Consistente con la marca")
                        elif consistente is False:
                            st.warning(f"⚠️ Revisar: {copy.get('motivo', '')}")

                        if st.button("🎨 Generar pieza gráfica", key=f"generar_grafica_{i}"):
                            imagen_bytes = generate_graphic(perfil, copy.get("idea_titulo", ""))
                            st.session_state[f"grafica_{i}"] = imagen_bytes

                        grafica_bytes = st.session_state.get(f"grafica_{i}")
                        if grafica_bytes:
                            st.image(grafica_bytes, width=300)
                            st.download_button(
                                "⬇️ Descargar pieza (.png)",
                                data=grafica_bytes,
                                file_name=f"pieza-{perfil.slug}-{i}.png",
                                mime="image/png",
                                key=f"descargar_grafica_{i}",
                            )
                if st.button("🗑️ Borrar todos los copies de este negocio"):
                    storage.save_copies(perfil.slug, [])
                    st.rerun()
            else:
                st.info("Aún no hay copies generados para este negocio.")

# --- 4. Calendario ------------------------------------------------------------
with tab_calendario:
    if not st.session_state.slug_actual:
        st.info("Primero crea un perfil y genera copies.")
    else:
        perfil = storage.load_profile(st.session_state.slug_actual)
        copies_guardadas = storage.load_copies(perfil.slug)
        if not copies_guardadas:
            st.info("Primero genera copies en la pestaña 3.")
        else:
            st.subheader(f"Calendario de publicación — {perfil.nombre_negocio}")
            fecha_inicio = st.date_input("Fecha de inicio", value=date.today())

            if st.button("📅 Generar calendario"):
                calendario = build_calendar(copies_guardadas, perfil, start_date=fecha_inicio)
                st.session_state["calendario_actual"] = calendario

            calendario = st.session_state.get("calendario_actual")
            if calendario:
                st.dataframe(
                    [
                        {
                            "Fecha": e["fecha"],
                            "Canal": e["canal"],
                            "Pieza": e["idea_titulo"],
                            "Estado": e["estado"],
                        }
                        for e in calendario
                    ],
                    use_container_width=True,
                )

                ics_bytes = to_ics_bytes(calendario)
                ruta_guardada = storage.business_dir(perfil.slug) / "calendario.ics"
                ruta_guardada.write_bytes(ics_bytes)

                st.download_button(
                    "⬇️ Descargar calendario (.ics)",
                    data=ics_bytes,
                    file_name=f"calendario-{perfil.slug}.ics",
                    mime="text/calendar",
                )
                st.caption(f"También guardado en `{ruta_guardada}`.")
