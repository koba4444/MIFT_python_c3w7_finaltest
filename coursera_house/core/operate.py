import json

from .models import Setting
import requests

from coursera_house.settings import SMART_HOME_API_URL, SMART_HOME_ACCESS_TOKEN

# Controllers which can be written via standard API
CONTROLLER_WRITABLES = [
    "bedroom_light",
    "bathroom_light",
    "air_conditioner",
    "curtains",
    "boiler",
    "cold_water",
    "hot_water",
    "washing_machine"]
SMART_USER_API_URL = 'http://smarthome.webpython.graders.eldf.ru/api/auth.current'

def get_via_standard_api(obj):
    headers = {"Authorization": "Bearer " + str(SMART_HOME_ACCESS_TOKEN)}
    r = json.loads(requests.get(SMART_HOME_API_URL, headers=headers).text)
    obj.context["data"] = dict([(i['name'], i['value']) for i in r["data"]])
    obj.context["form"]["bedroom_target_temperature"] = \
        Setting.objects.get(controller_name="bedroom_target_temperature").value
    obj.context["form"]["hot_water_target_temperature"] = \
        Setting.objects.get(controller_name="hot_water_target_temperature").value
    return obj


def post_via_standard_api(obj, controllers_to_change):
    data_for_post_request = {
        "controllers": [
            {"name": controller_key, "value": controller_val}
            for controller_key, controller_val in obj.context['data'].items()
            if (controller_key in list(obj.controllers_to_change)
                and controller_key in CONTROLLER_WRITABLES)
        ]
    }
    headers = {"Authorization": "Bearer " + str(SMART_HOME_ACCESS_TOKEN)}
    data = json.dumps(data_for_post_request)
    if len(data_for_post_request["controllers"]) > 0:
        r1 = requests.post(SMART_HOME_API_URL, headers=headers, data=data)
    return obj




class HomeControllersData():
    """
    Consists and operates data from customer form and controllers from server via API as well as customer info
    """
    def __init__(self):
        self.context = dict()
        self.context["form"] = {}           #customer form data
        self.context["data"] = {}         #cntrollers from server
        self.context["user"] = {}
        self.context["new_value"] = dict([(i, None) for i in CONTROLLER_WRITABLES])
        self.context["must_have_value"] = dict([(i, None) for i in CONTROLLER_WRITABLES])
        self.context["do_not_change"] = dict([(i, "allowed") for i in CONTROLLER_WRITABLES])
        self.controllers_to_change = set()

    def compose_controllers_to_change(self):
        """
        Logic for list and new values of controllers to change from "must_have_value", "new_value" and "do_not_change"
        :return:
        """
        for i in CONTROLLER_WRITABLES:
            if self.context["must_have_value"][i] is not None:
                if self.context["must_have_value"][i] != self.context["data"][i]:
                    self.controllers_to_change |= {i}
                    self.context["data"][i] = self.context["must_have_value"][i]
                    #print(i, self.context["data"][i])
            else:
                if (not self.context["do_not_change"][i] == "forbidden" and self.context["new_value"][i] is not None\
                and self.context["data"][i] != self.context["new_value"][i]):
                    self.controllers_to_change |= {i}
                    self.context["data"][i] = self.context["new_value"][i]

    def get(self):
        return get_via_standard_api(self)

    def post(self, controllers_to_change=CONTROLLER_WRITABLES):
        return post_via_standard_api(self, controllers_to_change)

    def air_condition_on(self):
        self.context["new_value"]["air_conditioner"] = True

    def air_condition_off(self):
        self.context["new_value"]["air_conditioner"] = False

    def accident_boiler_and_washingmachine_off(self):
        self.context["must_have_value"]["boiler"] = False
        self.context["must_have_value"]["washing_machine"] = "off"

    def boiler_on(self):
            self.context["new_value"]["boiler"] = True

    def boiler_off(self):
        self.context["new_value"]["boiler"] = False

    def open_curtains(self):
        self.context["new_value"]["curtains"] = "open"

    def close_curtains(self):
        self.context["new_value"]["curtains"] = "close"


    def fire_accident_turning_off(self):
        self.context["must_have_value"]["air_conditioner"] = False
        self.context["must_have_value"]["bedroom_light"] = False
        self.context["must_have_value"]["bathroom_light"] = False
        self.context["must_have_value"]["boiler"] = False
        self.context["must_have_value"]["washing_machine"] = "off"

    def accident_water_close(self):
        print("water close")
        self.context["must_have_value"]["cold_water"] = False
        self.context["must_have_value"]["hot_water"] = False



