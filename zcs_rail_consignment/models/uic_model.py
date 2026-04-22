from enum import Enum

class FreightGaugeType(Enum):
    FIXED = "fixed"
    VARIABLE = "variable"
    BOTH_POSSIBLE = "both_possible"
    INVALID = "invalid"

class FreightAxleType(Enum):
    SINGLE = "single"
    BOGIE = "bogie"
    INVALID = "invalid"

class FreightWagonType(Enum):
    NORMAL_PPW = "normal_ppw"
    NORMAL_TEN_RIV = "normal_ten_riv"
    NORMAL_TEN_INTERFRIGO = "normal_ten_interfrigo"
    MAINTENANCE = "maintenance"
    MISC = "misc"
    NOT_IN_EU_REGISTERED = "not_in_eu_registered"
    FRIDGE_LEGACY = "fridge_legacy"
    INVALID = "invalid"

def _get_freight_wagon_type(n1, n2):
    if n1 in (0, 1, 2, 3):
        if n2 == 0: return FreightWagonType.INVALID
        if n1 in (0, 1) and n2 in (3, 4, 5, 6, 7, 8): return FreightWagonType.FRIDGE_LEGACY
        if n2 == 9: return FreightWagonType.NORMAL_PPW
        if n1 in (0, 1): return FreightWagonType.NORMAL_TEN_INTERFRIGO
        if n1 in (2, 3): return FreightWagonType.NORMAL_TEN_RIV
        return FreightWagonType.INVALID
    else:
        if n2 == 0: return FreightWagonType.MAINTENANCE
        if n2 == 9: return FreightWagonType.NOT_IN_EU_REGISTERED
        return FreightWagonType.MISC

def _get_gauge_type(n1, n2):
    if n1 in (4, 8) and n2 in (0, 9): return FreightGaugeType.BOTH_POSSIBLE
    if n1 in (0, 1) and n2 == 9:      return FreightGaugeType.VARIABLE
    if n1 in (2, 3) and n2 == 9:      return FreightGaugeType.FIXED
    if n2 in (2, 4, 6, 8):            return FreightGaugeType.VARIABLE
    if n2 in (1, 3, 5, 7):            return FreightGaugeType.FIXED
    return FreightGaugeType.INVALID

def _get_axle_type(n1):
    if n1 in (0, 2, 4): return FreightAxleType.SINGLE
    if n1 in (1, 3, 8): return FreightAxleType.BOGIE
    return FreightAxleType.INVALID