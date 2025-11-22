# Description
Borrowell offers free credit scores, reports and insights
The information seems to come from Equifax

This project is juste a scraper for the website to get the credit scores, the different factors and the opened accounts. These informations get published on a MQTT server to add them in Home Assistant.

it srapes https://app.borrowell.com/#/credit-factors for the credit scrore and the different factors


# Pre-requisite
Go to https://app.borrowell.com and create an account


# Executing

You can either execute it manually with python or run it in a docker

## Command line
pip install -r requirements.txt

Since it's using playwright, after installing the python requirements, you need to install playwright : playwright install --with-deps

python .\getCreditData.py --MQTT_URL localhost --MQTT_PORT 1883 --MQTT_USER my_mqtt_user --MQTT_PASSWORD my_mqtt_password --WEB_USER my_borrowell_user --WEB_PASSWORD my_borrowell_password --MYTIMEZONE America/Montreal



## Docker
Build the docker from the clone repository
```
docker build --no-cache -t mikamap/credit-borrowell:VERSION .
```

or you can use the one already build on dockerhub : https://hub.docker.com/repository/docker/mikamap/credit-borrowell

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
docker run -d --rm --name credit-borrowell -p 8080:8080 -e "MQTT_URL=localhost" -e "MQTT_PORT=1883" -e "MQTT_USER=my_mqtt_user" -e "MQTT_PASSWORD=my_mqtt_password" -e "WEB_USER=my_borrowell_user" -e "WEB_PASSWORD=my_borrowell_password" mikamap/credit-borrowell 
```
### Docker build and push to dockerhub

Because i'm a noob and never remember what to do : 

```
docker login
docker push mikamap/credit-borrowell:1.X
```


# Home Assistant

All my mqtt sensor config is in a mqtt.yaml file.

configuration.yaml
```
...
mqtt: !include mqtt.yaml
...
```

And my mqtt.yaml file : 
```
########################################################
##
##  C R E D I T 
##
##  Borrowell
##
########################################################

## BORROWELL
  - name: borrowell_credit_score
    state_topic: "borrowell/credit_score"
    unique_id: "borrowell_credit_score"

  - name: borrowell_credit_score_maj
    state_topic: "borrowell/date_maj"
    unique_id: "borrowell_credit_score_maj"

### Accounts
  - name: borrowell_account_tangerine
    state_topic: "borrowell/accounts/CCNAME_0"
    unique_id: "borrowell_account_cc_one"

  - name: borrowell_account_pc_optimum
    state_topic: "borrowell/accounts/OTHERCCNAME_1"
    unique_id: "borrowell_account_cc_two"

```

# Appel rest

we can directly call a rest endpoint to force the refresh with http://IP:8080/run-now