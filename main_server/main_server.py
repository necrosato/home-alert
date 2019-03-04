from flask import Flask, Response, request
import argparse
import json
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import datetime
import pytz

# This is where home alerts get sent
NOTIFY_EMAILS = ['sato@naookie.com']

class EndpointAction():
    '''
    action is expected to return a valid response
    '''
    def __init__(self, action):
        self.action = action


    def __call__(self, *args):
        return self.action()


class HomeAlert():
    '''
    Class holding a flask app and smtp server
    '''
    def __init__(self, smtp_info):
        self.smtp_info = smtp_info
        self.smtp_connect()
        self.app = Flask('Home Alert Main Server')
        self.front_door_lock = False

    def smtp_connect(self):
        '''
        Opens/refreshes an smtp connection
        '''
        self.smtp = smtplib.SMTP(host=self.smtp_info['smtp_host'], port=self.smtp_info['smtp_port'])
        self.smtp.starttls()
        self.smtp.login(self.smtp_info['user_address'], self.smtp_info['user_pass'])


    def get_mime_message(self, subject, body):
        '''
        Builds a MIME message and returns it.
        '''
        msg = MIMEMultipart()
        msg['From'] = self.smtp_info['user_address']
        msg['To'] = ', '.join(NOTIFY_EMAILS)
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        return msg


    def index(self):
        '''
        Index page, default route.
        '''
        return 'This is the index, it currently does nothing.'


    def front_door(self):
        '''
        This can lock and unlock the door via the lock argument from a get request
        '''
        lock = request.args.get('lock')
        if lock is not None:
            try:
                self.front_door_lock = bool(lock)
            except:
                return 'Cannot pass arg "lock" with value other than "True" or "False".'
        return 'Front door lock: ' + lock


    def front_door_open(self):
        '''
        Endpoint method for when front door opens
        '''
        time = datetime.datetime.now(pytz.timezone('America/Los_Angeles'))
        body = 'Front door was opened on ' + time
        # if the lock is true, alert
        if self.front_door_lock:
            subject = 'Home Alert: Door Open'
            # Might need to catch an exception to refresh the connection
            try:
                self.smtp.send_message(self.get_mime_message(subject, body))
            except:
                self.smtp_connect()
                self.smtp.send_message(self.get_mime_message(subject, body))
        return body


    def run(self):
        '''
        Run the flask app
        '''
        self.app.run(debug=True, host='0.0.0.0', port=5000)


    def add_endpoint(self, endpoint=None, endpoint_name=None, handler=None):
        '''
        Register an endpoint function to the flask app
        '''
        self.app.add_url_rule(endpoint, endpoint_name, EndpointAction(handler))


def main():
    parser = argparse.ArgumentParser(description='Run the main home alert server.')
    parser.add_argument('-l', '--login', type=str, required=True,
                         help='Path to a file containing mail login '
                              'credentials to send alerts.')
    args = parser.parse_args()

    smtp_info = json.load(open(args.login, 'r'))

    home_alert = HomeAlert(smtp_info)
    # Add endpoints
    home_alert.add_endpoint(endpoint='/',
            endpoint_name='index', handler=home_alert.index)
    home_alert.add_endpoint(endpoint='/front_door_open',
            endpoint_name='front_door_open', handler=home_alert.front_door_open)
    home_alert.add_endpoint(endpoint='/front_door',
            endpoint_name='front_door', handler=home_alert.front_door)
    # Start web server
    home_alert.run()


if __name__ == '__main__':
    main()
