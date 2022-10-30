import os
from flask import Flask, Response, request, render_template, send_file, redirect
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import datetime
import pytz
import threading

import home_alert_logging
from home_alert_camera import HomeAlertCamera
import aws_utils
import pprint

# TODO: Pull this out and pass to node
NODE_DIR = '/home/home-alert/home-alert/'
VIDEO_DIR = os.path.join(NODE_DIR, 'video')
TEMPLATE_DIR = os.path.join(NODE_DIR, 'python/templates')
HLS_MANIFEST='video.m3u8'

class EndpointAction:
    '''
    action is expected to return a valid response
    '''
    def __init__(self, action):
        self.action = action


    def __call__(self, **args):
        return self.action(**args)

class LoggingMiddleware(object):
    def __init__(self, app):
        self._app = app

    def __call__(self, environ, resp):
        errorlog = environ['wsgi.errors']
        pprint.pprint(('REQUEST', environ), stream=errorlog)

        def log_response(status, headers, **args):
            pprint.pprint(('RESPONSE', status, headers), stream=errorlog)
            return resp(status, headers, **args)

        return self._app(environ, log_response)

class HomeAlertWebServer:
    '''
    Class holding a flask app and smtp server
    '''
    def __init__(self, location, smtp_info, camera, notify_emails, http_logging = False, s3_bucket = None):
        '''
        location - string
        smtp_info - path to yaml file
        camera - HomeAlertCamera Object
        '''
        self.logger = home_alert_logging.GetHomeAlertLogger("Home Alert Node - {}".format(location))
        self.location = location
        self.smtp_info = smtp_info
        self.camera = camera
        self.camera_handler_thread = threading.Thread(target=self.camera_handler)
        self.camera_handler_thread.start()
        self.notify_emails = notify_emails
        self.s3_bucket = s3_bucket
        self.armed = True

        self.logger.info("Creating Web Server")
        self.app = Flask('Home Alert Node - ' + self.location, template_folder=TEMPLATE_DIR)
        if http_logging:
            self.app.wsgi_app = LoggingMiddleware(self.app.wsgi_app)

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
        self.add_endpoint(endpoint='/video',
                endpoint_name='video_base', handler=self.video, defaults={'subpath':''})
        self.add_endpoint(endpoint='/video/<path:subpath>',
                endpoint_name='video', handler=self.video)
        self.add_endpoint(endpoint='/current_video',
                endpoint_name='current_video', handler=self.current_video)


    def camera_handler(self):
        while True:
            dt = datetime.datetime.now(pytz.timezone('America/Los_Angeles'))
            suffix = str(dt.date()) + '/' + str(dt.time())
            video_dir = os.path.join(VIDEO_DIR, suffix)
            if not os.path.exists(video_dir):
                os.makedirs(video_dir)
            video_name = HLS_MANIFEST
            self.camera.capture(os.path.join(video_dir, video_name))
 

    def smtp_connect(self):
        '''
        Opens/refreshes an smtp connection
        '''
        self.logger.info("Connecting to mail server")
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
        Arms the node.
        '''
        self.armed = True
        return self.location + ' is armed.'


    def disarm(self):
        '''
        Disarms the node.
        '''
        self.armed = False
        return self.location + ' is disarmed.'


    def trigger(self):
        '''
        If armed, sends emails to notify list.
        Returns a message containing the request time.
        '''
        dt = datetime.datetime.now(pytz.timezone('America/Los_Angeles'))
        response_str = self.location + ' recieved trigger: ' + str(dt)

        # if armed, alert
        if self.armed:
            subject = 'Home Alert: ' + self.location
            msg = self.get_mime_message(subject, response_str, [])
            # Might need to catch an exception to refresh the connection
            try:
                self.smtp.send_message(msg)
            except:
                self.smtp_connect()
                self.smtp.send_message(msg)

        return response_str


    def status(self):
        '''
        Returns node location and arm status:
        '''
        return render_template('index.html', location=self.location, armed=str(self.armed))


    def stream(self):
        current_date = sorted(os.listdir(VIDEO_DIR))[-1]
        current_time = sorted(os.listdir(os.path.join(VIDEO_DIR, current_date)))[-1]
        return render_template('player.html', source=os.path.join('video', current_date, current_time, HLS_MANIFEST))


    def video(self, subpath):
        arg_path = subpath.strip('/')
        abs_path = os.path.join(VIDEO_DIR, arg_path)
        self.logger.info("Looking for " + abs_path)

        # Return 404 if path doesn't exist
        if not os.path.exists(abs_path):
            exit(1)

        # Check if path is a file and serve
        if os.path.isfile(abs_path):
            return send_file(abs_path)

        # check if video in path and serve
        files = []
        for f in reversed(sorted(os.listdir(abs_path))):
            vpath = os.path.join(abs_path, f, HLS_MANIFEST)
            if os.path.isfile(vpath):
                files.append(os.path.join(f, HLS_MANIFEST))
            else:
                files.append(f)

        # Show directory contents
        return render_template('files.html', files=files)

    def current_video(self):
        current_date = sorted(os.listdir(VIDEO_DIR))[-1]
        current_time = sorted(os.listdir(os.path.join(VIDEO_DIR, current_date)))[-1]
        return redirect(os.path.join('video', current_date, current_time, HLS_MANIFEST))

    def run(self, port):
        '''
        Run the flask app
        '''
        self.app.run(debug=False, host='0.0.0.0', port=port)


    def add_endpoint(self, endpoint=None, endpoint_name=None, handler=None, **options):
        '''
        Register an endpoint function to the flask app
        '''
        self.app.add_url_rule('/' + self.location + '/' + endpoint, endpoint_name, EndpointAction(handler), **options)


