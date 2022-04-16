from __future__ import absolute_import, unicode_literals

import json

import requests
from celery import task
from django.views.generic import FormView

from . import form
from .models import Setting
from ..settings import SMART_HOME_API_URL, SMART_HOME_ACCESS_TOKEN
from . import operate as op


#    Example from https://dev-gang.ru/article/celery-python-osnovy-i-primery-ba4pn1pyb9/
from django.conf import settings
from django.core.mail import send_mail
from django.template import Engine, Context
from coursera_house.celery import app

def render_template(template, context):
   engine = Engine.get_default()
   tmpl = engine.get_template(template)
   return tmpl.render(Context(context))
# End of example

@app.task()
def smart_home_manager():
    headers = {"Authorization": "Bearer " + SMART_HOME_ACCESS_TOKEN}
    r = json.loads(requests.get(SMART_HOME_API_URL, headers=headers).text)
    controllers_data = dict([(i['name'], i['value']) for i in r["data"]])
    form_data = {}
    form_data["bedroom_target_temperature"] = Setting.objects.get(controller_name="bedroom_target_temperature").value
    form_data["hot_water_target_temperature"] = \
        Setting.objects.get(controller_name="hot_water_target_temperature").value
    if controllers_data["bedroom_temperature"] >= 1.1 * form_data["bedroom_target_temperature"]:
        op.air_condition_on()
        print("AC on")
    if controllers_data["bedroom_temperature"] < form_data["bedroom_target_temperature"]:
        op.air_condition_off()
        print("AC off")

@app.task
def send_mail_task(recipients, subject, template, context):
   send_mail(
       subject=subject,
       message=render_template(f'{template}.txt', context),
       from_email=settings.DEFAULT_FROM_EMAIL,
       recipient_list=recipients,
       fail_silently=False,
       html_message=render_template(f'{template}.html', context)
   )

@app.task
def addd(a, b):
    c = a + b
    print(c)

