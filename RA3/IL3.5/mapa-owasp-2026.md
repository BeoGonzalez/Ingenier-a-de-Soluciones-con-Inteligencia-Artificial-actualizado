# Mapa OWASP 2026 → este repositorio

Dos listas, vigentes. Los códigos cambian entre ediciones: se cita el año.

- [OWASP GenAI LLM Top 10 2026](https://genai.owasp.org/resource/owasp-genai-llm-top-10-2026/) (publicada el 4 de agosto de 2026).
- [OWASP Top 10 for Agentic Applications 2026](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/) (ASI01–ASI10).

Los ejemplos se corren sin Groq y sin AWS:

```bash
uv run python RA3/IL3.5/3-ejemplos-owasp.py
uv run pytest tests/ra3/test_ejemplos_owasp.py -q
```

Tres estados, y solo esos:

| Estado | Qué significa en la defensa |
|---|---|
| **aplicado** | El control corre en el código y el script lo ejecuta. |
| **parcial** | Corre una parte. La frase de al lado dice el hueco. |
| **en la defensa** | Este artefacto no lo cierra. Se nombra; no se simula. |

## LLM01–LLM10

| Código | Riesgo | Estado | Dónde se aplica | Ejemplo listo |
|---|---|---|---|---|
| LLM01:2026 | Prompt Injection | parcial | `validar_entrada` y `validar_conversacion` en `deploy/backend/guardrails.py` | La frase «Ignora las instrucciones anteriores…» se bloquea. Partida en tres turnos, cada pieza pasa y la concatenación se bloquea. Una instrucción dentro de un documento o de una tool no se mira. |
| LLM02:2026 | Sensitive Information Disclosure | aplicado | `sanitizar_pii`; `app.py` loguea el motivo, no el mensaje | `ana@duoc.cl` y `12.345.678-9` salen como `CORREO_ELECTRONICO_REDACTADO` y `RUT_CHILE_REDACTADO`. |
| LLM03:2026 | Excessive Agency | en la defensa | `AgentClient` no registra tools | El chat no puede borrar, pagar ni enviar. En el grafo, el control es el permiso de cada `@tool` y una persona en la acción irreversible. |
| LLM04:2026 | Supply Chain | parcial | `uv.lock` | El lockfile existe y fija versiones de Python. No revisa el modelo de Groq ni un MCP. |
| LLM05:2026 | Data and Model Poisoning | en la defensa | `RA1/IL1.3` | El índice RAG no firma documentos. El deploy no tiene RAG. |
| LLM06:2026 | Unbounded Consumption | aplicado | tope de 2000 caracteres, presupuesto de 8000, `20/minute` en `app.py`, `LimitadorTasa` en IL3.3 | 2001 caracteres se rechazan. La segunda petición dentro de la ventana se niega. En 2025 este ítem era LLM10; en 2023 se citaba como «DoS». |
| LLM07:2026 | Misinformation | en la defensa | notebook `RA3/IL3.3/2-security-ethics-practice.ipynb` | Esa revisión llama al modelo y gasta cuota. El deploy no la trae. |
| LLM08:2026 | Hidden Context Exposure | parcial | `hay_fuga_de_instrucciones` contra `SYSTEM_PROMPT` | Repetir seis palabras seguidas del system prompt se detecta. Una respuesta de clase, no. Un resumen con otras palabras, tampoco. El prompt no lleva la API key. |
| LLM09:2026 | Vector and Embedding Weaknesses | en la defensa | embeddings de `RA1/IL1.3` | El vector no distingue una instrucción de un dato. Mismo hueco que LLM05. |
| LLM10:2026 | Improper Output Handling | aplicado | `html.escape` en `deploy/frontend/app_frontend.py`; AST en `evaluar_matematica_segura` | Una marca HTML del modelo se escapa. `(2 + 3) * 4` da `20`. Una llamada que no es aritmética vuelve `Error`. En 2025 este ítem era LLM05. |

`app.py` además no devuelve el traceback al cliente: el detalle queda en el log y la respuesta es «Ocurrió un error procesando tu solicitud.» Eso acompaña a LLM02 y a LLM10.

## ASI01–ASI10

La lista de agentes no reemplaza a la de LLMs. ASI01 conversa con LLM01; ASI02 y ASI03 con LLM03; ASI05 con LLM10.

| Código | Riesgo | Estado | Dónde se aplica | Qué se dice |
|---|---|---|---|---|
| ASI01:2026 | Agent Goal Hijack | parcial | el mismo filtro que LLM01 | En el chat, la frase directa no llega al modelo. En IL2.3, un handoff hacia otro especialista no pasa por ese filtro. |
| ASI02:2026 | Tool Misuse and Exploitation | en la defensa | IL2.2, permiso de cada tool | El deploy no tiene tools. Si se enchufa `create_agent`, cada una lleva el alcance justo. |
| ASI03:2026 | Identity and Privilege Abuse | aplicado | la key vive en el backend; en AWS, `LabRole` | El navegador no recibe `GROQ_API_KEY`. La imagen no lleva claves de AWS. |
| ASI04:2026 | Agentic Supply Chain | en la defensa | un servidor MCP de IL2.2 | `uv.lock` cubre librerías (LLM04). Un tool MCP entra en runtime y no se firma. |
| ASI05:2026 | Unexpected Code Execution | aplicado | lista blanca de nodos AST en IL3.3 | Misma evidencia que LLM10: aritmética sí, otra llamada no. |
| ASI06:2026 | Memory and Context Poisoning | parcial | `validar_conversacion`; `thread_id` de IL2.2 | Juntar los turnos cierra la frase partida. No revisa un hilo ya guardado en el checkpointer. |
| ASI07:2026 | Insecure Inter-Agent Communication | en la defensa | `Command` y `Send` en IL2.3 | Los nodos del taller confían en quien está dentro del mismo proceso. |
| ASI08:2026 | Cascading Failures | parcial | IL3.4, sección 5 (circuit breaker) | El notebook desconecta un servicio que falla seguido. El chat de deploy no trae ese corte. |
| ASI09:2026 | Human-Agent Trust Exploitation | parcial | IL3.3, sección 5 (human-in-the-loop) | El notebook deja la acción en una cola humana. El chat de deploy no tiene esa pausa. |
| ASI10:2026 | Rogue Agents | en la defensa | fuera del taller | Un agente que se desvía solo, sin un atacante en el turno, se nombra y no se simula. |

## Equivalencias que todavía circulan en apuntes viejos

| Se decía | Hoy (2026) |
|---|---|
| LLM01 Prompt Injection | LLM01:2026, mismo nombre |
| LLM02 Sensitive Information Disclosure (2025) | LLM02:2026, mismo nombre. En 2023 era LLM06 |
| LLM06 Excessive Agency (2025) | LLM03:2026 |
| LLM04 DoS (2023) y LLM10 Unbounded Consumption (2025) | LLM06:2026 |
| LLM05 Insecure Output Handling (2025) | LLM10:2026 |
| «System Prompt Leakage» | LLM08:2026 Hidden Context Exposure |
