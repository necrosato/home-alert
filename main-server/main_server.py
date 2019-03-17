from flask import Flask, Response, request
import argparse
import json
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import datetime
import pytz
import subprocess

import os,sys,inspect
# Add other path if in repo
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir + '/video-security/photo-burst')
import photo_burst

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
        self.controllers = { 'door_front': { 'armed': True } }

    def smtp_connect(self):
        '''
        Opens/refreshes an smtp connection
        '''
        self.smtp = smtplib.SMTP(host=self.smtp_info['smtp_host'], port=self.smtp_info['smtp_port'])
        self.smtp.starttls()
        self.smtp.login(self.smtp_info['user_address'], self.smtp_info['user_pass'])


    def get_mime_message(self, subject, body, files):
        '''
        Builds a MIME message and returns it.
        '''
        msg = MIMEMultipart()
        msg['From'] = self.smtp_info['user_address']
        msg['To'] = ', '.join(NOTIFY_EMAILS)
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        # attach files
        for attachment_file in files:
            with open(attachment_file, 'rb') as f:
                name = os.path.basename(attachment_file)
                attachment = MIMEApplication(f.read(), Name=name)
                attachment['Content-Disposition'] = 'attachment; filename="%s"' % name
                msg.attach(attachment)
        return msg


    def index(self):
        '''
        Index page, default route.
        '''
        return 'This is the index, it currently does nothing.'


    def handle_controller_arm(self, controller_id):
        '''
        This function handles the current request's 'arm' argument if one is present. Does nothing if not present.
        Requires controller id.
        Retuns a message about the arm status, or a help/error message given the value passed.
        '''
        response_str = ''
        arm = request.args.get('arm')
        if arm is not None:
            if arm == 'True':
                self.controllers[controller_id]['armed'] = True
            elif arm == 'False':
                self.controllers[controller_id]['armed'] = False
            elif arm == 'Help':
                return 'Use argument "arm=True" or "arm=False" to set controller arm status. '\
                       'Email notifications will be sent for an armed conroller.'
            else:
                return 'Cannot pass arg "arm" with value other than "True", "False", or "Help".'
        return 'Armed: ' + str(self.controllers[controller_id]['armed'])


    def handle_controller_trigger(self, controller_id):
        '''
        This function handles the current request's 'trigger' argument if one is present. Does nothing if not present.
        Requires controller id.
        Returns a message containing the request time if 'open=True'.
        '''
        response_str = ''
        controller_trigger = request.args.get('trigger')
        if controller_trigger is not None:
            # TODO: Change open to take the open time (maybe?)
            # Pro: More accurate time when the duur was actually opened
            # Con: Microcontroller must keep synced time, no way to verify
            if controller_trigger == 'True':
                time = datetime.datetime.now(pytz.timezone('America/Los_Angeles'))
                response_str += 'Recieved trigger: ' + str(time)

                # Save some photos 
                # TODO: remove hardcoded directory and photo names
                photo_suffix = 'photos/door_front/' + str(time)
                photo_dir = '/home/main-server/' + photo_suffix
                os.mkdir(photo_dir)
                photo_burst.photo_burst_ffmpeg('/dev/video0', photo_dir, 'photo_', '2', 10, 1280, 720)
                photos = [photo_dir + '/photo_01.jpg', photo_dir + '/photo_06.jpg']

                # if the arm is true, alert
                if self.controllers[controller_id]['armed']:
                    subject = 'Home Alert: ' + controller_id
                    msg = self.get_mime_message(subject, response_str, photos)
                    # Might need to catch an exception to refresh the connection
                    try:
                        self.smtp.send_message(msg)
                    except:
                        self.smtp_connect()
                        self.smtp.send_message(msg)

                # Move photos to s3
                s3_cmd = ['aws', 's3', 'mv', photo_dir,
                          's3://com.necrosato.home-alert/' + photo_suffix, '--recursive']
                subprocess.check_call(s3_cmd)
                os.rmdir(photo_dir)

        return response_str


    def controller(self):
        '''
        This sends controller commands via get requests.
        Requests must have a 'id' argument with the controller's id.
        Optionally, an 'arm' value can be passed True or False
        This can arm and disarm the controller via the arm argument from a get request
        '''
        controller_id = request.args.get('id')
        if controller_id is None:
            return 'Controller must be given an "id" argument in request.'
        elif controller_id not in self.controllers:
            return 'Invalid controller id.'
        response_str = 'Controller ID: ' + controller_id
        response_str += '<br>' + self.handle_controller_arm(controller_id)
        response_str += '<br>' + self.handle_controller_trigger(controller_id)
        return response_str


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
    home_alert.add_endpoint(endpoint='/controller',
            endpoint_name='controller', handler=home_alert.controller)
    # Start web server
    home_alert.run()


if __name__ == '__main__':
    main()
