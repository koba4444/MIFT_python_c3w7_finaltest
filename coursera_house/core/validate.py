#using marshlow for validating forms

from marshmallow import Schema, fields
from marshmallow.validate import Length, Range

class SettingSchema(Schema):
    bedroom_target_temperature = fields.Int(validate=Range(16, 50), required=True)
    hot_water_target_temperature = fields.Int(validate=Range(24, 90), required=True)
    bedroom_light = fields.Bool()
    bathroom_light = fields.Bool()

