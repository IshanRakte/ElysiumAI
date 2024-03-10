import speech_recognition as sr
import pyttsx3
import os
import webbrowser
import openai
import asyncio
from datetime import datetime, timedelta
import asyncio
from telegram import Bot
from telegram.helpers import escape_markdown

api_key = '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'
telegram_token = '6723957326:AAFby6ENH9QYHGhdjOvKGBk3PC0eMiQMjDY'
telegram_chat_id = '-4077193516'


def generate_meeting_invite(agenda, time, duration, venue, name, date):
    prompt = f"Generate a well-structured meeting invitation for a discussion about **{agenda}**. The meeting is scheduled on **{date}** at **{time}** for **{duration}** hours at **{venue}**. You are the organizer, and your name is **{name}**. Include important details such as the subject, introduction, meeting details, and closing. Make it formal and informative. Emphasize key information using markdown-like formatting."
    response = openai.Completion.create(
        engine="text-davinci-003",  # text-davinci engine for better performance
        prompt=prompt,
        max_tokens=500,  # Adjust the max_tokens value based on the desired response length
        api_key=api_key
    )

    assistant_response = response['choices'][0]['text']

    return assistant_response


async def send_telegram_message(message, token, chat_id):
    bot = Bot(token=token)
    parse_mode = 'MarkdownV2'
    escaped_message = escape_markdown(message, version=2)
    await bot.send_message(chat_id=chat_id, text=escaped_message, parse_mode=parse_mode)


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


# Function to send reminders
def send_reminder(agenda, timing):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    async def _send_reminder():
        reminder_message = f"Reminder: Meeting '{agenda}' will start in {timing}."
        await send_telegram_message(reminder_message, telegram_token, telegram_chat_id)

    loop.run_until_complete(_send_reminder())


# Modify the schedule_reminders function
def schedule_reminders(start_datetime, agenda):
    reminder_30min = start_datetime - timedelta(minutes=30)
    reminder_15min = start_datetime - timedelta(minutes=15)

    threading.Timer((reminder_30min - datetime.now()).total_seconds(), send_reminder,
                    args=(agenda, "30 minutes")).start()
    threading.Timer((reminder_15min - datetime.now()).total_seconds(), send_reminder,
                    args=(agenda, "15 minutes")).start()


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
            schedule_reminders(start_datetime, agenda)
            speak(meeting_invite)

            asyncio.run(send_telegram_message(meeting_invite, telegram_token, telegram_chat_id))