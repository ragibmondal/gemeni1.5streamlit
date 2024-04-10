import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv
load_dotenv()

def fetch_response(user_input, model_name):
    genai.configure(api_key=os.environ['GOOGLE_API'])
    model = genai.GenerativeModel(model_name)

    response = model.generate_content(user_input)

    return response.text

def main():
    st.title("Google Generative AI Chatbot")
    st.sidebar.header("Input")
    user_input = st.sidebar.text_input("Enter your message here:")
    model_selection = st.sidebar.selectbox("Select Model", ["Gemini 1", "Gemini 1.5"])

    if st.sidebar.button("Send"):
        if model_selection == "Gemini 1":
            model_name = "gemini-1.0-base-latest"
        else:
            model_name = "gemini-1.5-pro-latest"

        response = fetch_response(user_input, model_name)
        st.subheader("Output")
        st.text_area("", value=response, height=999, max_chars=None, key=None)

if __name__ == "__main__":
    main()
