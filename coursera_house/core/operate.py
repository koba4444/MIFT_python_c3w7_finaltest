import json

import requests

from coursera_house.settings import SMART_HOME_API_URL, SMART_HOME_ACCESS_TOKEN


def air_condition_on():
    headers = {"Authorization": "Bearer " + SMART_HOME_ACCESS_TOKEN}
    data = {"controllers":[{"name": "air_conditioner", "value": True}]}
    headers = {"Authorization": "Bearer " + SMART_HOME_ACCESS_TOKEN}
    data = json.dumps(data)
    r1 = requests.post(SMART_HOME_API_URL, headers=headers, data=data)

def air_condition_off():
    headers = {"Authorization": "Bearer " + SMART_HOME_ACCESS_TOKEN}
    data = {"controllers":[{"name": "air_conditioner", "value": False}]}
    headers = {"Authorization": "Bearer " + SMART_HOME_ACCESS_TOKEN}
    data = json.dumps(data)
    r1 = requests.post(SMART_HOME_API_URL, headers=headers, data=data)