import time
import os
import argparse
import schedule
from getCreditData import getDataFromWebsite

HEARTBEAT_FREQUENCY_IN_HOUR = 1
SCHEDULE_GET_BOROWELL_IN_HOUR = 12

def _printHearbeat():
    print("The cron in {} is still alive and python is working...".format(os.environ.get('PLATFORM')))

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

    print('***** ARGUMENTS BORROWELL *****')
    print('* MQTT_URL      : {}'.format(args.MQTT_URL))
    print('* MQTT_PORT     : {}'.format(args.MQTT_PORT))
    print('* MQTT_USER     : {}'.format(args.MQTT_USER))
    print('* MQTT_PASSWORD : {}*******'.format(args.MQTT_PASSWORD[0:3]))
    print('* WEB_USER      : {}'.format(args.WEB_USER))
    print('* WEB_PASSWORD  : {}*******'.format(args.WEB_PASSWORD[0:3]))
    print('* MYTIMEZONE    : {}'.format(args.MYTIMEZONE))
    print('*******************************')
    print('')


    print("Run the BORROWELL scraper now")
    getDataFromWebsite(username = args.WEB_USER, password = args.WEB_PASSWORD, headless = True, args = args)
    # Pour test - Headless à False
    # getDataFromWebsite(username = args.WEB_USER, password = args.WEB_PASSWORD, headless = False, args = args)
    print("")
    print("")
    print("------------------------------------------------------------------------------------------")
    schedule.every(SCHEDULE_GET_BOROWELL_IN_HOUR).hours.do(getDataFromWebsite, username = args.WEB_USER, password = args.WEB_PASSWORD, headless = True, args = args)
    print("Scheduled the BORROWELL scraper every {} hours from now".format(SCHEDULE_GET_BOROWELL_IN_HOUR))
    schedule.every(HEARTBEAT_FREQUENCY_IN_HOUR).hours.do(_printHearbeat)
    print("Scheduled Heartbeat every {} hour from now".format(HEARTBEAT_FREQUENCY_IN_HOUR))
    print("------------------------------------------------------------------------------------------")
    print("")
    
    while True:
        schedule.run_pending()
        time.sleep(1)
