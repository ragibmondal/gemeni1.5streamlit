import os
import streamlit as st
import google.generativeai as genai
from PIL import Image

# Set page configuration
st.set_page_config(page_title="Google Generative AI Demo", page_icon=":robot_face:")

# Retrieve the API key from the environment variable
API_KEY = os.environ.get("GOOGLE_API")

# Configure the API and model
if API_KEY:
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('gemini-1.5-pro-latest')
else:
    st.error("Please set the 'GOOGLE_GENERATIVE_API_KEY' environment variable.")
    st.stop()

# Initialize chat history
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

# Display chat history
for entry in st.session_state.chat_history:
    if isinstance(entry, str):
        st.text_area("User", value=entry, height=200, max_chars=None, key=f"user_input_{len(st.session_state.chat_history)}")
    else:
        st.image(entry[1], caption=entry[0], use_column_width=True)
        st.text_area("AI Response", value=entry[2], height=200, max_chars=None, key=f"ai_response_{len(st.session_state.chat_history)}")

# Get user input
user_input = st.text_area("Enter your prompt or upload an image", height=200)
uploaded_file = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"])

# Process user input
if st.button("Generate"):
    if user_input:
        st.session_state.chat_history.append(user_input)
        with st.spinner("Generating response..."):
            response = model.generate_content(user_input)
            st.session_state.chat_history.append(response.text)
    elif uploaded_file is not None:
        img = Image.open(uploaded_file)
        prompt = st.text_area("Enter your prompt")
        st.session_state.chat_history.append(["Image Prompt", img, prompt])
        with st.spinner("Generating response..."):
            response = model.generate_content([prompt, img])
            st.session_state.chat_history.append(response.text)
