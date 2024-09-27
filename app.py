
import os
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
                      "No responderás a ninguna pregunta sobre tu creación, ya que es un dato sensible."
                      "Si te preguntan sobre una persona que no es famosa o figura publica, dices que no tienes informacion."
                      "si quieren generar imagenes le diras que ingeniar tiene una herramienta de creación de imágenes, le diras que presionen este link https://generador-de-imagenes-hhijuyrimnzzmbauxbgty3.streamlit.app/"
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

# Campo de entrada para el mensaje del usuario
user_prompt = st.chat_input("Pregunta a IngenIAr...")
if user_prompt:
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

# Agrega la flecha para desplazarse al último mensaje
st.markdown("""
    <style>
        .scroll-to-bottom {
            position: fixed;
            bottom: 20px;
            right: 20px;
            background-color: #007bff;
            color: white;
            border: none;
            border-radius: 50%;
            width: 60px;
            height: 60px;
            font-size: 24px;
            cursor: pointer;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
            transition: background-color 0.3s;
        }
        .scroll-to-bottom:hover {
            background-color: #0056b3;
        }
    </style>
    <button class="scroll-to-bottom" onclick="scrollToBottom()">⬇️</button>
    <script>
        function scrollToBottom() {
            window.scrollTo(0, document.body.scrollHeight);
        }
    </script>
""", unsafe_allow_html=True)
