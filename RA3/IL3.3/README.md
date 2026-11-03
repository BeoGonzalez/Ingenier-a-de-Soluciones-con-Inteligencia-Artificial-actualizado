# IL3.3: Seguridad y Ética en Agentes de IA

Este módulo cubre las mejores prácticas para proteger tus agentes de IA contra usos malintencionados y garantizar un comportamiento ético y responsable.

**Puente desde la observabilidad:** IL3.1 midió la llamada e IL3.2 la partió en
etapas. Aquí un ataque tiene que **verse** en esa traza: `validacion_entrada`
en error, el modelo sin llamarse, y el correo reemplazado por
`CORREO_ELECTRONICO_REDACTADO`. El contador `bloqueados` de `/metrics` es el
tablero de abusos; la latencia sigue siendo el otro.

**Puente RA2:** el riesgo no es solo el prompt. Un grafo tiene **tools**, **handoff**
(`Command`) y **memoria** (`thread_id`). Injection indirecta entra por Wikipedia/MCP;
un supervisor confundido enruta al especialista equivocado; un hilo envenenado
condiciona la siguiente consulta. El mínimo privilegio de las tools (IL2.2) pesa más
que un filtro de regex.

**Dos capas, para no mezclarlas en la defensa:** esta sesión es la seguridad
**del agente** (qué puede hacer con el texto, las tools y la memoria) y la
ética (sesgo, transparencia). La ciberseguridad **del sistema** (secretos,
HTTPS, quién llega al puerto) es IL3.5.

## Objetivos de Aprendizaje

- Validar entradas de usuario para prevenir injection de prompts
- Implementar guardrails y restricciones de seguridad
- Diseñar respuestas responsables y libres de sesgos
- Evaluar implicaciones éticas del despliegue de agentes

## Archivos del Módulo

| Archivo | Descripción |
|---------|-------------|
| `1-security_ethics.py` | Script principal con ejemplos de validación de entradas, sanitización y respuestas responsables |
| `2-security-ethics-practice.ipynb` | Notebook práctico para implementar seguridad y ética en un agente |
| `presentacion.md` | Diapositivas de apoyo con conceptos teóricos |

## Requisitos Previos

| Archivo | ¿Necesita API key? | Notas |
|---|---|---|
| `1-security_ethics.py` | No | Es una **simulación pura**: no llama a ningún modelo. Se puede ejecutar sin cuota. |
| `2-security-ethics-practice.ipynb` | Sí (`GROQ_API_KEY`) | Hace más de **30 llamadas reales** a `openai/gpt-oss-120b` (el modelo se usa además como clasificador de seguridad, verificador de alucinaciones y evaluador de confianza). |

- Dependencias: `uv sync` en la raíz del repo (usa `groq`).
- La credencial se carga igual en Colab (*Secrets*) que en local (archivo `.env`).
- ⚠️ Este es el notebook más caro de RA3 en cuota: gpt-oss tiene
  **200.000 tokens al día** en la capa gratuita. Si aparece un error **`429`**, lee el
  mensaje: si dice `tokens per minute` basta esperar; si dice `tokens per day` hay que
  continuar al día siguiente o cambiar `GROQ_MODEL` a `openai/gpt-oss-20b`.
  Tabla de límites vigentes en [`RA1/IL1.1/README.md`](../../RA1/IL1.1/README.md).

## Gestión de la API key: el caso real de este repositorio

La primera credencial que hay que proteger es la propia. Dos reglas que **este repositorio
aprendió a la mala** (hubo que revocar la clave y limpiar el historial dos veces):

1. **Al ejecutar un notebook, las salidas se guardan dentro del `.ipynb`** y ese archivo se
   versiona en git. Todo lo que se imprima queda publicado en el repositorio, aunque la
   celda ya no se vuelva a ejecutar.
2. **Nunca imprimas la key, ni siquiera parcialmente.** El patrón "muestro solo el principio
   y el final para verificar que cargó" publica parte del secreto y reduce el trabajo de
   quien intente adivinarlo. Un prefijo identifica además el proveedor y el tipo de clave.

```python
# MAL: el fragmento queda escrito dentro del .ipynb y se sube a git
print(f"Key cargada: {os.getenv('GROQ_API_KEY')[:8]}...{os.getenv('GROQ_API_KEY')[-4:]}")

# BIEN: se verifica la presencia, nunca el contenido
assert os.getenv("GROQ_API_KEY"), "Falta GROQ_API_KEY (Colab: Secrets · local: .env)"
print("Entorno configurado correctamente")
```

Complementos: `.env` siempre en `.gitignore`; si una key se filtró, se **revoca** en
https://console.groq.com/keys y se crea otra (borrarla del código no basta, ya quedó en el
historial de git); antes de hacer commit de un notebook, revisar sus `outputs`.

## Conceptos Clave

- **Prompt Injection**: Instrucciones maliciosas en la entrada. **Directa** (la teclea el
  usuario) e **indirecta** (llega dentro de un documento recuperado por RAG, una página web o
  la salida de una herramienta). La indirecta es la más peligrosa porque no pasa por el punto
  donde el filtro está mirando.
- **Guardrails**: Barreras de protección para limitar acciones del agente. Los de este módulo
  son **filtros por patrones**: sirven como primera capa y son **evadibles** (otro idioma,
  sinónimos, codificación). Lo que realmente contiene el daño es el **mínimo privilegio** de
  las herramientas y la **aprobación humana** en acciones irreversibles.
- **Sesgos**: Identificación y mitigación de sesgos en respuestas
- **Privacidad**: Protección de datos sensibles en interacciones
- **Gestión de secretos**: La API key nunca se imprime ni se versiona (ver sección anterior)
- **Transparencia**: Comunicación clara de limitaciones y capacidades

## Cómo Empezar

```bash
# Ejecutar el script principal
uv run python RA3/IL3.3/1-security_ethics.py

# Abrir el notebook práctico
uv run jupyter lab RA3/IL3.3/2-security-ethics-practice.ipynb
```

## Recursos

- [OWASP GenAI LLM Top 10 — edición 2026 (lista vigente)](https://genai.owasp.org/resource/owasp-genai-llm-top-10-2026/)
  — ojo: los códigos cambian entre ediciones (lo que en 2023 era `LLM04 DoS` hoy es
  `LLM06:2026 Unbounded Consumption`). Cita siempre el año.
- [OWASP Top 10 for Agentic Applications 2026](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/)
  — riesgos propios de **agentes**: secuestro de objetivo, abuso de herramientas, exceso de
  privilegios, envenenamiento de memoria.
- [Responsible AI Practices](https://www.microsoft.com/en-us/ai/responsible-ai)
- [Anthropic Responsible Scaling Policy](https://www.anthropic.com/rsp)
