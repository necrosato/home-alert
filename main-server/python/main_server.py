import argparse
import yaml

from home_alert_camera import HomeAlertCamera
from home_alert_main_server import HomeAlertMainServer
import aws_utils

def main():
    parser = argparse.ArgumentParser(description='Run the main home alert server.')
    parser.add_argument('-c', '--config', type=str, required=True,
                         help='Path to a home alert main server config file.')
    args = parser.parse_args()

    config = yaml.safe_load(open(args.config, 'r'))
    # TODO: Don't bother pulling these out, pass dict to HomeAlertMainServer
    location = config['main_server']['location']

    video_device = config['main_server']['video_device']
    video_width = config['main_server']['video_width']
    video_height = config['main_server']['video_height']
    camera = HomeAlertCamera(video_device, video_width, video_height)

    smtp_info = config['smtp_info']
    notify_emails = config['notify_emails']
    s3_bucket = config['s3_upload_bucket']

    home_alert = HomeAlertMainServer(location, smtp_info, camera, notify_emails, s3_bucket)
    # Start web server
    port = config['main_server']['server_port']
    home_alert.run(port)


if __name__ == '__main__':
    main()
