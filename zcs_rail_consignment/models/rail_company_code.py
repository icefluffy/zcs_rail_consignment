# -*- coding: utf-8 -*-
from odoo import models, fields


class RailCompanyCode(models.Model):
    _name = "rail.company.code"
    _description = "Railway Company Registry (RICS Codes)"

    code = fields.Char(string="Code", size=4, required=True)
    short_name = fields.Char(string="Short Name", size=64)
    full_name = fields.Char(string="Full Name", size=128)
    country = fields.Char(string="Country", size=2)
    url = fields.Char(string="URL", size=256)

    _sql_constraints = [
        ("rail_company_code_unique", "unique(code)", "Company code must be unique."),
    ]