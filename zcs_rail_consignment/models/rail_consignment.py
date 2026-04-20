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
    technical_code = fields.Char(string="Technical Code (digits 5-8)", readonly=True)
    technical_desc = fields.Char(string="Technical Description", readonly=True)
    serial_number = fields.Char(string="Serial Number", readonly=True)
    check_digit = fields.Char(string="Check Digit", readonly=True)
    error_message = fields.Char(string="Error", readonly=True)
    #company_code = fields.Char(string="Company Code", readonly=True)
    #company_short_name = fields.Char(string="Company Short Name", readonly=True)
    #company_full_name = fields.Char(string="Company Full Name", readonly=True)

    def _decode_evn(self, evn):
        evn = (evn or "").strip().replace(" ", "").replace("-", "")
        if len(evn) != 12 or not evn.isdigit():
            return {
                "valid_evn": False,
                "error_message": "Enter exactly 12 digits.",
                #"company_code": False,
                #"company_short_name": False,
                #"company_full_name": False,
            }

        type_code = int(evn[0:2])
        country_code = int(evn[2:4])
        technical_code = str(evn[4:8])
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
            10: "Finland",
            20: "Russia",
            21: "Belarus",
            22: "Ukraine",
            23: "Moldova",
            24: "Lithuania",
            25: "Latvia",
            26: "Estonia",
            27: "Kazakhstan",
            28: "Georgia",
            29: "Uzbekistan",
            30: "North Korea",
            31: "Mongolia",
            32: "Vietnam",
            33: "China",
            34: "Laos",
            40: "Cuba",
            41: "Albania",
            42: "Japan",
            44: "Bosnia and Herzegovina, Serb Republic of",
            49: "Bosnia and Herzegovina",
            50: "Bosnia and Herzegovina, Muslim-Croat Federation of",
            51: "Poland",
            52: "Bulgaria",
            53: "Romania",
            54: "Czech Republic",
            55: "Hungary",
            56: "Slovakia",
            57: "Azerbaijan",
            58: "Armenia",
            59: "Kyrgyzstan",
            60: "Ireland",
            61: "South Korea",
            62: "Montenegro",
            65: "North Macedonia",
            66: "Tajikistan",
            67: "Turkmenistan",
            68: "Afghanistan",
            70: "United Kingdom",
            71: "Spain",
            72: "Serbia",
            73: "Greece",
            74: "Sweden",
            75: "Turkey",
            76: "Norway",
            78: "Croatia",
            79: "Slovenia",
            80: "Germany",
            81: "Austria",
            82: "Luxembourg",
            83: "Italy",
            84: "Netherlands",
            85: "Switzerland",
            86: "Denmark",
            87: "France",
            88: "Belgium",
            89: "Tanzania",
            90: "Egypt",
            91: "Tunisia",
            92: "Algeria",
            93: "Morocco",
            94: "Portugal",
            95: "Israel",
            96: "Iran",
            97: "Syria",
            98: "Lebanon",
            99: "Iraq",
        }
        country_name = country_map.get(country_code, f"Unknown country {country_code}")

        # Freight wagon class (digit 5 = evn[4])
        WAGON_CLASS = {
            "0": "T - Wagon with opening roof",
            "1": "G - Ordinary covered wagon",
            "2": "H - Special covered wagon",
            "3": "K/R/O - Flat wagon (separate axles or bogies)",
            "4": "L/S - Special flat wagon",
            "5": "E - Ordinary open high-sided wagon",
            "6": "F - Special open high-sided wagon",
            "7": "Z - Tank wagon",
            "8": "I - Refrigerated/temperature controlled",
            "9": "U - Special wagon",
        }

        # Only decode for freight wagons (type_code 0x-8x)
        if 80 <= type_code <= 89:
            # Freight wagons: digit 5 = wagon class
            wagon_class_digit = evn[4]
            technical_desc = WAGON_CLASS.get(wagon_class_digit, f"Unknown class digit {wagon_class_digit}")
        elif type_code >= 90:
            # Traction (locos, MUs): digits 5-8 = class number
            technical_desc = f"Loco/MU class {technical_code}"
        else:
            # Passenger coaches, special vehicles: not yet decoded
            technical_desc = f"Technical code {technical_code} (type {type_code})"

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
            "technical_code": technical_code,
            "technical_desc": technical_desc,
            "serial_number": serial_number,
            "check_digit": check_digit,
            "error_message": "" if valid else f"Invalid check digit. Expected {calculated}.",
            #"company_code": technical_code,
            #"company_short_name": company.short_name if company else False,
            #"company_full_name": company.full_name if company else False,
        }

    @api.onchange("voorwerp_nummer")
    def _onchange_voorwerp_nummer(self):
        for rec in self:
            rec.update(rec._decode_evn(rec.voorwerp_nummer))

    def action_validate_voorwerp(self):
        for rec in self:
            rec.write(rec._decode_evn(rec.voorwerp_nummer))
