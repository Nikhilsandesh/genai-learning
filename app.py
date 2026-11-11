
import os
import streamlit as st
from pathlib import Path
from dotenv import load_dotenv
from google import genai

# Load local API key from .env
load_dotenv(Path(__file__).parent / "genai-chatbot" / ".env")

# Get API key from Streamlit Cloud Secrets or local environment
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    api_key = os.getenv("GEMINI_API_KEY")

st.set_page_config(
    page_title="Nikhil's AI Chatbot",
    page_icon="🤖"
)

st.title("🤖 Nikhil's AI Chatbot")
st.caption("Powered by Google Gemini AI")

if not api_key:
    st.error("API key not found. Check your local .env file or Streamlit Cloud Secrets.")
    st.stop()

client = genai.Client(api_key=api_key)

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Get user input
question = st.chat_input("Ask me anything...")

if question:
    st.session_state.messages.append(
        {"role": "user", "content": question}
    )

    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Gemini is thinking..."):
            try:
                history = []

                for message in st.session_state.messages[:-1]:
                    role = "user" if message["role"] == "user" else "model"
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

                st.session_state.messages.append(
                    {"role": "assistant", "content": answer}
                )

            except Exception as error:
                st.error(f"Something went wrong: {error}")
                st.session_state.messages.pop()
