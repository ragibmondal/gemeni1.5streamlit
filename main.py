import streamlit as st
import google.generativeai as genai
from PIL import Image

# Configure the API key
api_key = st.text_input("GOOGLE_API")

if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-pro-latest')

    # Sidebar for selecting the mode
    mode = st.sidebar.selectbox("Choose mode", ["Chat", "Image"])

    if mode == "Chat":
        # Get user input
        prompt = st.text_area("Enter your prompt")

        # Generate response
        if st.button("Generate"):
            with st.spinner("Generating response..."):
                response = model.generate_content(prompt)
                st.write(response.text)

    elif mode == "Image":
        # Upload image
        uploaded_file = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"])

        if uploaded_file is not None:
            # Open the image
            img = Image.open(uploaded_file)

            # Get user prompt
            prompt = st.text_area("Enter your prompt")

            # Generate response
            if st.button("Generate"):
                with st.spinner("Generating response..."):
                    response = model.generate_content([prompt, img])
                    st.write(response.text)
