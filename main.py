import speech_recognition as sr
import pyttsx3
import os
import webbrowser

def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()


def takecommand():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        r.pause_threshold = 1
        audio = r.listen(source)
        try:
            print("Recognizing...")
            query = r.recognize_google(audio, language="en-in")
            print(f"User said: {query}")
            return query
        except Exception as e:
            return "Some Error Occurred. Sorry from Elysium"

if __name__ == '__main__':
    print('Welcome to Elysium AI')
    speak("Elysium AI")
    while True:
        print("Listening...")
        query = takecommand()
        sites = [["youtube", "https://www.youtube.com"], ["wikipedia", "https://www.wikipedia.com"],
                 ["google", "https://www.google.com"], ]
        for site in sites:
            if f"Open {site[0]}".lower() in query.lower():
                speak(f"Opening {site[0]}")
                webbrowser.open(site[1])

        if "open music" in query:
            musicPath = "C:/Users/Ishan/Downloads/downfall.mp3"
            os.system(f"start {musicPath}")

        elif "the time" in query:
            hour = datetime.datetime.now().strftime("%H")
            minutes = datetime.datetime.now().strftime("%M")
            speak(f"Sir the time is {hour} and {minutes} minutes")

        elif "open camera".lower() in query.lower():
            os.system("start microsoft.windows.camera:")