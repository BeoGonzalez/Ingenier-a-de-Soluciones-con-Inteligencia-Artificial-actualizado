# Antes de la clase — checklist del docente

Documento interno. Reúne lo que conviene comprobar y anticipar antes de cada sesión, con los
riesgos reales detectados al probar el material. Los alumnos tienen su propia
[Guía del Estudiante](GUIA_DEL_ESTUDIANTE.md).

---

## 1. El día antes

```bash
git pull
uv sync
uv run python scripts/verify_groq.py
```

Si eso termina en verde, el entorno está listo. `verify_groq.py` comprueba la API key, el SDK
de Groq, `ChatGroq` y los embeddings locales.

**Revisa tu cuota antes de empezar.** Cada gpt-oss tiene **200.000 tokens al día** y
es el límite que se agota primero. Si estuviste preparando la clase ejecutando notebooks, es
muy posible que ya la hayas consumido. Compruébalo en
[console.groq.com](https://console.groq.com/) → Usage.

---

## 2. Lo que hay que pedir a los alumnos con antelación

| Qué | Por qué |
|---|---|
| Crear su **propia** API key en console.groq.com | Los límites son por cuenta. Si comparten, se quedan todos sin cuota. |
| Ejecutar `verify_groq.py` **en casa** | Descarga ~470 MB del modelo de embeddings. Con 30 personas a la vez sobre el wifi de la sala, es el cuello de botella más probable de todo el curso. |
| Tener el `.env` creado y funcionando | Es el fallo nº 1 en la primera sesión. |

Esto aplica sobre todo antes de **RA1/IL1.3** (RAG), que es donde entran los embeddings.

---

## 3. Riesgos por módulo

### RA1/IL1.3 e IL1.4 — RAG
- La **descarga de 470 MB** ocurre aquí si no la hicieron antes.
- La app Streamlit de IL1.4 (`1-evaluation-rag.py`) gasta bastante cuota en la pestaña de
  evaluación completa (≈5 llamadas por caso × 3 casos). Si la vas a demostrar, ponte antes
  `GROQ_MODEL=openai/gpt-oss-20b`.

### RA1/IL1.2 — Prompt engineering
- `4-advanced-techniques.ipynb` es de los que más queman cuota (self-consistency y
  árbol de pensamientos hacen muchas llamadas).

### RA2/IL2.1 e IL2.2 — Agentes
- El camino actual es **LangGraph** (`3-langgraph-agent.ipynb`, memoria con `thread_id`).
  `3-langchain-agent.ipynb` es contraste clásico (`AgentExecutor`): no lo saltes, es para
  criterio. Cierra la sesión con `5-criterio-frameworks.md`.
- Los notebooks con herramientas usan **modelos distintos a propósito**, y está medido:
  por SDK crudo el 8B es más fiable que el 70B, por LangChain es al revés, y en cadenas
  multi-paso ninguno de los dos, por eso se usa `openai/gpt-oss-20b`. Si un alumno pregunta
  por qué no es todo el mismo modelo, la respuesta está en el README de IL2.1.
- El error `400 tool_use_failed` puede salir en vivo. **No es un fallo del código**: es el
  modelo generando mal la llamada. Los agentes del curso lo reintentan.
- En Colab, instalar CrewAI tarda varios minutos. No lo dejes para el momento.

### RA2/IL2.3 — Planificación
- ⚠️ **`Swarm_101.ipynb` es el archivo más frágil del curso.** Está ejecutado y funciona,
  pero depende de una librería que OpenAI archivó y que se instala desde git, así que puede
  romperse sin aviso. Adaptarla a Groq costó tres parches y un cambio de modelo, todo
  explicado dentro: ese recorrido es su mejor material de clase. Si lo llevas en vivo,
  ejecútalo antes; si falla, no bloquea el resto de IL2.3.
- Empieza por `3-langgraph-planning.py`, `3-langgraph-orquestacion.py` y
  `4-langgraph-multiagente.ipynb` (supervisor, handoff, `Send`). Cierra con
  `4-tendencias-multiagente.md`. Los `1-basic_planning.py` son el contraste clásico.
-   De los 24 archivos del módulo, **13 no necesitan API key**: son simulaciones puras.
  La tabla está en el README del módulo.

### RA2/IL2.4 — Documentación y arquitectura
- No gasta Groq. Empieza por `0-arquitectura-ra2.md` (plantilla del entregable)
  y corre los dos `.py`. El orquestador del script 1 es un supervisor **sin LLM**:
  es el mismo patrón que IL2.3, para que documenten el grafo que ya corrieron.
- El ADR debe elegir LangGraph (`create_agent` / `StateGraph`) o justificar CrewAI.
  `AgentExecutor` y Swarm no van como arquitectura nueva.

### RA3 — Observabilidad y ciberseguridad (relato)
- El mapa de la unidad está en `RA3/0-puente-ra2.md`. Carpetas iguales;
  el relato son dos tableros (calidad de la llamada vs. abusos en `/metrics`)
  y dos capas (qué puede hacer el agente vs. quién llega a la API).
- Lo que se observa es el **grafo** de RA2 (nodos, tools, `thread_id`).
  LangSmith entra en IL1.4 y se retoma aquí, y es opcional.
- El notebook de IL3.1 usa SDK crudo (13+ llamadas). Cierra con
  `3-observar-grafo.py` (1–2 llamadas) si queda cuota.
- En IL3.5 la demo de casa es un solo ataque: inyección → `bloqueado`,
  correo → texto redactado, `/metrics` con `bloqueados` más alto. Después
  di en voz alta lo que el filtro sigue sin ver: inyección indirecta, hex
  y una paráfrasis que no esté escrita.
- Para mostrarlo **sin cuota**: `uv run python RA3/IL3.1/1-observability_tools.py`
  y `uv run pytest tests/ra3/test_observabilidad.py -q`. El recorrido completo
  está en [RA3/README.md](RA3/README.md#demostrarlo-en-casa).

### RA3/IL3.3 — Seguridad y ética
- Es el notebook que **más cuota consume** de todo RA3 (más de 30 llamadas al modelo grande).
  Si ya usaste la key ese día, hay riesgo real de `429` en clase. Ten preparado
  `GROQ_MODEL=openai/gpt-oss-20b`.

### RA3/IL3.5 — Despliegue en AWS
- El paso a paso está revisado comando a comando, pero **no se ha probado en una EC2 real**.
- El navegador **siempre** mostrará aviso de certificado no confiable al abrir `https://<IP>`:
  Caddy emite uno self-signed. Anticípalo antes de proyectar.
- Si el chat responde `[modo demo]`, es que el backend arrancó sin `GROQ_API_KEY`.

---

## 4. Errores que van a aparecer en vivo

Todos están explicados con su solución en la
[Guía del Estudiante](GUIA_DEL_ESTUDIANTE.md#6-errores-frecuentes). Los tres más probables:

| Error | Qué decir |
|---|---|
| `429 tokens per day` | Se acabó la cuota diaria de ese modelo. Cambiar a `openai/gpt-oss-20b`, que tiene 5× más. |
| `400 tool_use_failed` | El modelo generó mal la llamada a la herramienta. No es su código. Reintentar. |
| `401` de LangSmith | LangSmith es opcional. Dejar `LANGSMITH_TRACING="false"`. |

---

## 5. Estado de verificación del material

Última pasada local de observabilidad y ciberseguridad: **27 de octubre de 2026**
(`uv run pytest tests/ -q` y `uv run python scripts/validate_repo.py`).
Cómo repetirla en casa: [RA3/README.md](RA3/README.md#demostrarlo-en-casa).

| Qué | Estado |
|---|---|
| Instalación desde cero (`git clone` + `uv sync` + verificación) | ✅ Probado en agosto 2026, ~3 min. No se repitió el 27 oct. |
| Tests (despliegue + observabilidad IL3.1/IL3.2 + calculadora y rate limit de IL3.3) | ✅ 83 pasando, sin `xfailed` (3 nov 2026) |
| `scripts/validate_repo.py` | ✅ El 27 oct. Antes fallaba por salidas guardadas |
| Scripts `.py` | ✅ Todos compilan; los de simulación de RA3, ejecutables sin key |
| Notebooks contra Groq | ✅ Corrida de agosto 2026. El 27 oct **no** se reejecutaron (cuota) |
| Salidas de notebook con `429`, key inválida o id de organización | ✅ Limpiadas el 27 oct en IL1.4 (LangSmith) e IL3.4 (el fallback sigue, sin el JSON de Groq) |
| CI (GitHub Actions) | ✅ Verde en la pasada de agosto: tests, Docker, Trivy. Esta pasada no relanzó la CI |
| Despliegue en EC2 real | ❌ No probado. En casa se muestra la API local |
| Windows y Linux | ❌ No probado (esta pasada, en macOS) |

---

## 5.b Plan B verificado: Mistral

Si Groq falla o agotas la cuota **en mitad de la clase**, tienes salida. Está probado, no
es teoría: levantamos el artefacto de `deploy/` apuntado a Mistral y respondió, con los
guardrails funcionando igual.

| | Groq gpt-oss-120b | Groq gpt-oss-20b | Mistral small |
|---|---|---|---|
| Peticiones/min | 30 | 30 | **50** |
| Tokens/min | 8.000 | 8.000 | **50.000** |
| Tokens/día | 200.000 | 200.000 | **sin tope declarado** |
| Embeddings | no | no | **sí** |

- **En notebooks:** una línea, documentada en GUIA_DEL_ESTUDIANTE.md apartado 4.b.
- **En el servicio desplegado:** dos variables de entorno (`LLM_BASE_URL`, `LLM_API_KEY`),
  sin tocar código.

Ten una key de Mistral creada **antes** de la clase, aunque no pienses usarla. Sacarla en
caliente con 30 alumnos esperando no es plan.

> Lo que no verificamos: el tope mensual de Mistral. Terceros hablan de unos 1.000 millones
> de tokens/mes, pero no lo comprobamos.

---

## 6. Si algo se rompe en clase

1. `uv run python scripts/verify_groq.py` te dice en 10 segundos si el problema es la key,
   la red o el entorno.
2. Si es cuota, cambia `GROQ_MODEL` a `openai/gpt-oss-20b` en tu `.env` y reinicia el kernel.
3. Los módulos de RA2/IL2.3 y RA3 tienen scripts `.py` que **no necesitan API key**: son un
   buen plan B para seguir la clase sin conexión al modelo.
