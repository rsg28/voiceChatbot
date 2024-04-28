import speech_recognition as sr
import pyttsx3
import openai
import keyboard
import threading
import os

# Initialize the recognizer and TTS engine
r = sr.Recognizer()
engine = pyttsx3.init()

# Set OpenAI API key
openai.api_key = os.getenv('OPENAI_API_KEY')

def speak_text(command):
    """Converts text to speech."""
    engine.say(command)
    engine.runAndWait()

def listen_for_stop_command(event):
    """Listens for the 'f' key press to signal to stop recording."""
    keyboard.wait('f')
    event.set()

def record_text():
    """Records audio on 'f' key press and stops recording on second 'f' key press."""
    with sr.Microphone() as source:
        print("Press 'f' to start recording...")
        keyboard.wait('f')  # Wait for 'f' key press to start recording
        print("Recording started... Press 'f' again to stop.")

        stop_event = threading.Event()
        threading.Thread(target=listen_for_stop_command, args=(stop_event,)).start()

        r.adjust_for_ambient_noise(source, duration=0.2)
        audio = r.listen(source, phrase_time_limit=20)  # Adjust time limit as needed

        if stop_event.is_set():
            print("Recording stopped.")
            try:
                text = r.recognize_google(audio)
                print("You said: " + text)
                return text
            except sr.RequestError as e:
                print(f"Could not request results; {e}")
                return None
            except sr.UnknownValueError:
                print("Unknown error occurred.")
                return None
        else:
            print("No stop key pressed.")
            return None

def chat_with_bot(user_input):
    """Sends user input to OpenAI's API and returns the AI's response."""
    messages = [{"role": "user", "content": user_input}]
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        max_tokens=100,
        temperature=0.5,
    )
    message = response.choices[0].message["content"]
    return message

if __name__ == "__main__":
    chat_with_bot("Act Like Jarvis from Iron Man")
    while True:
        user_input = record_text()
        if user_input and user_input.lower() in ["quit", "exit"]:
            break
        elif user_input:
            response = chat_with_bot(user_input)
            print("gpt:", response)
            speak_text(response)