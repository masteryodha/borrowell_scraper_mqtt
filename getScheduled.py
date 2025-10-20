import time
import os
import schedule
import threading
from getBorrowellSelenium import getDataFromWebsite
from flask import Flask, request, jsonify
import logging

app = Flask(__name__)

#Configuration
HEARTBEAT_FREQUENCY_IN_HOUR = 1
SCHEDULE_GET_BOROWELL_IN_HOUR = 12
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')


#Arguments
arguments = {
    'MQTT_URL': os.environ.get('MQTT_URL'),
    'MQTT_PORT': os.environ.get('MQTT_PORT'),
    'MQTT_USER': os.environ.get('MQTT_USER'),
    'MQTT_PASSWORD': os.environ.get('MQTT_PASSWORD'),
    'WEB_USER': os.environ.get('WEB_USER'),
    'WEB_PASSWORD': os.environ.get('WEB_PASSWORD'),
    'MYTIMEZONE': os.environ.get('MYTIMEZONE'),
}

def _printHearbeat():
    logging.info("The cron in {} is still alive and python is working...".format(os.environ.get('PLATFORM')))

# Tâche planifiée
def run_scheduled_tasks():

    #On va chercher les informations tout de suite
    logging.info("Aller chercher les informations de Borrowell Maintenant")
    getDataFromWebsite(args=arguments, headless=True)

    logging.info("")
    logging.info("")
    logging.info("------------------------------------------------------------------------------------------")
    schedule.every(SCHEDULE_GET_BOROWELL_IN_HOUR).hours.do(getDataFromWebsite, args = arguments, headless = True)
    logging.info("Scheduled the BORROWELL scraper every {} hours from now".format(SCHEDULE_GET_BOROWELL_IN_HOUR))
    schedule.every(HEARTBEAT_FREQUENCY_IN_HOUR).hours.do(_printHearbeat)
    logging.info("Scheduled Heartbeat every {} hour from now".format(HEARTBEAT_FREQUENCY_IN_HOUR))
    logging.info("------------------------------------------------------------------------------------------")
    logging.info("")
    logging.info("")

    while True:
        schedule.run_pending()
        time.sleep(1)

# Endpoint REST
@app.route('/run-now', methods=['GET'])
def run_now():
    logging.info("RUN-NOW - Aller chercher les informations de Borrowell")
    try:
        getDataFromWebsite(args=arguments, headless=True)
        return jsonify({'status': 'success'}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# Lancement
if __name__ == '__main__':
    logging.info("Démarrage du service Flask + scheduler")
    threading.Thread(target=run_scheduled_tasks, daemon=True).start()
    app.run(host='0.0.0.0', port=8080)
