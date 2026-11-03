# Presentación IL3.1 - Herramientas de Observabilidad y Métricas

Guion de clase. El detalle del orden de toda RA3 está en `RA3/0-puente-ra2.md`.

## Slide 1: Título y Objetivos
**Título:** IL3.1 - Herramientas de Observabilidad y Métricas
**Subtítulo:** Ver la llamada antes de defenderla

**Objetivos:**
- Registrar cada interacción con hora y nivel (log)
- Medir latencia, tokens y tasa de error de esa llamada
- Dejar nombrado el `trace_id` que IL3.2 va a abrir en árbol
- Distinguir este tablero del de `/metrics` (abusos), que se usa en IL3.5

---

## Slide 2: Por qué se observa
**Título:** Sin números, el agente es una caja

**Lo que pasa si no mides:**
- Un `429` y un timeout se ven igual: "no respondió"
- La factura de tokens aparece cuando ya se acabó el día (200.000 en Groq free)
- Un bloqueo de seguridad y un fallo del modelo se confunden

**Lo que esta sesión deja en la mano:**
- Un log por entrada y por salida
- Un JSON con promedio, máximo, mínimo, tokens y `%` de error
- La frase que cierra la clase: *esto mide la llamada; el ataque se cuenta en otro tablero*

---

## Slide 3: El script que se ejecuta
**Título:** `1-observability_tools.py` — simulación, cero cuota

```python
class AgenteObservable:
    def procesar(self, mensaje: str) -> str:
        self.logger.info(f"Entrada: {mensaje!r}")
        inicio = time.perf_counter()
        ...
        duracion_ms = (time.perf_counter() - inicio) * 1000
        self.metricas.registrar(duracion_ms, tokens_in, tokens_out, exitoso=True)
        self.logger.info(f"Salida ({duracion_ms:.1f}ms, {tokens_in}+{tokens_out} tokens)")
        return respuesta
```

**Qué decir mientras corre:**
- El `sleep` y el 15 % de error son teatro. El contrato (latencia, tokens, éxito) es el de verdad.
- `RecolectorMetricas.resumen()` es el tablero de **calidad de la llamada**.
- La misma aritmética, sin azar, la fija `tests/ra3/test_observabilidad.py`.

```bash
uv run python RA3/IL3.1/1-observability_tools.py
uv run pytest tests/ra3/test_observabilidad.py -q
```

---

## Slide 4: Tres señales
**Título:** Log, métrica, traza — y en qué archivo vive cada una

| Señal | Pregunta que responde | En este curso |
|---|---|---|
| **Log** | ¿Qué pasó, a qué hora? | Líneas `Entrada` / `Salida` / `Error simulado` del script |
| **Métrica** | ¿Cómo viene el conjunto? | `resumen()`: promedio, máximo, mínimo, tokens, tasa de error |
| **Traza** | ¿Por qué etapas pasó *esta* petición? | IL3.2. Aquí solo se anuncia |

El notebook `2-observability-practice.ipynb` mide **una** llamada del SDK crudo
(13 llamadas reales a `openai/gpt-oss-20b`). El grafo de RA2 tiene varios nodos;
por eso el cierre opcional es `3-observar-grafo.py` (`create_agent` + `thread_id`,
1–2 llamadas).

---

## Slide 5: Dos tableros, no uno
**Título:** Calidad de la llamada y abusos del sistema

**Tablero A — esta sesión** (`RecolectorMetricas`):
- `tiempo_promedio_ms`, `tiempo_maximo_ms`, `tiempo_minimo_ms`
- `total_tokens`
- `tasa_errores_pct`
- `total_peticiones`

**Tablero B — la API, se muestra en IL3.5** (`GET /metrics`):
- `total_requests`
- `bloqueados`
- `errores`

El tablero B no trae latencia ni tokens. Sirve para señalar en vivo que una
inyección subió `bloqueados`. Decirlo ahora evita que en IL3.5 parezca que
"faltan métricas".

---

## Slide 6: LangSmith, y lo que no se instala
**Título:** La misma traza, en la nube, si hay key

LangSmith (ya visto en IL1.4) dibuja nodos, tools y `thread_id` del grafo
cuando `LANGSMITH_TRACING="true"` y hay `LANGSMITH_API_KEY`.

Sin key, el tracing se deja en `"false"`. Un `401` no es un fallo del agente.

El programa nombra también Langfuse y Arize. Son de la misma familia
(traza de una app con LLM). Este curso no los instala: la práctica se hace
con el log, el JSON y, si hay cuenta, LangSmith sobre LangGraph.

OpenTelemetry es el nombre del estándar de spans. Jaeger, Prometheus y
Grafana leen ese estándar en un equipo de plataforma. No entran en el taller.

---

## Slide 7: Cierre de la sesión
**Título:** Qué tiene que poder decir un estudiante al salir

1. Un log dice el evento; una métrica resume muchos eventos; una traza abre una petición.
2. El JSON de IL3.1 responde si la llamada está sana.
3. `/metrics` va a responder si alguien fue bloqueado. Todavía no se abre.
4. `trace_id` será una petición; `thread_id` (IL2.2) será la conversación. Eso es IL3.2.

**Si queda cuota:** `uv run python RA3/IL3.1/3-observar-grafo.py`.
**Si no queda:** el script y el pytest alcanzan. El notebook puede esperar.

---

## Slide 8: Hacia IL3.2
**Título:** El siguiente corte es el árbol

Hoy la llamada es un número (ms, tokens, éxito o error).
Mañana esa misma llamada se parte en etapas:

```text
trace_id
├── validacion_entrada
├── clasificacion_intencion
└── generacion_respuesta
```

Cuando alguien escriba "ignora las instrucciones anteriores", la primera etapa
tiene que quedar en error y la tercera no debe correr. Eso ya es IL3.3.
La red (HTTPS, secretos, Security Group) es IL3.5.
