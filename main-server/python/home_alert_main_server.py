import os
from flask import Flask, Response, request
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import datetime
import pytz
import threading

from home_alert_camera import HomeAlertCamera
import aws_utils

# TODO: Pull this out and pass to main server
MAIN_SERVER_DIR = '/home/main-server/main-server/'

class EndpointAction():
    '''
    action is expected to return a valid response
    '''
    def __init__(self, action):
        self.action = action


    def __call__(self, *args):
        return self.action()


class HomeAlertMainServer():
    '''
    Class holding a flask app and smtp server
    '''
    def __init__(self, location, smtp_info, camera, notify_emails, s3_bucket):
        '''
        location - string
        smtp_info - path to yaml file
        camera - HomeAlertCamera Object
        '''
        self.location = location
        self.smtp_info = smtp_info
        self.camera = camera
        self.notify_emails = notify_emails
        self.s3_bucket = s3_bucket
        self.armed = True

        self.smtp_connect()
        self.app = Flask('Home Alert Main Server - ' + self.location)

        # Add endpoints
        self.add_endpoint(endpoint='/',
                endpoint_name='index', handler=self.index)
        self.add_endpoint(endpoint='/status',
                endpoint_name='status', handler=self.status)
        self.add_endpoint(endpoint='/trigger',
                endpoint_name='trigger', handler=self.trigger)
        self.add_endpoint(endpoint='/arm',
                endpoint_name='arm', handler=self.arm)
        self.add_endpoint(endpoint='/disarm',
                endpoint_name='disarm', handler=self.disarm)
        self.add_endpoint(endpoint='/stream',
                endpoint_name='stream', handler=self.stream)


    def smtp_connect(self):
        '''
        Opens/refreshes an smtp connection
        '''
        self.smtp = smtplib.SMTP(host=self.smtp_info['host'], port=self.smtp_info['port'])
        self.smtp.starttls()
        self.smtp.login(self.smtp_info['user_address'], self.smtp_info['user_pass'])


    def get_mime_message(self, subject, body, files):
        '''
        Builds a MIME message and returns it.
        '''
        msg = MIMEMultipart()
        msg['From'] = self.smtp_info['user_address']
        msg['To'] = ', '.join(self.notify_emails)
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
        Index page, returns status page.
        '''
        return self.status()


    def arm(self):
        '''
        Arms the server.
        '''
        self.armed = True
        return self.location + ' is armed.'


    def disarm(self):
        '''
        Disarms the server.
        '''
        self.armed = False
        return self.location + ' is disarmed.'


    def trigger(self):
        '''
        This function handles a trigger request. It captures images from camera.
        If armed, sends emails to notify list.
        Returns a message containing the request time.
        '''
        time = datetime.datetime.now(pytz.timezone('America/Los_Angeles'))
        response_str = self.location + ' recieved trigger: ' + str(time)

        # Save some photos 
        photo_suffix = '/photos/' + str(time)
        photo_dir = MAIN_SERVER_DIR + photo_suffix
        os.mkdir(photo_dir)
        self.camera.write_video_frames(photo_dir, 'photo_', 5, 2, 1)
        photos = [photo_dir + '/photo_00.jpeg',
                  photo_dir + '/photo_02.jpeg',
                  photo_dir + '/photo_04.jpeg']

        # if armed, alert
        if self.armed:
            # TODO: Make this a function
            subject = 'Home Alert: ' + self.location
            msg = self.get_mime_message(subject, response_str, photos)
            # Might need to catch an exception to refresh the connection
            try:
                self.smtp.send_message(msg)
            except:
                self.smtp_connect()
                self.smtp.send_message(msg)

        # Move photos to s3
        dest = self.s3_bucket + self.location + photo_suffix
        s3_thread = threading.Thread(target=aws_utils.s3_mv_rmdir,
                                     args=[photo_dir, dest])
        s3_thread.start()

        return response_str


    def status(self):
        '''
        Returns controller location and arm status
        '''
        response_str = 'Location: ' + self.location + '<br>'
        response_str += 'Armed: ' + str(self.armed)
        return response_str


    def stream(self):
        return Response(self.camera.gen_video_stream(),
                        mimetype='multipart/x-mixed-replace; boundary=frame')


    def run(self, port):
        '''
        Run the flask app
        '''
        self.app.run(debug=False, host='0.0.0.0', port=port)


    def add_endpoint(self, endpoint=None, endpoint_name=None, handler=None):
        '''
        Register an endpoint function to the flask app
        '''
        self.app.add_url_rule(endpoint, endpoint_name, EndpointAction(handler))


