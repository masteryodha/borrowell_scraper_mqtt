# Description
Borrowell offers free credit scores, reports and insights
The information seems to come from Equifax

This project is juste a scraper for the website to get the credit scores, the different factors and the opened accounts. These informations get published on a MQTT server to add them in Home Assistant.

it srapes https://app.borrowell.com/#/credit-factors for the credit scrore and the different factors


# Pre-requisite
Go to https://app.borrowell.com and create an account.


# Executing.

You can either execute it manually with python or run it in a docker

## Command line
pip install -r requirements.txt
python .\getCreditData.py --MQTT_URL localhost --MQTT_PORT 1883 --MQTT_USER my_mqtt_user --MQTT_PASSWORD my_mqtt_password --WEB_USER my_borrowell_user --WEB_PASSWORD my_borrowell_password --MYTIMEZONE America/Montreal



## Docker
Build the docker
```
docker build -t credit-borrowell .
```

## Docker
Build the docker
```
docker build -t credit-borrowell .
```

Parameters : 
| Parameters | Mandatory |  Description |
|:-----|:--------:|:--------:|
| MQTT_URL   | Yes | IP of the MQTT server.  Example : 192.178.0.20|
| MQTT_PORT   | Yes |  Port of the MQTT server.  Example : 1883  |
| MQTT_USER   | Yes | User of MQTT |
| MQTT_PASSWORD | Yes  | Password of MQTT |
| WEB_USER   | Yes | User on Borrowell |
| WEB_PASSWORD | Yes  | Password on Borrowell |
| MYTIMEZONE | No  | The timezone for formatting the dates.  Default value : America/Montreal |
| GECKODRIVER_VER | No  | Version of geckoDriver.  Default value : 0.33.0.  This needs to match the value of Firefox |
| FIREFOX_VER | No  | Version of firefox to use for selenium.  Default value : 116.0 |

Run with : 
```
docker run -d --rm --name credit-borrowell -e "MQTT_URL=localhost" -e "MQTT_PORT=1883" -e "MQTT_USER=my_mqtt_user" -e "MQTT_PASSWORD=my_mqtt_password" -e "WEB_USER=my_borrowell_user" -e "WEB_PASSWORD=my_borrowell_password" credit-borrowell
```

# Home Assistant

All my mqtt sensor config is in a mqtt.yaml file.

configuration.yaml
```
...
mqtt: !include mqtt.yaml
...
```

