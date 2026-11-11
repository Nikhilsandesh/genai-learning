
import os
from pathlib import Path
from dotenv import load_dotenv
from google import genai

# Load API key from the .env file
load_dotenv(Path(__file__).with_name(".env"))

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("API key not found. Please check your .env file.")
    raise SystemExit

# Connect to Gemini
client = genai.Client(api_key=api_key)

print("Welcome to Nikhil's GenAI Chatbot!")
print("Type 'exit' to stop the chatbot.")

# Chat loop
while True:
    question = input("\nYou: ")

    if question.lower() == "exit":
        print("Goodbye!")
        break

    try:
        response = client.models.generate_content(
            model="gemini-3.8-flash",
            contents=question
        )

        print("\nGemini:", response.text)

    except Exception as error:
        print("Something went wrong:", error)
