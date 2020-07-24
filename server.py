from datetime import datetime
from flask import Flask, request
import time
import requests

# creating Flask app
app = Flask(__name__)
server_start = datetime.now().strftime('%H:%M:%S %d/%m/%Y')

# list of the starting and future user's messages
messages = [
    {'username': 'Jack', 'text': 'Hello, everyone!', 'timestamp': time.time()},
    {'username': 'Jack2', 'text': 'Hello, Jack!', 'timestamp': time.time()},
]

# list of starting and future usernames and passwords
users = {
    'Jack': '123',
    'Jack2': '123',
    'WeatherBot': '123'
}


@app.route('/')
def hello():
    """ Returns the main page text and link to the Messenger status page."""
    return 'Hello, User! This is a status of Messenger: <a href="/status">status</a>'


@app.route('/status')
def status():
    """ Page shows the status of Messenger. """
    return {
        'status': 'OK',
        "name": 'Messenger',
        'server_start_time': server_start,
        'server_current_time': datetime.now().strftime('%H:%M:%S %d/%m/%Y'),
        'current_time_seconds': time.time(),  # the Unix time
        'amount_of_users': len(users),
        'amount_of_messages': len(messages)
    }


@app.route('/send_message')
def send_message():
    """
    From GET request this function receives the ['username'], ['password'] and ['text'] and stores this information.
    Also, checks if input data isn't empty, and if the password is entered correctly.

    WeatherBot: If user's message starts with '/weather' it will be the command for this Bot to start
    searching weather in location entered after the command, using 'api.openweathermap.org'.

    :return: status of request ({'OK': True} or {'OK': False})
    """

    username = request.json['username']
    password = request.json['password']
    text = request.json['text']

    # Check if input data is valid
    if username == '' or password == '' or text == '':
        return {'OK': False}

    # Check if entered username and password exist, if not - create them and add to the list of usernames
    if username in users:
        if users[username] != password:
            return {'OK': False}
    else:
        users[username] = password

    messages.append({'username': username, 'text': text, 'timestamp': time.time()})

    # This if-statement handles and processes Bot request
    if text.startswith('/weather'):
        api_key = 'YOUR-PRIVATE-API-KEY'  # private api_key, got from "http://api.openweathermap.org/"
        location = text[text.find(' '):]
        try:
            response = requests.get("http://api.openweathermap.org/data/2.5/weather",
                                    params={'units': 'metric', 'q': location, 'APPID': api_key})
            data = response.json()
            current_temperature = data['main']["temp"]
            current_pressure = data['main']["pressure"]
            current_humidity = data['main']["humidity"]
            weather_description = data["weather"][0]["description"]

            text = f'Entered city name : {location}\nTemperature (in Celsius) = {current_temperature}\n' \
                   f'Atmospheric pressure (in hPa unit) = {current_pressure}\n' \
                   f'Humidity = {current_humidity}%\n' \
                   f'Description = {weather_description}\n'

        except KeyError:
            text = 'No information about your location. Try again.'

        # Appends the answer from Bot to the list of messages
        messages.append({'username': 'WeatherBot', 'text': text, 'timestamp': time.time()})

    return {'OK': True}


@app.route('/get_messages')
def get_messages():
    """
    From GET request this function receives messages, and get the last_timestamp parameter (described below).
    :return: list of messages.
    """

    # In order to constantly not reload all the messages for users, the last_timestamp parameter is created.
    # The last_timestamp parameter stores the timestamp of the last loaded message. Initially last_timestamp == 0.0.
    last_timestamp = float(request.args['last_timestamp'])

    # get all messages after the time stored in last_timestamp parameter
    new_messages = []
    for message in messages:
        if message['timestamp'] > last_timestamp:
            new_messages.append(message)

    return {
        'messages': new_messages
    }


if __name__ == '__main__':
    # Launch server
    app.run()
