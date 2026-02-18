import os
import speech_recognition as sr
import pyttsx3
import pyautogui
import requests
import json
import datetime
import time





# ================= CONFIG =================
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_URL = "https://openrouter.ai/api/v1/chat/completions"
recognizer = sr.Recognizer()

# ================= SPEAK =================
def speak(text):
    if not text:
        return

    try:
        engine = pyttsx3.init()
        engine.setProperty("rate", 160)
        engine.setProperty("volume", 1.0)

        engine.say(text)
        engine.runAndWait()
        engine.stop()

    except Exception as e:
        print("Speech Error:", e)

    time.sleep(0.5)


# ================= LISTEN =================
def listen():
    with sr.Microphone() as source:
        print("🎙 Listening...")
        recognizer.adjust_for_ambient_noise(source, duration=1)

        try:
            audio = recognizer.listen(
                source,
                timeout=5,
                phrase_time_limit=10
            )
        except sr.WaitTimeoutError:
            print("No speech detected...")
            return ""

    try:
        text = recognizer.recognize_google(audio, language="en-IN")
        print("You:", text)
        return text

    except sr.UnknownValueError:
        print("Could not understand audio")
        return ""

    except Exception as e:
        print("Recognition Error:", e)
        return ""


# ================= DEEPSEEK =================
def ask_ai(prompt):
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost",
        "X-Title": "Jarvis AI Assistant"
    }

    data = {
        "model": "openai/gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": "You are Jarvis, a helpful AI assistant."},
            {"role": "user", "content": prompt}
        ]
    }

    try:
        response = requests.post(DEEPSEEK_URL, headers=headers, json=data, timeout=20)

        print("Status Code:", response.status_code)
        result = response.json()

        answer = result["choices"][0]["message"]["content"]
        print("\n🧠 JARVIS:", answer, "\n")

        return answer


    except Exception as e:
        return f"AI error: {e}"

# ================= FILE SEARCH =================

def find_file(filename, search_path):
        for root, dirs, files in os.walk(search_path):
            for file in files:
                if filename.lower() in file.lower():
                    return os.path.join(root, file)
        return None


# ================= COMMANDS =================
def handle_command(command):
    command = command.lower()

    # 🔹 Time
    if "time" in command:
        current_time = datetime.datetime.now().strftime("%I:%M %p")
        speak(f"The time is {current_time}")

    # 🔹 Date
    elif "date" in command or "day" in command:
        today = datetime.datetime.now().strftime("%A, %d %B %Y")
        speak(f"Today is {today}")

    # 🔹 CLOSE APPLICATION  👈 ADDED HERE
    elif "close" in command:

        if "whatsapp" in command:
            os.system('taskkill /F /FI "WINDOWTITLE eq WhatsApp*"')
            speak("Closing WhatsApp")
            return

        apps = {
            "chrome": "chrome.exe",
            "notepad": "notepad.exe",
            "edge": "msedge.exe",
            "vscode": "Code.exe",
        }

        for key in apps:
            if key in command:
                os.system(f'taskkill /IM "{apps[key]}" /F')
                speak(f"Closing {key}")
                return

        speak("I cannot find that application to close")


    # 🔹 OPEN APPLICATION
    elif command.startswith("open"):
        app_name = command.replace("open", "").strip()

        apps = {
            "chrome": "chrome",
            "notepad": "notepad",
            "edge": "msedge",
            "calculator": "calc",
            "calc": "calc",
            "settings": "ms-settings:",
            "youtube": "https://youtube.com",
            "whatsapp": "whatsapp:",
            "vscode": "code",
            "vs code": "code",
            "file explorer": "explorer",
            "explorer": "explorer",
        }

        if app_name in apps:
            os.system(f"start {apps[app_name]}")
            speak(f"Opening {app_name}")
        else:
            speak("I don't know that application")

    # 🔹 Shutdown
    elif "shutdown" in command:
        speak("Shutting down system")
        os.system("shutdown /s /t 5")

    # 🔹 AI Fallback
    else:
        reply = ask_ai(command)
        speak(reply)


# ================= MAIN LOOP =================
WAKE_WORD = "jarvis"

speak("Jarvis is ready sir`")

while True:
    command = listen()

    if not command:
        continue

    command = command.lower()

    if WAKE_WORD in command:
        command = command.replace(WAKE_WORD, "").strip()

        if "exit" in command or "stop" in command:
            speak("Goodbye")
            break

        if command:
            handle_command(command)
        else:
            speak("Yes Sir")

