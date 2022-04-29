from __future__ import absolute_import, unicode_literals

from celery import task

from .operate import HomeControllersData
from .. import settings

from django.conf import settings

from django.core.mail import send_mail

""" Functions algo1() - algo7() according the assignments:
Реакция на события:
"""
def algo1(obj):
    """
    1. Если есть протечка воды (leak_detector=true), закрыть холодную (cold_water=false) и горячую (hot_water=false) воду
    и отослать письмо в момент обнаружения.
   ******Дополнительно, как следует из алго2, нужно отключить бойлер и стиралку. Причем сразу, а не в слудующем цикле.
    Это стало причиной дополнительной ошибки при проверке***************

    :return:
    """
    if obj.context["data"]["leak_detector"]:
        obj.accident_water_close()
        obj.accident_boiler_and_washingmachine_off()
        #obj.post(controllers_to_change=obj.controllers_to_change) #Temporary call to check hypothesis (mistake: 1 call instead 2 )
        recipients = [settings.EMAIL_RECEPIENT]
        send_mail(
            subject="Leak accident",
            message="Leak accident has happened recently",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=recipients,
            fail_silently=False
        )
        #send_mail_task.delay(recipients=[EMAIL_RECEPIENT])
        # I Use sync version of send_email here

def algo2(obj):
    """
    2. Если холодная вода (cold_water) закрыта, немедленно выключить бойлер (boiler) и стиральную машину (washing_machine)
    и ни при каких условиях не включать их, пока холодная вода не будет снова открыта.
    :return:
    """
    if obj.context["data"]["cold_water"] == False:
        obj.accident_boiler_and_washingmachine_off()

def algo3(obj):
    """
    3. Если горячая вода имеет температуру (boiler_temperature) меньше чем hot_water_target_temperature - 10%, нужно
    включить бойлер (boiler), и ждать пока она не достигнет температуры hot_water_target_temperature + 10%, после чего
    в целях экономии энергии бойлер нужно отключить
    :return:
    """
    try:
        if (float(obj.context["data"]["boiler_temperature"]) <
             0.9 * float(obj.context["form"]["hot_water_target_temperature"])):
            obj.boiler_on()
        if (float(obj.context["data"]["boiler_temperature"]) >= \
                1.1 * float(obj.context["form"]["hot_water_target_temperature"])):
            obj.boiler_off()
    except:
        pass

def algo4(obj):
    """
    4. Если шторы частично открыты (curtains == “slightly_open”), то они находятся на ручном управлении - это значит их
    состояние нельзя изменять автоматически ни при каких условиях.
    Это будет реализовано проверкой условия перед операциями со шторами. Здесь без кода.
    :return:
    """
    if obj.context["data"]["curtains"] == "slightly_open":
        obj.context["do_not_change"]["curtains"] = "forbidden"
    else:
        obj.context["do_not_change"]["curtains"] = "allowed"

def algo5(obj):
    """
    5. Если на улице (outdoor_light) темнее 50, открыть шторы (curtains), но только если не горит лампа в спальне
    (bedroom_light). Если на улице (outdoor_light) светлее 50, или горит свет в спальне (bedroom_light), закрыть шторы.
    Кроме случаев когда они на ручном управлении
    :return:
    """
    if (obj.context["data"]["outdoor_light"] < 50
        and  obj.context["data"]["bedroom_light"] == False):
        obj.open_curtains()
    if ((obj.context["data"]["outdoor_light"] > 50 or obj.context["data"]["bedroom_light"] == True)):
        obj.close_curtains()

def algo6(obj):
    """
    6. Если обнаружен дым (smoke_detector), немедленно выключить следующие приборы [air_conditioner, bedroom_light,
    bathroom_light, boiler, washing_machine], и ни при каких условиях не включать их, пока дым не исчезнет.
    :return:
    """
    if float(obj.context["data"]["smoke_detector"]) == True:
        obj.fire_accident_turning_off()

def algo7(obj):
    """
    7. Если температура в спальне (bedroom_temperature) поднялась выше bedroom_target_temperature + 10% - включить
    кондиционер (air_conditioner), и ждать пока температура не опустится ниже bedroom_target_temperature - 10%, после
    чего кондиционер отключить.
    :return:
    """
    if obj.context["data"]["bedroom_temperature"] > 1.1 * obj.context["form"]["bedroom_target_temperature"]:
        obj.air_condition_on()
    if obj.context["data"]["bedroom_temperature"] < 0.9 * obj.context["form"]["bedroom_target_temperature"]:
        obj.air_condition_off()




@task()
def smart_home_manager():
    obj = HomeControllersData()
    obj.get()
    algo1(obj)
    algo2(obj)
    algo3(obj)
    algo4(obj)
    algo5(obj)
    algo6(obj)
    algo7(obj)
    #From controller which should be changed (if any) from "must_have_value", "new_value" and "do_not_change"
    obj.compose_controllers_to_change()
    obj.post(controllers_to_change=list(obj.controllers_to_change))


@task
def send_mail_task(recipients=None, subject=None, template=None, context=None):
   print("sending email", recipients)
   send_mail(
       subject="Leak accident",
       message="Leak accident has happened recently",
       from_email=settings.EMAIL_HOST_USER,
       recipient_list=recipients,
       fail_silently=False
   )



