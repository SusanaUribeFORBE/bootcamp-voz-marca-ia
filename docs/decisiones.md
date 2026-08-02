# Log de decisiones

Registro cronológico de decisiones de diseño, tomadas a medida que avanza el
proyecto (no reconstruido al final). Cada entrada indica qué se decidió, por
qué, y qué alternativas se descartaron.

## 1. Interfaz: Streamlit en vez de CLI o app completa (frontend+backend separado)

**Decisión:** app web liviana con Streamlit, un solo `app.py`.

**Por qué:** el usuario final es el dueño de una pyme, no un desarrollador —
una CLI es una barrera de entrada innecesaria. Streamlit permite un formulario
+ resultados visuales (tabla de calendario, botón de descarga) con muy poco
código, ideal para un MVP defendible en un Demo Day.

**Descartado:**
- **CLI pura**: más rápida de construir, pero no es "usable por una pyme desde
  el día 1" (requisito explícito del reto).
- **Frontend + backend separados (ej. React + FastAPI)**: sobre-ingeniería
  para el alcance de un MVP de bootcamp; añade complejidad de despliegue sin
  aportar valor adicional al caso de uso.

## 2. Motor de IA: Claude API directa, sin capa de abstracción multi-proveedor

**Decisión:** usar el SDK oficial `anthropic` directamente en `ai_engine.py`,
sin una capa de abstracción para soportar múltiples proveedores de LLM.

**Por qué:** el alcance del reto no pide portabilidad entre proveedores, y una
capa de abstracción prematura añadiría indirección sin beneficio real. Si en
el futuro se necesita soportar otro proveedor, `ai_engine.py` es el único
punto de contacto con la API — refactorizar ahí es sencillo.

**Descartado:**
- **Fallback "modo mock" sin API key**: se consideró pero no se incluyó en el
  alcance cerrado con el usuario; se prefirió que la app sea explícita sobre
  la falta de configuración en vez de simular contenido falso.

## 3. Voz de marca consistente: perfil → un solo system prompt reutilizado

**Decisión:** `BrandProfile` se serializa a un único `system prompt` (función
`build_system_prompt` en `prompts.py`) que se inyecta igual en *toda* llamada
a Claude (generación de ideas y de cada copy, sin importar el canal).

**Por qué:** es el mecanismo central para que la voz de marca no varíe entre
una idea y otra, o entre canales — el "adaptar el canal" ocurre solo en las
instrucciones de formato del *user prompt* (`build_copy_prompt`), nunca en el
tono o los valores de fondo, que vienen siempre del mismo system prompt.

**Descartado:**
- **Un prompt distinto por canal con el tono re-explicado cada vez**: genera
  riesgo de que el tono se redacte de forma ligeramente distinta en cada
  plantilla y diverja con el tiempo.

## 4. Persistencia: archivos JSON locales por negocio, sin base de datos

**Decisión:** cada negocio vive en `data/<slug-negocio>/{perfil,ideas,copies}.json`
+ `calendario.ics`.

**Por qué:** el alcance es un MVP de bootcamp para una sola pyme a la vez; una
base de datos añadiría infraestructura (migraciones, conexión, backups) sin
necesidad real. JSON es legible, versionable y fácil de inspeccionar durante
la demo.

**Descartado:**
- **SQLite**: más robusto para datos relacionales, pero innecesario para el
  volumen y la forma de los datos (perfiles, listas de ideas/copies) de este
  MVP.

## 5. Calendario: algoritmo determinista, no delegado a la IA

**Decisión:** `calendar_builder.build_calendar` asigna fechas con un algoritmo
propio (intervalo = `7 / frecuencia_semana` por canal, sin repetir fecha entre
canales), sin llamar a Claude.

**Por qué:** la fecha de publicación es una restricción de negocio dura
(sostenibilidad para una sola persona, "máximo 1 pieza por día") — dejar que
un LLM decida fechas introduce no-determinismo y complejidad de testeo
innecesaria. Un algoritmo simple es testeable con `pytest` sin depender de la
API (ver `tests/test_calendar_builder.py`), y es trivial de razonar y ajustar.

**Descartado:**
- **Pedirle a Claude que arme el calendario completo**: se descartó porque
  haría el resultado no determinista y mucho más difícil de testear y de
  explicar en la demo.

## 6. Exportación de calendario: `.ics` en vez de integración directa con Google Calendar API

**Decisión:** exportar un archivo `.ics` estándar (vía `icalendar`), importable
manualmente en Google Calendar, Outlook o Apple Calendar.

**Por qué:** una integración OAuth con la Google Calendar API añade un flujo
de autenticación completo (credenciales, consentimiento, tokens) que está
fuera del alcance de un MVP de bootcamp, y el usuario ya cerró esta opción
("exportable a Google Calendar / archivo .ics") como suficiente.

**Descartado:**
- **Integración directa vía Google Calendar API (OAuth)**: mucho mayor
  complejidad de configuración para el usuario final, sin beneficio
  proporcional en el alcance del MVP.

## 7. Caso de ejemplo: negocio ficticio "Fonda Doña Pola"

**Decisión:** todo el contenido de demo usa un restaurante ficticio de comida
antioqueña en Laureles, Medellín, explícitamente marcado como ficticio en el
README.

**Por qué:** el reto pide un ejemplo realista pero genérico, sin usar datos de
una empresa real — esto evita cualquier problema de confidencialidad y permite
compartir el repo libremente (incluyendo en el Demo Day) sin exponer datos de
terceros.

## 8. Refactor de `calendar_builder`: separar construcción de `.ics` en memoria vs. en disco

**Decisión:** se extrajo `_build_ical()` (interno) y se expuso `to_ics_bytes()`
como función pública; `export_ics(calendario, path)` ahora es un envoltorio
delgado sobre `to_ics_bytes()`.

**Por qué:** `st.download_button` de Streamlit necesita los bytes del archivo
directamente (sin pasar por disco), pero el plan también pide guardar una
copia en `data/<slug>/calendario.ics`. Separar la construcción del objeto
`Calendar` de su serialización a bytes permite reusar la misma lógica para
ambos casos sin duplicar código ni escribir a disco solo para leer de vuelta.

## 9. Métrica de tiempo ahorrado: aproximación simple y transparente, mostrada en la UI

**Decisión:** `src/impact_metrics.py` calcula minutos ahorrados comparando
supuestos fijos de "tiempo a mano" vs. "tiempo con IA" por idea/copy/
calendario, y el resultado se muestra directamente en `app.py` (no solo en
docs), junto con un expander que expone la tabla de supuestos usada.

**Por qué:** el valor de la herramienta debe ser explícito, no algo que el
usuario tenga que inferir. Pero un cálculo de impacto puede sentirse
inflado o poco creíble si es una caja negra — por eso se optó por supuestos
simples, declarados abiertamente en la misma UI, en vez de un modelo de
"tiempo ahorrado" más sofisticado (que sería más difícil de auditar y de
defender en una demo).

**Descartado:**
- **Un modelo de impacto más sofisticado (ej. ponderado por tipo de
  negocio o histórico real de uso)**: fuera del alcance de un MVP, y menos
  transparente/auditable que una tabla fija de minutos.

## 10. Validador de consistencia de voz de marca: llamada a Claude, no heurística de palabras clave

**Decisión:** `validate_ideas`/`validate_copy` en `ai_engine.py` hacen una
llamada adicional a Claude (reutilizando el mismo `system prompt` de
`build_system_prompt`) para evaluar cada pieza contra el perfil de marca,
en vez de una heurística de palabras clave. Las ideas del lote se validan
en **una sola llamada** (evita multiplicar llamadas por `cantidad`); los
copies se validan **individualmente**, uno por uno, porque se generan y
muestran de forma independiente en la UI.

**Por qué:** las `restricciones` del perfil son semánticas (ej. "no
promesas de salud", "sin urgencia falsa") — una frase puede violarlas sin
contener ninguna palabra prohibida literal (ver el caso real detectado en
`fonda-dona-pola`: "las mesas grandes vuelan" fue marcado inconsistente por
generar urgencia falsa, sin usar ninguna palabra "prohibida" obvia). Una
heurística de keywords no habría detectado eso. Ambas funciones están
envueltas en `try/except` para que un fallo de validación (red, API) nunca
rompa el flujo principal de generación — en ese caso se marca
`consistente=None` y la UI no muestra ningún badge.

**Descartado:**
- **Heurística de palabras clave/regex contra las restricciones**: más
  rápida y sin costo de API, pero poco confiable para restricciones
  semánticas — se habría descartado en la práctica al validar contra los
  datos reales de la demo.
- **Validar cada idea del lote con una llamada separada**: más simple de
  implementar, pero multiplica el costo/latencia de API sin necesidad — la
  validación en lote logra lo mismo en una sola llamada.

## 11. Piezas gráficas: plantilla con Pillow, no generación de imágenes con IA

**Decisión:** `src/graphic_generator.py` compone una imagen 1080x1080 por
plantilla fija (fondo = `color_marca`, logo opcional en la esquina inferior
derecha, título centrado) usando Pillow, sin llamar a ningún modelo de
generación de imágenes. La fuente de texto usa `ImageFont.load_default(size=64)`
— la fuente vectorial que trae Pillow desde la versión 10.1 — en vez de
bundlear un `.ttf` propio o depender de fuentes instaladas en el sistema
operativo.

**Por qué:** el alcance pedido es explícitamente "plantillas, no generación de
imágenes con IA" — evita costo y latencia de API adicional, y el resultado es
100% determinista (mismo perfil + mismo título → misma imagen), lo cual es
más fácil de testear (`tests/test_graphic_generator.py`) y de defender en la
demo. Sobre la fuente: depender de rutas de fuentes del sistema operativo
(ej. `C:\Windows\Fonts\arial.ttf`) es frágil y no portable entre Windows/
macOS/Linux; bundlear un `.ttf` de terceros añade una dependencia de licencia
innecesaria. La fuente por defecto de Pillow evita ambos problemas sin
sacrificar legibilidad (el color de texto se elige automáticamente por
contraste según la luminancia del color de fondo). La ausencia de logo (o un
`logo_path` inválido/corrupto) nunca rompe la generación: se captura con
`try/except` y la pieza se genera igual, sin logo.

**Descartado:**
- **Generación de imágenes con un modelo de IA**: fuera del alcance pedido
  explícitamente por el usuario, y añadiría costo, latencia y
  no-determinismo sin necesidad para una pieza de plantilla simple.
- **Bundlear una fuente `.ttf` propia**: se descartó por la carga de gestión
  de licencia que implica distribuir una fuente de terceros en el repo,
  cuando la fuente por defecto de Pillow ya es suficiente para el alcance.
