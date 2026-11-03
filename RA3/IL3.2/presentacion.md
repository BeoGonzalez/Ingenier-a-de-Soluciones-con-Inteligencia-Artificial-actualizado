# Presentación IL3.2 - Análisis de Trazabilidad y Logs

## Slide 1: Título y Objetivos
**Título:** IL3.2 - Análisis de Trazabilidad y Logs  
**Subtítulo:** Seguimiento y Análisis del Comportamiento de Agentes

**Objetivos:**
- Abrir una petición en árbol (`trace_id` + etapas)
- Separar esa petición de la conversación (`thread_id`)
- Leer tasa de éxito y la etapa más lenta en `AnalizadorTrazas`
- Reconocer un ataque como un span que corta el árbol (puente a IL3.3)

---

## Slide 2: ¿Por qué Trazabilidad?
**Título:** Importancia del Seguimiento en Sistemas IA

**Desafíos sin trazabilidad:**
- Decisiones de agentes como "caja negra"
- Imposible reproducir errores o comportamientos
- Falta de accountability en decisiones automáticas
- Dificultad para cumplir regulaciones de auditoría

**Beneficios de la trazabilidad:**
- **Debugging eficiente:** Reproducir errores exactos
- **Auditoría completa:** Registro de todas las decisiones
- **Compliance:** Cumplir regulaciones de transparencia
- **Optimización:** Análisis de patrones de comportamiento

---

## Slide 3: Trazabilidad Básica - Implementación
**Título:** Script 1 - Trazas Estructuradas y Análisis

**Implementación** (`1-traceability_analysis.py`, simulación sin llamar al modelo):
```python
@dataclass
class Traza:
    trace_id: str          # uuid4 corto, identifica la peticion completa
    timestamp: str
    mensaje_entrada: str
    eventos: List[Evento]  # una etapa: nombre, inicio, duracion, estado

# El agente registra una etapa por paso del procesamiento
traza.agregar_evento("validacion_entrada", inicio, duracion, "ok", detalle)
traza.agregar_evento("clasificacion_intencion", inicio, duracion, "ok", detalle)
traza.agregar_evento("generacion_respuesta", inicio, duracion, "error", "Timeout")

print(traza.a_json())                       # traza completa en JSON
AnalizadorTrazas.resumir(historial_trazas)  # tasa de exito, etapa mas lenta
```

**Características clave:**
- **Trazabilidad:** un `trace_id` correlaciona todas las etapas de una petición
- **Estructura:** trazas serializables a JSON (no texto libre)
- **Análisis:** `AnalizadorTrazas` calcula tasa de éxito y promedio por etapa

---

## Slide 4: Tres identificadores
**Título:** Petición, conversación, etapa

| Nombre | Qué agrupa | De dónde sale |
|---|---|---|
| `trace_id` | Una petición, de la entrada a la salida | `uuid` corto en `1-traceability_analysis.py` |
| `thread_id` | La conversación, varias peticiones | Memoria de IL2.2 (`InMemorySaver`) |
| Etapa / span | Un paso dentro de la petición | `validacion_entrada`, `clasificacion_intencion`, `generacion_respuesta` |

En el grafo de RA2 la etapa es un nodo: `model`, `tools`, supervisor, especialista.
LangSmith dibuja ese árbol si hay key. Este script lo imprime en JSON para
leerlo sin cuenta.

---

## Slide 5: Qué calcula el analizador
**Título:** Tres preguntas, un método

`AnalizadorTrazas.resumir(historial)` responde:

1. **¿Cuántas peticiones terminaron bien?** Tasa de éxito.
2. **¿Cuánto duró cada etapa?** Promedio por nombre de span.
3. **¿Dónde se fue el tiempo?** La etapa más lenta.

Eso es el diagnóstico. El notebook agrega el árbol padre/hijo y marca
outliers de duración. El pytest `tests/ra3/test_observabilidad.py` fija
el caso sin azar: una traza con error conserva el `trace_id` en el JSON.

```bash
uv run python RA3/IL3.2/1-traceability_analysis.py
```

---

## Slide 6: El ataque es un span
**Título:** Puente directo a IL3.3

Una consulta sana:

```text
trace_id abc
├── validacion_entrada        ok
├── clasificacion_intencion   ok
└── generacion_respuesta      ok     ← aquí se gastan los tokens
```

"Ignora las instrucciones anteriores":

```text
trace_id def
└── validacion_entrada        error  ← se corta
    (no hay generacion_respuesta)
```

Un correo en el mensaje sigue el árbol sano, pero el texto guardado en el
log ya es `CORREO_ELECTRONICO_REDACTADO`. La traza de auditoría no es un
segundo sistema: es este JSON, con el dato personal fuera.

En Chile eso conversa con la Ley 19.628 y la Ley 21.719: el `thread_id`
guarda conversación, así que guarda datos personales. Por eso el hilo no
se loguea crudo.

---

## Slide 7: Cierre
**Título:** Qué tiene que poder señalar el estudiante

1. Una traza es un árbol, no un párrafo de log.
2. `trace_id` ≠ `thread_id`.
3. La etapa más lenta y la etapa en error son hallazgos distintos.
4. Mañana (IL3.3) el hallazgo de seguridad es: `validacion_entrada` en error
   y el modelo sin llamarse.
5. La red, el HTTPS y el secreto de la API son IL3.5. Todavía no.

OpenTelemetry es el nombre del estándar de estos spans. No se instala un
Jaeger ni un ELK en el taller: el árbol ya está en el script.