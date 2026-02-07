"""
Tariff import and export functionality.

Handles loading URDB JSON into session state and building export JSON
from session state.
"""

import copy
from datetime import datetime, date
from typing import Dict, List, Optional

import streamlit as st

from src.constants import DEFAULT_ENERGY_PERIODS
from src.utils import normalize_tariff, extract_periods_from_structure


def import_tariff_data(raw: Dict) -> None:
    """Populate session state from an imported tariff dict."""
    # Unwrap items array
    if "items" in raw and isinstance(raw["items"], list) and raw["items"]:
        tariff = raw["items"][0]
    else:
        tariff = raw

    t = normalize_tariff(tariff)

    # Increment version so grids re-initialize from session state
    st.session_state.sched_version = st.session_state.get("sched_version", 0) + 1

    # Clear stale widget keys so text inputs pick up fresh imported values
    # (Streamlit caches widget values by key; without clearing, period 0's
    # inputs would still show values from the previous session.)
    for prefix in ("energy", "demand", "flat"):
        for idx in range(12):
            for suffix in (f"_lbl_{idx}", f"_rate_{idx}", f"_adj_{idx}"):
                key = prefix + suffix
                if key in st.session_state:
                    del st.session_state[key]
        num_key = f"{prefix}_num_periods"
        if num_key in st.session_state:
            del st.session_state[num_key]

    # Basic info
    st.session_state.basic_utility = t.get("utility", "")
    st.session_state.basic_name = t.get("name", "")
    st.session_state.basic_sector = t.get("sector", "Commercial")
    st.session_state.basic_servicetype = t.get("servicetype", "Bundled")
    st.session_state.basic_description = t.get("description", "")
    st.session_state.basic_source = t.get("source", "")
    st.session_state.basic_sourceparent = t.get("sourceparent", "")
    st.session_state.basic_eiaid = t.get("eiaid", None)
    st.session_state.basic_voltagecategory = t.get("voltagecategory", "")
    st.session_state.basic_phasewiring = t.get("phasewiring", "")
    st.session_state.basic_peakkwcapacitymin = t.get("peakkwcapacitymin", None)
    st.session_state.basic_peakkwcapacitymax = t.get("peakkwcapacitymax", None)

    sd = t.get("startdate")
    if sd and isinstance(sd, (int, float)):
        try:
            st.session_state.basic_startdate = datetime.fromtimestamp(sd).date()
        except (ValueError, OSError):
            st.session_state.basic_startdate = date.today()
    else:
        st.session_state.basic_startdate = date.today()

    # Energy rates
    e_struct = t.get("energyratestructure", [])
    e_labels = t.get("energytoulabels", [])
    if e_struct:
        st.session_state.energy_periods = extract_periods_from_structure(
            e_struct, e_labels, "Period"
        )
    else:
        st.session_state.energy_periods = copy.deepcopy(DEFAULT_ENERGY_PERIODS)
    st.session_state.energy_weekday_sched = t.get(
        "energyweekdayschedule", [[0] * 24 for _ in range(12)]
    )
    st.session_state.energy_weekend_sched = t.get(
        "energyweekendschedule", [[0] * 24 for _ in range(12)]
    )
    st.session_state.energy_comments = t.get("energycomments", "")

    # TOU Demand
    d_struct = t.get("demandratestructure", [])
    d_labels = t.get("demandtoulabels", [])
    if d_struct:
        st.session_state.demand_enabled = True
        st.session_state.demand_periods = extract_periods_from_structure(
            d_struct, d_labels, "Period"
        )
        st.session_state.demand_weekday_sched = t.get(
            "demandweekdayschedule", [[0] * 24 for _ in range(12)]
        )
        st.session_state.demand_weekend_sched = t.get(
            "demandweekendschedule", [[0] * 24 for _ in range(12)]
        )
    else:
        st.session_state.demand_enabled = False
    st.session_state.demand_rateunit = t.get("demandrateunit", "kW")
    st.session_state.demand_window = t.get("demandwindow", None)
    st.session_state.demand_reactive = t.get("demandreactivepowercharge", None)
    st.session_state.demand_comments = t.get("demandcomments", "")

    # Flat demand
    f_struct = t.get("flatdemandstructure", [])
    f_months = t.get("flatdemandmonths", [])
    if f_struct:
        st.session_state.flat_enabled = True
        st.session_state.flat_periods = []
        for idx, tiers in enumerate(f_struct):
            rate, adj = 0.0, 0.0
            if isinstance(tiers, list) and tiers:
                tier = tiers[0]
                if isinstance(tier, dict):
                    rate = float(tier.get("rate", 0) or 0)
                    adj = float(tier.get("adj", 0) or 0)
            st.session_state.flat_periods.append(
                {"label": f"Season {idx}", "rate": rate, "adj": adj}
            )
        st.session_state.flat_months = (
            f_months if len(f_months) == 12 else [0] * 12
        )
    else:
        st.session_state.flat_enabled = False
    st.session_state.flat_unit = t.get("flatdemandunit", "kW")

    # Fixed charges
    st.session_state.fixed_charge = t.get("fixedchargefirstmeter", None)
    st.session_state.fixed_charge_units = t.get("fixedchargeunits", "$/month")
    st.session_state.min_monthly_charge = t.get("minmonthlycharge", None)
    st.session_state.annual_min_charge = t.get("annualmincharge", None)


def build_tariff_json(
    energy_wd: Optional[List] = None,
    energy_we: Optional[List] = None,
    demand_wd: Optional[List] = None,
    demand_we: Optional[List] = None,
) -> Dict:
    """Assemble the complete tariff JSON from session state.

    Schedule parameters override session state when provided (used by the
    JS export component reading from localStorage).
    """
    ss = st.session_state
    tariff: Dict = {}

    # Basic info
    if ss.basic_utility:
        tariff["utility"] = ss.basic_utility
    if ss.basic_name:
        tariff["name"] = ss.basic_name
    tariff["sector"] = ss.basic_sector
    if ss.basic_servicetype:
        tariff["servicetype"] = ss.basic_servicetype
    if ss.basic_description:
        tariff["description"] = ss.basic_description
    if ss.basic_source:
        tariff["source"] = ss.basic_source
    if ss.basic_sourceparent:
        tariff["sourceparent"] = ss.basic_sourceparent
    if ss.basic_startdate:
        tariff["startdate"] = int(
            datetime.combine(ss.basic_startdate, datetime.min.time()).timestamp()
        )
    if ss.basic_eiaid:
        tariff["eiaid"] = int(ss.basic_eiaid)
    if ss.basic_voltagecategory:
        tariff["voltagecategory"] = ss.basic_voltagecategory
    if ss.basic_phasewiring:
        tariff["phasewiring"] = ss.basic_phasewiring
    if ss.basic_peakkwcapacitymin is not None:
        tariff["peakkwcapacitymin"] = ss.basic_peakkwcapacitymin
    if ss.basic_peakkwcapacitymax is not None:
        tariff["peakkwcapacitymax"] = ss.basic_peakkwcapacitymax

    # Energy rates
    ep = ss.energy_periods
    tariff["energyratestructure"] = [
        [{"unit": "kWh", "rate": p["rate"], "adj": p["adj"]}] for p in ep
    ]
    tariff["energytoulabels"] = [p["label"] for p in ep]
    tariff["energyweekdayschedule"] = energy_wd or ss.energy_weekday_sched
    tariff["energyweekendschedule"] = energy_we or ss.energy_weekend_sched
    if ss.energy_comments:
        tariff["energycomments"] = ss.energy_comments

    # TOU Demand
    if ss.demand_enabled and ss.demand_periods:
        dp = ss.demand_periods
        tariff["demandrateunit"] = ss.demand_rateunit
        tariff["demandunits"] = ss.demand_rateunit
        tariff["demandratestructure"] = [
            [{"rate": p["rate"], "adj": p["adj"]}] for p in dp
        ]
        tariff["demandtoulabels"] = [p["label"] for p in dp]
        tariff["demandweekdayschedule"] = demand_wd or ss.demand_weekday_sched
        tariff["demandweekendschedule"] = demand_we or ss.demand_weekend_sched
        if ss.demand_window is not None:
            tariff["demandwindow"] = ss.demand_window
        if ss.demand_reactive is not None:
            tariff["demandreactivepowercharge"] = ss.demand_reactive
        if ss.demand_comments:
            tariff["demandcomments"] = ss.demand_comments

    # Flat demand
    if ss.flat_enabled and ss.flat_periods:
        fp = ss.flat_periods
        tariff["flatdemandunit"] = ss.flat_unit
        tariff["flatdemandstructure"] = [
            [{"rate": p["rate"], "adj": p["adj"]}] for p in fp
        ]
        tariff["flatdemandmonths"] = ss.flat_months

    # Fixed charges
    if ss.fixed_charge is not None:
        tariff["fixedchargefirstmeter"] = ss.fixed_charge
        tariff["fixedchargeunits"] = ss.fixed_charge_units
    if ss.min_monthly_charge is not None:
        tariff["minmonthlycharge"] = ss.min_monthly_charge
    if ss.annual_min_charge is not None:
        tariff["annualmincharge"] = ss.annual_min_charge

    tariff["country"] = "USA"
    return {"items": [tariff]}
