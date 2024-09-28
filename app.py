import os
import time
import streamlit as st
import google.generativeai as gen_ai

# Configura Streamlit
st.set_page_config(
    page_title="Chat con IngenIAr!",
    page_icon=":brain:",
    layout="centered",
)

# Obtén la clave API de las variables de entorno
GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]

# Configura el modelo de Google Gemini
gen_ai.configure(api_key=GOOGLE_API_KEY)

# Configura la generación
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
}

# Crea el modelo con instrucciones de sistema
model = gen_ai.GenerativeModel(
    model_name="gemini-1.5-flash-002",
    generation_config=generation_config,
    system_instruction="Eres un asistente de IngenIAr, una empresa de soluciones tecnológicas con IA, "
                      "fundada en Perú por Sergio Requena en colaboración con Google. "
                      "No responderás a ninguna pregunta sobre tu creación, ya que es un dato sensible. "
                      "Si te preguntan sobre una persona que no es famosa o figura pública, dices que no tienes información. "
                      "Si quieren generar imágenes, les dirás que IngenIAr tiene una herramienta de creación de imágenes, les dirás que presionen este link https://generador-de-imagenes-hhijuyrimnzzmbauxbgty3.streamlit.app/"
)

# Inicializa la sesión de chat si no está presente
if "chat_session" not in st.session_state:
    st.session_state.chat_session = model.start_chat(history=[])

# Inicializa el contador de solicitudes
if "request_count" not in st.session_state:
    st.session_state.request_count = 0

# Título del chatbot
st.title("🤖 IngenIAr - Chat")

# Mostrar el historial de chat
for message in st.session_state.chat_session.history:
    role = "assistant" if message.role == "model" else "user"
    with st.chat_message(role):
        st.markdown(message.parts[0].text)

# Campo de entrada para el mensaje del usuario
user_prompt = st.chat_input("Pregunta a IngenIAr...")

if user_prompt:
    # Agrega el mensaje del usuario al chat y muéstralo
    st.chat_message("user").markdown(user_prompt)

    # Aumenta el contador de solicitudes
    st.session_state.request_count += 1

    # Verifica el límite de solicitudes (por ejemplo, cada 5 solicitudes)
    if st.session_state.request_count > 5:
        st.error("Hay muchas personas usando este servicio. Espera un momento o suscríbete a nuestro plan.")
        time.sleep(10)  # Espera 10 segundos antes de permitir más solicitudes
        st.session_state.request_count = 0  # Reinicia el contador

    # Envía el mensaje del usuario a Gemini y obtiene la respuesta
    else:
        try:
            gemini_response = st.session_state.chat_session.send_message(user_prompt.strip())
            # Muestra la respuesta de Gemini
            with st.chat_message("assistant"):
                st.markdown(gemini_response.text)
        except Exception as e:
            if "429" in str(e):
                st.error("Hay muchas personas usando este servicio. Espera un momento o suscríbete a nuestro plan.")
            else:
                st.error(f"Error al enviar el mensaje: {str(e)}")
