import streamlit as st
import google.generativeai as genai
import os
from PIL import Image

# Initialize session state for chat history and user input
if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []
if 'user_input' not in st.session_state:
    st.session_state['user_input'] = ""

def fetch_response(user_input, model_name, image=None):
    try:
        # Configure the API with your key (ensure secure storage)
        genai.configure(api_key=os.environ.get('GOOGLE_API'))
        model = genai.GenerativeModel(model_name)
        if image:
            response = model.generate_content([user_input, image])
        else:
            response = model.generate_content(user_input)
        return response.text
    except Exception as e:
        return f"Error: {e}"

def main():
    st.title("Google Generative AI Chatbot")

    # User input and model selection in sidebar
    st.sidebar.header("Input")
    st.session_state['user_input'] = st.sidebar.text_input("Enter your message here:", 
                                                          value=st.session_state['user_input'])
    uploaded_file = st.sidebar.file_uploader("Upload an image", type=["png", "jpg", "jpeg"])
    model_selection = st.sidebar.selectbox("Select Model", ["Gemini 1", "Gemini 1.5"])

    # Display chat history
    for i, entry in enumerate(st.session_state['chat_history']):
        with st.expander(f"Conversation {i+1}"):
            if 'image' in entry:
                st.write("User uploaded an image")
                st.image(entry['image'], caption="Uploaded Image", use_column_width=True)
            st.write(f"User: {entry['user_input']}")
            st.write(f"Model: {entry['model_name']}")
            st.write(f"Response: {entry['response']}")

    # Send message and process response
    if st.sidebar.button("Send"):
        with st.spinner("Generating response..."):
            if model_selection == "Gemini 1":
                model_name = "gemini-1.0-pro-latest"
            else:
                model_name = "gemini-1.5-pro-latest"

            if uploaded_file is not None:
                image = Image.open(uploaded_file)
                response = fetch_response(st.session_state['user_input'], model_name, image=image)
                st.session_state['chat_history'].append({
                    'user_input': st.session_state['user_input'], 
                    'model_name': model_name, 
                    'response': response,
                    'image': image
                })
            else:
                response = fetch_response(st.session_state['user_input'], model_name)
                st.session_state['chat_history'].append({
                    'user_input': st.session_state['user_input'], 
                    'model_name': model_name, 
                    'response': response
                })
        st.session_state['user_input'] = "" # Clear input box after sending

    # Display output 
    st.subheader("Output")
    st.write(response) 

if __name__ == "__main__":
    main()
