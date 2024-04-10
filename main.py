import streamlit as st
import google.generativeai as genai
import os
from PIL import Image
from datetime import datetime
import yaml
import markdown

# Load configuration from YAML file
with open('config.yaml', 'r') as file:
    config = yaml.safe_load(file)

# Initialize session state for chat history
if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []

def fetch_response(chat_history, model_name, image=None):
    # Configure the API with your key
    genai.configure(api_key=os.environ.get('GOOGLE_API'))
    model = genai.GenerativeModel(model_name)

    # Construct prompt with chat history
    prompt = ""
    for entry in chat_history:
        if 'image' in entry:
            prompt += "User uploaded an image. "
        prompt += f"User: {entry['user_input']}\nModel: {entry['response']}\n"

    # Add new user input to the prompt
    prompt += f"User: {chat_history[-1]['user_input']}\nModel: " 

    if image:
        response = model.generate_content([prompt, image])
    else:
        response = model.generate_content(prompt)
    return response.text

def main():
    # ... (rest of the code is the same as before)

    if st.sidebar.button("Send"):
        # ... (get model_name and image as before)

        response = fetch_response(st.session_state['chat_history'], model_name, image=image)
        st.session_state['chat_history'].append({
            # ... (rest of the append logic is the same)
        })

        # ... (rest of the code is the same as before)

if __name__ == "__main__":
    main()
