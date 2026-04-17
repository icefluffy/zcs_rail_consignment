from odoo import models, fields

class RailCompanyCode(models.Model):
    _name = 'zcs.rail.company.code'
    _description = 'Railway Company Registry (RICS Codes)'

    code = fields.Char('Code', size=4, required=True)
    short_name = fields.Char('Short Name', size=64)
    full_name = fields.Char('Full Name', size=128)
    country = fields.Char('Country', size=2)
    url = fields.Char('URL', size=256)
