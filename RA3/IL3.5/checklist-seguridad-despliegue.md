# Checklist de Seguridad y Despliegue (IL3.5)

## En casa, antes de proyectar

Sin AWS y sin gastar tokens. El detalle y los `curl` están en
[RA3/README.md](../README.md#demostrarlo-en-casa).

- [ ] `uv run pytest tests/ -q` termina sin `failed` ni `xfailed`.
- [ ] `uv run python scripts/validate_repo.py` deja las cinco comprobaciones en `OK`.
- [ ] `uv run python RA3/IL3.1/1-observability_tools.py` muestra latencia, tokens
      y tasa de error.
- [ ] La API en local bloquea `ignora las instrucciones anteriores` y redacta
      un correo (`curl` del README de RA3). `/metrics` sube `bloqueados`.
- [ ] `LANGSMITH_TRACING` sigue en `"false"` salvo que ya tengas key en
      [smith.langchain.com](https://smith.langchain.com/).

## Antes de desplegar
- [ ] `.env` NO está en git (`git status` no lo muestra).
- [ ] La `GROQ_API_KEY` está solo en el `.env` del servidor (nunca en git) y se
      puede revocar desde https://console.groq.com/keys.
- [ ] Los contenedores corren como usuario no-root.
- [ ] Solo el proxy publica puertos; backend/frontend en red interna.

## En AWS
- [ ] Security Group: 443/80 abiertos; 22 solo a mi IP (no 0.0.0.0/0).
- [ ] La instancia usa el rol `LabRole` (no claves embebidas).
- [ ] HTTPS funciona y redirige desde HTTP.

## Seguridad de la app (OWASP LLM)
- [ ] Prompt injection bloqueado en el mensaje y en el historial (probado).
- [ ] Rate limiting devuelve 429 al exceder el límite.
- [ ] La salida del modelo se muestra escapada (sin HTML crudo).
- [ ] PII redactada en respuestas y logs.
- [ ] Los errores no exponen trazas internas al cliente.
- [ ] Sé explicar **qué no cubre** el guardrail: hex, texto invertido, un idioma
      que no esté en la lista, una paráfrasis nueva, y la **inyección indirecta**
      (la que llega dentro de un documento, una web o la salida de una herramienta).
      Base64, rot13 y letras separadas por puntos sí se decodifican.
- [ ] Si mi agente tiene herramientas: cada una con el **mínimo permiso** necesario, y las
      acciones irreversibles (borrar, pagar, enviar) piden **confirmación humana**.
- [ ] `/metrics` es público solo a propósito (demo de observabilidad); en
      producción se protege con token o IP interna.

## Después de la demo
- [ ] Recursos apagados/terminados para no gastar créditos.
- [ ] Capturas/evidencia guardadas para la entrega.
