# -*- coding: utf-8 -*-
from odoo import models, fields, api

class RailConsignmentValidator(models.Model):
    _name = "rail.consignment.validator"
    _description = "European Vehicle Number (EVN) Validator"

    voorwerp_nummer = fields.Char(string="EVN (12 digits)", size=12)
    valid_evn = fields.Boolean(string="Valid EVN", readonly=True)
    type_code = fields.Char(string="Type Code", readonly=True)
    type_desc = fields.Char(string="Vehicle Type", readonly=True)
    country_code = fields.Char(string="Country Code", readonly=True)
    country_name = fields.Char(string="Country", readonly=True)
    keeper_code = fields.Char(string="Keeper Code", readonly=True)
    serial_number = fields.Char(string="Serial Number", readonly=True)
    check_digit = fields.Char(string="Check Digit", readonly=True)
    error_message = fields.Char(string="Error", readonly=True)

    def _decode_evn(self, evn):
        evn = (evn or "").strip().replace(" ", "").replace("-", "")
        if len(evn) != 12 or not evn.isdigit():
            return {
                "valid_evn": False,
                "error_message": "Enter exactly 12 digits.",
            }

        type_code = int(evn[0:2])
        country_code = int(evn[2:4])
        keeper_code = evn[4:8]
        serial_number = evn[8:11]
        check_digit = evn[11]

        type_desc = {
            30: "Locomotives (non-standard gauge)",
            31: "Locomotives (standard gauge)",
            32: "Electric locomotives",
            33: "Diesel locomotives",
            40: "Multiple units (non-standard)",
            41: "Multiple units (standard)",
            50: "Passenger coaches",
            80: "Freight wagons (standard)",
            81: "Freight wagons (other gauges)",
            82: "Freight wagons (special)",
            91: "Electric locomotives",
            92: "Diesel locomotives",
            93: "Shunting locomotives",
        }.get(type_code, f"Unknown type {type_code}")

        country_map = {
            11: "Germany", 12: "Belgium", 13: "Netherlands", 14: "Luxembourg",
            20: "France", 23: "Italy", 25: "Switzerland", 26: "Austria",
            30: "Czech Republic", 31: "Slovakia", 32: "Hungary", 33: "Poland",
            34: "Bulgaria", 35: "Spain", 36: "Portugal", 37: "Romania",
            40: "Sweden", 41: "Norway", 42: "Finland", 43: "Denmark",
            44: "Greece", 45: "Turkey", 46: "Serbia", 47: "Croatia",
            49: "Ireland", 51: "UK", 52: "Northern Ireland", 54: "North Macedonia",
            55: "Estonia", 56: "Latvia", 57: "Lithuania", 80: "Russia",
            85: "Ukraine", 86: "Belarus", 87: "Moldova", 88: "Kazakhstan",
        }
        country_name = country_map.get(country_code, f"Unknown country {country_code}")

        weights = [2, 1] * 6
        total = 0
        for i in range(11):
            v = int(evn[i]) * weights[i]
            total += v if v < 10 else v - 9
        calculated = (10 - (total % 10)) % 10
        valid = int(check_digit) == calculated

        return {
            "valid_evn": valid,
            "type_code": str(type_code),
            "type_desc": type_desc,
            "country_code": str(country_code),
            "country_name": country_name,
            "keeper_code": keeper_code,
            "serial_number": serial_number,
            "check_digit": check_digit,
            "error_message": "" if valid else f"Invalid check digit. Expected {calculated}.",
        }

    @api.onchange("voorwerp_nummer")
    def _onchange_voorwerp_nummer(self):
        for rec in self:
            vals = rec._decode_evn(rec.voorwerp_nummer)
            rec.update(vals)

    def action_validate_voorwerp(self):
        for rec in self:
            vals = rec._decode_evn(rec.voorwerp_nummer)
            rec.write(vals)