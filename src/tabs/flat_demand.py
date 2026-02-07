"""
Tab: Flat Demand — optional seasonal/monthly flat demand charges.
"""

import streamlit as st

from src.constants import MONTH_NAMES, DEMAND_UNIT_OPTIONS


def render_flat_demand_tab():
    """Render the Flat Demand configuration tab."""
    st.session_state.flat_enabled = st.toggle(
        "Enable Flat (Seasonal/Monthly) Demand Charges",
        value=st.session_state.flat_enabled,
        help="Toggle on to add flat demand charges applied to the monthly peak regardless of time.",
    )

    if not st.session_state.flat_enabled:
        st.info(
            "Flat demand charges are **disabled**. Toggle on above to configure "
            "seasonal demand periods and assign months."
        )
        return

    st.markdown("### Flat Demand Unit")
    fu = st.session_state.flat_unit
    st.session_state.flat_unit = st.selectbox(
        "Unit",
        options=DEMAND_UNIT_OPTIONS,
        index=DEMAND_UNIT_OPTIONS.index(fu) if fu in DEMAND_UNIT_OPTIONS else 0,
        key="flat_unit_sel",
    )

    st.markdown("### Seasonal/Monthly Demand Periods")
    fp = st.session_state.flat_periods

    num = st.number_input(
        "Number of Periods (seasons)",
        min_value=1,
        max_value=6,
        value=len(fp),
        key="flat_num_periods",
        help="1 = same rate all year, 2 = summer/winter, etc.",
    )

    while len(fp) < num:
        fp.append({"label": f"Season {len(fp)}", "rate": 0.0, "adj": 0.0})
    while len(fp) > num:
        fp.pop()
        # Clamp month mappings
        st.session_state.flat_months = [
            min(m, len(fp) - 1) for m in st.session_state.flat_months
        ]

    for idx in range(len(fp)):
        p = fp[idx]
        total = p["rate"] + p["adj"]
        with st.expander(
            f"Period {idx}: {p['label']}  —  ${total:.2f}/{st.session_state.flat_unit}",
            expanded=True,
        ):
            c1, c2, c3 = st.columns(3)
            with c1:
                p["label"] = st.text_input(
                    "Label", value=p["label"], key=f"flat_lbl_{idx}"
                )
            with c2:
                r_str = st.text_input(
                    f"Rate ($/{st.session_state.flat_unit})",
                    value=f"{p['rate']:.2f}",
                    key=f"flat_rate_{idx}",
                )
                try:
                    p["rate"] = max(0.0, float(r_str))
                except ValueError:
                    st.error("Invalid number")
            with c3:
                a_str = st.text_input(
                    f"Adjustment ($/{st.session_state.flat_unit})",
                    value=f"{p['adj']:.2f}",
                    key=f"flat_adj_{idx}",
                )
                try:
                    p["adj"] = float(a_str)
                except ValueError:
                    st.error("Invalid number")

    st.session_state.flat_periods = fp

    st.markdown("---")
    st.markdown("### Month-to-Period Assignment")
    st.caption("Assign each month to one of the seasonal periods defined above.")

    period_labels = [f"{i}: {fp[i]['label']}" for i in range(len(fp))]
    months_map = st.session_state.flat_months
    flat_unit = st.session_state.flat_unit

    # Build period color map for visual badges
    period_colors = [
        "#22c55e", "#eab308", "#ef4444", "#3b82f6", "#a855f7", "#f97316",
    ]

    for mi in range(12):
        current = months_map[mi] if mi < len(months_map) else 0
        current = min(current, len(fp) - 1)

        c1, c2, c3 = st.columns([1.2, 2, 2])
        with c1:
            st.markdown(
                f'<div style="padding:6px 0;font-weight:600;font-size:.95em;">'
                f'{MONTH_NAMES[mi]}</div>',
                unsafe_allow_html=True,
            )
        with c2:
            months_map[mi] = st.selectbox(
                f"Period for {MONTH_NAMES[mi]}",
                options=list(range(len(fp))),
                format_func=lambda x, pl=period_labels: pl[x]
                if x < len(pl)
                else str(x),
                index=current,
                key=f"flat_month_{mi}",
                label_visibility="collapsed",
            )
        with c3:
            pi = months_map[mi]
            p = fp[pi] if pi < len(fp) else {"label": "?", "rate": 0, "adj": 0}
            total = p["rate"] + p["adj"]
            pc = period_colors[pi % len(period_colors)]
            st.markdown(
                f'<div style="background:{pc};padding:6px 12px;border-radius:8px;'
                f'color:#fff;font-size:.85em;text-shadow:0 1px 2px rgba(0,0,0,.4);'
                f'display:inline-flex;align-items:center;gap:8px;margin-top:2px;">'
                f'<b>{p["label"]}</b>'
                f'<span style="opacity:.9;">${total:.2f}/{flat_unit}</span>'
                f'</div>',
                unsafe_allow_html=True,
            )

    st.session_state.flat_months = months_map
