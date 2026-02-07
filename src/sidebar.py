"""
Sidebar rendering: import, reset, and status display.
"""

import json

import streamlit as st

from src.tariff_io import import_tariff_data
from src.validation import validate_tariff


def render_sidebar():
    """Render the sidebar with import, reset, and status sections."""
    with st.sidebar:
        st.header("URDB Tariff Builder")

        # Import section
        st.subheader("Import Tariff")
        uploaded = st.file_uploader(
            "Load existing URDB JSON",
            type=["json"],
            help="Import an existing tariff to edit. Supports both API and local DB formats.",
        )

        if uploaded is not None:
            try:
                raw = json.loads(uploaded.read().decode("utf-8"))
                if st.button("Load Tariff", type="primary", use_container_width=True):
                    import_tariff_data(raw)
                    st.success(
                        f"Loaded: **{st.session_state.basic_name}** "
                        f"({st.session_state.basic_utility})"
                    )
                    st.rerun()
            except Exception as e:
                st.error(f"Error parsing JSON: {e}")

        st.markdown("---")

        # Reset
        if st.button("Reset to Defaults", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

        st.markdown("---")

        # Configuration summary
        st.subheader("Status")

        ss = st.session_state
        has_utility = bool(ss.basic_utility)
        has_name = bool(ss.basic_name)

        st.markdown(
            f"- Utility: {'**' + ss.basic_utility + '**' if has_utility else 'Not set'}\n"
            f"- Rate: {'**' + ss.basic_name + '**' if has_name else 'Not set'}\n"
            f"- Sector: {ss.basic_sector}\n"
            f"- Energy Periods: {len(ss.energy_periods)}\n"
            f"- TOU Demand: {'Enabled (' + str(len(ss.demand_periods)) + ' periods)' if ss.demand_enabled else 'Disabled'}\n"
            f"- Flat Demand: {'Enabled (' + str(len(ss.flat_periods)) + ' periods)' if ss.flat_enabled else 'Disabled'}\n"
            f"- Fixed Charge: {'$' + f'{ss.fixed_charge:.2f}' if ss.fixed_charge else 'Not set'}"
        )

        errors = [i for i in validate_tariff() if i["level"] == "error"]
        if errors:
            st.caption(f":red[{len(errors)} validation error(s)]")
        else:
            st.caption(":green[Ready to export]")
