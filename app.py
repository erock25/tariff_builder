"""
URDB Tariff JSON Builder

Build complete URDB-compatible tariff JSON files from scratch or by importing
and editing existing tariffs. Features interactive schedule painting grids,
configurable energy and demand rate periods, and structured export.

Run:
    streamlit run app.py
"""

import streamlit as st

from src.state import init_session_state
from src.sidebar import render_sidebar
from src.tabs.basic_info import render_basic_info_tab
from src.tabs.energy_rates import render_energy_rates_tab
from src.tabs.tou_demand import render_tou_demand_tab
from src.tabs.flat_demand import render_flat_demand_tab
from src.tabs.fixed_charges import render_fixed_charges_tab
from src.tabs.review_export import render_export_tab


def main():
    st.set_page_config(
        page_title="URDB Tariff Builder",
        page_icon="🏗️",
        layout="wide",
    )

    init_session_state()
    render_sidebar()

    st.title("URDB Tariff JSON Builder")
    st.caption(
        "Build a complete URDB-compatible tariff JSON from scratch, "
        "or import an existing tariff to edit."
    )

    tabs = st.tabs([
        "Basic Info",
        "Energy Rates",
        "TOU Demand",
        "Flat Demand",
        "Fixed Charges",
        "Review & Export",
    ])

    with tabs[0]:
        render_basic_info_tab()
    with tabs[1]:
        render_energy_rates_tab()
    with tabs[2]:
        render_tou_demand_tab()
    with tabs[3]:
        render_flat_demand_tab()
    with tabs[4]:
        render_fixed_charges_tab()
    with tabs[5]:
        render_export_tab()


if __name__ == "__main__":
    main()
