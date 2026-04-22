# -*- coding: utf-8 -*-
from odoo import models, fields

class RailUICWagon(models.Model):
    _name = "rail.uic.wagon"
    _description = "UIC Wagon Code Decoder"
    _inherit = ["rail.wagon.mixin"]

    name = fields.Char(string="Reference", required=True, default="New")
    notes = fields.Text(string="Notes")