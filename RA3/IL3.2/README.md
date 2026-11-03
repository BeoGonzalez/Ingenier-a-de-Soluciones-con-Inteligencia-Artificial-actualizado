# IL3.2: Análisis de Trazabilidad y Logs

Este módulo profundiza en cómo analizar y aprovechar los logs generados por los agentes para entender su comportamiento, depurar errores y realizar auditorías.

**Puente RA2:** cada etapa del script (`clasificacion_intencion`, `generacion_respuesta`)
es el análogo de un **nodo** LangGraph. El `trace_id` identifica *una* petición; el
`thread_id` identifica el hilo. LangSmith dibuja ese árbol si `LANGSMITH_TRACING=true`.

## Objetivos de Aprendizaje

- Implementar sistemas de trazabilidad en agentes de IA
- Analizar logs para identificar patrones de error
- Correlacionar eventos a través del flujo del agente
- Utilizar logs para auditoría y cumplimiento

## Archivos del Módulo

| Archivo | Descripción |
|---------|-------------|
| `1-traceability_analysis.py` | Script principal con ejemplos de guardado, lectura y análisis de logs de agentes |
| `2-traceability-practice.ipynb` | Notebook práctico para implementar trazabilidad y depuración |
| `presentacion.md` | Diapositivas de apoyo con conceptos teóricos |

## Requisitos Previos

| Archivo | ¿Necesita API key? | Notas |
|---|---|---|
| `1-traceability_analysis.py` | No | Es una **simulación pura**: no llama a ningún modelo. Se puede ejecutar sin cuota. |
| `2-traceability-practice.ipynb` | Sí (`GROQ_API_KEY`) | Hace **13 llamadas reales** a `openai/gpt-oss-20b`, más las del ejercicio final. |

- Dependencias: `uv sync` en la raíz del repo (usa `groq`, `pandas` y `matplotlib`).
- La credencial se carga igual en Colab (*Secrets*) que en local (archivo `.env`).
- Si aparece un error **`429`**, se alcanzó un límite de la capa gratuita: lee el mensaje
  para saber si es por minuto (espera) o por día (cambia de modelo o continúa mañana).
  Tabla de límites vigentes en [`RA1/IL1.1/README.md`](../../RA1/IL1.1/README.md).

## Conceptos Clave

- **Traza**: una petición. La identifica `trace_id`. Varias trazas del mismo
  hilo comparten el `thread_id` de IL2.2.
- **Span / etapa**: un nodo del recorrido (`validacion_entrada`,
  `clasificacion_intencion`, `generacion_respuesta`). En el grafo de RA2,
  el análogo es `model`, `tools` o un especialista.
- **Análisis**: `AnalizadorTrazas` responde tasa de éxito, duración por etapa
  y cuál fue la más lenta. El JSON conserva el `trace_id`.
- **Puente a IL3.3**: un ataque directo tiene que dejar `validacion_entrada`
  en error y no disparar `generacion_respuesta`. El log de esa traza no guarda
  el correo crudo.

El estándar de la industria para estos spans se llama OpenTelemetry. LangSmith
lo dibuja si hay key. Este módulo lo arma a mano para poder leer el árbol sin
cuenta.

## Cómo Empezar

```bash
# Ejecutar el script principal
uv run python RA3/IL3.2/1-traceability_analysis.py

# Abrir el notebook práctico
uv run jupyter lab RA3/IL3.2/2-traceability-practice.ipynb
```

## Recursos

- [Python Traceback Module](https://docs.python.org/3/library/traceback.html)
- [Structured Logging](https://docs.python.org/3/howto/logging-cookbook.html#implementing-structured-logging)
- [OpenTelemetry Traces](https://opentelemetry.io/docs/concepts/signals/traces/)
