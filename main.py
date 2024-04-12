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
    st.set_page_config(page_title="Premium Chatbot", page_icon="🤖", layout="wide")

    # Set custom CSS styles
    st.markdown("""
        <style>
            .chat-container {
                background-color: #f2f2f2;
                border-radius: 10px;
                box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            }
            .chat-header {
                background-color: #333;
                color: #fff;
                padding: 10px 20px;
                border-top-left-radius: 10px;
                border-top-right-radius: 10px;
                font-weight: bold;
                font-size: 18px;
            }
            .chat-history {
                max-height: 500px;
                overflow-y: auto;
                padding: 20px;
            }
            .chat-input {
                margin-top: 20px;
                display: flex;
                align-items: center;
                padding: 10px;
                background-color: #fff;
                border-top: 1px solid #ccc;
            }
            .chat-input input[type="text"] {
                flex-grow: 1;
                padding: 10px;
                border: none;
                border-radius: 5px;
                font-size: 16px;
                box-shadow: 0 0 5px rgba(0, 0, 0, 0.1);
            }
            .chat-input button {
                margin-left: 10px;
                padding: 10px 20px;
                background-color: #333;
                color: #fff;
                border: none;
                border-radius: 5px;
                font-size: 16px;
                cursor: pointer;
                transition: background-color 0.3s ease;
            }
            .chat-input button:hover {
                background-color: #555;
            }
        </style>
    """, unsafe_allow_html=True)

    st.title("Premium Chatbot 🤖")

    cols = st.columns([1, 3, 1])

    with cols[1]:
        with st.container(class_="chat-container"):
            st.subheader("Chat History", class_="chat-header")
            with st.container(class_="chat-history"):
                for i, entry in enumerate(st.session_state['chat_history']):
                    with st.expander(f"Conversation {i+1}", expanded=True):
                        if 'image' in entry:
                            st.write("User uploaded an image")
                            st.image(entry['image'], caption="Uploaded Image", use_column_width=True)
                            st.write(f"**User:** {entry['user_input']}")
                        else:
                            st.markdown(f"**User:** {entry['user_input']}")
                        st.markdown(f"**Model:** {entry['model_name']}")
                        st.markdown(f"**Response:** {entry['response']}")
                        st.write(f"Timestamp: {entry['timestamp']}")

    with cols[0]:
        st.sidebar.header("Input")
        user_input = st.sidebar.text_area("Enter your message here:")
        uploaded_file = st.sidebar.file_uploader("Upload an image", type=["png", "jpg", "jpeg"])
        model_selection = st.sidebar.selectbox("Select Model", config['models'])

        response = ""  # Initialize response variable

        with st.sidebar.container(class_="chat-input"):
            if st.button("Send"):
                model_name = config['model_mapping'][model_selection]
                if uploaded_file is not None:
                    image = Image.open(uploaded_file)
                    response = fetch_response(user_input, model_name, image=image)
                    st.session_state['chat_history'].append({
                        'user_input': user_input,
                        'model_name': model_selection,
                        'response': response,
                        'image': image,
                        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    })
                else:
                    response = fetch_response(user_input, model_name)
                    st.session_state['chat_history'].append({
                        'user_input': user_input,
                        'model_name': model_selection,
                        'response': response,
                        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    })

            if st.button("Clear History"):
                st.session_state['chat_history'] = []

    with cols[2]:
        st.sidebar.header("Output")
        st.markdown(markdown.markdown(response), unsafe_allow_html=True)

if __name__ == "__main__":
    main()
