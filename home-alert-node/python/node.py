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

    config = yaml.safe_load(open(args.config, 'r'))
    logger = home_alert_logging.GetLogger(logging_dir=config.get('logging_dir'))

    audio_options = {}
    if 'audio_options' in config['home_alert_node']:
        audio_options = config['home_alert_node']['audio_options']

    logger.info("Creating HomeAlertCamera")
    camera = HomeAlertCamera(config['home_alert_node']['video_options'], audio_options)

    logger.info("Logging into smtp server")
    smtp_info = config['smtp_info']
    notify_emails = config['notify_emails']
    s3_bucket = None if 's3_upload_bucket' not in config else config['s3_upload_bucket']

    logger.info("Creating HomeAlertWebServer")
    location = config['home_alert_node']['location']
    home_alert = HomeAlertWebServer(location, smtp_info, camera, notify_emails, args.http_logging, s3_bucket, logger=logger)
    # Start web server
    port = config['home_alert_node']['server_port']
    home_alert.run(port)


if __name__ == '__main__':
    main()
