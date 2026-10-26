"""JSON data contracts (Epic 4): normalise/validate model output before the UI renders it."""

SEVERITIES = ("Low", "Medium", "High", "Critical")
PPE_ITEMS = ("helmet", "high_vis_vest", "steel_toe_boots", "safety_harness")
PPE_STATUS = ("Detected", "Missing", "Not Visible")
DEFECTS = ("Hairline", "Settlement", "Structural Shear", "Thermal Expansion", "Spalling")


def _clamp(v, lo, hi, default=0):
    try:
        return max(lo, min(hi, int(round(float(v)))))
    except (TypeError, ValueError):
        return default


def _pick(v, allowed, default):
    for a in allowed:
        if str(v).strip().lower() == a.lower():
            return a
    return default


def normalize_ppe(d: dict) -> dict:
    d = d if isinstance(d, dict) else {}
    det = d.get("ppe_detection") if isinstance(d.get("ppe_detection"), dict) else {}
    ppe = {}
    for item in PPE_ITEMS:
        x = det.get(item) if isinstance(det.get(item), dict) else {}
        ppe[item] = {"status": _pick(x.get("status"), PPE_STATUS, "Not Visible"), "note": str(x.get("note", ""))}
    hazards = []
    for h in d.get("hazards") or []:
        if isinstance(h, dict):
            hazards.append({"hazard": str(h.get("hazard", "Unspecified hazard")),
                            "severity": _pick(h.get("severity"), SEVERITIES, "Medium"),
                            "remedy": str(h.get("remedy", ""))})
    return {"safety_score": _clamp(d.get("safety_score"), 0, 100),
            "overall_status": str(d.get("overall_status", "Unknown")),
            "workers_detected": _clamp(d.get("workers_detected"), 0, 10000),
            "ppe_detection": ppe, "hazards": hazards, "summary": str(d.get("summary", ""))}


def normalize_crack(d: dict) -> dict:
    d = d if isinstance(d, dict) else {}
    try:
        width = round(max(0.0, float(d.get("estimated_width_mm", 0))), 2)
    except (TypeError, ValueError):
        width = 0.0
    as_list = lambda v: [str(i) for i in v] if isinstance(v, list) else []
    return {"defect_type": _pick(d.get("defect_type"), DEFECTS, "Hairline"),
            "severity_score": _clamp(d.get("severity_score"), 0, 100),
            "estimated_width_mm": width,
            "urgency": _pick(d.get("urgency"), SEVERITIES, "Medium"),
            "root_causes": as_list(d.get("root_causes")),
            "recommended_repairs": as_list(d.get("recommended_repairs")),
            "monitoring_advice": str(d.get("monitoring_advice", "")),
            "summary": str(d.get("summary", ""))}
