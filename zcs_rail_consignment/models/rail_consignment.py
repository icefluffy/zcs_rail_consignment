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
            0:  "Spare",
            1:  "Fixed-axle wagon, fixed gauge, railway undertaking owned, TSI compliant",
            2:  "Fixed-axle wagon, variable gauge, railway undertaking owned, TSI compliant",
            9:  "Fixed-axle wagon, variable gauge, PPW compliant",
            10: "Bogie wagon, fixed or variable gauge, used by industry",
            11: "Bogie wagon, fixed gauge, railway undertaking owned, TSI compliant",
            12: "Bogie wagon, variable gauge, railway undertaking owned, TSI compliant",
            19: "Bogie wagon, variable gauge, PPW compliant",
            20: "Spare",
            21: "Fixed-axle wagon, fixed gauge, railway undertaking owned, TSI compliant",
            22: "Fixed-axle wagon, variable gauge, railway undertaking owned, TSI compliant",
            23: "Fixed-axle wagon, fixed gauge, TSI compliant",
            24: "Fixed-axle wagon, variable gauge, TSI compliant",
            25: "Fixed-axle wagon, fixed gauge, TSI compliant",
            26: "Fixed-axle wagon, variable gauge, TSI compliant",
            27: "Fixed-axle wagon, fixed gauge, TSI compliant",
            28: "Fixed-axle wagon, variable gauge, TSI compliant",
            29: "Fixed-axle wagon, fixed gauge, PPW compliant",
            30: "Spare",
            31: "Bogie wagon, fixed gauge, railway undertaking owned, TSI compliant",
            32: "Bogie wagon, variable gauge, railway undertaking owned, TSI compliant",
            33: "Bogie wagon, fixed gauge, TSI compliant",
            34: "Bogie wagon, variable gauge, TSI compliant",
            35: "Bogie wagon, fixed gauge, TSI compliant",
            36: "Bogie wagon, variable gauge, TSI compliant",
            37: "Bogie wagon, fixed gauge, TSI compliant",
            38: "Bogie wagon, variable gauge, TSI compliant",
            39: "Bogie wagon, fixed gauge, PPW compliant",
            40: "Fixed-axle wagon, fixed or variable gauge, non-TSI compliant service wagon",
            41: "Fixed-axle wagon, fixed gauge, railway undertaking owned, non-TSI compliant",
            42: "Fixed-axle wagon, variable gauge, railway undertaking owned, non-TSI compliant",
            43: "Fixed-axle wagon, fixed gauge, non-TSI compliant",
            44: "Fixed-axle wagon, variable gauge, non-TSI compliant",
            45: "Fixed-axle wagon, fixed gauge, non-TSI compliant",
            46: "Fixed-axle wagon, variable gauge, non-TSI compliant",
            47: "Fixed-axle wagon, fixed gauge, non-TSI compliant",
            48: "Fixed-axle wagon, variable gauge, non-TSI compliant",
            49: "Fixed-axle wagon, non-TSI compliant, special numbering for technical characteristics",
            50: "Hauled passenger coach",
            51: "Hauled passenger coach",
            52: "Hauled passenger coach",
            53: "Hauled passenger coach",
            54: "Hauled passenger coach",
            55: "Hauled passenger coach",
            56: "Hauled passenger coach",
            57: "Hauled passenger coach",
            58: "Hauled passenger coach",
            59: "Hauled passenger coach",
            60: "Hauled passenger coach",
            61: "Hauled passenger coach",
            62: "Hauled passenger coach",
            63: "Hauled passenger coach",
            64: "Hauled passenger coach",
            65: "Hauled passenger coach",
            66: "Hauled passenger coach",
            67: "Hauled passenger coach",
            68: "Hauled passenger coach",
            69: "Hauled passenger coach",
            70: "Hauled passenger coach",
            71: "Hauled passenger coach",
            72: "Hauled passenger coach",
            73: "Hauled passenger coach",
            74: "Hauled passenger coach",
            75: "Hauled passenger coach",
            76: "Hauled passenger coach",
            77: "Hauled passenger coach",
            78: "Hauled passenger coach",
            79: "Hauled passenger coach",
            80: "Bogie wagon, fixed or variable gauge, non-TSI compliant service wagon",
            81: "Bogie wagon, fixed gauge, railway undertaking owned, non-TSI compliant",
            82: "Bogie wagon, variable gauge, railway undertaking owned, non-TSI compliant",
            83: "Bogie wagon, fixed gauge, non-TSI compliant",
            84: "Bogie wagon, variable gauge, non-TSI compliant",
            85: "Bogie wagon, fixed gauge, non-TSI compliant",
            86: "Bogie wagon, variable gauge, non-TSI compliant",
            87: "Bogie wagon, fixed gauge, non-TSI compliant",
            88: "Bogie wagon, variable gauge, non-TSI compliant",
            89: "Bogie wagon, non-TSI compliant, special numbering for technical characteristics",
            90: "Miscellaneous tractive unit",
            91: "Electric locomotive",
            92: "Diesel locomotive",
            93: "Electric multiple unit (high speed) power car or trailer",
            94: "Electric multiple unit (not high speed) power car or trailer",
            95: "Diesel multiple unit power car or trailer",
            96: "Specialised trailer",
            97: "Electric shunter",
            98: "Diesel shunter",
            99: "Special vehicle",
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

        # Digits 6-8 sub-characteristics, keyed by digit 5 (class)
        # Format: WAGON_SUBTYPE[digit5][digits6to8] = description
        # digits6to8 is a 3-character string e.g. "000", "012", "123"
        
        WAGON_SUBTYPE = {
        
            # ── G: Ordinary Covered Wagon (1xxx) ──────────────────────────────────
            "1": {
                "000": "2 axles, load gauge G1, up to 22.5t axle load, max 100 km/h",
                "001": "2 axles, load gauge G1, up to 20t axle load, max 100 km/h",
                "002": "2 axles, load gauge G1, sliding walls, max 100 km/h",
                "003": "2 axles, load gauge G1, sliding walls + opening roof, max 100 km/h",
                "004": "2 axles, load gauge G1, special fittings, max 100 km/h",
                "010": "2 axles, load gauge G2, up to 22.5t axle load, max 100 km/h",
                "011": "2 axles, load gauge G2, up to 20t axle load, max 100 km/h",
                "012": "2 axles, load gauge G2, sliding walls, max 100 km/h",
                "020": "2 axles, load gauge G1, max 120 km/h",
                "021": "2 axles, load gauge G1, sliding walls, max 120 km/h",
                "030": "2 axles, load gauge G2, max 120 km/h",
                "100": "Bogie wagon, load gauge G1, up to 22.5t axle load, max 100 km/h",
                "101": "Bogie wagon, load gauge G1, up to 20t axle load, max 100 km/h",
                "102": "Bogie wagon, load gauge G1, sliding walls, max 100 km/h",
                "103": "Bogie wagon, load gauge G1, sliding walls + opening roof, max 100 km/h",
                "110": "Bogie wagon, load gauge G2, up to 22.5t axle load, max 100 km/h",
                "111": "Bogie wagon, load gauge G2, up to 20t axle load, max 100 km/h",
                "120": "Bogie wagon, load gauge G1, max 120 km/h",
                "121": "Bogie wagon, load gauge G1, sliding walls, max 120 km/h",
                "130": "Bogie wagon, load gauge G2, max 120 km/h",
                "200": "2 axles, load gauge G1, bulk discharge, max 100 km/h",
                "300": "Bogie wagon, load gauge G1, bulk discharge, max 100 km/h",
            },
        
            # ── E: Ordinary open high-sided wagon (5xxx) ──────────────────────────
            "5": {
                "000": "2 axles, load gauge G1, up to 22.5t axle load, max 100 km/h",
                "001": "2 axles, load gauge G1, up to 20t axle load, max 100 km/h",
                "010": "2 axles, load gauge G2, up to 22.5t axle load, max 100 km/h",
                "020": "2 axles, load gauge G1, max 120 km/h",
                "100": "Bogie wagon, load gauge G1, up to 22.5t axle load, max 100 km/h",
                "110": "Bogie wagon, load gauge G2, up to 22.5t axle load, max 100 km/h",
                "120": "Bogie wagon, load gauge G1, max 120 km/h",
                "200": "2 axles, self-discharge, max 100 km/h",
                "300": "Bogie wagon, self-discharge, max 100 km/h",
            },
        
            # ── Z: Tank wagon (7xxx) ──────────────────────────────────────────────
            "7": {
                "000": "2 axles, non-pressurised, up to 22.5t axle load, max 100 km/h",
                "001": "2 axles, non-pressurised, up to 20t axle load, max 100 km/h",
                "010": "2 axles, pressurised, up to 22.5t axle load, max 100 km/h",
                "020": "2 axles, non-pressurised, max 120 km/h",
                "030": "2 axles, pressurised, max 120 km/h",
                "100": "Bogie wagon, non-pressurised, up to 22.5t axle load, max 100 km/h",
                "110": "Bogie wagon, pressurised, up to 22.5t axle load, max 100 km/h",
                "120": "Bogie wagon, non-pressurised, max 120 km/h",
                "130": "Bogie wagon, pressurised, max 120 km/h",
                "200": "2 axles, cryogenic (liquefied gas), max 100 km/h",
                "300": "Bogie wagon, cryogenic (liquefied gas), max 100 km/h",
            },
        
            # ── K/R/O: Flat wagon (3xxx) ──────────────────────────────────────────
            "3": {
                "000": "2 axles (K), load gauge G1, up to 22.5t axle load, max 100 km/h",
                "001": "2 axles (K), load gauge G1, up to 20t axle load, max 100 km/h",
                "010": "2 axles (K), load gauge G2, max 100 km/h",
                "020": "2 axles (K), load gauge G1, max 120 km/h",
                "100": "Bogie wagon (R), load gauge G1, up to 22.5t axle load, max 100 km/h",
                "101": "Bogie wagon (R), load gauge G1, up to 20t axle load, max 100 km/h",
                "110": "Bogie wagon (R), load gauge G2, max 100 km/h",
                "120": "Bogie wagon (R), load gauge G1, max 120 km/h",
                "200": "Composite flat wagon (O), max 100 km/h",
            },
        
            # ── Remaining classes: add as needed ─────────────────────────────────
            # "0": { ... },  # T - opening roof
            # "2": { ... },  # H - special covered
            # "4": { ... },  # L/S - special flat
            # "6": { ... },  # F - special open
            # "8": { ... },  # I - temperature controlled
            # "9": { ... },  # U - special
        }

        # Only decode for freight wagons (type_code 0x-8x)
        if 80 <= type_code <= 89:
            # Freight wagons: digit 5 = wagon class, digits 6-8 = sub-characteristics
            wagon_class_digit = evn[4]
            digits_6_to_8 = evn[5:8]
        
            wagon_class_desc = WAGON_CLASS.get(wagon_class_digit, f"Unknown class {wagon_class_digit}")
            subtype_map = WAGON_SUBTYPE.get(wagon_class_digit, {})
            subtype_desc = subtype_map.get(digits_6_to_8, f"Sub-type {digits_6_to_8} (not yet decoded)")
        
            technical_desc = f"{wagon_class_desc} | {subtype_desc}"
        
        elif type_code >= 90:
            # Traction (locos, MUs): digits 5-8 = class number, no sub-decode
            technical_desc = f"Loco/MU class {technical_code}"
        
        else:
            # Passenger coaches (5x), multiple units (4x), special vehicles: not yet decoded
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
