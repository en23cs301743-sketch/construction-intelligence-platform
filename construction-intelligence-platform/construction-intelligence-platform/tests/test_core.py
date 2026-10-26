import pytest

from core import ai
from core.contracts import normalize_crack, normalize_ppe
from core.cost import calculate_project, inr
from core.weather import WEATHER


def test_parse_json_plain_and_fenced():
    assert ai.parse_json('{"a": 1}') == {"a": 1}
    assert ai.parse_json('```json\n{"a": 2}\n```') == {"a": 2}
    assert ai.parse_json('Here you go: {"a": 3} thanks') == {"a": 3}
    with pytest.raises(Exception):
        ai.parse_json("no json here")


def test_ppe_contract_clamps_and_defaults():
    r = normalize_ppe({"safety_score": 250, "hazards": [{"hazard": "x", "severity": "bogus"}]})
    assert r["safety_score"] == 100
    assert r["hazards"][0]["severity"] == "Medium"
    assert set(r["ppe_detection"]) == {"helmet", "high_vis_vest", "steel_toe_boots", "safety_harness"}
    assert normalize_ppe(None)["safety_score"] == 0


def test_crack_contract():
    r = normalize_crack({"defect_type": "spalling", "severity_score": "-5", "estimated_width_mm": "abc", "urgency": "critical"})
    assert r["defect_type"] == "Spalling" and r["severity_score"] == 0
    assert r["estimated_width_mm"] == 0.0 and r["urgency"] == "Critical"


def test_demo_data_passes_contract():
    assert normalize_ppe(ai.DEMO_PPE)["safety_score"] == 62
    assert normalize_crack(ai.DEMO_CRACK)["defect_type"] == "Structural Shear"


def test_cost_logic():
    p = calculate_project("Residential House", 1000, "Tier 1", 50)
    assert p["budget"] == 2_200_000 and p["capex"] == 1_100_000
    assert p["remaining"] == p["budget"] - p["capex"]
    assert calculate_project("Residential House", 1000, "Tier 3", 50)["budget"] < p["budget"]
    done = calculate_project("Residential House", 1000, "Tier 1", 100)
    assert done["current_value"] == done["full_value"]
    with pytest.raises(ValueError):
        calculate_project("Castle", 1000, "Tier 1", 10)
    with pytest.raises(ValueError):
        calculate_project("Residential House", 0, "Tier 1", 10)


def test_inr_format():
    assert inr(2_500_000) == "₹25.00 Lakh"
    assert inr(25_000_000) == "₹2.50 Cr"


def test_weather_has_all_conditions():
    assert set(WEATHER) == {"Normal", "High Wind", "Heavy Rain", "Extreme Heat"}
    assert any("crane" in a.lower() for a in WEATHER["High Wind"][2])


def test_demo_reply():
    assert "M25" in ai.demo_reply("What is M25 mix?")
    assert "demo mode" in ai.demo_reply("tell me a joke").lower()
