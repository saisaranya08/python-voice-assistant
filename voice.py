import speech_recognition as sr
import pyttsx3
import nltk
from nltk.tokenize import word_tokenize
import requests
import datetime
import webbrowser
import wikipedia
import threading
import dateparser
import pywhatkit as kit
import asyncio

# Initializing the speech recognition
recognizer = sr.Recognizer()

# Adjusting for ambient noise
with sr.Microphone() as source:
    recognizer.adjust_for_ambient_noise(source)
    print("Adjusted microphone for ambient noise.")

# Initializing text-to-speech engine
engine = pyttsx3.init()

# Function to listen and recognize speech with timeout
async def recognize_speech():
    with sr.Microphone() as source:
        print("Listening...")
        try:
            audio = recognizer.listen(source, timeout=3)  # Timeout is set to 3 seconds
            text = recognizer.recognize_google(audio)
            print(f"Recognized: {text}")
            return text
        except sr.UnknownValueError:
            print("Sorry, I did not understand that.")
            return ""
        except sr.RequestError:
            print("Request Error. Check your internet connection.")
            return ""

# Function to convert text to speech
def speak(text):
    engine.say(text)
    engine.runAndWait()

speak("Hello, I am your Python voice assistant. How can I help you?")

# Function to process the text using NLP
def process_text(text):
    tokens = word_tokenize(text)
    return tokens

# Function to get weather information
def get_weather(city):
    api_key = "64c1b521cbcb1af9806ea8b35d4890a6" 
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    try:
        response = requests.get(url, timeout=10)  # Timeout is set to 10 seconds
        data = response.json()
        if data.get("cod") != "404":
            main = data.get("main", {})
            weather = data.get("weather", [{}])[0]
            temperature = main.get("temp", "N/A")
            weather_description = weather.get("description", "N/A")
            weather_report = f"The temperature in {city} is {temperature}°C with {weather_description}."
            return weather_report
        else:
            return f"City '{city}' not found. Please try again."
    except requests.Timeout:
        return "Request to weather API timed out. Please try again later."
    except requests.RequestException as e:
        return f"Error fetching weather: {str(e)}"

async def answer_general_knowledge(question):
    try:
        summary = wikipedia.summary(question, sentences=2)
        speak(summary)
        return summary
    except wikipedia.exceptions.DisambiguationError as e:
        options = e.options[:5]
        response = f"Your question is ambiguous. Did you mean: {', '.join(options)}?"
        speak(response)
        return response
    except wikipedia.exceptions.PageError:
        response = "Sorry, I couldn't find any information on that topic."
        speak(response)
        return response
    except Exception as e:
        response = f"An error occurred: {str(e)}"
        speak(response)
        return response

def play_music_or_podcast():
    speak("Opening your music streaming service.")
    webbrowser.open("https://www.spotify.com")
    return "Playing music or podcasts."
def play_song(song):
    try:
        speak(f"Playing {song} on YouTube.")
        kit.playonyt(song)
        return f"Playing {song}."
    except Exception as e:
        return f"An error occurred: {str(e)}"

reminders = []

def set_reminder(reminder_text, reminder_time):
    reminder_time = dateparser.parse(reminder_time)
    if not reminder_time:
        return "Sorry, I couldn't understand the time format."
    now = datetime.datetime.now()
    delay = (reminder_time - now).total_seconds()
    if delay <= 0:
        return "The specified time is in the past. Please try again."
    reminder = threading.Timer(delay, remind, [reminder_text])
    reminder.start()
    reminders.append(reminder)
    return f"Reminder set for {reminder_time.strftime('%H:%M')}."

def remind(reminder_text):
    speak(f"Reminder: {reminder_text}")

# Function to perform tasks based on recognized commands
async def perform_task(command):
    command_text = " ".join(command).lower()
    if "weather" in command_text:
        speak("Please say the city name.")
        city = await recognize_speech()
        if city:
            weather_report = get_weather(city)
            speak(weather_report)
            return weather_report
        else:
            return "Sorry, I didn't get the city name."
    elif "time" in command_text:
        now = datetime.datetime.now()
        time_report = f"The current time is {now.strftime('%H:%M')}"
        speak(time_report)
        return time_report
    elif "open youtube" in command_text:
        webbrowser.open("https://www.youtube.com")
        return "Opening YouTube."
    elif "play music" in command_text or "play podcast" in command_text:
        return play_music_or_podcast()
    elif "play song" in command_text:
        speak("Please say the song name.")
        song = await recognize_speech()
        if song:
            return play_song(song)
        else:
            return "Sorry, I didn't get the song name."
    elif "reminder" in command_text or "alarm" in command_text:
        speak("What do you want to be reminded about?")
        reminder_text = await recognize_speech()
        speak("At what time? Please say the time.")
        reminder_time = await recognize_speech()
        return set_reminder(reminder_text, reminder_time)
    elif "question" in command_text:
        speak("What do you want to know?")
        question = await recognize_speech()
        return await answer_general_knowledge(question)
    else:
        speak("I'm sorry, I can't do that yet.")
        return "I'm sorry, I can't do that yet."

# Main function to run the assistant
async def main():
    print("Voice Assistant is running...")
    while True:
        command = await recognize_speech()
        if command:
            tokens = process_text(command)
            result = await perform_task(tokens)
            print(f"Assistant: {result}")

if __name__ == "__main__":
    nltk.download('punkt')
    asyncio.run(main())