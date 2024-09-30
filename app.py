import os
import time
import streamlit as st
import google.generativeai as gen_ai
from difflib import SequenceMatcher
import re
from collections import deque

# Función para calcular la similitud entre dos textos
def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

# Función para normalizar el texto
def normalize_text(text):
    text = text.lower()  # Convierte a minúsculas
    text = re.sub(r'[^\w\s]', '', text)  # Elimina signos de puntuación
    text = re.sub(r'(.)\1+', r'\1', text)  # Normaliza caracteres repetidos
    return text

# Configura Streamlit
st.set_page_config(
    page_title="Chat con IngenIAr!",
    page_icon=":brain:",
    layout="centered",
)

# Lista de claves API
API_KEYS = [
    st.secrets["GOOGLE_API_KEY_1"],
    st.secrets["GOOGLE_API_KEY_2"],
    st.secrets["GOOGLE_API_KEY_3"],
    st.secrets["GOOGLE_API_KEY_4"],
    st.secrets["GOOGLE_API_KEY_5"],
    st.secrets["GOOGLE_API_KEY_6"],
    st.secrets["GOOGLE_API_KEY_7"],
]

# Inicializa variables de estado
if "current_api_index" not in st.session_state:
    st.session_state.current_api_index = 0
if "daily_request_count" not in st.session_state:
    st.session_state.daily_request_count = 0
if "message_count" not in st.session_state:
    st.session_state.message_count = 0
if "waiting" not in st.session_state:
    st.session_state.waiting = False
if "last_user_messages" not in st.session_state:
    st.session_state.last_user_messages = []
if "message_timestamps" not in st.session_state:
    st.session_state.message_timestamps = deque(maxlen=8)  # Limitar a 8 mensajes

# Configura la API con la clave actual
def configure_api():
    gen_ai.configure(api_key=API_KEYS[st.session_state.current_api_index])

# Rotar la clave API si alcanzas el límite diario
def rotate_api():
    st.session_state.current_api_index = (st.session_state.current_api_index + 1) % len(API_KEYS)
    st.session_state.daily_request_count = 0  # Reinicia el conteo de solicitudes diarias
    configure_api()

# Verificar y rotar si se alcanza el límite diario
def check_and_rotate_api():
    if st.session_state.daily_request_count >= 1500:  # Límite diario
        st.warning(f"Clave API {API_KEYS[st.session_state.current_api_index]} alcanzó el límite diario. Rotando...")
        rotate_api()

# Configura la API al inicio
configure_api()

# Configura la generación
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
}

# Crea el modelo con instrucciones de sistema
model = gen_ai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
    system_instruction="Eres un asistente de IngenIAr, una empresa de soluciones tecnológicas con IA, "
                      "fundada en Perú por Sergio Requena en colaboración con Google. "
                      "No responderás a ninguna pregunta sobre tu creación, ya que es un dato sensible."
                      "Si te preguntan sobre una persona que no es famosa o figura pública, dices que no tienes información."
                      "Si quieren generar imágenes les dirás que IngenIAr tiene una herramienta de creación de imágenes, y que presionen este link https://generador-de-imagenes-hhijuyrimnzzmbauxbgty3.streamlit.app/ "
                      "Solo hablarás de las herramientas de IngenIAr, nada de otras herramientas en internet."
)

# Inicializa la sesión de chat si no está presente
if "chat_session" not in st.session_state:
    st.session_state.chat_session = model.start_chat(history=[])

# Título del chatbot
st.title("🤖 IngenIAr - Chat")

# Mostrar el historial de chat
for message in st.session_state.chat_session.history:
    role = "assistant" if message.role == "model" else "user"
    with st.chat_message(role):
        st.markdown(message.parts[0].text)

# Botón para borrar la conversación
if st.button("Borrar Conversación"):
    st.session_state.chat_session = model.start_chat(history=[])
    st.session_state.last_user_messages.clear()
    st.session_state.message_count = 0
    st.session_state.daily_request_count = 0
    st.session_state.message_timestamps.clear()
    st.success("Conversación borrada.")

# Campo de entrada para el mensaje del usuario
user_prompt = st.chat_input("Pregunta a IngenIAr...")
if user_prompt:
    # Agrega el mensaje del usuario al chat y muéstralo
    st.chat_message("user").markdown(user_prompt)

    # Normaliza el texto del mensaje del usuario
    normalized_user_prompt = normalize_text(user_prompt.strip())

    # Verificar si el mensaje es repetitivo
    is_similar = any(similar(normalized_user_prompt, normalize_text(previous)) > 0.90 for previous in st.session_state.last_user_messages)
    if is_similar:
        st.warning("Por favor, no envíes mensajes repetitivos.")
    else:
        # Agrega el nuevo mensaje a la lista de mensajes anteriores
        st.session_state.last_user_messages.append(normalized_user_prompt)
        # Limitar el número de mensajes guardados para evitar que la lista crezca indefinidamente
        if len(st.session_state.last_user_messages) > 10:  # Puedes ajustar el número según tus necesidades
            st.session_state.last_user_messages.pop(0)

        # Agregar la marca de tiempo del nuevo mensaje
        st.session_state.message_timestamps.append(time.time())

        # Verificar si se han enviado más de 8 mensajes en los últimos 40 segundos
        if len(st.session_state.message_timestamps) >= 8:
            # Calcular el tiempo desde el primer mensaje en la lista
            if (st.session_state.message_timestamps[-1] - st.session_state.message_timestamps[0]) <= 40:
                st.session_state.waiting = True
                st.warning("Hay mucha gente usando el servicio. Por favor, espere 15 segundos...")
                
                # Rueda girando
                with st.spinner("Procesando..."):
                    time.sleep(15)  # Espera 15 segundos
                
                st.session_state.waiting = False
                st.session_state.message_count = 0  # Reinicia el contador después de esperar

        # Envía el mensaje del usuario a Gemini y obtiene la respuesta
        try:
            check_and_rotate_api()  # Verifica si se debe rotar la clave API
            gemini_response = st.session_state.chat_session.send_message(user_prompt.strip())
            
            # Muestra la respuesta de Gemini
            with st.chat_message("assistant"):
                st.markdown(gemini_response.text)

            # Incrementa el contador de solicitudes
            st.session_state.daily_request_count += 1
            st.session_state.message_count += 1  # Incrementa el contador de mensajes enviados

        except Exception as e:
            if "Resource has been exhausted" in str(e):
                st.error("Hay muchas personas usando esto. Por favor, espera un momento o suscríbete a un plan de pago. También puedes solicitar tu propia credencial de acceso.")
            else:
                st.error(f"Error al enviar el mensaje: {str(e)}")
