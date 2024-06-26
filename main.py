import streamlit as st
import google.generativeai as genai
import os
from PIL import Image
from datetime import datetime
import yaml
import markdown
import pdfkit
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load configuration from YAML file
with open('config.yaml', 'r') as file:
    config = yaml.safe_load(file)

# Initialize session state for chat history
if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []

def fetch_response(user_input, model_name, image=None, previous_context=None, tone="default"):
    # Configure the API with your key
    try:
        genai.configure(api_key=os.environ.get('GOOGLE_API'))
        model = genai.GenerativeModel(model_name)

        # Create prompt with tone adjustment (optional)
        if tone == "formal":
            prompt = f"Please provide a formal response to the following: {user_input}"
        elif tone == "casual":
            prompt = f"Respond casually to this: {user_input}"
        elif tone == "friendly":
            prompt = f"Be friendly and respond to this: {user_input}"
        elif tone == "technical":
            prompt = f"Provide a technical response to: {user_input}"
        else:
            prompt = user_input

        # Add previous context if available
        if previous_context:
            prompt = f"{previous_context} {prompt}"
            logging.info(f"Prompt with previous context: {prompt}")

        # Send request with image if provided
        if image:
            response = model.generate_content([{"text": prompt}, image])
        else:
            response = model.generate_content({"text": prompt})

        logging.info(f"API Response: {response.text}")
        return response.text
    except Exception as e:
        logging.error(f"Error fetching response: {str(e)}")
        return "An error occurred while processing your request. Please try again later."

def main():
    st.set_page_config(page_title="Gemini AI Assistant", page_icon=":robot_face:", layout="wide")

    # Sidebar components
    with st.sidebar:
        st.header("Settings")
        model_selection = st.selectbox("Select Model", config['models'], help="Choose the model you want to use.")
        tone_selection = st.radio("Select Tone", ["Default", "Formal", "Casual", "Friendly", "Technical"], help="Choose the tone of the conversation.")

    # Main content area
    st.title("Gemini AI Assistant")
    st.write("Welcome to Gemini, your AI companion! You can chat with me, ask questions, or provide images for analysis.")

    # Chat container
    chat_container = st.container()

    # User input and file upload (sticky)
    user_input = st.text_area("Message Gemini...", key="user_input", placeholder="Type your message here...", height=100)
    uploaded_file = st.file_uploader("Upload an image (optional)", type=["png", "jpg", "jpeg"], key="uploaded_file", help="You can upload an image for Gemini to analyze.")

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
                    response = fetch_response(user_input, model_name, image=image, previous_context=previous_context, tone=tone)
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
                    response = fetch_response(user_input, model_name, previous_context=previous_context, tone=tone)
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

                if 'image' in entry:
                    st.image(entry['image'], caption="Uploaded Image", use_column_width=True)

    # Disclaimer
    st.markdown("**Disclaimer:** Gemini can make mistakes. Consider verifying important information from reliable sources.", unsafe_allow_html=True)

    # Conversation management
    with st.sidebar:
        st.header("Conversation Management")
        if st.button("Clear Chat History"):
            st.session_state['chat_history'] = []

        if st.button("Save Chat History as Text"):
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
            try:
                chat_history_html = "\n".join([
                    f"\n<p><strong>User:</strong> {entry['user_input']}</p>\n\n<p><strong>Model:</strong> {entry['model_name']}</p>\n\n<p><strong>Tone:</strong> {entry['tone']}</p>\n\n<p><strong>Response:</strong> {entry['response']}</p>\n\n<p><strong>Timestamp:</strong> {entry['timestamp']}</p>\n"
                    for entry in st.session_state['chat_history']
                ])
                pdf_file = pdfkit.from_string(chat_history_html, False)
                st.download_button(
                    label="Download Chat History as PDF",
                    data=pdf_file,
                    file_name="chat_history.pdf",
                    mime="application/pdf",
                )
            except Exception as e:
                st.error(f"Error generating PDF: {str(e)}")

if __name__ == "__main__":
    main()
