import argparse
import yaml

from home_alert_camera import HomeAlertCamera
from home_alert_main_server import HomeAlertMainServer
import aws_utils

# This is where home alerts get sent
# TODO: Load this from config file
notify_emails = ['sato@naookie.com']
# The video device connected to the main server
# TODO: Load these from config file
video_device = '/dev/video0'
video_max_width = 1280
video_max_height = 720
location = 'front_door'
s3_bucket = 's3://com.necrosato.home-alert/'
port = '5000'


def main():
    parser = argparse.ArgumentParser(description='Run the main home alert server.')
    parser.add_argument('-l', '--login', type=str, required=True,
                         help='Path to a file containing mail login '
                              'credentials to send alerts.')
    args = parser.parse_args()

    smtp_info = yaml.safe_load(open(args.login, 'r'))

    camera = HomeAlertCamera(video_device, video_max_width, video_max_height)
    home_alert = HomeAlertMainServer(location, smtp_info, camera, notify_emails, s3_bucket)
    # Start web server
    home_alert.run(port)


if __name__ == '__main__':
    main()
