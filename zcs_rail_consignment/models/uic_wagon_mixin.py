# -*- coding: utf-8 -*-
"""
UIC Wagon Code decoder — Python/Odoo 18 Community Edition
Ported from gc_wizard (Dart) – ERA Appendix 6 / P9 data.

JSON data files expected under the module's data/ folder:
  uic_country_codes.json
  uic_freight_classification_codes.json
  uic_freight_classification_descriptions.json
"""

import json
import os
import logging
from odoo import models, fields, api

_logger = logging.getLogger(__name__)

# ── Data loading ───────────────────────────────────────────────────────────────

def _data_path(filename):
    return os.path.join(os.path.dirname(__file__), '..', 'data', filename)

def _load_json(filename):
    with open(_data_path(filename), encoding="utf-8") as fh:
        return json.load(fh)

# Country lookup: number_code (str) → {name, letter_code}
# Duplicates (44, 49, 50 → BIH) are preserved; first entry wins on dup.
_COUNTRY_LIST = _load_json("uic_country_codes.json")
_COUNTRY_BY_CODE: dict[str, dict] = {}
for _entry in reversed(_COUNTRY_LIST):
    _COUNTRY_BY_CODE[_entry["number_code"]] = {
        "name":        _entry["name"],
        "letter_code": _entry["letter_code"],
    }

# Freight classification codes: d0 → d2d3 → d9 → concatenated letter code string
_FREIGHT_CLASSIFICATION: dict[str, dict[str, dict[str, str]]] = \
    _load_json("uic_freight_classification_codes.json")

# Freight letter code descriptions:
# letter_code (lowercase) → { i18n_key: [wagon_class_letters, ...], ... }
_FREIGHT_DESCRIPTIONS_RAW: dict[str, dict[str, list[str]]] = \
    _load_json("uic_freight_classification_descriptions.json")

# Human-readable descriptions keyed by the i18n key suffix (e.g. "a_1").
_FREIGHT_CODE_DESCRIPTIONS: dict[str, str] = {
    # a
    "a_1": "4 axles",
    "a_2": "4 axles",
    "a_3": "4 axles",
    # aa
    "aa_1": "6 axles",
    "aa_2": "6 axles",
    "aa_3": "6 axles",
    # aaa
    "aaa_1": "8 axles",
    # b
    "b_1": "loading length >= 18.4 m",
    "b_2": "loading length >= 18.4 m",
    "b_3": "loading length >= 18.4 m",
    "b_4": "loading length >= 18.4 m",
    "b_5": "loading length >= 18.4 m",
    "b_6": "loading length >= 18.4 m",
    "b_7": "loading length >= 18.4 m",
    "b_8": "loading length >= 18.4 m",
    "b_9": "loading length >= 18.4 m",
    # bb
    "bb_1": "loading length >= 22.5 m",
    "bb_2": "loading length >= 22.5 m",
    "bb_3": "loading length >= 22.5 m",
    # c
    "c_1": "load limit D",
    "c_2": "load limit D",
    "c_3": "load limit D",
    "c_4": "load limit D",
    "c_5": "load limit D",
    "c_6": "load limit D",
    # cc
    "cc_1": "load limit D + higher",
    "cc_2": "load limit D + higher",
    # d
    "d_1": "load limit E",
    "d_2": "load limit E",
    "d_3": "load limit E",
    "d_4": "load limit E",
    # dd
    "dd_1": "load limit E + higher",
    # e
    "e_1": "load limit F",
    "e_2": "load limit F",
    "e_3": "load limit F",
    "e_4": "load limit F",
    "e_5": "load limit F",
    "e_6": "load limit F",
    # ee
    "ee_1": "load limit F + higher",
    # f
    "f_1": "rolling floor",
    # ff
    "ff_1": "rolling floor (both ends)",
    # fff
    "fff_1": "rolling floor (all)",
    # g
    "g_1": "approved for trains up to 120 km/h",
    "g_2": "approved for trains up to 120 km/h",
    "g_3": "approved for trains up to 120 km/h",
    "g_4": "approved for trains up to 120 km/h",
    "g_5": "approved for trains up to 120 km/h",
    # gg
    "gg_1": "approved for trains up to 120 km/h (higher)",
    "gg_2": "approved for trains up to 120 km/h (higher)",
    # h
    "h_1": "automatic emptying device",
    "h_2": "automatic emptying device",
    "h_3": "automatic emptying device",
    # hh
    "hh_1": "automatic emptying device (both sides)",
    # i
    "i_1": "with individual axle load-dependent braking",
    "i_2": "with individual axle load-dependent braking",
    "i_3": "with individual axle load-dependent braking",
    "i_4": "with individual axle load-dependent braking",
    "i_5": "with individual axle load-dependent braking",
    # ii
    "ii_2": "with individual axle load-dependent braking (higher)",
    # j
    "j_1": "special coupling",
    # k
    "k_1": "braked with disc brakes",
    "k_2": "braked with disc brakes",
    "k_3": "braked with disc brakes",
    "k_4": "braked with disc brakes",
    "k_5": "braked with disc brakes",
    # kk
    "kk_1": "braked with disc brakes (both bogies)",
    "kk_2": "braked with disc brakes (both bogies)",
    "kk_3": "braked with disc brakes (both bogies)",
    # l
    "l_1": "approx. carrying capacity >= 60 t",
    "l_2": "approx. carrying capacity >= 60 t",
    "l_3": "approx. carrying capacity >= 60 t",
    "l_4": "approx. carrying capacity >= 60 t",
    "l_5": "approx. carrying capacity >= 60 t",
    "l_6": "approx. carrying capacity >= 60 t",
    # ll
    "ll_1": "approx. carrying capacity >= 80 t",
    "ll_2": "approx. carrying capacity >= 80 t",
    # m
    "m_1": "load mass m > 60 t (load limit C)",
    "m_2": "load mass m > 60 t (load limit C)",
    "m_3": "load mass m > 60 t (load limit C)",
    "m_4": "load mass m > 60 t (load limit C)",
    "m_5": "load mass m > 60 t (load limit C)",
    "m_6": "load mass m > 60 t (load limit C)",
    "m_7": "load mass m > 60 t (load limit C)",
    "m_8": "load mass m > 60 t (load limit C)",
    "m_9": "load mass m > 60 t (load limit C)",
    "m_10": "load mass m > 60 t (load limit C)",
    # mm
    "mm_1": "load mass m > 80 t (load limit C)",
    "mm_2": "load mass m > 80 t (load limit C)",
    "mm_3": "load mass m > 80 t (load limit C)",
    # n
    "n_1": "loading mass m > 60 t (load limit C)",
    "n_2": "loading mass m > 60 t (load limit C)",
    "n_3": "loading mass m > 60 t (load limit C)",
    "n_4": "loading mass m > 60 t (load limit C)",
    "n_5": "loading mass m > 60 t (load limit C)",
    "n_6": "loading mass m > 60 t (load limit C)",
    "n_7": "loading mass m > 60 t (load limit C)",
    # o
    "o_1": "not front tiltable",
    "o_2": "not front tiltable",
    "o_3": "not front tiltable",
    "o_4": "not front tiltable",
    "o_5": "not front tiltable",
    "o_6": "not front tiltable",
    "o_7": "not front tiltable",
    # oo
    "oo_1": "not tiltable",
    "oo_2": "not tiltable",
    # p
    "p_1": "pneumatic emptying device",
    "p_2": "pneumatic emptying device",
    "p_3": "pneumatic emptying device",
    "p_4": "pneumatic emptying device",
    # pp
    "pp_1": "pneumatic emptying device (double)",
    "pp_2": "pneumatic emptying device (double)",
    # q
    "q_1": "with EP brake",
    # qq
    "qq_1": "with EP brake (higher)",
    # r
    "r_1": "approved for trains up to 100 km/h",
    "r_2": "approved for trains up to 100 km/h",
    # rr
    "rr_1": "approved for trains up to 100 km/h (higher)",
    # s
    "s_1": "approved for trains up to 100 km/h",
    # ss
    "ss_1": "approved for trains up to 120 km/h",
}

def _resolve_letter_description(letter_code: str, wagon_class_letter: str) -> str:
    """
    Given a single lowercase letter code (e.g. 'a') and the wagon class
    letter (e.g. 'E'), return the human-readable description string.
    Falls back to the raw key suffix if not in the translation table.
    """
    entry = _FREIGHT_DESCRIPTIONS_RAW.get(letter_code, {})
    for i18n_key, wagon_list in entry.items():
        if wagon_class_letter in wagon_list:
            parts = i18n_key.split("_")
            suffix = "_".join(parts[3:])
            return _FREIGHT_CODE_DESCRIPTIONS.get(suffix, suffix)
    return letter_code

# Wagon class lookup: d4 digit → (number_code, letter_code, description)
_WAGON_CLASS = {
    "0": ("0", "T", "Opening roof wagon"),
    "1": ("1", "G", "Ordinary covered wagon"),
    "2": ("2", "H", "Special covered wagon"),
    "3": ("3", "K", "Flat wagon (2-axle)"),
    "4": ("4", "L", "Special flat wagon"),
    "5": ("5", "E", "Ordinary open high-sided wagon"),
    "6": ("6", "F", "Special open high-sided wagon"),
    "7": ("7", "Z", "Tank wagon"),
    "8": ("8", "I", "Temperature controlled wagon"),
    "9": ("9", "U", "Special wagon"),
}

# ── UIC structure constants ────────────────────────────────────────────────────
#
# A UIC EVN (European Vehicle Number) is 12 digits:
#
#   d0  d1  d2  d3  d4  d5  d6  d7  d8  d9 d10 d11
#   [0] [1] [2] [3] [4] [5] [6] [7] [8] [9][10][11]
#
#   d0-d1   – interoperability / wagon type code
#   d2-d3   – country code
#   d4-d8   – series / individual number
#   d9      – used for freight letter-code classification
#   d11     – check digit
#
# Wagon category is determined by d0:
#   0-3   → freight wagon
#   4-8   → special/service/infrastructure wagon
#   9     → passenger/coaching stock

_WAGON_CATEGORY_BY_D0 = {
    "0": "freight", "1": "freight", "2": "freight", "3": "freight",
    "4": "special", "5": "special", "6": "special",
    "7": "special", "8": "special",
    "9": "passenger",
}

# ── Core decoder ───────────────────────────────────────────────────────────────


class UICWagonDecodeResult:
    """Plain data object returned by decode_uic_evn()."""

    __slots__ = (
        "raw", "valid", "check_digit_ok",
        "country_code", "country_name", "country_letter_code",
        "wagon_category",
        "freight_letter_codes",
        "freight_letter_descs",
        "d0", "d1", "d2d3", "d4_d8", "d9", "d10", "d11",
    )

    def __init__(self):
        for s in self.__slots__:
            setattr(self, s, None)
        self.freight_letter_codes = []
        self.freight_letter_descs = []
        self.valid = False
        self.check_digit_ok = False

    def to_dict(self):
        return {s: getattr(self, s) for s in self.__slots__}


def _luhn_check(digits: str) -> bool:
    total = 0
    for i, ch in enumerate(reversed(digits)):
        n = int(ch)
        if i % 2 == 1:
            n *= 2
            if n > 9:
                n -= 9
        total += n
    return total % 10 == 0


def _resolve_freight_letter_codes(d0: str, d2d3: str, d9: str) -> list[str]:
    level1 = _FREIGHT_CLASSIFICATION.get(d0, {})
    level2 = level1.get(d2d3, {})
    raw = level2.get(d9, "").strip()
    if not raw:
        return []
    return sorted(set(raw))


def decode_uic_evn(raw: str) -> UICWagonDecodeResult:
    result = UICWagonDecodeResult()
    result.raw = raw

    digits = "".join(c for c in raw if c.isdigit())
    if len(digits) != 12:
        return result

    result.valid = True
    result.d0 = digits[0]
    result.d1 = digits[1]
    result.d2d3 = digits[2:4]
    result.d4_d8 = digits[4:9]
    result.d9 = digits[9]
    result.d10 = digits[10]
    result.d11 = digits[11]

    result.check_digit_ok = _luhn_check(digits)

    country = _COUNTRY_BY_CODE.get(result.d2d3, {})
    result.country_code = result.d2d3
    result.country_name = country.get("name")
    result.country_letter_code = country.get("letter_code")

    result.wagon_category = _WAGON_CATEGORY_BY_D0.get(result.d0, "unknown")

    if result.wagon_category == "freight":
        result.freight_letter_codes = _resolve_freight_letter_codes(
            result.d0, result.d2d3, result.d9
        )
        cls_letter = False
        if result.d4_d8:
            cls_letter = _WAGON_CLASS.get(result.d4_d8[0], (False, False, False))[1]
        if cls_letter:
            result.freight_letter_descs = [
                (lc, _resolve_letter_description(lc, cls_letter))
                for lc in result.freight_letter_codes
            ]

    return result


# ── Odoo model mixin ───────────────────────────────────────────────────────────


class RailWagonMixin(models.AbstractModel):
    """
    Mix into any wagon / rolling-stock model to get UIC decoding fields.

    Usage:
        class MyWagon(models.Model):
            _name = "my.wagon"
            _inherit = ["rail.wagon.mixin"]
    """
    _name = "rail.wagon.mixin"
    _description = "UIC Wagon Code Mixin"

    uic_evn = fields.Char(
        string="UIC EVN (12 digits)",
        size=20,
        help="European Vehicle Number - 12 digits, spaces/dashes allowed.",
    )

    uic_interoperability_code = fields.Char(
        string="Interoperability Code",
        compute="_compute_uic_decoded", store=True,
    )
    uic_freight_wagon_type = fields.Char(
        string="Freight Wagon Type",
        compute="_compute_uic_decoded", store=True,
    )
    uic_gauge_type = fields.Char(
        string="Gauge Type",
        compute="_compute_uic_decoded", store=True,
    )
    uic_axle_type = fields.Char(
        string="Axle Type",
        compute="_compute_uic_decoded", store=True,
    )
    uic_wagon_class_number = fields.Char(
        string="Class Number Code",
        compute="_compute_uic_decoded", store=True,
    )
    uic_wagon_class_letter = fields.Char(
        string="Class Letter Code",
        compute="_compute_uic_decoded", store=True,
    )
    uic_wagon_class_desc = fields.Char(
        string="Class Description",
        compute="_compute_uic_decoded", store=True,
    )
    uic_classification_code = fields.Char(
        string="Classification Code",
        compute="_compute_uic_decoded", store=True,
        help="Combined wagon class letter + freight letter codes (e.g. 'Eanos').",
    )
    uic_country_code = fields.Char(
        string="Country Code",
        compute="_compute_uic_decoded", store=True,
    )
    uic_country_name = fields.Char(
        string="Country",
        compute="_compute_uic_decoded", store=True,
    )
    uic_country_letter = fields.Char(
        string="Country Letter Code",
        compute="_compute_uic_decoded", store=True,
    )
    uic_wagon_category = fields.Selection(
        selection=[
            ("freight", "Freight"),
            ("passenger", "Passenger"),
            ("special", "Special / Infrastructure"),
            ("unknown", "Unknown"),
        ],
        string="Wagon Category",
        compute="_compute_uic_decoded", store=True,
    )
    uic_freight_letter_codes = fields.Char(
        string="Freight Letter Codes",
        compute="_compute_uic_decoded", store=True,
        help="Individual letter codes from ERA Appendix 6 / P9 table, "
             "space-separated. Only populated for freight wagons.",
    )
    uic_max_speed = fields.Char(
        string="Max Speed",
        compute="_compute_uic_decoded", store=True,
    )
    uic_load_capacity = fields.Char(
        string="Load Capacity",
        compute="_compute_uic_decoded", store=True,
    )
    uic_axle_count = fields.Char(
        string="Axle Count",
        compute="_compute_uic_decoded", store=True,
    )
    uic_lc1_code = fields.Char(string="Code 1", compute="_compute_uic_decoded", store=True)
    uic_lc1_desc = fields.Char(string="Description 1", compute="_compute_uic_decoded", store=True)
    uic_lc2_code = fields.Char(string="Code 2", compute="_compute_uic_decoded", store=True)
    uic_lc2_desc = fields.Char(string="Description 2", compute="_compute_uic_decoded", store=True)
    uic_lc3_code = fields.Char(string="Code 3", compute="_compute_uic_decoded", store=True)
    uic_lc3_desc = fields.Char(string="Description 3", compute="_compute_uic_decoded", store=True)
    uic_lc4_code = fields.Char(string="Code 4", compute="_compute_uic_decoded", store=True)
    uic_lc4_desc = fields.Char(string="Description 4", compute="_compute_uic_decoded", store=True)
    uic_lc5_code = fields.Char(string="Code 5", compute="_compute_uic_decoded", store=True)
    uic_lc5_desc = fields.Char(string="Description 5", compute="_compute_uic_decoded", store=True)
    uic_lc6_code = fields.Char(string="Code 6", compute="_compute_uic_decoded", store=True)
    uic_lc6_desc = fields.Char(string="Description 6", compute="_compute_uic_decoded", store=True)
    uic_lc7_code = fields.Char(string="Code 7", compute="_compute_uic_decoded", store=True)
    uic_lc7_desc = fields.Char(string="Description 7", compute="_compute_uic_decoded", store=True)
    uic_lc8_code = fields.Char(string="Code 8", compute="_compute_uic_decoded", store=True)
    uic_lc8_desc = fields.Char(string="Description 8", compute="_compute_uic_decoded", store=True)

    uic_check_digit_ok = fields.Boolean(
        string="Check Digit Valid",
        compute="_compute_uic_decoded", store=True,
    )
    uic_decode_valid = fields.Boolean(
        string="EVN Parseable",
        compute="_compute_uic_decoded", store=True,
    )

    @api.depends("uic_evn")
    def _compute_uic_decoded(self):
        for rec in self:
            evn = rec.uic_evn or ""
            res = decode_uic_evn(evn)

            rec.uic_decode_valid = res.valid
            rec.uic_check_digit_ok = res.check_digit_ok
            rec.uic_country_code = res.country_code
            rec.uic_country_name = res.country_name
            rec.uic_country_letter = res.country_letter_code
            rec.uic_wagon_category = res.wagon_category if res.valid else False
            rec.uic_freight_letter_codes = (
                " ".join(res.freight_letter_codes)
                if res.freight_letter_codes else False
            )

            rec.uic_interoperability_code = (res.d0 + res.d1) if res.valid else False

            fwt = gauge = axle = False
            if res.valid:
                type_int = int(res.d0 + res.d1)
                if 0 <= type_int <= 9:
                    fwt, gauge, axle = "TEN/COTIF RIV", "Fixed gauge", "Single axles"
                elif 10 <= type_int <= 19:
                    fwt, gauge, axle = "TEN/COTIF RIV", "Fixed gauge", "Bogies"
                elif 20 <= type_int <= 29:
                    fwt, gauge, axle = "TEN/COTIF RIV", "Variable gauge", "Single axles"
                elif 30 <= type_int <= 39:
                    fwt, gauge, axle = "TEN/COTIF RIV", "Fixed gauge", "Bogies"
                elif 40 <= type_int <= 49:
                    fwt, gauge, axle = "Other", "Fixed/variable gauge", "Single axles"
                elif 80 <= type_int <= 89:
                    fwt, gauge, axle = "Other", "Fixed/variable gauge", "Bogies"
            rec.uic_freight_wagon_type = fwt
            rec.uic_gauge_type = gauge
            rec.uic_axle_type = axle

            cls_letter = False
            if res.valid and res.wagon_category == "freight" and res.d4_d8:
                cls = _WAGON_CLASS.get(res.d4_d8[0], (False, False, False))
                rec.uic_wagon_class_number = cls[0]
                rec.uic_wagon_class_letter = cls[1]
                rec.uic_wagon_class_desc = cls[2]
                cls_letter = cls[1]
            else:
                rec.uic_wagon_class_number = False
                rec.uic_wagon_class_letter = False
                rec.uic_wagon_class_desc = False

            if cls_letter and res.freight_letter_codes:
                rec.uic_classification_code = cls_letter + "".join(res.freight_letter_codes)
            elif cls_letter:
                rec.uic_classification_code = cls_letter
            else:
                rec.uic_classification_code = False

            lc_set = set(res.freight_letter_codes) if res.freight_letter_codes else set()

            if "ss" in lc_set:
                rec.uic_max_speed = "120 km/h"
            elif "s" in lc_set or "g" in lc_set:
                rec.uic_max_speed = "100 km/h"
            elif "rr" in lc_set:
                rec.uic_max_speed = "100 km/h (special)"
            elif "r" in lc_set:
                rec.uic_max_speed = "100 km/h"
            else:
                rec.uic_max_speed = False

            if "ll" in lc_set:
                rec.uic_load_capacity = ">= 80 t"
            elif "l" in lc_set:
                rec.uic_load_capacity = ">= 60 t"
            elif "mm" in lc_set:
                rec.uic_load_capacity = "> 80 t"
            elif "m" in lc_set:
                rec.uic_load_capacity = "> 60 t"
            else:
                rec.uic_load_capacity = False

            if "aaa" in lc_set:
                rec.uic_axle_count = "8 axles"
            elif "aa" in lc_set:
                rec.uic_axle_count = "6 axles"
            elif "a" in lc_set:
                rec.uic_axle_count = "4 axles"
            else:
                rec.uic_axle_count = False

            descs = res.freight_letter_descs or []
            for i in range(1, 9):
                if i <= len(descs):
                    setattr(rec, f"uic_lc{i}_code", descs[i - 1][0])
                    setattr(rec, f"uic_lc{i}_desc", descs[i - 1][1])
                else:
                    setattr(rec, f"uic_lc{i}_code", False)
                    setattr(rec, f"uic_lc{i}_desc", False)

    def action_decode_uic(self):
        self.ensure_one()
        res = decode_uic_evn(self.uic_evn or "")
        if not res.valid:
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": "UIC Decode",
                    "message": "Invalid or incomplete EVN - must be 12 digits.",
                    "type": "warning",
                    "sticky": False,
                },
            }
        lines = [
            f"Country:      {res.country_name or '?'} ({res.country_code})",
            f"Letter code:  {res.country_letter_code or '-'}",
            f"Category:     {res.wagon_category}",
            f"Check digit:  {'OK' if res.check_digit_ok else 'FAIL'}",
        ]
        if res.freight_letter_codes:
            lines.append(f"Freight codes: {' '.join(res.freight_letter_codes)}")
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": f"UIC EVN {self.uic_evn}",
                "message": "\n".join(lines),
                "type": "info",
                "sticky": True,
            },
        }

    def get_uic_decode_dict(self) -> dict:
        self.ensure_one()
        return decode_uic_evn(self.uic_evn or "").to_dict()