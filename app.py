import os
import streamlit as st
import google.generativeai as gen_ai
import PyPDF2  # Asegúrate de instalar PyPDF2 para manejar la lectura de PDFs
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
                      "si quieren generar imagenes le diras que ingeniar tiene una herramienta de creación de imágenes, le diras que presionen este link https://generador-de-imagenes-hhijuyrimnzzmbauxbgty3.streamlit.app/"
)

# Inicializa la sesión de chat si no está presente
if "chat_session" not in st.session_state:
    st.session_state.chat_session = model.start_chat(history=[])

# Inicializa el estado para almacenar el PDF subido
if "uploaded_pdf" not in st.session_state:
    st.session_state.uploaded_pdf = None
    st.session_state.pdf_text = ""

# Título del chatbot
st.title("🤖 IngenIAr - Chat")

# Mostrar el historial de chat
for message in st.session_state.chat_session.history:
    role = "assistant" if message.role == "model" else "user"
    with st.chat_message(role):
        st.markdown(message.parts[0].text)

# Campo para subir el archivo PDF
uploaded_file = st.file_uploader("Sube un archivo PDF", type="pdf")

# Leer el PDF y extraer el texto
if uploaded_file is not None:
    try:
        # Leer el contenido del PDF
        pdf_reader = PyPDF2.PdfReader(uploaded_file)
        pdf_text = ""
        for page in pdf_reader.pages:
            pdf_text += page.extract_text()

        # Almacenar el archivo PDF subido y su contenido en la sesión de estado
        st.session_state.uploaded_pdf = uploaded_file
        st.session_state.pdf_text = pdf_text

        # Mostrar un mensaje en el chat con un ícono de PDF
        with st.chat_message("user"):
            st.markdown(f"📄 **{uploaded_file.name}** subido con éxito.")
            st.image("https://cdn-icons-png.flaticon.com/512/337/337946.png", width=30)  # Ícono de PDF

    except Exception as e:
        st.error(f"Error al leer el PDF: {str(e)}")

# Campo de entrada para el mensaje del usuario
user_prompt = st.chat_input("Pregunta a IngenIAr...")
if user_prompt:
    # Agrega el mensaje del usuario al chat y muéstralo
    st.chat_message("user").markdown(user_prompt)

    # Combina el mensaje del usuario con el contenido del PDF (si se subió uno)
    combined_prompt = user_prompt
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

    except Exception as e:
        st.error(f"Error al enviar el mensaje: {str(e)}")
