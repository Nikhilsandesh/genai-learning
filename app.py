
import os
import streamlit as st
from pathlib import Path
from dotenv import load_dotenv
from google import genai

# Load API key from local .env file
load_dotenv(Path(__file__).parent / "genai-chatbot" / ".env")

# Get API key from Streamlit Cloud Secrets or local environment
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    api_key = os.getenv("GEMINI_API_KEY")

# Website configuration
st.set_page_config(
    page_title="Nikhil's AI Chatbot",
    page_icon="🤖",
    layout="centered"
)

# Website branding
st.title("🤖 Nikhil's AI Chatbot")
st.caption("Your Personal AI Assistant")

# Check API key
if not api_key:
    st.error("API key not found. Please check your configuration.")
    st.stop()

# Initialize AI client
client = genai.Client(api_key=api_key)

# Initialize conversation memory
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
question = st.chat_input("Ask me anything...")

if question:
    # Display user message
    st.session_state.messages.append(
        {"role": "user", "content": question}
    )

    with st.chat_message("user"):
        st.markdown(question)

    # Generate AI response
    with st.chat_message("assistant"):
        with st.spinner("Nikhil's AI is thinking..."):
            try:
                history = []

                for message in st.session_state.messages[:-1]:
                    role = (
                        "user"
                        if message["role"] == "user"
                        else "model"
                    )

                    history.append({
                        "role": role,
                        "parts": [{"text": message["content"]}]
                    })

                history.append({
                    "role": "user",
                    "parts": [{"text": question}]
                })

                response = client.models.generate_content(
                    model="gemini-3.5-flash-lite",
                    contents=history
                )

                answer = response.text or "No response received."

                st.markdown(answer)

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer
                })

            except Exception as error:
                st.error(f"Something went wrong: {error}")
                st.session_state.messages.pop()
