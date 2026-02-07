"""
Tab: TOU Demand — optional TOU demand periods and schedule painting.
"""

import copy

import streamlit as st

from src.constants import DEMAND_UNIT_OPTIONS, DEFAULT_DEMAND_PERIODS
from src.utils import assign_heatmap_colors
from src.components import create_grid_html, render_rate_period_editor


def render_tou_demand_tab():
    """Render the TOU Demand configuration tab."""
    was_enabled = st.session_state.demand_enabled
    st.session_state.demand_enabled = st.toggle(
        "Enable TOU Demand Charges",
        value=st.session_state.demand_enabled,
        help="Toggle on to add Time-of-Use demand charges ($/kW) to the tariff.",
    )

    # When first enabled, reset schedules and bump version to clear stale localStorage
    if st.session_state.demand_enabled and not was_enabled:
        st.session_state.demand_weekday_sched = [[0] * 24 for _ in range(12)]
        st.session_state.demand_weekend_sched = [[0] * 24 for _ in range(12)]
        st.session_state.sched_version = st.session_state.get("sched_version", 0) + 1

    if not st.session_state.demand_enabled:
        st.info(
            "TOU demand charges are **disabled**. Toggle on above to configure "
            "demand rate periods and paint demand schedules."
        )
        return

    st.markdown("### TOU Demand Settings")
    c1, c2, c3 = st.columns(3)
    with c1:
        ru = st.session_state.demand_rateunit
        st.session_state.demand_rateunit = st.selectbox(
            "Demand Rate Unit",
            options=DEMAND_UNIT_OPTIONS,
            index=DEMAND_UNIT_OPTIONS.index(ru) if ru in DEMAND_UNIT_OPTIONS else 0,
            key="demand_rateunit_sel",
        )
    with c2:
        dw = st.session_state.demand_window
        dw_str = st.text_input(
            "Demand Window (min)",
            value=str(dw) if dw else "",
            key="demand_window_inp",
        )
        try:
            st.session_state.demand_window = (
                float(dw_str) if dw_str.strip() else None
            )
        except ValueError:
            st.session_state.demand_window = None
    with c3:
        dr = st.session_state.demand_reactive
        dr_str = st.text_input(
            "Reactive Power ($/kVAR)",
            value=str(dr) if dr else "",
            key="demand_reactive_inp",
        )
        try:
            st.session_state.demand_reactive = (
                float(dr_str) if dr_str.strip() else None
            )
        except ValueError:
            st.session_state.demand_reactive = None

    st.markdown("---")
    st.markdown("### TOU Demand Rate Periods")

    render_rate_period_editor(
        periods_key="demand_periods",
        prefix="demand",
        rate_unit="$/kW",
        default_periods=DEFAULT_DEMAND_PERIODS,
    )

    st.markdown("---")
    st.markdown("### Demand Weekday Schedule (Mon–Fri)")
    st.caption(
        "Paint the demand TOU schedule. Period indices map to the demand rate periods above."
    )

    demand_show_rates = st.toggle(
        "Show rates on grid cells",
        value=True,
        key="demand_show_rates",
        help="Display the total rate (base + adjustment) on each cell in the demand schedule grids.",
    )
    demand_grid_height = 720 if demand_show_rates else 640

    dperiods = assign_heatmap_colors(copy.deepcopy(st.session_state.demand_periods))
    html_wd = create_grid_html(
        grid_id="demand_weekday",
        schedule=st.session_state.demand_weekday_sched,
        rate_periods=dperiods,
        title="Demand Weekday Schedule",
        rate_unit="$/kW",
        sched_version=st.session_state.sched_version,
        show_rates=demand_show_rates,
    )
    st.components.v1.html(html_wd, height=demand_grid_height, scrolling=False)

    st.markdown("### Demand Weekend Schedule (Sat–Sun)")
    html_we = create_grid_html(
        grid_id="demand_weekend",
        schedule=st.session_state.demand_weekend_sched,
        rate_periods=dperiods,
        title="Demand Weekend Schedule",
        rate_unit="$/kW",
        sched_version=st.session_state.sched_version,
        copy_from_id="demand_weekday",
        show_rates=demand_show_rates,
    )
    st.components.v1.html(html_we, height=demand_grid_height, scrolling=False)

    st.markdown("---")
    st.session_state.demand_comments = st.text_area(
        "Demand Comments",
        value=st.session_state.demand_comments,
        height=80,
        help="Notes about demand rate components, adjustments, etc.",
    )
