import streamlit as st
import google.generativeai as genai
import os
from PIL import Image

# Initialize session state for chat history
if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []

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

    # Display chat history
    for i, entry in enumerate(st.session_state['chat_history']):
        if 'image' in entry:
            st.write(f"**User:** {entry['user_input']}")
            st.image(entry['image'], caption="Uploaded Image", use_column_width=True)
        else:
            st.write(f"**User:** {entry['user_input']}")

        st.write(f"**{entry['model_name']}:** {entry['response']}")
        st.write("---")

    # Get user input
    user_input = st.text_area("Enter your message here:")
    uploaded_file = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"])
    model_selection = st.selectbox("Select Model", ["Gemini 1", "Gemini 1.5"])

    if st.button("Send"):
        if model_selection == "Gemini 1":
            model_name = "gemini-1.0-pro-latest"
        else:
            model_name = "gemini-1.5-pro-latest"

        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            response = fetch_response(user_input, model_name, image=image)
            st.session_state['chat_history'].append({
                'user_input': user_input,
                'model_name': model_name,
                'response': response,
                'image': image
            })
        else:
            response = fetch_response(user_input, model_name)
            st.session_state['chat_history'].append({
                'user_input': user_input,
                'model_name': model_name,
                'response': response
            })

if __name__ == "__main__":
    main()
