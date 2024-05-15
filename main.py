import streamlit as st
import google.generativeai as genai
import os
from PIL import Image
from datetime import datetime
import yaml
import markdown
import pdfkit
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load configuration from YAML file
with open('config.yaml', 'r') as file:
    config = yaml.safe_load(file)

# Initialize session state for chat history
if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []

def fetch_response(user_input, model_name, image=None, previous_context=None, tone="default"):
    # ... (same as before) ...

def main():
    st.set_page_config(page_title="Gemini AI Assistant", page_icon=":robot_face:", layout="wide")

    # Sidebar components
    with st.sidebar:
        st.header("Settings")
        model_selection = st.selectbox("Select Model", config['models'], help="Choose the model you want to use.")
        tone_selection = st.radio("Select Tone", ["Default", "Formal", "Casual", "Friendly", "Technical"], help="Choose the tone of the conversation.")

    # Main content area
    st.title("Gemini AI Assistant")
    st.write("Welcome to Gemini, your AI companion! You can chat with me, ask questions, or provide images for analysis.")

    # Chat container
    chat_container = st.container()

    # User input and file upload (moved to the sidebar)
    with st.sidebar:
        st.header("Input")
        user_input = st.text_area("Message Gemini...", key="user_input", placeholder="Type your message here...", height=100)
        uploaded_file = st.file_uploader("Upload an image (optional)", type=["png", "jpg", "jpeg"], key="uploaded_file", help="You can upload an image for Gemini to analyze.")

    # Send button container
    send_button_container = st.container()
    with send_button_container:
        if st.button("Send", key="send_button"):
            model_name = config['model_mapping'][model_selection]
            previous_context = " ".join([entry['response'] for entry in st.session_state['chat_history']])
            tone = tone_selection.lower()

            # ... (same as before) ...

    # Display chat history
    with chat_container:
        for i, entry in enumerate(st.session_state['chat_history']):
            with st.container():
                # ... (same as before) ...

    # Disclaimer
    st.markdown("**Disclaimer:** Gemini can make mistakes. Consider verifying important information from reliable sources.", unsafe_allow_html=True)

    # Conversation management
    with st.sidebar:
        # ... (same as before) ...

if __name__ == "__main__":
    main()
