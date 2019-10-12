import argparse
import yaml

import home_alert_logging
from home_alert_camera import HomeAlertCamera
from home_alert_web_server import HomeAlertWebServer
import aws_utils

def main():
    parser = argparse.ArgumentParser(description='Run the main home alert service.')
    parser.add_argument('-c', '--config', type=str, required=True,
                         help='Path to a home alert node config file.')
    parser.add_argument('--http_logging', action='store_true', default=False,
                        help='Enable debug http request logging.')
    args = parser.parse_args()

    logger = home_alert_logging.GetHomeAlertLogger()
    logger.info("Loading config file")
    config = yaml.safe_load(open(args.config, 'r'))
    # TODO: Don't bother pulling these out, pass dict to HomeAlertWebServer
    location = config['home_alert_node']['location']

    logger.info("Creating HomeAlertCamera")
    video_device = config['home_alert_node']['video_device']
    video_width = config['home_alert_node']['video_width']
    video_height = config['home_alert_node']['video_height']
    camera = HomeAlertCamera(video_device, video_width, video_height)

    smtp_info = config['smtp_info']
    notify_emails = config['notify_emails']
    s3_bucket = None if 's3_upload_bucket' not in config else config['s3_upload_bucket']

    logger.info("Creating HomeAlertWebServer")
    home_alert = HomeAlertWebServer(location, smtp_info, camera, notify_emails, args.http_logging, s3_bucket)
    # Start web server
    logger.info("Running Web Server")
    port = config['home_alert_node']['server_port']
    home_alert.run(port)


if __name__ == '__main__':
    main()
