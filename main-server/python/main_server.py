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
    location = config['location']
    port = config['server_port']
    video_device = config['video_device']
    video_width = config['video_width']
    video_height = config['video_height']
    s3_bucket = config['upload_path']
    notify_emails = config['notify_emails']

    camera = HomeAlertCamera(video_device, video_width, video_height)
    home_alert = HomeAlertMainServer(location, config['smtp_info'], camera, notify_emails, s3_bucket)
    # Start web server
    home_alert.run(port)


if __name__ == '__main__':
    main()
