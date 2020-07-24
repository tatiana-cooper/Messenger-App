from datetime import datetime
import requests
from PyQt5 import QtWidgets, QtCore
import clientui


class MessengerApp(QtWidgets.QMainWindow, clientui.Ui_MainWindow):
    """
    This class represents Messenger's buttons functionality
    """
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.pushButton.pressed.connect(self.send_message)  # Connects the button with 'send_message' method

        # last_timestamp attribute stores the timestamp of the last loaded message
        self.last_timestamp = 0.0

        # Launches the timer which calls 'update_messages' method every 1000 milliseconds
        # in order to check the new messages on server
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_messages)
        self.timer.start(1000)

        # hides the chars in password field
        self.lineEdit_2.setEchoMode(QtWidgets.QLineEdit.Password)

    def send_message(self):
        """
        The method sends user's request to the server and handles incorrectly entered data.
        :return: None
        """
        username = self.lineEdit.text()
        password = self.lineEdit_2.text()
        text = self.textEdit.toPlainText()

        message = requests.get('http://127.0.0.1:5000/send_message', json={
            'username': username,
            'password': password,
            'text': text
        })

        # check response of the request (True or False)
        if not message.json()['OK']:
            self.textBrowser.append('')
            self.textBrowser.append("Your password is incorrect. Or you have empty field('s)")
            self.textBrowser.append('')
        self.textEdit.setText('')

    def update_messages(self):
        """
        This method loads and constantly (every 1000 milliseconds) updates messages
        on the screen (self.textBrowser Object).
        :return: None
        """

        # Request to the server with param self.last_timestamp, got response is the list of messages
        response = requests.get('http://127.0.0.1:5000/get_messages', params={'last_timestamp': self.last_timestamp})
        messages = response.json()['messages']

        for message in messages:

            # converts the Unix time to the GMT time standard
            dt = datetime.fromtimestamp(message['timestamp'])
            dt = dt.strftime('%H:%M:%S %d/%m/%Y')
            # Adding messages to the Messenger's screen
            self.textBrowser.append(dt + ' ' + message['username'])
            self.textBrowser.append(message['text'])
            self.textBrowser.append('')

            # self.last_timestamp == timestamp of the last message loaded to the screen (textBrowser Object)
            self.last_timestamp = message['timestamp']

# launch Messenger
app = QtWidgets.QApplication([])
window = MessengerApp()
window.show()
app.exec_()
