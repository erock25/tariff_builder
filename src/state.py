"""
Session state initialization for the Streamlit app.
"""

import copy
from datetime import date

import streamlit as st



def _default(key, value):
    """Set session state default if key not present."""
    if key not in st.session_state:
        st.session_state[key] = value


def init_session_state():
    """Initialize all session state keys with defaults."""

    # Schedule version — increment on import / reset to invalidate localStorage
    _default("sched_version", 1)

    # Basic info
    _default("basic_utility", "")
    _default("basic_name", "")
    _default("basic_sector", "Commercial")
    _default("basic_servicetype", "Bundled")
    _default("basic_description", "")
    _default("basic_source", "")
    _default("basic_sourceparent", "")
    _default("basic_startdate", date.today())
    _default("basic_eiaid", None)
    _default("basic_voltagecategory", "")
    _default("basic_phasewiring", "")
    _default("basic_peakkwcapacitymin", None)
    _default("basic_peakkwcapacitymax", None)

    # Energy rates
    _default("energy_periods", [{"label": "Period 0", "rate": 0.0, "adj": 0.0}])
    _default("energy_weekday_sched", [[0] * 24 for _ in range(12)])
    _default("energy_weekend_sched", [[0] * 24 for _ in range(12)])
    _default("energy_comments", "")

    # TOU Demand (optional)
    _default("demand_enabled", False)
    _default("demand_periods", [{"label": "Period 0", "rate": 0.0, "adj": 0.0}])
    _default("demand_weekday_sched", [[0] * 24 for _ in range(12)])
    _default("demand_weekend_sched", [[0] * 24 for _ in range(12)])
    _default("demand_rateunit", "kW")
    _default("demand_window", None)
    _default("demand_reactive", None)
    _default("demand_comments", "")

    # Flat demand (optional)
    _default("flat_enabled", False)
    _default("flat_periods", [{"label": "All Months", "rate": 0.0, "adj": 0.0}])
    _default("flat_months", [0] * 12)
    _default("flat_unit", "kW")

    # Fixed charges
    _default("fixed_charge", None)
    _default("fixed_charge_units", "$/month")
    _default("min_monthly_charge", None)
    _default("annual_min_charge", None)
