import os
import streamlit as st
import google.generativeai as gen_ai
import PyPDF2  # Para manejar la lectura de PDFs
import io

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

# Configuración de generación
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
                      "Si quieren generar imágenes, les dirás que IngenIAr tiene una herramienta de creación de imágenes, les dirás que presionen este link: https://generador-de-imagenes-hhijuyrimnzzmbauxbgty3.streamlit.app/"
)

# Inicializa la sesión de chat si no está presente
if "chat_session" not in st.session_state:
    st.session_state.chat_session = model.start_chat(history=[])

# Inicializa el estado para almacenar el PDF subido
if "uploaded_pdf" not in st.session_state:
    st.session_state.uploaded_pdf = None
    st.session_state.pdf_text = ""
    st.session_state.pdf_uploaded = False

# Título del chatbot
st.title("🤖 IngenIAr - Chat")

# Mostrar el historial de chat
for message in st.session_state.chat_session.history:
    role = "assistant" if message.role == "model" else "user"
    with st.chat_message(role):
        st.markdown(message.parts[0].text)

# Función para leer PDF y extraer el texto
def process_pdf(uploaded_file):
    pdf_text = ""
    try:
        pdf_reader = PyPDF2.PdfReader(uploaded_file)
        for page in pdf_reader.pages:
            pdf_text += page.extract_text()
        return pdf_text
    except Exception as e:
        st.error(f"Error al leer el PDF: {str(e)}")
        return ""

# Mostrar un campo de entrada de chat con el ícono de clip
col1, col2 = st.columns([0.1, 0.9])

# Columna 1: Ícono de clip para subir archivo
with col1:
    uploaded_file = st.file_uploader("", type="pdf", label_visibility="collapsed", key="file_uploader")

# Columna 2: Campo de texto para el mensaje del usuario
with col2:
    if st.session_state.pdf_uploaded:
        st.text_input("Escribe tu mensaje...", "📄 Archivo adjunto: " + st.session_state.uploaded_pdf.name, key="user_input", label_visibility="collapsed")
    else:
        user_prompt = st.text_input("Escribe tu mensaje...", key="user_input", label_visibility="collapsed")

# Manejar el archivo PDF cuando se suba
if uploaded_file:
    st.session_state.uploaded_pdf = uploaded_file
    st.session_state.pdf_text = process_pdf(uploaded_file)
    st.session_state.pdf_uploaded = True

# Si se ha subido un PDF y el usuario ha escrito un mensaje
if st.session_state.pdf_uploaded and st.session_state.user_input:
    # Combina el mensaje del usuario con el contenido del PDF
    combined_prompt = st.session_state.user_input
    if st.session_state.pdf_text:
        combined_prompt += f"\n\n**Contenido del PDF**: {st.session_state.pdf_text}"

    # Envía el mensaje del usuario (y el PDF si se subió) a Gemini y obtiene la respuesta
    try:
        gemini_response = st.session_state.chat_session.send_message(combined_prompt.strip())

        # Muestra la respuesta de Gemini
        with st.chat_message("assistant"):
            st.markdown(gemini_response.text)

        # Limpiar el texto del PDF después de enviar
        st.session_state.uploaded_pdf = None
        st.session_state.pdf_text = ""
        st.session_state.pdf_uploaded = False

    except Exception as e:
        st.error(f"Error al enviar el mensaje: {str(e)}")
