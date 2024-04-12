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

def fetch_response(user_input, model_name, image=None, previous_context=None):
    # Configure the API with your key
    genai.configure(api_key=os.environ.get('GOOGLE_API'))
    model = genai.GenerativeModel(model_name)

    if image:
        if previous_context:
            prompt = f"{previous_context} {user_input}"
            response = model.generate_content([{"text": prompt}, image])
        else:
            response = model.generate_content([{"text": user_input}, image])
    else:
        if previous_context:
            prompt = f"{previous_context} {user_input}"
            response = model.generate_content({"text": prompt})
        else:
            response = model.generate_content({"text": user_input})

    return response.text

def main():
    st.set_page_config(page_title="Google Generative AI Chatbot", page_icon=":robot_face:", layout="wide")

    # Sidebar components
    st.sidebar.header("Input")
    user_input = st.sidebar.text_area("Enter your message here:", height=200)
    uploaded_file = st.sidebar.file_uploader("Upload an image", type=["png", "jpg", "jpeg"])
    model_selection = st.sidebar.selectbox("Select Model", config['models'])
    theme_selection = st.sidebar.selectbox("Select Theme", ["Light", "Dark"])

    # Apply selected theme
    if theme_selection == "Dark":
        st.markdown("""
            <style>
            .main {
                background-color: #2d2d2d;
                color: #ffffff;
            }
            </style>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
            <style>
            .main {
                background-color: #ffffff;
                color: #000000;
            }
            </style>
        """, unsafe_allow_html=True)

    # Main content area
    st.title("Google Generative AI Chatbot")

    # Display chat history
    st.header("Chat History")
    for i, entry in enumerate(st.session_state['chat_history']):
        with st.expander(f"Conversation {i+1}", expanded=True):
            if 'image' in entry:
                st.write("User uploaded an image")
                st.image(entry['image'], caption="Uploaded Image", use_column_width=True)
                st.write(f"User prompt: {entry['user_input']}")
            else:
                st.markdown(f"**User:** {entry['user_input']}")
            st.markdown(f"**Model:** {entry['model_name']}")
            st.markdown(f"**Response:** {entry['response']}")
            st.write(f"Timestamp: {entry['timestamp']}")

    if st.button("Send"):
        model_name = config['model_mapping'][model_selection]
        previous_context = " ".join([entry['response'] for entry in st.session_state['chat_history']])

        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            try:
                response = fetch_response(user_input, model_name, image=image, previous_context=previous_context)
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
            else:
                st.session_state['chat_history'].append({
                    'user_input': user_input,
                    'model_name': model_selection,
                    'response': response,
                    'image': image,
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
        else:
            try:
                response = fetch_response(user_input, model_name, previous_context=previous_context)
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
            else:
                st.session_state['chat_history'].append({
                    'user_input': user_input,
                    'model_name': model_selection,
                    'response': response,
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })

        st.subheader("Output")
        st.markdown(markdown.markdown(response), unsafe_allow_html=True)

        # Clear user input after sending
        user_input = ""

    # Conversation management
    st.sidebar.header("Conversation Management")
    if st.sidebar.button("Clear Chat History"):
        st.session_state['chat_history'] = []

    if st.sidebar.button("Save Chat History"):
        chat_history_text = "\n".join([
            f"User: {entry['user_input']}\nModel: {entry['model_name']}\nResponse: {entry['response']}\nTimestamp: {entry['timestamp']}\n\n"
            for entry in st.session_state['chat_history']
        ])
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"chat_history_{timestamp}.txt"
        with open(filename, "w", encoding="utf-8") as file:
            file.write(chat_history_text)
        st.sidebar.success(f"Chat history saved as {filename}")

if __name__ == "__main__":
    main()
