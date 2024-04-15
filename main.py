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
    with st.sidebar:
        st.header("Settings")
        model_selection = st.selectbox("Select Model", config['models'])
        tone_selection = st.selectbox("Select Tone", ["Default", "Formal", "Casual", "Friendly", "Technical"])

    # Main content area
    st.title("Google Generative AI Chatbot")

    # Chat container
    chat_container = st.container()

    # User input and file upload (sticky)
    user_input = st.text_input("Message Gemini...", key="user_input", placeholder="Type your message here...", disabled=False)
    uploaded_file = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"], key="uploaded_file")

    # Send button container
    send_button_container = st.container()
    with send_button_container:
        if st.button("Send", key="send_button"):
            model_name = config['model_mapping'][model_selection]
            previous_context = " ".join([entry['response'] for entry in st.session_state['chat_history']])
            tone = tone_selection.lower()

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
                        'tone': tone,
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
                        'tone': tone,
                        'response': response,
                        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    })

            # Clear user input after sending
            user_input = ""

    # Display chat history
    with chat_container:
        for i, entry in enumerate(st.session_state['chat_history']):
            with st.container():
                cols = st.columns([1, 10])
                with cols[0]:
                    st.image("https://cdn-icons-png.flaticon.com/512/3135/3135786.png", width=48)
                with cols[1]:
                    st.markdown(f"**You:** {entry['user_input']}")

                cols = st.columns([1, 10])
                with cols[0]:
                    st.image("https://cdn-icons-png.flaticon.com/512/3103/3103453.png", width=48)
                with cols[1]:
                    st.markdown(f"**Gemini:** {entry['response']}")

    # Disclaimer
    st.markdown("ChatGPT can make mistakes. Consider checking important information. Read our Terms and Privacy Policy.", unsafe_allow_html=True)

    # Conversation management
    with st.sidebar:
        st.header("Conversation Management")
        if st.button("Clear Chat History"):
            st.session_state['chat_history'] = []

        if st.button("Save Chat History"):
            chat_history_text = "\n".join([
                f"User: {entry['user_input']}\nModel: {entry['model_name']}\nTone: {entry['tone']}\nResponse: {entry['response']}\nTimestamp: {entry['timestamp']}\n\n"
                for entry in st.session_state['chat_history']
            ])
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"chat_history_{timestamp}.txt"
            with open(filename, "w", encoding="utf-8") as file:
                file.write(chat_history_text)
            st.success(f"Chat history saved as {filename}")

        if st.button("Download Chat History as PDF"):
            chat_history_html = "\n".join([
                f"\nUser: {entry['user_input']}\n\nModel: {entry['model_name']}\n\nTone: {entry['tone']}\n\nResponse: {entry['response']}\n\nTimestamp: {entry['timestamp']}\n"
                for entry in st.session_state['chat_history']
            ])
            pdf_file = st.components.v1.html2pdf(chat_history_html, css=".pdf{font-family:Arial;}")
            st.download_button(
                label="Download Chat History as PDF",
                data=pdf_file,
                file_name="chat_history.pdf",
                mime="application/pdf",
            )

if __name__ == "__main__":
    main()
