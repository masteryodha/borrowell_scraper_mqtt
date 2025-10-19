import time
import os
import argparse
import schedule
import pytz
from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
import paho.mqtt.client as mqttClient
import datetime

client = mqttClient.Client()

INITIAL_WAIT_IN_SECONDS = 15
WAIT_AFTER_LOGIN_IN_SECONDS = 15

#Se connecter sur MQTT
def _on_connect_mqtt(client, userdata, flags, rc):
    print('MQTT CONNECT - CONNACK received with code %d.' % (rc))

def _connectToMQTT (mqtt_address, mqtt_port, mqtt_user, mqtt_password):
    
    client.username_pw_set(mqtt_user, password=str(mqtt_password))
    client.on_connect = _on_connect_mqtt
    client.connect(mqtt_address, mqtt_port)
    client.loop_start()

def _login(driver, username: str, password: str):
    print('login...')
    url = "https://app.borrowell.com/"

    driver.get(url)
    
    #Attendre que le site load complètement.
    print('Wait for {} seconds, the site is really slow'.format(INITIAL_WAIT_IN_SECONDS))
    time.sleep(INITIAL_WAIT_IN_SECONDS)

    #Pour une raison weird, le site change entre username et emailAddress parfois.  On le gère donc avec une exception
    print("Set username and password")
    elem=driver.find_element(By.NAME, "username")
    elem.send_keys(username)
       
    elem = driver.find_element(By.NAME, "password")
    elem.send_keys(password)
    
    elem.send_keys(Keys.RETURN)

    #Wait for the login to happen
    print('Waiting {} more secondes for the login to complete...'.format(WAIT_AFTER_LOGIN_IN_SECONDS))
    time.sleep(WAIT_AFTER_LOGIN_IN_SECONDS)
    print('*** Login successful ***')


def _getCreditFactors(driver, args):
    url = "https://app.borrowell.com/#/credit-factors"
    print('Get credit score and factors from {}'.format(url))

    driver.get(url)
    
    #Attendre que le site load complètement.
    time.sleep(10)

    #data-testid="credit-score-card-score"
    elem=driver.find_element(By.XPATH, "//span[@data-cy='credit-score-text']")
    credit_score = elem.get_attribute("innerHTML")
    print('Credit Score from Equifax : {}'. format(credit_score))
    client.publish('borrowell/credit_score', credit_score, retain=True)

    #Publish the date also
    client.publish('borrowell/date_maj', str(datetime.datetime.now(tz=pytz.timezone(args.MYTIMEZONE))), retain=True)

    #data-testid="credit-score-card-score"
    elems=driver.find_elements(By.CLASS_NAME, "factor-summary")
    
    for elem in elems:
        #print('ELEMENT *** : {}'.format(elem.get_attribute("innerHTML")))
        
        paragraphs = elem.find_elements(By.TAG_NAME, "p")
        factor = paragraphs[0].get_attribute("innerHTML")
        value_elem = elem.find_element(By.CLASS_NAME, "factor-value")
        #print('Value : {}'.format(value_elem.get_attribute("innerHTML")))
        value = value_elem.get_attribute("innerHTML")
        print('Factor : {}. Value : {}'.format(factor, value))
        client.publish('borrowell/factors/{}'.format(factor), value, retain=True)

def _getAccounts(driver):
    url = "https://app.borrowell.com/#/app/creditReport"
    print('Get accounts from {}'.format(url))

    driver.get(url)
    
    #Attendre que le site load complètement.
    time.sleep(10)

    account_names = []
    account_balances = []
    account_reported_dates = []
    account_status = []

    account_names_elems = driver.find_elements(By.XPATH, "//div[@data-cy='account-name']")
    for a in account_names_elems:
        account_names.append(a.get_attribute("innerHTML"))

    account_balances_elems = driver.find_elements(By.XPATH, "//div[@data-cy='account-balance']")
    for a in account_balances_elems:
        account_balances.append(a.get_attribute("innerHTML"))

    reported_dates_elems = driver.find_elements(By.XPATH, "//div[@data-cy='reported-date']")
    for a in reported_dates_elems:
        account_reported_dates.append(a.get_attribute("innerHTML"))

    account_status_elems = driver.find_elements(By.XPATH, "//div[@data-cy='account-status']")
    for a in account_status_elems:
        account_status.append(a.get_attribute("innerHTML"))

    print("{} accounts found".format(len(account_names)))
    for x in range(0, len(account_names)):
        my_account = account_names[x].strip()
        my_balance = account_balances[x].strip().replace('$', '')
        my_reported_date = account_reported_dates[x].strip().replace('Reported: ', '')
        my_status = account_status[x].strip()
        
        print("Account : {}_{}.  Balance : {}.  Reported date : {}.  Status : {}".format(my_account, x, my_balance, my_reported_date, my_status))
        if my_status == 'Open':
            #Addind the index as sometimes the account names are the same
            print("Publishing to MQTT only Open account")
            client.publish('borrowell/accounts/{}_{}'.format(my_account, x), my_balance, retain=True)
            client.publish('borrowell/accounts/{}_{}_date'.format(my_account, x), my_reported_date, retain=True)



def getDataFromWebsite (username: str, password: str, headless: bool, args):
    options = Options()
    
    if (os.environ.get('PLATFORM')) == "docker":
        options.binary_location = r'/opt/firefox/firefox'
    else :
        options.binary_location = r'C:\Program Files\Mozilla Firefox\firefox.exe'


    if (headless) :
        #options.headless = True  #deprecated
        options.add_argument('-headless')

    driver = webdriver.Firefox(options=options)

    print('Connecting to MQTT')
    _connectToMQTT(args.MQTT_URL, int(args.MQTT_PORT), args.MQTT_USER, args.MQTT_PASSWORD)

    _login(driver, username, password)
    _getCreditFactors(driver, args)
    _getAccounts(driver)
    
    driver.close()
    client.disconnect()

