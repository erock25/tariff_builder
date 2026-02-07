"""
Utility functions for color mapping, tariff normalization, and period extraction.
"""

from typing import Dict, List

from src.constants import FIELD_MAP


def get_heatmap_color(value: float) -> str:
    """Generate heatmap color from green (0) through yellow (0.5) to red (1)."""
    value = max(0.0, min(1.0, value))
    if value <= 0.5:
        r = int(255 * (value * 2))
        g = 200
        b = int(100 * (1 - value * 2))
    else:
        r = 255
        g = int(200 * (1 - (value - 0.5) * 2))
        b = 0
    return f"#{r:02x}{g:02x}{b:02x}"


def assign_heatmap_colors(periods: List[Dict]) -> List[Dict]:
    """Assign colors based on rate *rank*, evenly spaced across the palette.

    This ensures every period gets a visually distinct color regardless of
    how close the actual rate values are to each other.  Periods with the
    exact same total rate share the same rank (and therefore the same color).
    """
    if not periods:
        return periods

    n = len(periods)
    if n == 1:
        periods[0]["color"] = get_heatmap_color(0.0)
        return periods

    # Build (total_rate, original_index) pairs and sort by rate
    indexed = [(p.get("rate", 0) + p.get("adj", 0), i) for i, p in enumerate(periods)]
    indexed.sort(key=lambda x: x[0])

    # Assign dense ranks (ties share the same rank)
    ranks = [0] * n
    current_rank = 0
    for pos, (rate, orig_idx) in enumerate(indexed):
        if pos > 0 and rate != indexed[pos - 1][0]:
            current_rank += 1
        ranks[orig_idx] = current_rank

    max_rank = current_rank  # highest rank value

    # Map ranks to evenly-spaced positions on the 0-1 color scale
    for i, p in enumerate(periods):
        norm = ranks[i] / max_rank if max_rank > 0 else 0.0
        p["color"] = get_heatmap_color(norm)

    return periods


def normalize_tariff(tariff: Dict) -> Dict:
    """Normalize a tariff dict to API-format lowercase field names."""
    out = {}
    for k, v in tariff.items():
        api_key = FIELD_MAP.get(k, k)
        out[api_key] = v

    # Normalize nested rate structures (energyRateStrux style -> flat arrays)
    for struct_key in ["energyratestructure", "demandratestructure", "flatdemandstructure"]:
        struct = out.get(struct_key)
        if not isinstance(struct, list):
            continue
        converted = []
        for item in struct:
            if isinstance(item, dict):
                # Find a tier key like energyRateTiers, flatDemandTiers, etc.
                tier_key = next((k for k in item if "Tier" in k or "tier" in k), None)
                if tier_key:
                    converted.append(item[tier_key])
                else:
                    converted.append([item])
            elif isinstance(item, list):
                converted.append(item)
            else:
                converted.append([])
        out[struct_key] = converted

    return out


def extract_periods_from_structure(
    structure: List, labels: List, default_label: str = "Period"
) -> List[Dict]:
    """Extract period configs from a URDB rate structure + label array."""
    periods = []
    for idx, period_tiers in enumerate(structure):
        rate, adj = 0.0, 0.0
        if isinstance(period_tiers, list) and period_tiers:
            tier = period_tiers[0]
            if isinstance(tier, dict):
                rate = float(tier.get("rate", 0) or 0)
                adj = float(tier.get("adj", 0) or 0)
        label = labels[idx] if idx < len(labels) else f"{default_label} {idx}"
        periods.append({"label": label, "rate": rate, "adj": adj})
    return assign_heatmap_colors(periods) if periods else []
