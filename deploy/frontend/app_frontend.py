"""Frontend Streamlit que consume la API del backend.

No invoca el modelo directamente: toda la lógica (y la seguridad) vive en el
backend. Esto mantiene la GROQ_API_KEY fuera del navegador.
"""
import os
import html

import requests
import streamlit as st

BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:8000")

st.set_page_config(page_title="Agente IA — Curso ISIA", page_icon="🤖")
st.title("🤖 Agente IA — Curso ISIA")
st.caption("Frontend Streamlit → API FastAPI con guardrails")

if "historial" not in st.session_state:
    st.session_state.historial = []

for turno in st.session_state.historial:
    with st.chat_message(turno["role"]):
        # Escapamos la salida del modelo: nunca renderizar HTML crudo (LLM10:2026).
        st.markdown(html.escape(turno["content"]))

pregunta = st.chat_input("Escribe tu pregunta…")
if pregunta:
    st.session_state.historial.append({"role": "user", "content": pregunta})
    with st.chat_message("user"):
        st.markdown(html.escape(pregunta))
    try:
        r = requests.post(f"{BACKEND_URL}/chat", json={"mensaje": pregunta}, timeout=30)
        r.raise_for_status()
        data = r.json()
        respuesta = data["respuesta"]
        if data.get("bloqueado"):
            respuesta = f"⚠️ {respuesta} ({data.get('motivo','')})"
    except requests.RequestException:
        respuesta = "No se pudo contactar al backend. Intenta más tarde."
    st.session_state.historial.append({"role": "assistant", "content": respuesta})
    with st.chat_message("assistant"):
        st.markdown(html.escape(respuesta))
