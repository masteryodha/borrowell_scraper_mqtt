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

You also need to install firefox and GeckoDriver.
The version of firefox and GeckoDriver needs to match.  Check the docker ENV variables to see which version it uses.

python .\getCreditData.py --MQTT_URL localhost --MQTT_PORT 1883 --MQTT_USER my_mqtt_user --MQTT_PASSWORD my_mqtt_password --WEB_USER my_borrowell_user --WEB_PASSWORD my_borrowell_password --MYTIMEZONE America/Montreal



## Docker
Build the docker from the clone repository
```
docker build -t credit-borrowell .
```

or you can user the one already build on dockerhub : https://hub.docker.com/repository/docker/mikamap/credit-borrowell

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


### Factors
  - name: borrowell_factor_missed_payments
    state_topic: "borrowell/factors/Missed payments"
    unique_id: "borrowell_factor_missed_payments"

  - name: borrowell_factor_credit_utilization
    state_topic: "borrowell/factors/Credit utilization"
    unique_id: "borrowell_factor_credit_utilization"
    
  - name: borrowell_factor_derogatory_marks
    state_topic: "borrowell/factors/Derogatory marks"
    unique_id: "borrowell_factor_derogatory_marks"

  - name: borrowell_factor_credit_age
    state_topic: "borrowell/factors/Avg. credit age"
    unique_id: "borrowell_factor_credit_age"

  - name: borrowell_factor_total_accounts
    state_topic: "borrowell/factors/Total accounts"
    unique_id: "borrowell_factor_total_accounts"

  - name: borrowell_factor_hard_inquiries
    state_topic: "borrowell/factors/Hard inquiries"
    unique_id: "borrowell_factor_hard_inquiries"

### Accounts
  - name: borrowell_account_tangerine
    state_topic: "borrowell/accounts/CCNAME_0"
    unique_id: "borrowell_account_cc_one"

  - name: borrowell_account_pc_optimum
    state_topic: "borrowell/accounts/OTHERCCNAME_1"
    unique_id: "borrowell_account_cc_two"

```
