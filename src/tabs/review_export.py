"""
Tab: Review & Export — validation, JSON preview, and download.
"""

import json
from datetime import datetime

import streamlit as st

from src.tariff_io import build_tariff_json
from src.validation import validate_tariff


def render_export_tab():
    """Render the Review & Export tab."""
    st.markdown("### Validation")
    issues = validate_tariff()
    errors = [i for i in issues if i["level"] == "error"]
    warns = [i for i in issues if i["level"] == "warn"]
    infos = [i for i in issues if i["level"] == "info"]

    if errors:
        for e in errors:
            st.error(e["msg"])
    if warns:
        for w in warns:
            st.warning(w["msg"])
    if infos:
        for i in infos:
            st.info(i["msg"])
    if not errors:
        st.success("Tariff passes all required-field checks.")

    st.markdown("---")
    st.markdown("### Configuration Summary")

    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Energy Periods", len(st.session_state.energy_periods))
    with c2:
        dp = (
            len(st.session_state.demand_periods)
            if st.session_state.demand_enabled
            else 0
        )
        st.metric("TOU Demand Periods", dp)
    with c3:
        fp = (
            len(st.session_state.flat_periods)
            if st.session_state.flat_enabled
            else 0
        )
        st.metric("Flat Demand Periods", fp)

    st.markdown("---")
    st.markdown("### JSON Preview & Download")
    st.caption(
        "The export reads painted schedules directly from the grids. "
        "Make sure you've painted your schedules in the Energy Rates "
        "and TOU Demand tabs before exporting."
    )

    # Build the non-schedule portion as a JSON string to pass into JS
    tariff_json_obj = build_tariff_json()
    tariff_json_str = json.dumps(tariff_json_obj, indent=2)

    # Also pass schedule keys that JS should read from localStorage
    demand_enabled = st.session_state.demand_enabled

    # Create JS export component — filename: utility - tariff - date
    utility_name = st.session_state.basic_utility or "utility"
    tariff_name = st.session_state.basic_name or "custom_tariff"
    today_str = datetime.now().strftime("%Y-%m-%d")
    raw_name = f"{utility_name} - {tariff_name} - {today_str}"
    safe_name = "".join(c if c.isalnum() or c in "-_ " else "" for c in raw_name)
    safe_name = safe_name.strip().replace(" ", "_")

    export_html = f"""
<style>
.exp-c{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;padding:20px;
  background:linear-gradient(135deg,#1a1a2e,#16213e);border-radius:16px;
  box-shadow:0 20px 40px -12px rgba(0,0,0,.5)}}
.exp-btn{{padding:12px 24px;border-radius:12px;cursor:pointer;transition:all .2s;font-size:1em;
  font-weight:600;border:none;margin:5px;color:#fff}}
.exp-btn:hover{{transform:translateY(-2px)}}
.exp-btn.g{{background:linear-gradient(135deg,#22c55e,#16a34a);box-shadow:0 4px 15px rgba(34,197,94,.4)}}
.exp-btn.b{{background:linear-gradient(135deg,#3b82f6,#2563eb);box-shadow:0 4px 15px rgba(59,130,246,.4)}}
.exp-btn.p{{background:linear-gradient(135deg,#a855f7,#7c3aed);box-shadow:0 4px 15px rgba(168,85,247,.4)}}
.json-out{{margin-top:15px;padding:15px;background:rgba(0,0,0,.3);border-radius:10px;
  font-family:Consolas,Monaco,monospace;font-size:.78em;color:#e2e8f0;max-height:450px;
  overflow-y:auto;white-space:pre-wrap;word-break:break-all;display:none}}
.exp-info{{color:rgba(255,255,255,.6);font-size:.82em;margin-top:12px;text-align:center}}
</style>
<div class="exp-c">
  <div style="display:flex;flex-wrap:wrap;justify-content:center;gap:10px">
    <button class="exp-btn g" onclick="dl()">Download JSON File</button>
    <button class="exp-btn b" onclick="togglePreview()">Toggle JSON Preview</button>
    <button class="exp-btn p" onclick="copyJ()">Copy JSON to Clipboard</button>
  </div>
  <div id="jout" class="json-out"></div>
  <div class="exp-info">
    Schedules are read from the painted grids. Ensure you've painted them before exporting.
  </div>
</div>
<script>
(function(){{
  const base={tariff_json_str};
  const demandOn={'true' if demand_enabled else 'false'};
  const ver='{st.session_state.sched_version}';

  function readLS(key){{
    try{{
      const d=JSON.parse(localStorage.getItem(key)||'null');
      if(d&&d.v===ver&&d.s)return d.s;
    }}catch(e){{}}
    return null;
  }}

  function build(){{
    const t=JSON.parse(JSON.stringify(base));
    const item=t.items[0];
    const ewd=readLS('tou_sched_energy_weekday');
    const ewe=readLS('tou_sched_energy_weekend');
    if(ewd)item.energyweekdayschedule=ewd;
    if(ewe)item.energyweekendschedule=ewe;
    if(demandOn){{
      const dwd=readLS('tou_sched_demand_weekday');
      const dwe=readLS('tou_sched_demand_weekend');
      if(dwd)item.demandweekdayschedule=dwd;
      if(dwe)item.demandweekendschedule=dwe;
    }}
    return t;
  }}

  window.togglePreview=()=>{{
    const o=document.getElementById('jout');
    if(o.style.display==='none'){{o.textContent=JSON.stringify(build(),null,2);o.style.display='block';}}
    else o.style.display='none';
  }};

  window.copyJ=()=>{{
    const txt=JSON.stringify(build(),null,2);
    navigator.clipboard.writeText(txt).then(()=>alert('JSON copied to clipboard!')).catch(()=>{{
      togglePreview();alert('Copy failed. JSON is shown below — select and copy manually.');
    }});
  }};

  window.dl=()=>{{
    const txt=JSON.stringify(build(),null,2);
    const blob=new Blob([txt],{{type:'application/json'}});
    const url=URL.createObjectURL(blob);
    const a=document.createElement('a');
    a.href=url;a.download='{safe_name}.json';
    document.body.appendChild(a);a.click();document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }};
}})();
</script>"""

    st.components.v1.html(export_html, height=550, scrolling=True)

    # Also show a Streamlit-native JSON preview (uses session-state schedules as fallback)
    with st.expander(
        "Streamlit JSON Preview (session state — may differ from painted grids)"
    ):
        st.json(build_tariff_json())
