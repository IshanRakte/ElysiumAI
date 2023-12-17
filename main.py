import speech_recognition as sr
import pyttsx3
import os
import webbrowser
import openai
import asyncio
from datetime import datetime, timedelta
from telegram import Bot
from telegram.helpers import escape_markdown
from google_auth_oauthlib.flow import InstalledAppFlow
import googleapiclient.discovery
from dateutil import parser
import threading

api_key = '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'
telegram_token = '6723957326:AAFby6ENH9QYHGhdjOvKGBk3PC0eMiQMjDY'
telegram_chat_id = '-4077193516'

SCOPES = ['https://www.googleapis.com/auth/calendar.events']


def get_google_calendar_service():
    flow = InstalledAppFlow.from_client_secrets_file(
        'client_secret_546479796583-hqkn2k7t4e08hiq0johqt284s794oq97.apps.googleusercontent.com.json', SCOPES)
    creds = flow.run_local_server(port=0)
    service = googleapiclient.discovery.build('calendar', 'v3', credentials=creds)
    return service


def generate_meeting_invite(agenda, time, duration, venue, name, date):
    prompt = f"Generate a well-structured meeting invitation for a discussion about **{agenda}**. The meeting is scheduled on **{date}** at **{time}** for **{duration}** hours at **{venue}**. You are the organizer, and your name is **{name}**. Include important details such as the subject, introduction, meeting details, and closing. Make it formal and informative. Emphasize key information using markdown-like formatting."
    response = openai.Completion.create(
        engine="text-davinci-003",  # text-davinci engine for better performance
        prompt=prompt,
        max_tokens=500,  # Adjust the max_tokens value based on the desired response length
        api_key=api_key
    )

    assistant_response = response['choices'][0]['text']

    # Parse user-provided date and time
    parsed_date = parser.parse(date)
    parsed_time = parser.parse(time).time()

    combined_datetime = datetime.combine(parsed_date, parsed_time)

    duration_timedelta = timedelta(hours=float(duration))

    end_datetime = combined_datetime + duration_timedelta

    # Create Google Calendar event
    try:
        service = get_google_calendar_service()
        calendar_id = '91b974b8b947d533c5523a1fae1167a3995e9121ae42b8d18877a439014729e5@group.calendar.google.com'
        event = {
            'summary': f'Meeting: {agenda}',
            'location': venue,
            'description': f'Agenda: {agenda}\nOrganizer: {name}',
            'start': {
                'dateTime': combined_datetime.strftime('%Y-%m-%dT%H:%M:%S'),
                'timeZone': 'Asia/Kolkata',
            },
            'end': {
                'dateTime': end_datetime.strftime('%Y-%m-%dT%H:%M:%S'),
                'timeZone': 'Asia/Kolkata',
            },
        }
        event = service.events().insert(calendarId=calendar_id, body=event).execute()
        print('Event created: %s' % (event.get('htmlLink')))
    except Exception as e:
        print(f"Error creating event: {e}")

    return assistant_response, combined_datetime


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


# Function to cancel the meeting
def cancel_meeting(agenda, start_datetime):
    cancel_message = f"The meeting '{agenda}' scheduled for {start_datetime} has been cancelled."
    asyncio.run(send_telegram_message(cancel_message, telegram_token, telegram_chat_id))


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

        elif "generate meeting invite" in query.lower():
            speak("Sure, let's create a meeting invite.")

            name = "Ishan"
            duration = "1"
            speak("What's the meeting date.")
            date = takecommand()
            speak("What's the meeting agenda.")
            agenda = takecommand()
            speak("What's the meeting time.")
            time = takecommand()
            # speak("What's the meeting duration.")
            # duration = takecommand()
            speak("What's the meeting venue.")
            venue = takecommand()

            meeting_invite, start_datetime = generate_meeting_invite(agenda, time, duration, venue, name, date)
            print(meeting_invite)
            schedule_reminders(start_datetime, agenda)
            speak(meeting_invite)

            asyncio.run(send_telegram_message(meeting_invite, telegram_token, telegram_chat_id))

        elif "cancel meeting" in query.lower():
            cancel_meeting(agenda, start_datetime)
