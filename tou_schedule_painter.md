# TOU Schedule Painter — URDB Tariff JSON Builder

## Overview

`tou_schedule_painter.py` is a Streamlit application for building, editing, and exporting URDB-compatible tariff JSON files. Users can create tariffs from scratch or import existing ones, configure rate periods across six tabs, paint interactive 12×24 TOU schedule grids, and export the result as a complete JSON file.

**Run with:** `streamlit run tou_schedule_painter.py`

---

## Application Tabs

| Tab | Purpose |
|-----|---------|
| **Basic Info** | Utility name, rate name, sector, service type, dates, applicability criteria (voltage, phase, demand min/max) |
| **Energy Rates** | TOU energy periods (label, base rate, adjustment in $/kWh), weekday and weekend 12×24 schedule grids |
| **TOU Demand** | Optional TOU demand periods ($/kW), weekday/weekend schedule grids, demand window and reactive power settings |
| **Flat Demand** | Optional seasonal/monthly flat demand charges with month-to-period assignment |
| **Fixed Charges** | Fixed monthly charge, minimum monthly charge, annual minimum charge |
| **Review & Export** | Validation, configuration summary, JSON preview, download, and clipboard copy |

---

## Architecture

### State Management

- **Streamlit `st.session_state`** — stores all form inputs, rate period definitions, and schedule arrays.
- **Browser `localStorage`** — the interactive HTML/JS schedule grids persist painted state in localStorage to survive Streamlit rerenders. A `sched_version` counter in session state invalidates localStorage when tariffs are imported or reset.
- **Export** — the JS export component reads schedules from localStorage and merges them with the Python-built tariff JSON at download time.

### Key Data Structures

**Rate Period** (energy and TOU demand):
```python
{"label": "On-Peak", "rate": 0.25, "adj": 0.0, "color": "#ff6400"}
```

**Schedule Matrix** — 12×24 array (12 months × 24 hours), each cell is a period index:
```python
[[0, 0, 0, 1, 1, 1, 2, 2, ...],  # January
 [0, 0, 0, 1, 1, 1, 2, 2, ...],  # February
 ...]
```

**Flat Demand Period**:
```python
{"label": "Summer", "rate": 12.50, "adj": 0.0}
```

**Flat Demand Months** — 12-element list mapping each month to a period index:
```python
[0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0]  # Summer (1) for Apr-Sep
```

---

## Key Functions

### Utility Functions

| Function | Description |
|----------|-------------|
| `get_heatmap_color(value)` | Maps a 0.0–1.0 float to a green-yellow-red hex color string |
| `assign_heatmap_colors(periods)` | Assigns visually distinct colors based on rate **rank** (not value), so even similar rates get different colors |
| `normalize_tariff(tariff)` | Converts local DB format (camelCase) field names to API-format (lowercase) using `FIELD_MAP`; flattens nested tier structures |
| `extract_periods_from_structure(structure, labels, default_label)` | Extracts period configs from a URDB `energyratestructure` or `demandratestructure` array |

### State & Data Functions

| Function | Description |
|----------|-------------|
| `init_session_state()` | Sets all session state defaults (called once at app start) |
| `import_tariff_data(raw)` | Parses uploaded JSON, normalizes fields, increments `sched_version`, and populates session state |
| `build_tariff_json(energy_wd, energy_we, demand_wd, demand_we)` | Assembles a complete `{"items": [tariff]}` JSON dict from session state; schedule parameters override session state when provided |
| `validate_tariff()` | Returns a list of `{"level", "msg"}` validation results (error/warn/info) |

### UI Rendering Functions

| Function | Description |
|----------|-------------|
| `render_basic_info_tab()` | Tariff identification and applicability criteria inputs |
| `render_rate_period_editor(...)` | Shared editor for energy/demand rate periods (add/remove periods, edit labels/rates/adjustments) |
| `render_energy_rates_tab()` | Energy period editor + weekday/weekend schedule grids |
| `render_tou_demand_tab()` | TOU demand toggle, settings, period editor + schedule grids |
| `render_flat_demand_tab()` | Flat demand toggle, seasonal periods, vertical month-to-period assignment |
| `render_fixed_charges_tab()` | Fixed/minimum/annual charge inputs |
| `render_export_tab()` | Validation display, config summary metrics, JS-based export component |
| `render_sidebar()` | Import JSON, reset to defaults, configuration status summary |

### Schedule Grid Component

`create_grid_html(grid_id, schedule, rate_periods, title, rate_unit, sched_version, copy_from_id, show_rates)` generates a self-contained HTML/CSS/JS component embedded via `st.components.v1.html`. Features:

- **Interactive painting** — click-and-drag to assign periods to cells
- **Period selector buttons** — color-coded with label and rate
- **Fill tools** — Fill All, Fill Month Row, Fill Hour Column, Clear All, Copy From (weekday → weekend)
- **Show rates toggle** — displays the total rate (3 decimal places) on each cell when enabled
- **Hour labels** — AM/PM format (e.g., 12AM, 1AM, ... 12PM, 1PM, ... 11PM), representing the hour starting at
- **localStorage persistence** — grid state persists across Streamlit reruns; invalidated by `sched_version`

---

## Import & Export

### Import

- Accepts both **OpenEI API format** (lowercase keys, `{"items": [tariff]}` wrapper) and **local database format** (camelCase keys, nested tier structures)
- `normalize_tariff()` handles field name mapping and structure flattening
- Uploaded via sidebar file uploader

### Export

- **Filename format**: `{utility} - {tariff name} - {YYYY-MM-DD}.json`
- **JSON structure**: Standard URDB `{"items": [tariff]}` wrapper
- Schedule data is read from localStorage at export time (JS-side), merged with Python-built tariff fields
- Three export options: Download file, Toggle JSON preview, Copy to clipboard
- A Streamlit-native JSON preview (using session state schedules) is also available as a fallback

---

## Constants

| Constant | Value |
|----------|-------|
| `MONTH_NAMES` | `["Jan", "Feb", ..., "Dec"]` |
| `SECTOR_OPTIONS` | `["Commercial", "Residential", "Industrial", "Lighting"]` |
| `SERVICE_TYPE_OPTIONS` | `["Bundled", "Delivery", "Energy"]` |
| `VOLTAGE_CATEGORIES` | `["", "Secondary", "Primary", "Transmission"]` |
| `PHASE_OPTIONS` | `["", "Single Phase", "3-Phase", "Single and 3-Phase"]` |
| `DEMAND_UNIT_OPTIONS` | `["kW", "hp", "kVA", "kW daily", "hp daily", "kVA daily"]` |
| `DEFAULT_ENERGY_PERIODS` | Off-Peak ($0.08), Mid-Peak ($0.15), On-Peak ($0.25) |
| `DEFAULT_DEMAND_PERIODS` | Off-Peak ($0.00), On-Peak ($15.00) |

---

## Custom Extension Fields

The app uses two project-specific fields not in the official URDB schema:

| Field | Type | Description |
|-------|------|-------------|
| `energytoulabels` | `string[]` | Human-readable labels for energy TOU periods (e.g., `["Off-Peak", "Mid-Peak", "On-Peak"]`) |
| `demandtoulabels` | `string[]` | Human-readable labels for demand TOU periods |

These arrays align 1:1 with `energyratestructure` and `demandratestructure` indices.

---

## Session State Keys

### Basic Info
`basic_utility`, `basic_name`, `basic_sector`, `basic_servicetype`, `basic_description`, `basic_source`, `basic_sourceparent`, `basic_startdate`, `basic_eiaid`, `basic_voltagecategory`, `basic_phasewiring`, `basic_peakkwcapacitymin`, `basic_peakkwcapacitymax`

### Energy Rates
`energy_periods` (list of dicts), `energy_weekday_sched` (12×24), `energy_weekend_sched` (12×24), `energy_comments`

### TOU Demand
`demand_enabled`, `demand_periods`, `demand_weekday_sched`, `demand_weekend_sched`, `demand_rateunit`, `demand_window`, `demand_reactive`, `demand_comments`

### Flat Demand
`flat_enabled`, `flat_periods`, `flat_months` (12-element list), `flat_unit`

### Fixed Charges
`fixed_charge`, `fixed_charge_units`, `min_monthly_charge`, `annual_min_charge`

### Internal
`sched_version` — incremented on import/reset to invalidate localStorage grids

---

## Known Limitations

- **No tiered/block rate support** — the `max` field in `energyratestructure` tiers (used for inclining block rates, e.g., Austin Energy Residential) is not currently supported. The app reads only the first tier per period on import and exports single-tier periods. Tariffs with tiered pricing will lose tier breakpoint data.
- **Schedule grids use localStorage** — painted schedule data lives in the browser, not in Streamlit session state. This means schedules are not preserved across browser sessions or different browsers. The JS export component reads from localStorage at download time.
- **Single-tier demand rates** — similar to energy, demand rate structures only support one tier per period (no `max`/block pricing for demand).

---

## Dependencies

- **Python**: `streamlit`, `json`, `copy`, `datetime`, `typing`
- **Browser**: Modern browser with localStorage and ES6 support
