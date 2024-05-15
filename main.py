import os
import streamlit as st
from typing import Generator
import google.generativeai as genai
from PIL import Image
from datetime import datetime
import yaml
import pdfkit
from dotenv import load_dotenv  # Import load_dotenv

load_dotenv()  # Load environment variables from .env file

# Load configuration from config.yaml
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

st.set_page_config(page_icon="💬", layout="wide", page_title="Gemini AI Assistant")

# Load Groq API key from environment variable
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    st.error("GOOGLE_API_KEY environment variable not found. Please set it in the .env file.")
    st.stop()

# Define model details
model_option = st.sidebar.selectbox("Select Model", config["models"].keys())
model_info = {
    "model_id": config["model_mapping"][model_option],
    "name": model_option,
    "developer": "Google",
    "description": "A powerful language model by Google."
}

# Display model information
st.sidebar.header("Model Information")
st.sidebar.markdown(f"**Name:** {model_info['name']}")
st.sidebar.markdown(f"**Developer:** {model_info['developer']}")
st.sidebar.markdown(f"**Description:** {model_info['description']}")

# Tone selection
tone_selection = st.sidebar.selectbox("Select Tone", ["Default", "Formal", "Casual", "Friendly", "Technical"], help="Choose the tone of the conversation.")

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    avatar = '🤖' if message["role"] == "assistant" else '👨‍💻'
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

if prompt := st.chat_input("Enter your prompt here...", key="user_input"):
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user", avatar='👨‍💻'):
        st.markdown(prompt)

    # Fetch response from Google Generative AI API
    try:
        genai.configure(api_key=GOOGLE_API_KEY)
        model = genai.GenerativeModel(model_info["model_id"])

        uploaded_file = st.file_uploader("Upload an image (optional)", type=["png", "jpg", "jpeg"], key="uploaded_file", help="You can upload an image for analysis.")

        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            previous_context = " ".join([entry['response'] for entry in st.session_state['messages']])
            prompt = f"{previous_context} {prompt}"
            response = model.generate_content([{"text": prompt}, image])
        else:
            previous_context = " ".join([entry['response'] for entry in st.session_state['messages']])
            prompt = f"{previous_context} {prompt}"
            response = model.generate_content({"text": prompt})

        with st.chat_message("assistant", avatar="🤖"):
            st.markdown(response.text)

    except Exception as e:
        st.error(f"Error: {e}", icon="🚨")

    # Append the full response to session_state.messages
    st.session_state.messages.append({
        "role": "assistant",
        "content": response.text,
        "model_name": model_option,
        "tone": tone_selection.lower(),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

# Add a clear chat button
if st.sidebar.button("Clear Chat"):
    st.session_state.messages = []

# Add a download chat history button
if st.sidebar.button("Download Chat History"):
    chat_history = "\n".join([f"{m['role'].capitalize()}: {m['content']}" for m in st.session_state.messages])
    st.download_button(
        label="Download Chat History",
        data=chat_history,
        file_name="chat_history.txt",
        mime="text/plain",
    )

# Add a download chat history as PDF button
if st.sidebar.button("Download Chat History as PDF"):
    try:
        chat_history_html = "\n".join([
            f"\n<p><strong>{m['role'].capitalize()}:</strong> {m['content']}</p>\n\n<p><strong>Model:</strong> {m['model_name']}</p>\n\n<p><strong>Tone:</strong> {m['tone']}</p>\n\n<p><strong>Timestamp:</strong> {m['timestamp']}</p>\n"
            for m in st.session_state.messages
        ])
        pdf_file = pdfkit.from_string(chat_history_html, False)
        st.download_button(
            label="Download Chat History as PDF",
            data=pdf_file,
            file_name="chat_history.pdf",
            mime="application/pdf",
        )
    except Exception as e:
        st.error(f"Error generating PDF: {str(e)}")
