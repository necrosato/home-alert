import argparse

from home_alert_camera import HomeAlertCamera
import aws_utils

# This is where home alerts get sent
# TODO: Load this from config file
NOTIFY_EMAILS = ['sato@naookie.com']
# The video device connected to the main server
# TODO: Load these from config file
VIDEO_DEVICE = '/dev/video0'
VIDEO_MAX_WIDTH = 1280
VIDEO_MAX_HEIGHT = 720
LOCATION = ''
S3_BUCKET = 's3://com.necrosato.home-alert/'
PORT = ''


def main():
    parser = argparse.ArgumentParser(description='Run the main home alert server.')
    parser.add_argument('-l', '--login', type=str, required=True,
                         help='Path to a file containing mail login '
                              'credentials to send alerts.')
    args = parser.parse_args()

    smtp_info = yaml.load(open(args.login, 'r'))

    camera = HomeAlertCamera(video_device, video_max_width, video_max_height)
    home_alert = HomeAlertMainServer(location, smtp_info, camera, notify_emails, s3_bucket)
    # Start web server
    home_alert.run(port)


if __name__ == '__main__':
    main()
