"""
Tariff validation logic.
"""

from typing import Dict, List

import streamlit as st


def validate_tariff() -> List[Dict]:
    """Return list of {level, msg} validation results."""
    issues: List[Dict] = []
    ss = st.session_state

    if not ss.basic_utility:
        issues.append({"level": "error", "msg": "Utility name is required."})
    if not ss.basic_name:
        issues.append({"level": "error", "msg": "Rate name is required."})
    if not ss.energy_periods:
        issues.append({"level": "error", "msg": "At least one energy rate period is required."})
    if ss.demand_enabled and not ss.demand_periods:
        issues.append({"level": "error", "msg": "TOU Demand is enabled but has no periods defined."})
    if ss.flat_enabled and not ss.flat_periods:
        issues.append({"level": "error", "msg": "Flat Demand is enabled but has no periods defined."})

    # Warnings
    if not ss.basic_description:
        issues.append({"level": "warn", "msg": "No description provided (optional)."})
    if not ss.basic_source:
        issues.append({"level": "warn", "msg": "No source URL provided (optional)."})
    if ss.fixed_charge is None:
        issues.append({"level": "warn", "msg": "No fixed monthly charge set (optional)."})
    if not ss.demand_enabled:
        issues.append({"level": "info", "msg": "TOU Demand charges are not enabled."})
    if not ss.flat_enabled:
        issues.append({"level": "info", "msg": "Flat Demand charges are not enabled."})

    return issues
