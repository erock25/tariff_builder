"""
Tab: Basic Info — utility, rate name, sector, dates, applicability.
"""

import streamlit as st

from src.constants import (
    SECTOR_OPTIONS,
    SERVICE_TYPE_OPTIONS,
    VOLTAGE_CATEGORIES,
    PHASE_OPTIONS,
)


def render_basic_info_tab():
    """Render the Basic Info configuration tab."""
    st.markdown("### Tariff Identification")
    st.caption("Fields marked with * are required for a valid tariff JSON.")

    c1, c2 = st.columns(2)
    with c1:
        st.session_state.basic_utility = st.text_input(
            "Utility Name *",
            value=st.session_state.basic_utility,
            help="Name of the utility company",
        )
        st.session_state.basic_name = st.text_input(
            "Rate Schedule Name *",
            value=st.session_state.basic_name,
            help="Name of the rate schedule (e.g., TOU-8 Option D)",
        )
        st.session_state.basic_sector = st.selectbox(
            "Sector *",
            options=SECTOR_OPTIONS,
            index=SECTOR_OPTIONS.index(st.session_state.basic_sector)
            if st.session_state.basic_sector in SECTOR_OPTIONS else 0,
        )
    with c2:
        st.session_state.basic_servicetype = st.selectbox(
            "Service Type",
            options=SERVICE_TYPE_OPTIONS,
            index=SERVICE_TYPE_OPTIONS.index(st.session_state.basic_servicetype)
            if st.session_state.basic_servicetype in SERVICE_TYPE_OPTIONS else 0,
        )
        st.session_state.basic_startdate = st.date_input(
            "Effective Date",
            value=st.session_state.basic_startdate,
        )
        eiaid_val = st.session_state.basic_eiaid
        eiaid_str = str(eiaid_val) if eiaid_val else ""
        eiaid_input = st.text_input(
            "EIA ID", value=eiaid_str, help="EIA utility identifier (integer)"
        )
        st.session_state.basic_eiaid = (
            int(eiaid_input) if eiaid_input.strip().isdigit() else None
        )

    st.markdown("---")
    st.markdown("### Description & Source")
    st.session_state.basic_description = st.text_area(
        "Description",
        value=st.session_state.basic_description,
        height=80,
        help="Rate schedule description or notes",
    )
    c1, c2 = st.columns(2)
    with c1:
        st.session_state.basic_source = st.text_input(
            "Source URL",
            value=st.session_state.basic_source,
            help="Link to the tariff document (PDF, web page)",
        )
    with c2:
        st.session_state.basic_sourceparent = st.text_input(
            "Source Parent URL",
            value=st.session_state.basic_sourceparent,
            help="Link to the parent tariff page",
        )

    st.markdown("---")
    st.markdown("### Applicability Criteria")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        vc = st.session_state.basic_voltagecategory
        st.session_state.basic_voltagecategory = st.selectbox(
            "Voltage Category",
            options=VOLTAGE_CATEGORIES,
            index=VOLTAGE_CATEGORIES.index(vc) if vc in VOLTAGE_CATEGORIES else 0,
        )
    with c2:
        pw = st.session_state.basic_phasewiring
        st.session_state.basic_phasewiring = st.selectbox(
            "Phase Wiring",
            options=PHASE_OPTIONS,
            index=PHASE_OPTIONS.index(pw) if pw in PHASE_OPTIONS else 0,
        )
    with c3:
        val = st.session_state.basic_peakkwcapacitymin
        inp = st.text_input(
            "Demand Min (kW)", value=str(val) if val is not None else ""
        )
        try:
            st.session_state.basic_peakkwcapacitymin = (
                float(inp) if inp.strip() else None
            )
        except ValueError:
            st.session_state.basic_peakkwcapacitymin = None
    with c4:
        val = st.session_state.basic_peakkwcapacitymax
        inp = st.text_input(
            "Demand Max (kW)", value=str(val) if val is not None else ""
        )
        try:
            st.session_state.basic_peakkwcapacitymax = (
                float(inp) if inp.strip() else None
            )
        except ValueError:
            st.session_state.basic_peakkwcapacitymax = None
