import speech_recognition as sr
import pyttsx3
import os
import webbrowser
import openai
import asyncio
from datetime import datetime, timedelta


api_key = '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'

def generate_meeting_invite(agenda, time, duration, venue, name, date):
    prompt = f"Generate a well-structured meeting invitation for a discussion about **{agenda}**. The meeting is scheduled on **{date}** at **{time}** for **{duration}** hours at **{venue}**. You are the organizer, and your name is **{name}**. Include important details such as the subject, introduction, meeting details, and closing. Make it formal and informative. Emphasize key information using markdown-like formatting."
    response = openai.Completion.create(
        engine="text-davinci-003",  #text-davinci engine for better performance
        prompt=prompt,
        max_tokens=500,  # Adjust the max_tokens value based on the desired response length
        api_key=api_key
    )

    assistant_response = response['choices'][0]['text']

    return assistant_response


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
    print('Welcome to Jarvis AI')
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

        elif "generate meeting invite" in query.lower():
            speak("Sure, let's create a meeting invite.")

            speak("What's the meeting date.")
            date = takecommand()
            speak("What's the meeting agenda.")
            agenda = takecommand()
            speak("What's the meeting time.")
            time = takecommand()
            speak("What's the meeting duration.")
            duration = takecommand()
            speak("What's the meeting venue.")
            venue = takecommand()

            meeting_invite = generate_meeting_invite(agenda, time, duration, venue, name, date)
            print(meeting_invite)