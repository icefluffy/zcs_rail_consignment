# -*- coding: utf-8 -*-
"""
UIC Wagon Code decoder — Python/Odoo 18 Community Edition
Ported from gc_wizard (Dart) – ERA Appendix 6 / P9 data.

JSON data files expected next to this module file:
  uic_country_codes.json
  uic_freight_classification_codes.json
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
# Duplicates (44, 49, 50 → BIH) are preserved as a list for display,
# but for fast single-result lookup the first entry wins.
_COUNTRY_LIST = _load_json("uic_country_codes.json")
_COUNTRY_BY_CODE: dict[str, dict] = {}
for _entry in reversed(_COUNTRY_LIST):          # reversed → first entry wins on dup
    _COUNTRY_BY_CODE[_entry["number_code"]] = {
        "name":        _entry["name"],
        "letter_code": _entry["letter_code"],
    }


# Freight classification: top-level key = digit-0 (str "0".."9")
#   → sub-key = digits-1-2 ("00".."99")
#   → sub-sub-key = digit-9 ("0".."9")
#   → value = concatenated character codes (str)
_FREIGHT_CLASSIFICATION: dict[str, dict[str, dict[str, str]]] = \
    _load_json("uic_freight_classification_codes.json")


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
#   d0      – wagon category / type group
#   d1      – wagon type / subtype qualifier
#   d0-d1   – together determine the wagon category (passenger/freight/special)
#   d2-d3   – country code (string, zero-padded to 2 digits)
#   d4-d8   – series / individual number
#   d9      – used together with d0-d3 for freight letter-code classification
#   d11     – check digit
#
# Freight letter code resolution uses the 3-level nested map:
#   [str(d0)] → [d1+d2 zero-padded to 2 digits? No → d2d3] → [str(d9)]
#
# From the Dart source, the freight classification key structure is:
#   level-1 key = str(d0)                   e.g. "0"
#   level-2 key = zero_pad(d2d3, 2)         e.g. "05"  (digits 2 and 3 = country digits)
#   level-3 key = str(d9)                   e.g. "7"
#
# Wagon category is determined by d0:
#   0-3   → freight wagon
#   4-8   → special/service/infrastructure wagon  (treated as "special" here)
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
        "wagon_category",         # "freight" | "passenger" | "special"
        "freight_letter_codes",   # list[str] – individual characters, freight only
        "d0", "d1", "d2d3", "d4_d8", "d9", "d10", "d11",
    )

    def __init__(self):
        for s in self.__slots__:
            setattr(self, s, None)
        self.freight_letter_codes = []
        self.valid = False
        self.check_digit_ok = False

    def to_dict(self):
        return {s: getattr(self, s) for s in self.__slots__}


def _luhn_check(digits: str) -> bool:
    """
    UIC uses a variant of the Luhn algorithm.
    Multiply alternate digits (starting from the rightmost non-check digit)
    by 2; sum all digits of the products; total mod 10 == 0.
    """
    total = 0
    for i, ch in enumerate(reversed(digits)):
        n = int(ch)
        if i % 2 == 1:          # every second digit from right
            n *= 2
            if n > 9:
                n -= 9
        total += n
    return total % 10 == 0


def _resolve_freight_letter_codes(d0: str, d2d3: str, d9: str) -> list[str]:
    """
    Look up the letter-code string in the 3-level nested freight map and
    return its characters as a sorted, deduplicated list.

    Returns [] when no entry is found (not an error – many combinations
    have no mapping).
    """
    level1 = _FREIGHT_CLASSIFICATION.get(d0, {})
    level2 = level1.get(d2d3, {})
    raw = level2.get(d9, "")
    raw = raw.strip()
    if not raw:
        return []
    return sorted(set(raw))       # deduplicate + sort, like the Dart UI does


def decode_uic_evn(raw: str) -> UICWagonDecodeResult:
    """
    Decode a UIC EVN (European Vehicle Number).

    Accepts the 12-digit string with or without spaces / dashes.
    Returns a UICWagonDecodeResult; check result.valid before using
    any other field.
    """
    result = UICWagonDecodeResult()
    result.raw = raw

    digits = "".join(c for c in raw if c.isdigit())
    if len(digits) != 12:
        return result

    result.valid = True
    result.d0    = digits[0]
    result.d1    = digits[1]
    result.d2d3  = digits[2:4]
    result.d4_d8 = digits[4:9]
    result.d9    = digits[9]
    result.d10   = digits[10]
    result.d11   = digits[11]

    # Check digit (digit 11 = last)
    result.check_digit_ok = _luhn_check(digits)

    # Country
    country = _COUNTRY_BY_CODE.get(result.d2d3, {})
    result.country_code        = result.d2d3
    result.country_name        = country.get("name")
    result.country_letter_code = country.get("letter_code")

    # Wagon category
    result.wagon_category = _WAGON_CATEGORY_BY_D0.get(result.d0, "unknown")

    # Freight letter codes (only meaningful for freight wagons)
    if result.wagon_category == "freight":
        result.freight_letter_codes = _resolve_freight_letter_codes(
            result.d0, result.d2d3, result.d9
        )

    return result


# ── Odoo model mixin ───────────────────────────────────────────────────────────


class RailWagonMixin(models.AbstractModel):
    """
    Mix into any wagon / rolling-stock model to get UIC decoding fields.

    Usage:
        class MyWagon(models.Model, RailWagonMixin):
            _name = "my.wagon"
            _inherit = ["rail.wagon.mixin"]
            ...
    """
    _name = "rail.wagon.mixin"
    _description = "UIC Wagon Code Mixin"

    uic_evn = fields.Char(
        string="UIC EVN (12 digits)",
        size=20,
        help="European Vehicle Number – 12 digits, spaces/dashes allowed.",
    )

    # ── Computed / decoded fields ──────────────────────────────────────────────

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
    uic_country_code = fields.Char(
        string="Country Code",
        compute="_compute_uic_decoded",
        store=True,
    )
    uic_country_name = fields.Char(
        string="Country",
        compute="_compute_uic_decoded",
        store=True,
    )
    uic_country_letter = fields.Char(
        string="Country Letter Code",
        compute="_compute_uic_decoded",
        store=True,
    )
    uic_wagon_category = fields.Selection(
        selection=[
            ("freight",   "Freight"),
            ("passenger", "Passenger"),
            ("special",   "Special / Infrastructure"),
            ("unknown",   "Unknown"),
        ],
        string="Wagon Category",
        compute="_compute_uic_decoded",
        store=True,
    )
    uic_freight_letter_codes = fields.Char(
        string="Freight Letter Codes",
        compute="_compute_uic_decoded",
        store=True,
        help="Individual letter codes from ERA Appendix 6 / P9 table, "
             "space-separated.  Only populated for freight wagons.",
    )
    uic_check_digit_ok = fields.Boolean(
        string="Check Digit Valid",
        compute="_compute_uic_decoded",
        store=True,
    )
    uic_decode_valid = fields.Boolean(
        string="EVN Parseable",
        compute="_compute_uic_decoded",
        store=True,
    )

    @api.depends("uic_evn")
    def _compute_uic_decoded(self):
        for rec in self:
            evn = rec.uic_evn or ""
            res = decode_uic_evn(evn)

            rec.uic_decode_valid         = res.valid
            rec.uic_check_digit_ok       = res.check_digit_ok
            rec.uic_country_code         = res.country_code
            rec.uic_country_name         = res.country_name
            rec.uic_country_letter       = res.country_letter_code
            rec.uic_wagon_category       = res.wagon_category if res.valid else False
            rec.uic_freight_letter_codes = (
                " ".join(res.freight_letter_codes)
                if res.freight_letter_codes else False
            )

            # ── Interoperability code (d0 + d1) ───────────────────────────────
            rec.uic_interoperability_code = (res.d0 + res.d1) if res.valid else False

            # ── Freight wagon type / gauge / axle from d0d1 ───────────────────
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
                    fwt, gauge, axle = "TEN/COTIF RIV", "Variable gauge", "Bogies"
                elif 40 <= type_int <= 49:
                    fwt, gauge, axle = "Other", "Fixed/variable gauge", "Single axles"
                elif 80 <= type_int <= 89:
                    fwt, gauge, axle = "Other", "Fixed/variable gauge", "Bogies"
            rec.uic_freight_wagon_type = fwt
            rec.uic_gauge_type         = gauge
            rec.uic_axle_type          = axle

            # ── Wagon class from d4 (first digit of series) ───────────────────
            if res.valid and res.wagon_category == "freight" and res.d4_d8:
                cls = _WAGON_CLASS.get(res.d4_d8[0], (False, False, False))
                rec.uic_wagon_class_number = cls[0]
                rec.uic_wagon_class_letter = cls[1]
                rec.uic_wagon_class_desc   = cls[2]
            else:
                rec.uic_wagon_class_number = False
                rec.uic_wagon_class_letter = False
                rec.uic_wagon_class_desc   = False

    # ── Utility methods ────────────────────────────────────────────────────────

    def action_decode_uic(self):
        """
        Call from a button to re-trigger decoding and show a wizard-style
        notification with the result.  Returns an ir.actions.client action.
        """
        self.ensure_one()
        res = decode_uic_evn(self.uic_evn or "")
        if not res.valid:
            return {
                "type":    "ir.actions.client",
                "tag":     "display_notification",
                "params": {
                    "title":   "UIC Decode",
                    "message": "Invalid or incomplete EVN – must be 12 digits.",
                    "type":    "warning",
                    "sticky":  False,
                },
            }
        lines = [
            f"Country:      {res.country_name or '?'} ({res.country_code})",
            f"Letter code:  {res.country_letter_code or '–'}",
            f"Category:     {res.wagon_category}",
            f"Check digit:  {'✓ OK' if res.check_digit_ok else '✗ FAIL'}",
        ]
        if res.freight_letter_codes:
            lines.append(f"Freight codes: {' '.join(res.freight_letter_codes)}")
        return {
            "type":    "ir.actions.client",
            "tag":     "display_notification",
            "params": {
                "title":   f"UIC EVN {self.uic_evn}",
                "message": "\n".join(lines),
                "type":    "info",
                "sticky":  True,
            },
        }

    def get_uic_decode_dict(self) -> dict:
        """Return the full decoded result as a plain dict (useful in RPC / tests)."""
        self.ensure_one()
        return decode_uic_evn(self.uic_evn or "").to_dict()
