"""Rule-based cost, valuation and material estimation in INR."""

RATE = {"Residential House": 2200, "Apartment Block": 2500, "Commercial Building": 2900, "Industrial Shed": 1600}
TIER_COST = {"Tier 1": 1.00, "Tier 2": 0.85, "Tier 3": 0.72}
TIER_MARKET = {"Tier 1": 9500, "Tier 2": 5800, "Tier 3": 3400}  # Rs per sqft market value
STRUCT_PREMIUM = {"Residential House": 1.0, "Apartment Block": 1.05, "Commercial Building": 1.35, "Industrial Shed": 0.7}
STEEL_KG = {"Residential House": 3.8, "Apartment Block": 4.2, "Commercial Building": 5.0, "Industrial Shed": 6.0}
CEMENT_BAGS_PER_SQFT = 0.4
UNFINISHED_DISCOUNT = 0.8
MILESTONES = [(10, "Site prep & excavation"), (25, "Foundation"), (45, "Superstructure / slabs"),
              (65, "Masonry & roofing"), (85, "MEP & plastering"), (100, "Finishing & handover")]


def inr(v: float) -> str:
    """Format rupees as Lakh / Crore."""
    return f"₹{v / 1e7:,.2f} Cr" if v >= 1e7 else f"₹{v / 1e5:,.2f} Lakh"


def calculate_project(structure: str, area_sqft: float, tier: str, completion_pct: float) -> dict:
    if structure not in RATE or tier not in TIER_COST:
        raise ValueError("Unknown structure type or tier")
    if area_sqft <= 0 or not 0 <= completion_pct <= 100:
        raise ValueError("Area must be > 0 and completion between 0 and 100")
    budget = area_sqft * RATE[structure] * TIER_COST[tier]
    capex = budget * completion_pct / 100
    full_value = area_sqft * TIER_MARKET[tier] * STRUCT_PREMIUM[structure]
    factor = 1 if completion_pct == 100 else UNFINISHED_DISCOUNT
    return {"budget": budget, "capex": capex, "remaining": budget - capex,
            "full_value": full_value, "current_value": full_value * completion_pct / 100 * factor,
            "steel_tonnes": area_sqft * STEEL_KG[structure] / 1000,
            "cement_bags": area_sqft * CEMENT_BAGS_PER_SQFT}
