# Voz de Marca IA 🗣️

Generador de contenido de marketing con voz de marca consistente para pymes,
construido con Claude (Anthropic) y Streamlit.

> Proyecto hecho para un reto de bootcamp. El negocio de ejemplo, **Fonda
> Doña Pola**, es **ficticio** — no corresponde a ninguna empresa real.

## ¿Qué hace?

A partir de un **perfil de marca** (tono, valores, público, canales,
restricciones), la app:

1. Genera **ideas de contenido** con IA.
2. Redacta **copies adaptados a cada canal** (Instagram, WhatsApp, Blog) que
   mantienen la misma voz de marca aunque cambie el formato.
3. Arma un **calendario de publicación sostenible** (respeta la frecuencia
   deseada por canal, nunca agenda más de una pieza el mismo día) y lo exporta
   a un archivo `.ics` importable en Google Calendar, Outlook o Apple
   Calendar.
4. Guarda todo localmente por negocio, para poder retomar el trabajo en
   cualquier momento.

Además, la app muestra una **estimación de tiempo ahorrado** (comparando
tiempo manual vs. con IA, de forma transparente) y valida automáticamente
cada idea/copy contra el perfil de marca, mostrando una señal
✓ *consistente* / ⚠️ *revisar* en la UI.

Todo el contenido se genera en español, pensado para una pyme colombiana.

## Instalación

Requiere Python 3.11+.

```bash
git clone <este-repo>
cd bootcamp-voz-marca-ia

python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
```

### Configurar la API key de Claude

1. Copia `.env.example` a `.env`.
2. Reemplaza el valor de `ANTHROPIC_API_KEY` por tu propia API key de
   [Anthropic](https://console.anthropic.com/).
3. **Nunca** subas tu `.env` a un repositorio — ya está incluido en
   `.gitignore`.

```
ANTHROPIC_API_KEY=sk-ant-tu-key-aqui
```

Opcional: puedes cambiar el modelo usado con la variable `CLAUDE_MODEL`
(por defecto usa `claude-sonnet-5`).

## Uso

```bash
streamlit run app.py
```

Esto abre la app en tu navegador (por defecto `http://localhost:8501`).

Flujo recomendado:

1. **Pestaña "1. Perfil de marca"** — crea o edita el perfil de tu negocio:
   tono de voz, valores, público objetivo, diferenciadores, canales con su
   frecuencia deseada (veces por semana) y restricciones (qué nunca debe
   hacer el contenido).
2. **Pestaña "2. Ideas"** — genera un lote de ideas de contenido con IA,
   opcionalmente indicando una temporada o contexto (ej. "diciembre"). Cada
   idea se valida contra el perfil de marca y muestra un badge
   ✓/⚠️ de consistencia.
3. **Pestaña "3. Copies"** — elige una idea y uno o más canales, y genera el
   texto final adaptado a cada canal (también validado contra el perfil de
   marca). Desde cada copy puedes generar una **pieza gráfica** (imagen
   1080x1080 con el color y logo de marca) y descargarla como `.png`.
4. **Pestaña "4. Calendario"** — elige una fecha de inicio, genera el
   calendario y descarga el archivo `.ics` (también se guarda en
   `data/<tu-negocio>/calendario.ics`).

Puedes cerrar la app y volver después: todo tu trabajo por negocio queda
guardado en `data/<slug-del-negocio>/`.

## Estructura del proyecto

```
bootcamp-voz-marca-ia/
├── app.py                     # UI de Streamlit (punto de entrada)
├── src/
│   ├── brand_profile.py       # Modelo de perfil de marca
│   ├── ai_engine.py           # Llamadas a la API de Claude
│   ├── calendar_builder.py    # Algoritmo de calendario + export .ics
│   ├── graphic_generator.py   # Piezas gráficas por plantilla (Pillow)
│   ├── storage.py             # Persistencia en data/<negocio>/
│   └── prompts.py             # Construcción de prompts (system + por función/canal)
├── scripts/
│   └── generate_placeholder_logo.py  # Genera el logo placeholder de demo
├── data/
│   └── fonda-dona-pola/       # Ejemplo ficticio ya incluido (incluye logo.png)
├── docs/
│   ├── decisiones.md          # Log de decisiones de diseño
│   └── guion-demo.md          # Guión para el Demo Day
└── tests/
    ├── test_calendar_builder.py
    └── test_graphic_generator.py
```

## Tests

El algoritmo de calendario es determinista y no depende de la API, así que se
puede testear sin API key:

```bash
pytest tests/ -v
```

## Diseño y decisiones

Ver [`docs/decisiones.md`](docs/decisiones.md) para el detalle de cada
decisión de arquitectura y las alternativas descartadas.

## Limitaciones conocidas (alcance del MVP)

- No hay edición manual de una idea/copy individual desde la UI (solo
  regenerar el lote completo).
- No hay integración directa (OAuth) con Google Calendar — la exportación es
  vía archivo `.ics`.
- Un solo idioma (español) y un solo modelo de IA (Claude).
- Pensado para un negocio a la vez desde la sesión activa de Streamlit
  (aunque los datos de varios negocios pueden convivir en `data/`).
