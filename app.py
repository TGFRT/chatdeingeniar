import os
import streamlit as st
import google.generativeai as gen_ai
import time

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
                      "Si te preguntan sobre una persona que no es famosa o figura publica, dices que no tienes informacion."
                      "si quieren generar imagenes le diras que ingeniar tiene una herramienta de creación de imágenes,le diras que presionen este link https://generador-de-imagenes-hhijuyrimnzzmbauxbgty3.streamlit.app/ "
                      "solo diras de las herramientas de ingeniar, nada de otras herramientas en el internet"
)

# Inicializa la sesión de chat si no está presente
if "chat_session" not in st.session_state:
    st.session_state.chat_session = model.start_chat(history=[])
    st.session_state.message_times = []  # Para rastrear los tiempos de los mensajes
    st.session_state.message_count = 0  # Contador de mensajes
    st.session_state.last_message_time = time.time()  # Tiempo del último mensaje

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
    current_time = time.time()

    # Actualiza el contador de mensajes y los tiempos
    st.session_state.message_count += 1
    st.session_state.message_times.append(current_time)

    # Mantiene solo los tiempos de los últimos 30 segundos
    st.session_state.message_times = [t for t in st.session_state.message_times if current_time - t <= 30]

    # Si hay más de 8 mensajes en los últimos 30 segundos, espera 15 segundos
    if st.session_state.message_count > 8:
        time.sleep(15)
        st.warning("Hay muchas personas usando el servicio, espera 15 segundos o suscríbete a un plan de pago.")

    # Agrega el mensaje del usuario al chat y muéstralo
    st.chat_message("user").markdown(user_prompt)

    # Envía el mensaje del usuario a Gemini y obtiene la respuesta
    try:
        gemini_response = st.session_state.chat_session.send_message(user_prompt.strip())
        # Muestra la respuesta de Gemini
        with st.chat_message("assistant"):
            st.markdown(gemini_response.text)
    except Exception as e:
        st.error(f"Error al enviar el mensaje: {str(e)}")

    # Resetea el contador y los tiempos después de enviar el mensaje
    if current_time - st.session_state.last_message_time > 30:
        st.session_state.message_count = 0
        st.session_state.message_times = []

    st.session_state.last_message_time = current_time
