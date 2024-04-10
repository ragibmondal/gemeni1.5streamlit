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

# Sidebar for selecting the mode
mode = st.sidebar.selectbox("Choose mode", ["Chat", "Image"])

# Chat mode
if mode == "Chat":
    prompt = st.text_area("Enter your prompt")
    if st.button("Generate"):
        with st.spinner("Generating response..."):
            response = model.generate_content(prompt)
            st.success(response.text)

# Image mode
elif mode == "Image":
    uploaded_file = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"])
    if uploaded_file is not None:
        img = Image.open(uploaded_file)
        prompt = st.text_area("Enter your prompt")
        if st.button("Generate"):
            with st.spinner("Generating response..."):
                response = model.generate_content([prompt, img])
                st.success(response.text)
