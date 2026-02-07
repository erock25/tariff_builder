"""
Tab: Energy Rates — TOU energy periods, labels, and schedule painting.
"""

import copy

import streamlit as st

from src.constants import DEFAULT_ENERGY_PERIODS
from src.utils import assign_heatmap_colors
from src.components import create_grid_html, render_rate_period_editor


def render_energy_rates_tab():
    """Render the Energy Rates configuration tab."""
    st.markdown("### Energy Rate Periods")
    st.caption(
        "Define TOU energy periods with labels and $/kWh rates. "
        "Colors are auto-assigned: green = lowest rate, red = highest."
    )

    render_rate_period_editor(
        periods_key="energy_periods",
        prefix="energy",
        rate_unit="$/kWh",
        default_periods=DEFAULT_ENERGY_PERIODS,
    )

    st.markdown("---")
    st.markdown("### Energy Weekday Schedule (Mon–Fri)")
    st.caption("Paint the 12×24 grid: select a period, then click-drag on cells.")

    energy_show_rates = st.toggle(
        "Show rates on grid cells",
        value=True,
        key="energy_show_rates",
        help="Display the total rate (base + adjustment) on each cell in the schedule grids.",
    )
    grid_height = 720 if energy_show_rates else 640

    periods = assign_heatmap_colors(copy.deepcopy(st.session_state.energy_periods))
    html_wd = create_grid_html(
        grid_id="energy_weekday",
        schedule=st.session_state.energy_weekday_sched,
        rate_periods=periods,
        title="Energy Weekday Schedule",
        rate_unit="$/kWh",
        sched_version=st.session_state.sched_version,
        show_rates=energy_show_rates,
    )
    st.components.v1.html(html_wd, height=grid_height, scrolling=False)

    st.markdown("### Energy Weekend Schedule (Sat–Sun)")
    html_we = create_grid_html(
        grid_id="energy_weekend",
        schedule=st.session_state.energy_weekend_sched,
        rate_periods=periods,
        title="Energy Weekend Schedule",
        rate_unit="$/kWh",
        sched_version=st.session_state.sched_version,
        copy_from_id="energy_weekday",
        show_rates=energy_show_rates,
    )
    st.components.v1.html(html_we, height=grid_height, scrolling=False)

    st.markdown("---")
    st.session_state.energy_comments = st.text_area(
        "Energy Comments",
        value=st.session_state.energy_comments,
        height=80,
        help="Notes about energy rate components, adjustments included in rates, etc.",
    )
