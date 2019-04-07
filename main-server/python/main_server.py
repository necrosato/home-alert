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
    port = config['main_server']['server_port']
    video_device = config['main_server']['video_device']
    video_width = config['main_server']['video_width']
    video_height = config['main_server']['video_height']
    s3_bucket = config['main_server']['upload_path']
    notify_emails = config['notify_emails']

    camera = HomeAlertCamera(video_device, video_width, video_height)
    home_alert = HomeAlertMainServer(location, config['smtp_info'], camera, notify_emails, s3_bucket)
    # Start web server
    home_alert.run(port)


if __name__ == '__main__':
    main()
