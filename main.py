import streamlit as st
import google.generativeai as genai
import os
from PIL import Image
from datetime import datetime
import yaml
import markdown
import base64
from io import BytesIO

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
    tone_selection = st.sidebar.selectbox("Select Tone", ["Default", "Formal", "Casual", "Friendly", "Technical"])

    # Main content area
    st.title("Google Generative AI Chatbot")

    # Display chat history
    st.header("Chat History")
    for i, entry in enumerate(st.session_state['chat_history']):
        with st.expander(f"Conversation {i+1}", expanded=True):
            cols = st.columns([1, 3])
            if 'image' in entry:
                with cols[0]:
                    st.image(entry['image'], caption="Uploaded Image", use_column_width=True)
                with cols[1]:
                    st.write(f"User prompt: {entry['user_input']}")
            else:
                with cols[1]:
                    st.markdown(f"**User:** {entry['user_input']}")
            with cols[1]:
                st.markdown(f"**Model:** {entry['model_name']}")
                st.markdown(f"**Tone:** {entry['tone']}")
                st.markdown(f"**Response:** {entry['response']}")
                st.write(f"Timestamp: {entry['timestamp']}")

    if st.button("Send"):
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
            f"User: {entry['user_input']}\nModel: {entry['model_name']}\nTone: {entry['tone']}\nResponse: {entry['response']}\nTimestamp: {entry['timestamp']}\n\n"
            for entry in st.session_state['chat_history']
        ])
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"chat_history_{timestamp}.txt"
        with open(filename, "w", encoding="utf-8") as file:
            file.write(chat_history_text)
        st.sidebar.success(f"Chat history saved as {filename}")

    if st.sidebar.button("Download Chat History as PDF"):
        chat_history_html = "\n".join([
            f"<p><strong>User:</strong> {entry['user_input']}</p>"
            f"<p><strong>Model:</strong> {entry['model_name']}</p>"
            f"<p><strong>Tone:</strong> {entry['tone']}</p>"
            f"<p><strong>Response:</strong> {entry['response']}</p>"
            f"<p><strong>Timestamp:</strong> {entry['timestamp']}</p><hr>"
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
