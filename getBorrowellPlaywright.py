import pytz
from playwright.sync_api import sync_playwright
import paho.mqtt.client as mqttClient
import datetime
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')

client = mqttClient.Client(
    callback_api_version=mqttClient.CallbackAPIVersion.VERSION2
)

#Se connecter sur MQTT
def _on_connect_mqtt(client, userdata, flags, reasonCode, properties):
    logging.info('MQTT CONNECT - CONNACK received with code {}.'.format(reasonCode))

def _connectToMQTT (mqtt_address, mqtt_port, mqtt_user, mqtt_password):
    
    client.username_pw_set(mqtt_user, password=str(mqtt_password))
    client.on_connect = _on_connect_mqtt
    client.connect(mqtt_address, mqtt_port)
    client.loop_start()

def _login(page, username: str, password: str):
    logging.info('login...')
    url = "https://my.borrowell.com/u/login"

    page.goto(url)
    
    #Attendre que le site load complètement.
    page.wait_for_load_state("domcontentloaded")

    logging.info('Attente du formulaire de login...')
    page.wait_for_selector("//input[@name='username']")
    
    #Pour une raison weird, le site change entre username et emailAddress parfois.  On le gère donc avec une exception
    logging.info("Set username ({}) and password".format(username))
    page.fill("input[name='username']", "jfa_@hotmail.com")
    page.fill("input[name='password']", "XxkrKWoTefpxnB9VbVB6piWUi")
    page.press("input[name='password']", "Enter")
    page.wait_for_selector("//span[contains(text(),'Jean Francois')]")


    #Wait for the login to happen
    logging.info('*** Login successful - User Name founded on page ***')

    #En docker, il est impossible d'obtenir les credit factor.  Donc, on va prendre le score directement après le login
    element = page.locator('[data-testid="credit-score-graph-score-text"]')

    credit_score = element.text_content()
    logging.info('Credit Score from Equifax : {}'. format(credit_score))
    client.publish('borrowell/credit_score', credit_score, retain=True)

def _printArguments(args):

    logging.info('***** ARGUMENTS BORROWELL *****')
    logging.info('* MQTT_URL      : {}'.format(args.MQTT_URL))
    logging.info('* MQTT_PORT     : {}'.format(args.MQTT_PORT))
    logging.info('* MQTT_USER     : {}'.format(args.MQTT_USER))
    logging.info('* MQTT_PASSWORD : {}*******'.format(args.MQTT_PASSWORD[0:3]))
    logging.info('* WEB_USER      : {}'.format(args.WEB_USER))
    logging.info('* WEB_PASSWORD  : {}*******'.format(args.WEB_PASSWORD[0:3]))
    logging.info('* MYTIMEZONE    : {}'.format(args.MYTIMEZONE))
    logging.info('*******************************')
    logging.info('')


def _getCreditFactors(page, args):
    
    url = "https://app.borrowell.com/#/credit-factors"
    logging.info('Get credit score and factors from {}'.format(url))

    page.goto(url, wait_until="networkidle")
    page.wait_for_selector("//span[@data-cy='credit-score-text']")

    element = page.locator("//span[@data-cy='credit-score-text']")
    credit_score = element.text_content()
    logging.info('Credit Score from Equifax : {}'. format(credit_score))
    client.publish('borrowell/credit_score', credit_score, retain=True)

    client.publish('borrowell/date_maj', str(datetime.datetime.now(tz=pytz.timezone(args.MYTIMEZONE))), retain=True)

    #data-testid="credit-score-card-score"
    elements=page.locator("//div[@class='factor-summary']").all()
    
    for elem in elements:
        
        paragraphs = elem.locator("p")
        factor = paragraphs.text_content()
        
        value_elem = elem.locator(".factor-value")
        value = value_elem.text_content()
        logging.info('Factor : {}. Value : {}'.format(factor, value))
        client.publish('borrowell/factors/{}'.format(factor), value, retain=True)

def _getAccounts(page):
    url = "https://app.borrowell.com/#/app/creditReport"
    logging.info('Get accounts from {}'.format(url))

    page.goto(url)
    page.wait_for_selector("//div[@data-cy='account-name']")

    account_names = []
    account_balances = []
    account_reported_dates = []
    account_status = []

    account_names_elems = page.locator("//div[@data-cy='account-name']").all()
    for a in account_names_elems:
        account_names.append(a.text_content())
    
    account_balances_elems = page.locator("//div[@data-cy='account-balance']").all()
    for a in account_balances_elems:
        account_balances.append(a.text_content())

    reported_dates_elems = page.locator("//div[@data-cy='reported-date']").all()
    for a in reported_dates_elems:
        account_reported_dates.append(a.text_content())

    account_status_elems = page.locator("//div[@data-cy='account-status']").all()
    for a in account_status_elems:
        account_status.append(a.text_content())

    logging.info("{} accounts found".format(len(account_names)))
    for x in range(0, len(account_names)):
        my_account = account_names[x].strip()
        my_balance = account_balances[x].strip().replace('$', '')
        my_reported_date = account_reported_dates[x].strip().replace('Reported: ', '')
        my_status = account_status[x].strip()
        
        logging.info("Account : {}_{}.  Balance : {}.  Reported date : {}.  Status : {}".format(my_account, x, my_balance, my_reported_date, my_status))
        if my_status == 'Open':
            #Addind the index as sometimes the account names are the same
            logging.info("Publishing to MQTT only Open account")
            client.publish('borrowell/accounts/{}_{}'.format(my_account, x), my_balance, retain=True)
            client.publish('borrowell/accounts/{}_{}_date'.format(my_account, x), my_reported_date, retain=True)


def getDataFromWebsite (args, headless: bool):
    _printArguments(args)
    
    with sync_playwright() as p:
        # Choix du navigateur : chromium, firefox, webkit      
        if (headless) :
            browser = p.chromium.launch(
                headless=True, 
                #args=["--headless=new"]
                args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"]
            )
        else :
            browser = p.chromium.launch(headless=False)

        context = browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )

        #Ajout pour masquer navigator.webdriver
        page = context.new_page()

        page.add_init_script("""
            // Neutraliser navigator.webdriver
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });

            // Simuler plugins
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5],
            });

            // Simuler languages
            Object.defineProperty(navigator, 'languages', {
                get: () => ['fr-FR', 'fr', 'en-US', 'en'],
            });

            // Simuler permissions (notifications, etc.)
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications'
                    ? Promise.resolve({ state: Notification.permission })
                    : originalQuery(parameters)
            );

            // Supprimer animations/transitions CSS
            const style = document.createElement('style');
            style.innerHTML = '* { transition: none !important; animation: none !important; }';
            document.head.appendChild(style);
        """)


        logging.info('Connecting to MQTT')
        _connectToMQTT(args.MQTT_URL, int(args.MQTT_PORT), args.MQTT_USER, args.MQTT_PASSWORD)

        _login(page, args.WEB_USER, args.WEB_PASSWORD)
        #_getCreditFactors(page, args)
        _getAccounts(page)

        client.publish('borrowell/date_maj', str(datetime.datetime.now(tz=pytz.timezone(args.MYTIMEZONE))), retain=True)

        browser.close()
        client.disconnect()
