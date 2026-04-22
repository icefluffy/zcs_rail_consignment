# models/my_wagon.py
from odoo import models, fields
from .uic_wagon_mixin import RailWagonMixin   # adjust import path

class RailCodeWagon(models.Model, RailWagonMixin):
    _name = "rail.code.wagon"
    _inherit = ["rail.wagon.mixin"]
    _description = "Rail Wagon"

    name = fields.Char(required=True)
    # uic_evn, uic_country_name, uic_wagon_category, etc. all come from the mixin