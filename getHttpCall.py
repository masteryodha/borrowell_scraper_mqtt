
import argparse
import schedule
import os
from getCreditData import getDataFromWebsite
import subprocess
from bottle import run, post, request, response, get, route

def _getItOnWithCustomProperties(mqtt_url : str, mqtt_port : str, mqtt_user : str, mqtt_pwd : str, web_user : str, web_pwd : str):
    
    parser = argparse.ArgumentParser(description='Scrape Borrowell website to get credit scores and factor')
    parser.add_argument('--MQTT_URL', dest='MQTT_URL', default=mqtt_url)
    parser.add_argument('--MQTT_PORT', dest='MQTT_PORT', default=mqtt_port)
    parser.add_argument('--MQTT_USER', dest='MQTT_USER', default=mqtt_user)
    parser.add_argument('--MQTT_PASSWORD', dest='MQTT_PASSWORD', default=mqtt_pwd)
    parser.add_argument('--WEB_USER', dest='WEB_USER', default=web_user)
    parser.add_argument('--WEB_PASSWORD', dest='WEB_PASSWORD', default=web_pwd)
    parser.add_argument('--MYTIMEZONE', dest='MYTIMEZONE', default="America/Montreal")

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

    print("ok, manual {}".format(mqtt_url))
    return "ok"
    getDataFromWebsite(username = args.WEB_USER, password = args.WEB_PASSWORD, headless = True, args = args)

def _getItOn():
    parser = argparse.ArgumentParser(description='Scrape Borrowell website to get credit scores and factor')
    parser.add_argument('--MQTT_URL', dest='MQTT_URL', default=os.environ.get('MQTT_URL'))
    parser.add_argument('--MQTT_PORT', dest='MQTT_PORT', default=os.environ.get('MQTT_PORT'))
    parser.add_argument('--MQTT_USER', dest='MQTT_USER', default=os.environ.get('MQTT_USER'))
    parser.add_argument('--MQTT_PASSWORD', dest='MQTT_PASSWORD', default=os.environ.get('MQTT_PASSWORD'))
    parser.add_argument('--WEB_USER', dest='WEB_USER', default=os.environ.get('WEB_USER'))
    parser.add_argument('--WEB_PASSWORD', dest='WEB_PASSWORD', default=os.environ.get('WEB_PASSWORD'))
    parser.add_argument('--MYTIMEZONE', dest='MYTIMEZONE', default=os.environ.get('MYTIMEZONE'))

    args = parser.parse_args()
    #print('***** ARGUMENTS BORROWELL *****')
    #print('* MQTT_URL      : {}'.format(args.MQTT_URL))
    #print('* MQTT_PORT     : {}'.format(args.MQTT_PORT))
    #print('* MQTT_USER     : {}'.format(args.MQTT_USER))
    #print('* MQTT_PASSWORD : {}'.format(args.MQTT_PASSWORD))
    #print('* WEB_USER      : {}'.format(args.WEB_USER))
    #print('* WEB_PASSWORD  : {}'.format(args.WEB_PASSWORD[0:3]))
    #print('* MYTIMEZONE    : {}*******'.format(args.MYTIMEZONE))
    #print('*******************************')
    #print('')

    #print("Run the BORROWELL scraper now")
    getDataFromWebsite(username = args.WEB_USER, password = args.WEB_PASSWORD, headless = True, args = args)

    return "OK DOCKER"


@route('/docker',method = 'GET')
def get():
    _getItOn()


@route('/manual/<mqtt_url>/<mqtt_port>/<mqtt_user>/<mqtt_pwd>/<web_user>/<web_pwd>',method = 'GET')
def get(mqtt_url, mqtt_port, mqtt_user, mqtt_pwd, web_user, web_pwd):
    _getItOnWithCustomProperties(mqtt_url, mqtt_port, mqtt_user, mqtt_pwd, web_user, web_pwd)

run(host='192.168.3.200', port=8080, debug=True)
