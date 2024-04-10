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

# Initialize session state for chat history and current conversation
if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = {}  # Store conversations by session ID
if 'current_conversation_id' not in st.session_state:
    st.session_state['current_conversation_id'] = None

def fetch_response(user_input, model_name, conversation_id, image=None):
    # Configure the API with your key
    genai.configure(api_key=os.environ.get('GOOGLE_API'))
    model = genai.GenerativeModel(model_name)

    # Pass conversation ID to maintain context
    if conversation_id:
        response = model.generate_content([user_input, image], conversation_id=conversation_id)
    else:
        response = model.generate_content([user_input, image])
        conversation_id = response.conversation_id  # Store new conversation ID

    return response.text, conversation_id

def main():
    st.set_page_config(
        page_title="Google Generative AI Chatbot",
        page_icon=":robot_face:",
        layout="wide"  # Use wide layout for better mobile responsiveness
    )

    st.title("Google Generative AI Chatbot")

    # Sidebar for user input and model selection
    with st.sidebar:
        user_input = st.text_area("Enter your message here:")
        uploaded_file = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"])
        model_selection = st.selectbox("Select Model", config['models'])

    # Manage conversations
    if st.session_state['current_conversation_id'] is None:
        st.session_state['current_conversation_id'] = str(datetime.now().timestamp())
        st.session_state['chat_history'][st.session_state['current_conversation_id']] = []

    # Display chat history for the current conversation
    st.header("Chat History")
    for entry in st.session_state['chat_history'][st.session_state['current_conversation_id']]:
        if 'image' in entry:
            st.write("User uploaded an image")
            st.image(entry['image'], caption="Uploaded Image", use_column_width=True)
            st.write(f"User prompt: {entry['user_input']}")
        else:
            st.markdown(f"**User:** {entry['user_input']}")
        st.markdown(f"**Model:** {entry['model_name']}")
        st.markdown(f"**Response:** {entry['response']}")

    # Send message and get response
    if st.button("Send"):
        model_name = config['model_mapping'][model_selection]
        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            response, conversation_id = fetch_response(user_input, model_name, st.session_state['current_conversation_id'], image=image)
            st.session_state['chat_history'][st.session_state['current_conversation_id']].append({
                'user_input': user_input,
                'model_name': model_selection,
                'response': response,
                'image': image,
            })
        else:
            response, conversation_id = fetch_response(user_input, model_name, st.session_state['current_conversation_id'])
            st.session_state['chat_history'][st.session_state['current_conversation_id']].append({
                'user_input': user_input,
                'model_name': model_selection,
                'response': response,
            })

        st.session_state['current_conversation_id'] = conversation_id
        st.subheader("Output")
        st.markdown(markdown.markdown(response), unsafe_allow_html=True)

if __name__ == "__main__":
    main()
