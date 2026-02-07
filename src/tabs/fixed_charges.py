"""
Tab: Fixed Charges — fixed monthly, minimum, and annual charges.
"""

import streamlit as st


def render_fixed_charges_tab():
    """Render the Fixed Charges configuration tab."""
    st.markdown("### Fixed Monthly Charges")
    st.caption("These charges apply regardless of usage or demand levels.")

    c1, c2 = st.columns(2)
    with c1:
        fc = st.session_state.fixed_charge
        fc_str = st.text_input(
            "Fixed Charge (first meter)",
            value=f"{fc:.2f}" if fc is not None else "",
            help="Monthly fixed charge for the first meter ($)",
        )
        try:
            st.session_state.fixed_charge = (
                float(fc_str) if fc_str.strip() else None
            )
        except ValueError:
            st.session_state.fixed_charge = None

    with c2:
        st.session_state.fixed_charge_units = st.text_input(
            "Units",
            value=st.session_state.fixed_charge_units,
            help='Typically "$/month"',
        )

    st.markdown("---")
    st.markdown("### Minimum Charges")

    c1, c2 = st.columns(2)
    with c1:
        mc = st.session_state.min_monthly_charge
        mc_str = st.text_input(
            "Minimum Monthly Charge ($)",
            value=f"{mc:.2f}" if mc is not None else "",
            help="Minimum charge applied to the monthly bill if usage charges are lower",
        )
        try:
            st.session_state.min_monthly_charge = (
                float(mc_str) if mc_str.strip() else None
            )
        except ValueError:
            st.session_state.min_monthly_charge = None

    with c2:
        ac = st.session_state.annual_min_charge
        ac_str = st.text_input(
            "Annual Minimum Charge ($)",
            value=f"{ac:.2f}" if ac is not None else "",
            help="Minimum charge applied across the full year",
        )
        try:
            st.session_state.annual_min_charge = (
                float(ac_str) if ac_str.strip() else None
            )
        except ValueError:
            st.session_state.annual_min_charge = None
