# IL3.5: Ciberseguridad y Despliegue en AWS

Este módulo lleva la app del curso a un despliegue real y seguro en AWS Academy,
cerrando RA3: de la observabilidad (IL3.1/3.2) y la seguridad del agente (IL3.3)
a la **ciberseguridad de la aplicación/infraestructura** y el **despliegue correcto**.

El artefacto de `deploy/` es un **chat + guardrails** (FastAPI): enseña HTTPS, secretos
y OWASP sin montar un grafo en EC2. El proyecto del curso sí puede sustituir
`AgentClient` por `create_agent`. Mismo `.env`: `GROQ_*` y, si trazas, `LANGSMITH_*`.
El ADR de IL2.4 dice *qué* se despliega.

## Objetivos de Aprendizaje
- Empaquetar una solución de IA (frontend + API) en contenedores.
- Aplicar esenciales de ciberseguridad: secretos, mínimo privilegio, HTTPS,
  rate limiting y mitigación del OWASP LLM Top 10.
- Desplegar en una EC2 de AWS Academy Learner Lab paso a paso.
- Verificar y luego apagar recursos para cuidar los créditos.

## Archivos del Módulo
| Archivo | Descripción |
|---|---|
| `1-deploy-aws-paso-a-paso.md` | Guía completa de despliegue en AWS Academy. |
| `2-security-hardening-practice.ipynb` | Práctica: LLM01, LLM02 y el mapa de los veinte ítems. |
| `3-ejemplos-owasp.py` | Corre el mapa sin Groq. |
| `mapa-owasp-2026.md` | Tabla LLM01–LLM10 y ASI01–ASI10, con estado. |
| `checklist-seguridad-despliegue.md` | Checklist para la entrega/presentación. |
| `presentacion.md` | Diapositivas de apoyo. |

## Artefacto desplegable
El código vive en la carpeta raíz [`deploy/`](../../deploy/README.md).

## Demo en clase, sin AWS

El orden para proyectar está en `presentacion.md` (sección 2): health, una
inyección, un correo, `/metrics`. En pantalla tienen que verse `bloqueado: true`,
el correo reemplazado por `CORREO_ELECTRONICO_REDACTADO` y `bloqueados` más alto.
Después se nombran las evasiones que el filtro deja abiertas.

Los `curl` y cómo levantar la API sin Docker están en
[`../README.md`](../README.md#demostrarlo-en-casa).

## Conceptos Clave
- **Contenedores no-root** y red interna (solo el proxy se expone).
- **HTTPS** con Caddy + cabeceras de seguridad (HSTS, X-Content-Type-Options).
- **Mínimo privilegio**: Security Group restrictivo, rol `LabRole`.
- **Secretos** fuera del repo (`.env` / SSM Parameter Store).
- **OWASP LLM Top 10** aplicado en el backend.

## Recursos
- [OWASP GenAI LLM Top 10 — edición 2026 (lista vigente, publicada en agosto de 2026)](https://genai.owasp.org/resource/owasp-genai-llm-top-10-2026/)
  — la presentación usa estos códigos y muestra la equivalencia con los de 2025 y 2023, porque
  la numeración **cambia en cada edición**.
- [OWASP Top 10 for Agentic Applications 2026 (ASI01–ASI10)](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/)
  — lista específica para agentes: secuestro de objetivo, abuso de herramientas, envenenamiento
  de memoria/contexto, comunicación insegura entre agentes.
- [AWS Academy Learner Lab](https://www.awsacademy.com/)
- [Caddy — Automatic HTTPS](https://caddyserver.com/docs/automatic-https)
