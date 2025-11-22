import os
import argparse
from getBorrowellPlaywright import getDataFromWebsite
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')

HEARTBEAT_FREQUENCY_IN_HOUR = 1
SCHEDULE_GET_BOROWELL_IN_HOUR = 12

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Scrape Borrowell website to get credit scores and factor')
    parser.add_argument('--MQTT_URL', dest='MQTT_URL', default=os.environ.get('MQTT_URL'))
    parser.add_argument('--MQTT_PORT', dest='MQTT_PORT', default=os.environ.get('MQTT_PORT'))
    parser.add_argument('--MQTT_USER', dest='MQTT_USER', default=os.environ.get('MQTT_USER'))
    parser.add_argument('--MQTT_PASSWORD', dest='MQTT_PASSWORD', default=os.environ.get('MQTT_PASSWORD'))
    parser.add_argument('--WEB_USER', dest='WEB_USER', default=os.environ.get('WEB_USER'))
    parser.add_argument('--WEB_PASSWORD', dest='WEB_PASSWORD', default=os.environ.get('WEB_PASSWORD'))
    parser.add_argument('--MYTIMEZONE', dest='MYTIMEZONE', default=os.environ.get('MYTIMEZONE'))

    args = parser.parse_args()

    logging.info("Run the BORROWELL scraper now")
    getDataFromWebsite(args = args, headless = True)
