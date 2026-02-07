# URDB Tariff JSON Builder

A Streamlit web application for creating and editing [URDB](https://openei.org/wiki/Utility_Rate_Database)-compatible electric utility tariff JSON files.

## Features

- **Visual schedule painting** — interactive 12×24 grids (months × hours) for TOU period assignment
- **Complete tariff configuration** — all URDB fields via a tabbed interface
- **Import / export** — load existing URDB tariff JSON files and export URDB-compatible JSON
- **Validation** — checks required fields before export
- **Six-tab workflow:**
  1. Basic Info — utility, rate name, sector, dates, applicability
  2. Energy Rates — TOU energy periods and schedule painting
  3. TOU Demand — optional TOU demand charges and schedules
  4. Flat Demand — optional seasonal/monthly flat demand charges
  5. Fixed Charges — fixed monthly and minimum charges
  6. Review & Export — validation, preview, and JSON download

## Project Structure

```
Tariff_Builder/
├── app.py                    # Main Streamlit entry point
├── requirements.txt          # Python dependencies
├── .streamlit/
│   └── config.toml           # Streamlit theme and server config
├── src/
│   ├── __init__.py
│   ├── constants.py           # Constants and configuration values
│   ├── utils.py               # Heatmap colors, tariff normalization, period extraction
│   ├── state.py               # Session state initialization
│   ├── tariff_io.py           # Tariff import and export logic
│   ├── validation.py          # Tariff validation
│   ├── components.py          # Shared UI components (schedule grid, rate editor)
│   ├── sidebar.py             # Sidebar rendering
│   └── tabs/
│       ├── __init__.py
│       ├── basic_info.py      # Basic Info tab
│       ├── energy_rates.py    # Energy Rates tab
│       ├── tou_demand.py      # TOU Demand tab
│       ├── flat_demand.py     # Flat Demand tab
│       ├── fixed_charges.py   # Fixed Charges tab
│       └── review_export.py   # Review & Export tab
├── tou_schedule_painter.md    # Application architecture docs
└── URDB_JSON_Documentation.md # URDB JSON field reference
```

## Quick Start

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

### Deploy to Streamlit Community Cloud

1. Push this repository to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repo
4. Set the main file path to `app.py`
5. Deploy

## Dependencies

- **streamlit** >= 1.24.0

All other imports (`json`, `copy`, `datetime`, `typing`) are Python standard library.

## License

MIT
