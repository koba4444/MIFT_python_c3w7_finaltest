import json

import requests
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views.generic import FormView
from .tasks import smart_home_manager, send_mail_task, addd

from .models import Setting
from .form import ControllerForm
from .validate import SettingSchema
from ..settings import SMART_HOME_API_URL, SMART_HOME_ACCESS_TOKEN, CONTROLLER_WRITABLES


class ControllerView(FormView):
    form_class = ControllerForm
    template_name = 'core/control.html'
    success_url = reverse_lazy('form')


# Validate controller form
    def get(self, request):
        cont = self.get_context_data()

        try:
            item = Setting.objects.get(controller_name="bedroom_target_temperature")
            cont["form"].fields["bedroom_target_temperature"].initial = item.value or 21
            item = Setting.objects.get(controller_name="hot_water_target_temperature")
            cont["form"].fields["hot_water_target_temperature"].initial = item.value or 80
            cont["form"].fields["bedroom_light"].initial = cont["data"]["bedroom_light"]
            cont["form"].fields["bathroom_light"].initial = cont["data"]["bathroom_light"]
            return self.render_to_response(cont)
        except:
            cont = {
                "bedroom_target_temperature": 21,
                "hot_water_target_temperature": 80,
                "bedroom_light": 0,
                "bathroom_light": 0
            }
            return self.render_to_response(cont)

    def get_context_data(self, **kwargs):
        context = super(ControllerView, self).get_context_data()

        headers = {"Authorization": "Bearer " + SMART_HOME_ACCESS_TOKEN}
        r = json.loads(requests.get(SMART_HOME_API_URL, headers=headers).text)
        curr_values = dict([(i['name'], i['value']) for i in r["data"]])
        context['data'] = curr_values



        return context

    def get_initial(self):
        return {}

    def form_valid(self, form):

        try:
            cont = self.get_context_data()
            form_data = form.cleaned_data
            for controller_key, controller_val in form_data.items():
                if controller_key not in CONTROLLER_WRITABLES:
                    obj = Setting.objects.get(controller_name=controller_key)
                    obj.value = controller_val
                    obj.save()
                else:
                    cont['data'][controller_key] = controller_val

                # Recording "bedroom_light" and "bathroom_light" to site via API
            data_for_post_request = {
                "controllers": [
                    {"name": controller_key, "value": controller_val}
                    for controller_key, controller_val in cont['data'].items()
                    if controller_key in CONTROLLER_WRITABLES
                ]
            }

            headers = {"Authorization": "Bearer " + SMART_HOME_ACCESS_TOKEN}
            data = json.dumps(data_for_post_request)
            r1 = requests.post(SMART_HOME_API_URL, headers=headers, data=data)
            pass

        except:
            return HttpResponse('No connection to controllers API', status=502)

        #super(ControllerView, self).form_valid(form)
        smart_home_manager.delay()
        addd.delay(1, 2)

        #send_mail_task.delay(('noreply@example.com',), 'Celery cookbook test', 'test', {})
        return super(ControllerView, self).form_valid(form)

