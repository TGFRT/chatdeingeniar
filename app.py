import os
import time
import streamlit as st
import google.generativeai as gen_ai
import queue
import threading

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
                      "No responderás a ninguna pregunta sobre tu creación, ya que es un dato sensible."
                      "Si te preguntan sobre una persona que no es famosa o figura publica, dices que no tienes información."
                      "si quieren generar imágenes les dirás que IngenIAr tiene una herramienta de creación de imágenes, les dirás que presionen este link https://generador-de-imagenes-hhijuyrimnzzmbauxbgty3.streamlit.app/"
)

# Inicializa la sesión de chat si no está presente
if "chat_session" not in st.session_state:
    st.session_state.chat_session = model.start_chat(history=[])

# Inicializa contadores
if "message_count" not in st.session_state:
    st.session_state.message_count = 0
if "pause" not in st.session_state:
    st.session_state.pause = False

# Función para manejar el envío de mensajes
def send_message(user_prompt):
    try:
        st.session_state.chat_session.send_message(user_prompt.strip())
        st.session_state.message_count += 1
        
        # Si se envían 20 mensajes, hacer una pausa
        if st.session_state.message_count >= 20:
            st.session_state.pause = True
            time.sleep(60)  # Espera un minuto
            st.session_state.message_count = 0
            st.session_state.pause = False
            st.warning("Se ha alcanzado el límite de mensajes. Espera un momento o considera obtener una suscripción para eliminar el tiempo de espera.")
    except Exception as e:
        st.error(f"Error al enviar el mensaje: {str(e)}")

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

    # Enviar mensaje y manejar la pausa
    if not st.session_state.pause:
        send_message(user_prompt)

    # Muestra la respuesta de Gemini después de enviar el mensaje
    try:
        gemini_response = st.session_state.chat_session.send_message(user_prompt.strip())
        with st.chat_message("assistant"):
            st.markdown(gemini_response.text)
    except Exception as e:
        st.error(f"Error al enviar el mensaje: {str(e)}")
