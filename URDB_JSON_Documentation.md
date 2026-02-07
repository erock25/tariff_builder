# URDB JSON Tariff Field Reference

Canonical field reference for OpenEI / URDB (Utility Rate Database) tariff JSON files used in this project.

**Official API Documentation:** [OpenEI URDB API v3 Response Fields](https://openei.org/services/doc/rest/util_rates/?version=3#response-fields)

---

## JSON Wrapper Structure

Tariff data from the OpenEI API is wrapped in an `items` array. All field references below describe the fields within a single tariff object.

```json
{
  "items": [
    {
      "label": "6757525f259975f54b0eccbf",
      "utility": "Pacific Gas & Electric Co",
      "name": "BEV-2-S Business Electric Vehicle",
      ...
    }
  ]
}
```

---

## Basic Information

| Field | Type | Description |
|-------|------|-------------|
| `label` | string | Unique tariff identifier (page label) |
| `utility` | string | Utility company name |
| `name` | string | Rate schedule name |
| `uri` | URI | Full page URI on OpenEI |
| `eiaid` | integer | EIA (Energy Information Administration) utility ID |
| `approved` | boolean | Whether an expert has verified the tariff |
| `startdate` | integer | Effective date (Unix timestamp) |
| `enddate` | integer | End date (Unix timestamp) |
| `supersedes` | string | Label of the rate this rate supersedes |
| `sector` | enumeration | One of `"Residential"`, `"Commercial"`, `"Industrial"`, or `"Lighting"` |
| `servicetype` | enumeration | One of `"Bundled"`, `"Delivery"`, or `"Energy"` |
| `description` | string | Rate description |
| `source` | string | Source document or reference URL |
| `sourceparent` | URI | Parent source page |
| `basicinformationcomments` | string | Basic information comments |

---

## Applicability Criteria

| Field | Type | Description |
|-------|------|-------------|
| `peakkwcapacitymin` | decimal | Demand minimum (kW) for rate eligibility |
| `peakkwcapacitymax` | decimal | Demand maximum (kW) for rate eligibility |
| `peakkwcapacityhistory` | decimal | Demand history period (months) |
| `peakkwhusagemin` | decimal | Energy minimum (kWh) for rate eligibility |
| `peakkwhusagemax` | decimal | Energy maximum (kWh) for rate eligibility |
| `peakkwhusagehistory` | decimal | Energy history period (months) |
| `voltageminimum` | decimal | Service voltage minimum (V) |
| `voltagemaximum` | decimal | Service voltage maximum (V) |
| `voltagecategory` | enumeration | One of `"Primary"`, `"Secondary"`, or `"Transmission"` |
| `phasewiring` | enumeration | One of `"Single Phase"`, `"3-Phase"`, or `"Single and 3-Phase"` |

---

## Energy Rate Fields

| Field | Type | Description |
|-------|------|-------------|
| `energyratestructure` | array | Tiered energy usage charge structure (see below) |
| `energyweekdayschedule` | array | Weekday energy schedule -- 12x24 matrix (month x hour), values are period indices into `energyratestructure` |
| `energyweekendschedule` | array | Weekend energy schedule -- 12x24 matrix (month x hour), values are period indices into `energyratestructure` |
| `usenetmetering` | boolean | Assume net metering (buy = sell) |
| `energyattrs` | array | Other energy attributes in key/value format |
| `energycomments` | string | Energy rate comments |

### energyratestructure Detail

Each element in the top-level array corresponds to one TOU period. Each array element within a period corresponds to one tier. Indices are zero-based and correspond with `energyweekdayschedule` and `energyweekendschedule` entries.

**Tier object fields:**

| Field | Type | Description |
|-------|------|-------------|
| `rate` | decimal | Base energy rate ($/kWh) |
| `adj` | decimal | Rate adjustment ($/kWh) -- added to base rate |
| `max` | decimal | Cumulative tier threshold (kWh). `null` or absent for the final (unlimited) tier |
| `unit` | enumeration | Unit of measurement (typically `"kWh"`) |
| `sell` | decimal | Sell-back rate for net metering ($/kWh) |

**Example:**

```json
"energyratestructure": [
  [{"unit": "kWh", "rate": 0.18081, "adj": 0.00}],
  [{"unit": "kWh", "rate": 0.15754, "adj": 0.00}],
  [{"unit": "kWh", "rate": 0.39404, "adj": 0.00}]
]
```

### Schedule Matrix Format

Both `energyweekdayschedule` and `energyweekendschedule` are arrays of 12 arrays (one per month, Jan=index 0). Each month array contains 24 integers (one per hour, 12am=index 0 through 11pm=index 23). Each integer is a zero-based index into `energyratestructure`.

```json
"energyweekdayschedule": [
  [0,0,0,0,0,0,0,0,0, 1,1,1,1,1, 0,0, 2,2,2,2,2, 0,0,0],
  ...
]
```

---

## Flat (Seasonal/Monthly) Demand Charge Fields

| Field | Type | Description |
|-------|------|-------------|
| `flatdemandunit` | enumeration | Rate units -- one of `"kW"`, `"hp"`, `"kVA"`, `"kW daily"`, `"hp daily"`, `"kVA daily"` |
| `flatdemandstructure` | array | Seasonal/monthly demand charge tiers by period (see below) |
| `flatdemandmonths` | array | Array of 12 integers mapping each month to a period index in `flatdemandstructure` |

### flatdemandstructure Detail

Each element in the top-level array corresponds to one seasonal period (indexed by `flatdemandmonths`). Each array element within a period corresponds to one tier.

**Tier object fields:**

| Field | Type | Description |
|-------|------|-------------|
| `rate` | decimal | Base demand rate ($/kW) |
| `adj` | decimal | Rate adjustment ($/kW) |
| `max` | decimal | Cumulative tier threshold (kW). `null` or absent for the final tier |

**Example:**

```json
"flatdemandstructure": [
  [{"rate": 25.36}]
],
"flatdemandmonths": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
```

---

## TOU Demand Charge Fields

| Field | Type | Description |
|-------|------|-------------|
| `demandrateunit` | enumeration | Rate units -- one of `"kW"`, `"hp"`, `"kVA"`, `"kW daily"`, `"hp daily"`, `"kVA daily"` |
| `demandunits` | enumeration | Demand measurement units (typically `"kW"`) |
| `demandratestructure` | array | TOU demand charge tiers by period (see below) |
| `demandweekdayschedule` | array | Weekday demand schedule -- 12x24 matrix, values are period indices into `demandratestructure` |
| `demandweekendschedule` | array | Weekend demand schedule -- 12x24 matrix, values are period indices into `demandratestructure` |
| `demandratchetpercentage` | array | Array of 12 decimal numbers, one demand ratchet percentage per month |
| `demandwindow` | decimal | Demand averaging window (minutes) |
| `demandreactivepowercharge` | decimal | Reactive power charge ($/kVAR) |
| `demandattrs` | array | Other demand attributes in key/value format |
| `demandcomments` | string | Demand rate comments |

### demandratestructure Detail

Each element in the top-level array corresponds to one TOU period. Each array element within a period corresponds to one tier. Indices are zero-based and correspond with `demandweekdayschedule` and `demandweekendschedule` entries.

**Tier object fields:**

| Field | Type | Description |
|-------|------|-------------|
| `rate` | decimal | Base demand rate ($/kW) |
| `adj` | decimal | Rate adjustment ($/kW) |
| `max` | decimal | Cumulative tier threshold (kW) |
| `sell` | decimal | Sell-back rate |

**Example:**

```json
"demandratestructure": [
  [{"rate": 0, "adj": 0}],
  [{"rate": 8.83}],
  [{"rate": 29.54}]
]
```

---

## Coincident Demand Charge Fields

| Field | Type | Description |
|-------|------|-------------|
| `coincidentrateunit` | enumeration | Rate units -- one of `"kW"`, `"hp"`, `"kVA"`, `"kW daily"`, `"hp daily"`, `"kVA daily"` |
| `coincidentratestructure` | array | Coincident rate tiers by period. Same format as `demandratestructure` |
| `coincidentrateschedule` | array | 12x24 matrix mapping month/hour to period indices in `coincidentratestructure` |

---

## Fixed Charge Fields

| Field | Type | Description |
|-------|------|-------------|
| `fixedchargefirstmeter` | decimal | Fixed monthly charge for first meter ($) |
| `fixedchargeunits` | string | Units for fixed charge (e.g., `"$/month"`) |
| `fixedmonthlycharge` | decimal | Fixed monthly charge ($) -- alternative field |
| `minmonthlycharge` | decimal | Minimum monthly charge ($) |
| `annualmincharge` | decimal | Annual minimum charge ($) |
| `fixedattrs` | array | Other fixed charge attributes in key/value format |

---

## Custom Extension Fields (Not in Official URDB API)

These fields are project-specific extensions added to improve human readability of tariff JSON files. They are **not** part of the official OpenEI/URDB API specification but are recognized and used throughout this project's codebase.

### energytoulabels

| | |
|---|---|
| **Type** | array of strings |
| **Purpose** | Human-readable labels for energy TOU periods |
| **Constraint** | Array length must match the number of periods in `energyratestructure` |
| **Index mapping** | Each label corresponds to the period at the same index |

**Example:**

```json
"energyratestructure": [
  [{"unit": "kWh", "rate": 0.18081, "adj": 0.00}],
  [{"unit": "kWh", "rate": 0.15754, "adj": 0.00}],
  [{"unit": "kWh", "rate": 0.39404, "adj": 0.00}]
],
"energytoulabels": [
  "Off-Peak",
  "Super Off-Peak",
  "Peak"
]
```

In this example, period index 0 in `energyratestructure` is labeled "Off-Peak", period 1 is "Super Off-Peak", and period 2 is "Peak".

### demandtoulabels

| | |
|---|---|
| **Type** | array of strings |
| **Purpose** | Human-readable labels for TOU demand charge periods |
| **Constraint** | Array length must match the number of periods in `demandratestructure` |
| **Index mapping** | Each label corresponds to the period at the same index |

**Example:**

```json
"demandratestructure": [
  [{"rate": 0.79, "adj": 2.06}],
  [{"rate": 12.81, "adj": 2.06}]
],
"demandtoulabels": [
  "Off-Peak",
  "On-Peak"
]
```

### Common Label Patterns

Labels typically follow the pattern `[Season] [Period Name]`:

| Label | Description |
|-------|-------------|
| `"On-Peak"` | Highest-cost period (typically afternoon/evening) |
| `"Off-Peak"` | Standard lower-cost period |
| `"Super Off-Peak"` | Lowest-cost period (typically overnight) |
| `"Mid-Peak"` | Intermediate period between on-peak and off-peak |
| `"Summer On-Peak"` | Season-specific peak period |
| `"Winter Off-Peak"` | Season-specific off-peak period |

When tariffs have combined season + TOU periods, each unique combination gets its own index in the rate structure and a corresponding label. For example, a tariff with summer/winter seasons and 3 TOU periods per season would have 6 entries in `energyratestructure` and 6 corresponding labels in `energytoulabels`.

---

## Local Database Field Mapping

When working with local URDB database exports (MongoDB / parquet) vs the API format, field names differ. This project expects the **API format** (lowercase). Conversion is required when importing from local database sources.

| Local DB Field (camelCase) | API Field (lowercase) |
|---|---|
| `_id.$oid` | `label` |
| `utilityName` | `utility` |
| `rateName` | `name` |
| `eiaId` | `eiaid` |
| `serviceType` | `servicetype` |
| `effectiveDate` | `startdate` |
| `endDate` | `enddate` |
| `demandMin` | `peakkwcapacitymin` |
| `demandMax` | `peakkwcapacitymax` |
| `energyMin` | `peakkwhusagemin` |
| `energyMax` | `peakkwhusagemax` |
| `voltageCategory` | `voltagecategory` |
| `phaseWiring` | `phasewiring` |
| **Energy Rates** | |
| `energyRateStrux` | `energyratestructure` |
| `energyWeekdaySched` | `energyweekdayschedule` |
| `energyWeekendSched` | `energyweekendschedule` |
| `energyTOULabels` | `energytoulabels` |
| `energyComments` | `energycomments` |
| **TOU Demand Rates** | |
| `demandRateStrux` | `demandratestructure` |
| `demandWeekdaySched` | `demandweekdayschedule` |
| `demandWeekendSched` | `demandweekendschedule` |
| `demandLabels` | `demandtoulabels` |
| `demandUnits` | `demandunits` |
| `demandRateUnit` | `demandrateunit` |
| **Flat Demand** | |
| `flatDemandStrux` | `flatdemandstructure` |
| `flatDemandMonths` | `flatdemandmonths` |
| `flatDemandUnit` | `flatdemandunit` |
| **Fixed Charges** | |
| `fixedChargeFirstMeter` | `fixedchargefirstmeter` |
| `fixedChargeUnits` | `fixedchargeunits` |
| `minMonthlyCharge` | `minmonthlycharge` |

### Rate Structure Format Differences

The local database format wraps tiers in a named key, while the API format uses flat arrays:

**API format (used by this project):**
```json
"energyratestructure": [
  [{"unit": "kWh", "rate": 0.18081, "adj": 0.00}],
  [{"unit": "kWh", "rate": 0.15754, "adj": 0.00}]
]
```

**Local DB format (requires conversion):**
```json
"energyRateStrux": [
  {"energyRateTiers": [{"unit": "kWh", "rate": 0.18081, "adj": 0.00}]},
  {"energyRateTiers": [{"unit": "kWh", "rate": 0.15754, "adj": 0.00}]}
]
```

---

## CSV Flattened Field Names

In the downloadable CSV from OpenEI, nested rate structures are flattened using this naming convention (period and tier numbers are zero-indexed):

| Structure | CSV Column Pattern |
|---|---|
| `energyratestructure` | `energyratestructure/period<N>/tier<N>rate`, `...max`, `...adj`, `...sell` |
| `demandratestructure` | `demandratestructure/period<N>/tier<N>rate`, `...max`, `...adj` |
| `flatdemandstructure` | `flatdemandstructure/period<N>/tier<N>rate`, `...max`, `...adj` |
| `coincidentratestructure` | `coincidentratestructure/period<N>/tier<N>rate`, `...max`, `...adj` |
| `flatdemandmonths` | `flatdemandmonth1` through `flatdemandmonth12` (1-indexed) |

---

## Complete Tariff JSON Example

A minimal but complete example showing a tariff with TOU energy rates, TOU demand charges, flat demand, and custom labels:

```json
{
  "items": [
    {
      "label": "6757525f259975f54b0eccbf",
      "utility": "Pacific Gas & Electric Co",
      "name": "BEV-2-S Business Electric Vehicle (Secondary Voltage)",
      "eiaid": 17609,
      "sector": "Commercial",
      "servicetype": "Bundled",
      "startdate": 1727762400,
      "voltagecategory": "Secondary",
      "phasewiring": "Single Phase",

      "energyratestructure": [
        [{"unit": "kWh", "rate": 0.18081, "adj": 0.00}],
        [{"unit": "kWh", "rate": 0.15754, "adj": 0.00}],
        [{"unit": "kWh", "rate": 0.39404, "adj": 0.00}]
      ],
      "energytoulabels": ["Off-Peak", "Super Off-Peak", "Peak"],
      "energyweekdayschedule": [
        [0,0,0,0,0,0,0,0,0, 1,1,1,1,1, 0,0, 2,2,2,2,2, 0,0,0],
        "... (12 rows total, one per month)"
      ],
      "energyweekendschedule": [
        [0,0,0,0,0,0,0,0,0, 1,1,1,1,1, 0,0, 2,2,2,2,2, 0,0,0],
        "... (12 rows total, one per month)"
      ],

      "flatdemandunit": "kW",
      "flatdemandstructure": [[{"rate": 1.91, "adj": 0}]],
      "flatdemandmonths": [0,0,0,0,0,0,0,0,0,0,0,0],

      "demandrateunit": "kW",

      "fixedchargefirstmeter": 447.44,
      "fixedchargeunits": "$/month"
    }
  ]
}
```
