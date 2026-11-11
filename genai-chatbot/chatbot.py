
import os
from pathlib import Path
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Load API key
load_dotenv(Path(__file__).with_name(".env"))

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("API key not found. Check your .env file.")
    raise SystemExit

# Connect to Gemini
client = genai.Client(api_key=api_key)

# Store conversation history
history = []

print("Welcome to Nikhil's GenAI Chatbot!")
print("Model: Gemini 3.5 Flash Lite")
print("Conversation memory: Enabled")
print("Type 'exit' to stop.\n")

while True:
    question = input("You: ").strip()

    if question.lower() == "exit":
        print("Goodbye!")
        break

    if not question:
        continue

    try:
        # Add user message to history
        history.append(
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=question)]
            )
        )

        print("Gemini is thinking...")

        response = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=history,
            config=types.GenerateContentConfig(
                http_options=types.HttpOptions(timeout=60000)
            )
        )

        answer = response.text or "Sorry, I couldn't generate a response."

        print("\nGemini:", answer, "\n")

        # Save Gemini response for conversation memory
        history.append(
            types.Content(
                role="model",
                parts=[types.Part.from_text(text=answer)]
            )
        )

    except Exception as error:
        print("\nSomething went wrong:", error, "\n")

        # Remove unanswered user message
        if history and history[-1].role == "user":
            history.pop()
