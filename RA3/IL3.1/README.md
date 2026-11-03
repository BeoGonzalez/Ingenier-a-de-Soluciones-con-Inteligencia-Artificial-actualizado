# IL3.1: Herramientas de Observabilidad y Métricas

En este módulo aprenderás a agregar logs, métricas y monitoreo a tus agentes de IA para comprender su funcionamiento, diagnosticar problemas y medir desempeño en producción.

**Puente desde RA2:** lo que observas es un **grafo** (`create_agent` / `StateGraph`), no un `AgentExecutor`. El `thread_id` de IL2.2 es el identificador de la conversación y de la traza. LangSmith (IL1.4) se retoma aquí sobre ese mismo grafo. El ADR de qué runtime elegiste está en `RA2/IL2.4/0-arquitectura-ra2.md`.

## Objetivos de Aprendizaje

- Implementar logging estructurado en agentes de IA
- Medir tiempos de respuesta y latencia de llamadas a modelos
- Registrar eventos clave (errores, decisiones, llamadas a herramientas)
- Visualizar métricas básicas de rendimiento

## Archivos del Módulo

| Archivo | Descripción |
|---------|-------------|
| `1-observability_tools.py` | Script principal con ejemplos de logging, medición de tiempo y registro de eventos en un agente |
| `2-observability-practice.ipynb` | Notebook práctico para implementar observabilidad en un agente conversacional (SDK crudo: ves tokens de UNA llamada) |
| `3-observar-grafo.py` | Opcional (1–2 llamadas Groq): las mismas métricas sobre `create_agent` + `thread_id` |
| `presentacion.md` | Diapositivas de apoyo con conceptos teóricos |

## Requisitos Previos

| Archivo | ¿Necesita API key? | Notas |
|---|---|---|
| `1-observability_tools.py` | No | Es una **simulación pura**: no llama a ningún modelo. Se puede ejecutar sin cuota. |
| `2-observability-practice.ipynb` | Sí (`GROQ_API_KEY`) | Hace **13 llamadas reales** a `openai/gpt-oss-20b`, más las del ejercicio final. |
| `3-observar-grafo.py` | Sí (`GROQ_API_KEY`) | **1–2 llamadas** a `GROQ_MODEL_FAST`. Opcional; cierra el puente con RA2. |

- Dependencias: `uv sync` en la raíz del repo (usa `groq`, `pandas` y `matplotlib`).
- La credencial se carga igual en Colab (*Secrets*) que en local (archivo `.env`).
- Si aparece un error **`429`**, se alcanzó un límite de la capa gratuita: lee el mensaje
  para saber si es por minuto (espera) o por día (cambia de modelo o continúa mañana).
  Tabla de límites vigentes en [`RA1/IL1.1/README.md`](../../RA1/IL1.1/README.md).

## Conceptos Clave

Tres señales, en este orden. El relato completo de la unidad está en
[`../0-puente-ra2.md`](../0-puente-ra2.md).

- **Log**: una línea con hora. En el script: `Entrada`, `Salida`, `Error simulado`.
- **Métrica de la llamada**: el JSON de `RecolectorMetricas.resumen()` — latencia
  (promedio, máximo, mínimo), tokens y tasa de error. El notebook arma el mismo
  tablero con matplotlib. `/metrics` de la API es **otro** tablero
  (`total_requests`, `bloqueados`, `errores`) y se usa en IL3.5.
- **Traza**: una petición abierta en etapas. Se anuncia aquí y se construye en IL3.2.
- **LangSmith**: la misma traza del grafo, en la nube, si hay key. Opcional.
  Langfuse y Arize son de la misma familia; este módulo no los instala.

## Cómo Empezar

```bash
# Ejecutar el script principal (no gasta cuota)
uv run python RA3/IL3.1/1-observability_tools.py

# La misma aritmética de métricas, fija, sin el azar del demo
uv run pytest tests/ra3/test_observabilidad.py -q

# Abrir el notebook práctico
uv run jupyter lab RA3/IL3.1/2-observability-practice.ipynb

# Opcional: observar el grafo de RA2 (create_agent + thread_id)
uv run python RA3/IL3.1/3-observar-grafo.py
```

## Recursos

- [OpenTelemetry Python](https://opentelemetry.io/docs/instrumentation/python/)
- [LangSmith Tracing](https://docs.smith.langchain.com/tracing)
- [Python Logging Cookbook](https://docs.python.org/3/howto/logging-cookbook.html)
