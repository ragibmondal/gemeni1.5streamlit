import streamlit as st
import google.generativeai as genai
import os
from PIL import Image

# Function to fetch response from the Generative AI model
def fetch_response(user_input, model_name, image=None):
    # Configure the API with your key
    genai.configure(api_key=os.environ.get('GOOGLE_API'))
    model = genai.GenerativeModel(model_name)

    if image:
        response = model.generate_content([user_input, image])
    else:
        response = model.generate_content(user_input)

    return response.text

def main():
    st.title("Google Generative AI Chatbot")

    # Initialize chat history if not present in session state
    if 'chat_history' not in st.session_state:
        st.session_state['chat_history'] = []

    # Container for chat messages
    chat_container = st.empty()

    # Sidebar for user input and model selection
    with st.sidebar:
        st.header("Input")
        user_input = st.text_input("Enter your message here:")
        uploaded_file = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"])
        model_selection = st.selectbox("Select Model", ["Gemini 1", "Gemini 1.5"])
        send_button = st.button("Send")

    # Process user input and display chat history on button click
    if send_button:
        if model_selection == "Gemini 1":
            model_name = "gemini-1.0-pro-latest"
        else:
            model_name = "gemini-1.5-pro-latest"

        # Fetch response based on user input and selected model
        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            response = fetch_response(user_input, model_name, image=image)
        else:
            response = fetch_response(user_input, model_name)

        # Update chat history
        st.session_state['chat_history'].append({
            'user_input': user_input,
            'model_name': model_name,
            'response': response,
            'image': image if uploaded_file is not None else None  # Store image info if available
        })

    # Display chat history within the container
    with chat_container.container():
        for entry in st.session_state['chat_history']:
            if 'image' in entry and entry['image']:
                st.image(entry['image'], caption="Uploaded Image", use_column_width=True)
            st.write(f"User: {entry['user_input']}")
            st.write(f"Model: {entry['response']}")
            st.write("---")  # Add separator between messages

if __name__ == "__main__":
