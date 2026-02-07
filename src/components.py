"""
Shared UI components: interactive schedule grid and rate period editor.
"""

import json
from typing import Dict, List, Optional

import streamlit as st

from src.constants import MONTH_NAMES
from src.utils import assign_heatmap_colors


def create_grid_html(
    grid_id: str,
    schedule: List[List[int]],
    rate_periods: List[Dict],
    title: str,
    rate_unit: str = "$/kWh",
    sched_version: int = 1,
    copy_from_id: Optional[str] = None,
    show_rates: bool = False,
) -> str:
    """Create an interactive liquid-glass schedule painting grid.

    Args:
        grid_id:       Unique identifier for this grid instance.
        schedule:      12x24 array of period indices (initial state).
        rate_periods:  List of {label, rate, adj, color} dicts.
        title:         Display title above the grid.
        rate_unit:     Unit string shown on period buttons.
        sched_version: Version counter; when it changes, localStorage is reset.
        copy_from_id:  If set, adds a 'Copy from <id>' fill button.
        show_rates:    If True, display the total rate value on each cell.
    """
    if not rate_periods:
        rate_periods = [{"label": "Period 0", "rate": 0, "adj": 0, "color": "#808080"}]

    # Build a JS-friendly array of total rates per period index
    period_totals = [p.get("rate", 0) + p.get("adj", 0) for p in rate_periods]
    period_totals_json = json.dumps(period_totals)

    # CSS for each period color
    period_css = ""
    for idx, p in enumerate(rate_periods):
        c = p.get("color", "#808080")
        r, g, b = int(c[1:3], 16), int(c[3:5], 16), int(c[5:7], 16)
        period_css += f"""
        .g-{grid_id} .cell[data-p="{idx}"]{{
          background:linear-gradient(135deg,rgba({r},{g},{b},.7),rgba({r},{g},{b},.5) 50%,rgba({r},{g},{b},.6));
          box-shadow:inset 0 1px 1px rgba(255,255,255,.4),inset 0 -1px 1px rgba(0,0,0,.1),0 2px 8px rgba({r},{g},{b},.3);
        }}
        .g-{grid_id} .cell[data-p="{idx}"]:hover{{
          background:linear-gradient(135deg,rgba({r},{g},{b},.85),rgba({r},{g},{b},.65) 50%,rgba({r},{g},{b},.75));
          transform:scale(1.05);z-index:10;
        }}"""

    # Initial cell HTML — include rate text span inside each cell
    cells = ""
    for mi in range(12):
        for hi in range(24):
            pi = 0
            if mi < len(schedule) and hi < len(schedule[mi]):
                pi = min(schedule[mi][hi], len(rate_periods) - 1)
            rate_text = f"{period_totals[pi]:.3f}" if show_rates else ""
            cells += (
                f'<div class="cell" data-m="{mi}" data-h="{hi}" data-p="{pi}">'
                f'<span class="rt">{rate_text}</span></div>'
            )

    # Period selector buttons
    btns = ""
    for idx, p in enumerate(rate_periods):
        c = p.get("color", "#808080")
        r, g, b = int(c[1:3], 16), int(c[3:5], 16), int(c[5:7], 16)
        total = p.get("rate", 0) + p.get("adj", 0)
        btns += f'''<button class="pbtn" data-p="{idx}" style="
          background:linear-gradient(135deg,rgba({r},{g},{b},.8),rgba({r},{g},{b},.6));
          border:2px solid rgba({r},{g},{b},.9);">
          <span class="pl">{p["label"]}</span>
          <span class="pr">${total:.4f}{rate_unit.replace("$","")}</span>
        </button>'''

    # Copy-from button
    copy_btn = ""
    if copy_from_id:
        copy_btn = (
            f'<button class="fbtn" onclick="copyFrom_{grid_id}()">'
            f'Copy from {copy_from_id.replace("_"," ").title()}</button>'
        )

    sched_json = json.dumps(schedule)

    html = f"""
<style>
.gc-{grid_id}{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;padding:16px;
  background:linear-gradient(135deg,#1a1a2e,#16213e);border-radius:16px;
  box-shadow:0 20px 40px -12px rgba(0,0,0,.5);margin-bottom:16px}}
.gt-{grid_id}{{color:#fff;font-size:1.15em;font-weight:600;margin-bottom:12px;text-align:center;text-shadow:0 2px 4px rgba(0,0,0,.3)}}
.ps-{grid_id}{{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:14px;justify-content:center}}
.pbtn{{padding:8px 14px;border-radius:10px;cursor:pointer;transition:all .2s;display:flex;flex-direction:column;
  align-items:center;gap:2px;backdrop-filter:blur(10px);box-shadow:0 4px 12px rgba(0,0,0,.2),inset 0 1px 1px rgba(255,255,255,.3)}}
.pbtn:hover{{transform:translateY(-2px);box-shadow:0 6px 18px rgba(0,0,0,.3)}}
.pbtn.sel{{transform:scale(1.05);box-shadow:0 0 16px rgba(255,255,255,.3);border-width:3px}}
.pl{{color:#fff;font-weight:600;font-size:.85em;text-shadow:0 1px 2px rgba(0,0,0,.5)}}
.pr{{color:rgba(255,255,255,.85);font-size:.72em;text-shadow:0 1px 2px rgba(0,0,0,.5)}}
.gw-{grid_id}{{display:flex;gap:4px}}
.ml-{grid_id}{{display:flex;flex-direction:column;gap:2px;padding-top:24px}}
.ml-{grid_id} div{{height:{'34' if show_rates else '26'}px;display:flex;align-items:center;justify-content:flex-end;padding-right:6px;
  color:rgba(255,255,255,.8);font-size:.72em;font-weight:500}}
.gm-{grid_id}{{flex:1;overflow-x:auto}}
.hl-{grid_id}{{display:grid;grid-template-columns:repeat(24,minmax({'44' if show_rates else '26'}px,1fr));gap:2px;margin-bottom:4px}}
.hl-{grid_id} div{{text-align:center;color:rgba(255,255,255,.75);font-size:.72em;font-weight:500;padding:3px 0}}
.g-{grid_id}{{display:grid;grid-template-columns:repeat(24,minmax({'44' if show_rates else '26'}px,1fr));grid-template-rows:repeat(12,{'34' if show_rates else '26'}px);
  gap:2px;user-select:none}}
.g-{grid_id} .cell{{border-radius:5px;cursor:pointer;transition:all .12s;backdrop-filter:blur(5px);
  border:1px solid rgba(255,255,255,.1);display:flex;align-items:center;justify-content:center}}
.g-{grid_id} .cell .rt{{color:#fff;font-size:.85em;font-weight:600;text-shadow:0 1px 2px rgba(0,0,0,.7);
  pointer-events:none;{'display:block' if show_rates else 'display:none'}}}
{period_css}
.ft-{grid_id}{{display:flex;gap:8px;margin-top:12px;justify-content:center;flex-wrap:wrap}}
.fbtn{{padding:7px 14px;background:rgba(255,255,255,.1);border:1px solid rgba(255,255,255,.2);
  border-radius:8px;color:#fff;cursor:pointer;font-size:.78em;transition:all .2s;backdrop-filter:blur(5px)}}
.fbtn:hover{{background:rgba(255,255,255,.2);transform:translateY(-1px)}}
.gi-{grid_id}{{margin-top:10px;padding:8px;background:rgba(255,255,255,.05);border-radius:8px;
  color:rgba(255,255,255,.6);font-size:.75em;text-align:center}}
</style>

<div class="gc-{grid_id}">
  <div class="gt-{grid_id}">{title}</div>
  <div class="ps-{grid_id}">{btns}</div>
  <div class="gw-{grid_id}">
    <div class="ml-{grid_id}">{''.join(f'<div>{m}</div>' for m in MONTH_NAMES)}</div>
    <div class="gm-{grid_id}">
      <div class="hl-{grid_id}">{''.join(f'<div>{"12" if h == 0 else str(h) if h < 12 else "12" if h == 12 else str(h-12)}{"AM" if h < 12 else "PM"}</div>' for h in range(24))}</div>
      <div class="g-{grid_id}">{cells}</div>
    </div>
  </div>
  <div class="ft-{grid_id}">
    <button class="fbtn" onclick="fa_{grid_id}()">Fill All</button>
    <button class="fbtn" onclick="fr_{grid_id}()">Fill Month Row</button>
    <button class="fbtn" onclick="fc_{grid_id}()">Fill Hour Column</button>
    <button class="fbtn" onclick="ca_{grid_id}()">Clear All</button>
    {copy_btn}
  </div>
  <div class="gi-{grid_id}">Click and drag to paint. Select a period above, then paint on the grid. Hours indicate the hour starting at (e.g. 1p = 1:00 PM – 1:59 PM).</div>
</div>

<script>
(function(){{
  const gid='{grid_id}',ver='{sched_version}',
    sk='tou_sched_'+gid,
    grid=document.querySelector('.g-'+gid),
    pbtns=document.querySelectorAll('.ps-'+gid+' .pbtn'),
    cells=grid.querySelectorAll('.cell'),
    initSched={sched_json},
    pRates={period_totals_json},
    showRates={'true' if show_rates else 'false'};
  let sp=0,md=false,lm=0,lh=0;

  function setRateText(c){{
    if(!showRates)return;
    const rt=c.querySelector('.rt');
    if(rt){{const pi=+c.dataset.p;rt.textContent=(pi<pRates.length)?pRates[pi].toFixed(3):'';}}
  }}

  /* Restore from localStorage if version matches, else use init schedule */
  try{{
    const saved=JSON.parse(localStorage.getItem(sk)||'null');
    if(saved&&saved.v===ver){{
      const s=saved.s;
      cells.forEach(c=>{{
        const m=+c.dataset.m,h=+c.dataset.h;
        if(m<s.length&&h<s[m].length) c.dataset.p=s[m][h];
        setRateText(c);
      }});
    }} else {{
      /* First render with this version — write init schedule */
      localStorage.setItem(sk,JSON.stringify({{v:ver,s:initSched}}));
    }}
  }}catch(e){{}}

  pbtns[0]&&pbtns[0].classList.add('sel');
  pbtns.forEach(b=>b.addEventListener('click',function(){{
    pbtns.forEach(x=>x.classList.remove('sel'));
    this.classList.add('sel');sp=+this.dataset.p;
  }}));

  function paint(c){{c.dataset.p=sp;setRateText(c);lm=+c.dataset.m;lh=+c.dataset.h;save();}}
  cells.forEach(c=>{{
    c.addEventListener('mousedown',e=>{{e.preventDefault();md=true;paint(c);}});
    c.addEventListener('mouseenter',()=>{{if(md)paint(c);}});
    c.addEventListener('touchstart',e=>{{e.preventDefault();paint(c);}});
    c.addEventListener('touchmove',e=>{{
      e.preventDefault();const t=e.touches[0],
      el=document.elementFromPoint(t.clientX,t.clientY);
      if(el&&el.classList.contains('cell'))paint(el);
    }});
  }});
  document.addEventListener('mouseup',()=>{{md=false;}});

  function getSched(){{
    const s=[];
    for(let m=0;m<12;m++){{const r=[];
      for(let h=0;h<24;h++){{
        const c=grid.querySelector(`.cell[data-m="${{m}}"][data-h="${{h}}"]`);
        r.push(c?+c.dataset.p:0);}}
      s.push(r);}}
    return s;
  }}

  function save(){{
    try{{localStorage.setItem(sk,JSON.stringify({{v:ver,s:getSched()}}));}}catch(e){{}}
  }}

  window['fa_'+gid]=()=>{{cells.forEach(c=>{{c.dataset.p=sp;setRateText(c);}});save();}};
  window['fr_'+gid]=()=>{{cells.forEach(c=>{{if(+c.dataset.m===lm){{c.dataset.p=sp;setRateText(c);}}}});save();}};
  window['fc_'+gid]=()=>{{cells.forEach(c=>{{if(+c.dataset.h===lh){{c.dataset.p=sp;setRateText(c);}}}});save();}};
  window['ca_'+gid]=()=>{{cells.forEach(c=>{{c.dataset.p=0;setRateText(c);}});save();}};
  window['getSched_'+gid]=getSched;

  /* Copy-from support */
  const copyFromId='{copy_from_id or ""}';
  if(copyFromId){{
    window['copyFrom_'+gid]=()=>{{
      try{{
        const src=JSON.parse(localStorage.getItem('tou_sched_'+copyFromId)||'null');
        if(src&&src.s){{
          cells.forEach(c=>{{
            const m=+c.dataset.m,h=+c.dataset.h;
            if(m<src.s.length&&h<src.s[m].length) c.dataset.p=src.s[m][h];
            setRateText(c);
          }});
          save();
        }}
      }}catch(e){{}}
    }};
  }}

  save();
}})();
</script>"""
    return html


def render_rate_period_editor(
    periods_key: str,
    prefix: str,
    rate_unit: str,
    default_periods: List[Dict],
    min_periods: int = 1,
    max_periods: int = 12,
):
    """Render an editor for rate periods as a compact table. Modifies session state in place."""
    periods = st.session_state[periods_key]

    num = st.number_input(
        "Number of Rate Periods",
        min_value=min_periods,
        max_value=max_periods,
        value=len(periods),
        key=f"{prefix}_num_periods",
        help="Number of TOU periods (e.g., Off-Peak, Mid-Peak, On-Peak)",
    )

    # Adjust list length
    while len(periods) < num:
        i = len(periods)
        periods.append({"label": f"Period {i}", "rate": 0.0, "adj": 0.0})
    while len(periods) > num:
        periods.pop()

    # Table header
    unit_short = rate_unit.lstrip("$/")
    h1, h2, h3, h4, h5 = st.columns([0.4, 1.4, 1.2, 1.2, 1.0])
    h1.markdown("**#**")
    h2.markdown("**Label**")
    h3.markdown(f"**Base Rate ({rate_unit})**")
    h4.markdown(f"**Adjustment ({rate_unit})**")
    h5.markdown(f"**Total ({rate_unit})**")

    # Table rows — one row per period, all visible at once
    for idx in range(len(periods)):
        p = periods[idx]
        c0, c1, c2, c3, c4 = st.columns([0.4, 1.4, 1.2, 1.2, 1.0])
        with c0:
            st.markdown(
                f'<div style="padding:8px 0;font-weight:600;">{idx}</div>',
                unsafe_allow_html=True,
            )
        with c1:
            p["label"] = st.text_input(
                "Label", value=p["label"], key=f"{prefix}_lbl_{idx}",
                label_visibility="collapsed",
            )
        with c2:
            rate_str = st.text_input(
                "Base Rate", value=f"{p['rate']:.4f}", key=f"{prefix}_rate_{idx}",
                label_visibility="collapsed",
            )
            try:
                p["rate"] = max(0.0, float(rate_str))
            except ValueError:
                st.error("Invalid number")
        with c3:
            adj_str = st.text_input(
                "Adjustment", value=f"{p['adj']:.4f}", key=f"{prefix}_adj_{idx}",
                label_visibility="collapsed",
            )
            try:
                p["adj"] = float(adj_str)
            except ValueError:
                st.error("Invalid number")
        with c4:
            total = p.get("rate", 0) + p.get("adj", 0)
            st.markdown(
                f'<div style="padding:8px 0;font-weight:600;">${total:.4f}</div>',
                unsafe_allow_html=True,
            )

    # Update colors
    assign_heatmap_colors(periods)
    st.session_state[periods_key] = periods

    # Color legend
    cols = st.columns(min(len(periods), 6))
    for idx, (col, p) in enumerate(zip(cols, periods)):
        c = p.get("color", "#808080")
        total = p.get("rate", 0) + p.get("adj", 0)
        col.markdown(
            f'<div style="background:{c};padding:8px;border-radius:8px;text-align:center;'
            f'color:#fff;font-size:.85em;text-shadow:0 1px 2px rgba(0,0,0,.5);">'
            f'<b>{p["label"]}</b><br>${total:.4f}/{unit_short}</div>',
            unsafe_allow_html=True,
        )
