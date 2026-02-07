"""
Constants and configuration values for the URDB Tariff Builder.
"""

MONTH_NAMES = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
               "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

SECTOR_OPTIONS = ["Commercial", "Residential", "Industrial", "Lighting"]
SERVICE_TYPE_OPTIONS = ["Bundled", "Delivery", "Energy"]
VOLTAGE_CATEGORIES = ["", "Secondary", "Primary", "Transmission"]
PHASE_OPTIONS = ["", "Single Phase", "3-Phase", "Single and 3-Phase"]
DEMAND_UNIT_OPTIONS = ["kW", "hp", "kVA", "kW daily", "hp daily", "kVA daily"]

DEFAULT_ENERGY_PERIODS = [
    {"label": "Off-Peak", "rate": 0.08, "adj": 0.0},
    {"label": "Mid-Peak", "rate": 0.15, "adj": 0.0},
    {"label": "On-Peak", "rate": 0.25, "adj": 0.0},
]

DEFAULT_DEMAND_PERIODS = [
    {"label": "Off-Peak", "rate": 0.0, "adj": 0.0},
    {"label": "On-Peak", "rate": 15.0, "adj": 0.0},
]

# Local DB -> API field mapping for import normalization
FIELD_MAP = {
    "utilityName": "utility",
    "rateName": "name",
    "eiaId": "eiaid",
    "serviceType": "servicetype",
    "voltageCategory": "voltagecategory",
    "phaseWiring": "phasewiring",
    "demandMin": "peakkwcapacitymin",
    "demandMax": "peakkwcapacitymax",
    "energyMin": "peakkwhusagemin",
    "energyMax": "peakkwhusagemax",
    "demandUnits": "demandunits",
    "demandRateUnit": "demandrateunit",
    "flatDemandUnit": "flatdemandunit",
    "flatDemandMonths": "flatdemandmonths",
    "fixedChargeFirstMeter": "fixedchargefirstmeter",
    "fixedChargeUnits": "fixedchargeunits",
    "minMonthlyCharge": "minmonthlycharge",
    "demandLabels": "demandtoulabels",
    "energyTOULabels": "energytoulabels",
    "energyComments": "energycomments",
    "demandComments": "demandcomments",
    "energyRateStrux": "energyratestructure",
    "energyWeekdaySched": "energyweekdayschedule",
    "energyWeekendSched": "energyweekendschedule",
    "demandRateStrux": "demandratestructure",
    "demandWeekdaySched": "demandweekdayschedule",
    "demandWeekendSched": "demandweekendschedule",
    "flatDemandStrux": "flatdemandstructure",
}
