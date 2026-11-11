
import os
import re
import requests
import streamlit as st
from pathlib import Path
from dotenv import load_dotenv
from google import genai

# Load API key
load_dotenv(Path(__file__).parent / "genai-chatbot" / ".env")

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

st.title("🤖 Nikhil's AI Chatbot")
st.caption("Your Personal AI Assistant")

if not api_key:
    st.error("API key not found. Check your configuration.")
    st.stop()

client = genai.Client(api_key=api_key)

# Conversation memory
if "messages" not in st.session_state:
    st.session_state.messages = []


# Weather condition descriptions
def weather_description(code):
    descriptions = {
        0: "Clear sky",
        1: "Mainly clear",
        2: "Partly cloudy",
        3: "Overcast",
        45: "Fog",
        48: "Depositing rime fog",
        51: "Light drizzle",
        53: "Moderate drizzle",
        55: "Dense drizzle",
        61: "Slight rain",
        63: "Moderate rain",
        65: "Heavy rain",
        71: "Slight snowfall",
        73: "Moderate snowfall",
        75: "Heavy snowfall",
        80: "Rain showers",
        81: "Moderate rain showers",
        82: "Violent rain showers",
        95: "Thunderstorm",
        96: "Thunderstorm with hail",
        99: "Thunderstorm with heavy hail"
    }
    return descriptions.get(code, "Unknown conditions")


# Get weather data for a city
def get_weather(city, forecast=False):
    # Find city coordinates
    geo_url = "https://geocoding-api.open-meteo.com/v1/search"

    geo_response = requests.get(
        geo_url,
        params={"name": city, "count": 1, "language": "en", "format": "json"},
        timeout=15
    )
    geo_response.raise_for_status()

    locations = geo_response.json().get("results", [])

    if not locations:
        return f"I couldn't find the location '{city}'. Please try another city."

    place = locations[0]
    latitude = place["latitude"]
    longitude = place["longitude"]
    place_name = place["name"]
    country = place.get("country", "")

    # Fetch current weather
    weather_url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": (
            "temperature_2m,relative_humidity_2m,"
            "apparent_temperature,precipitation,"
            "weather_code,wind_speed_10m"
        ),
        "timezone": "auto"
    }

    if forecast:
        params["daily"] = (
            "weather_code,temperature_2m_max,"
            "temperature_2m_min,precipitation_probability_max"
        )
        params["forecast_days"] = 3

    weather_response = requests.get(
        weather_url,
        params=params,
        timeout=15
    )
    weather_response.raise_for_status()

    data = weather_response.json()
    current = data["current"]

    result = f"""
## 🌤️ Weather in {place_name}, {country}

**Current conditions:** {weather_description(current['weather_code'])}

- 🌡️ Temperature: {current['temperature_2m']}°C
- 🌡️ Feels like: {current['apparent_temperature']}°C
- 💧 Humidity: {current['relative_humidity_2m']}%
- 🌧️ Precipitation: {current['precipitation']} mm
- 💨 Wind speed: {current['wind_speed_10m']} km/h

*Weather data time: {current['time']}*
"""

    if forecast:
        daily = data["daily"]
        result += "\n### 📅 3-Day Forecast\n"

        for i, date in enumerate(daily["time"]):
            condition = weather_description(daily["weather_code"][i])

            result += (
                f"\n**{date}** — {condition}\n"
                f"- Maximum: {daily['temperature_2m_max'][i]}°C\n"
                f"- Minimum: {daily['temperature_2m_min'][i]}°C\n"
                f"- Rain probability: "
                f"{daily['precipitation_probability_max'][i]}%\n"
            )

    result += "\n*Weather information provided by Open-Meteo.*"
    return result


# Display previous messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# Chat input
question = st.chat_input("Ask me anything...")

if question:
    st.session_state.messages.append(
        {"role": "user", "content": question}
    )

    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        try:
            # Detect weather-related questions
            weather_question = re.search(
                r"\b(weather|temperature|forecast|rain|humidity|wind speed)\b",
                question,
                re.IGNORECASE
            )

            if weather_question:
                # Extract city after "in", "for", or "at"
                match = re.search(
                    r"\b(?:in|for|at)\s+(.+)",
                    question,
                    re.IGNORECASE
                )

                if not match:
                    answer = (
                        "Which city would you like the weather for? "
                        "For example: What's the weather in Hyderabad?"
                    )
                else:
                    city = match.group(1).strip(" ?.,!")

                    city = re.sub(
                        r"\b(today|tomorrow|now|currently|this week|"
                        r"next week|next 3 days|forecast|weather|"
                        r"temperature)\b",
                        "",
                        city,
                        flags=re.IGNORECASE
                    ).strip(" ?.,!")

                    if not city:
                        answer = "Please tell me the city name."
                    else:
                        forecast = bool(re.search(
                            r"\b(forecast|tomorrow|next 3 days|"
                            r"this week|next week)\b",
                            question,
                            re.IGNORECASE
                        ))

                        with st.spinner("Checking live weather..."):
                            answer = get_weather(city, forecast)

            else:
                # Normal AI conversation with memory
                with st.spinner("Nikhil's AI is thinking..."):
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
