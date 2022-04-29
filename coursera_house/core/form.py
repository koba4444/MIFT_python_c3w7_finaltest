from django import forms


class ControllerForm(forms.Form):
    bedroom_target_temperature = forms.IntegerField(required=True)
    hot_water_target_temperature = forms.IntegerField(required=True)
    bedroom_light = forms.BooleanField(required=False)
    bathroom_light = forms.BooleanField(required=False)
