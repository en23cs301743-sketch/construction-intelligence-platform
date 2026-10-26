"""Gemini multimodal calls, prompts and demonstration fallbacks. No Streamlit imports here."""
import json
import re

PPE_PROMPT = """You are a certified construction safety officer auditing a site photo against OSHA 1926 and
Indian standards (IS 456 for concrete works, BOCW rules). Check workers for: helmet, high-vis vest, steel-toe boots,
safety harness (when working at height). Return ONLY JSON:
{"safety_score":0-100,"overall_status":"Compliant|Partially Compliant|Non-Compliant","workers_detected":int,
"ppe_detection":{"helmet":{"status":"Detected|Missing|Not Visible","note":""},"high_vis_vest":{...},
"steel_toe_boots":{...},"safety_harness":{...}},
"hazards":[{"hazard":"","severity":"Low|Medium|High|Critical","remedy":""}],"summary":""}"""

CRACK_PROMPT = """You are a structural engineer diagnosing a concrete/masonry surface photo. Return ONLY JSON:
{"defect_type":"Hairline|Settlement|Structural Shear|Thermal Expansion|Spalling","severity_score":0-100,
"estimated_width_mm":float,"urgency":"Low|Medium|High|Critical","root_causes":[""],
"recommended_repairs":["e.g. epoxy injection, structural re-grouting"],"monitoring_advice":"","summary":""}
Reference IS 456 durability/crack-width limits (0.3 mm for moderate exposure)."""

CHAT_SYSTEM = ("You are a senior site engineer assistant for Indian construction projects. Be concise, practical, "
               "cite IS codes (IS 456, IS 875, IS 1893, NBC 2016) and OSHA where relevant, use INR, and flag "
               "when a licensed structural engineer must be consulted.")

DEMO_PPE = {
    "safety_score": 62, "overall_status": "Partially Compliant", "workers_detected": 4,
    "ppe_detection": {
        "helmet": {"status": "Detected", "note": "3 of 4 workers wearing hard hats"},
        "high_vis_vest": {"status": "Detected", "note": "All visible workers compliant"},
        "steel_toe_boots": {"status": "Not Visible", "note": "Footwear not clearly visible"},
        "safety_harness": {"status": "Missing", "note": "Worker on scaffold without harness"}},
    "hazards": [
        {"hazard": "Unprotected work at height on scaffold", "severity": "Critical",
         "remedy": "Stop work; issue full-body harness anchored to a rated lifeline."},
        {"hazard": "Worker without helmet near overhead activity", "severity": "High",
         "remedy": "Enforce mandatory helmet zone; toolbox talk before shift."},
        {"hazard": "Loose rebar offcuts on walkway", "severity": "Medium",
         "remedy": "Housekeeping sweep; designate scrap bins."}],
    "summary": "DEMO MODE: sample audit shown. Add a Gemini API key for real image analysis."}

DEMO_CRACK = {
    "defect_type": "Structural Shear", "severity_score": 78, "estimated_width_mm": 1.8, "urgency": "High",
    "root_causes": ["Differential settlement of footing", "Inadequate shear reinforcement near support",
                    "Overloading beyond design capacity"],
    "recommended_repairs": ["Low-viscosity epoxy injection", "Structural re-grouting with non-shrink grout",
                            "Jacketing of affected member after structural review"],
    "monitoring_advice": "Install tell-tale gauges and record width weekly for 8 weeks.",
    "summary": "DEMO MODE: diagonal crack pattern suggests shear distress; engage a structural engineer."}

_DEMO_REPLIES = [
    (("cure", "curing"), "Cure concrete at least 7 days (10 for blended cements/hot weather), keeping surfaces continuously wet."),
    (("m25", "mix", "grade", "concrete"), "M25 nominal mix is 1 : 1 : 2 (cement : sand : aggregate) per IS 456, with w/c ≤ 0.50. Prefer a design mix with 28-day cube tests for structural members."),
    (("steel", "rebar"), "Typical residential RCC uses 3.5-4.5 kg steel per sqft. Use Fe500D with proper cover (e.g. 40 mm for columns)."),
    (("crack",), "Crack width < 0.3 mm is generally acceptable; wider or diagonal cracks need structural review. Use the Crack Diagnostics tab."),
    (("helmet", "ppe", "safety"), "Mandatory PPE: helmet, high-vis vest, safety boots, harness above 1.8 m, plus gloves and eye protection as required."),
]


def demo_reply(question: str) -> str:
    q = question.lower()
    for keys, ans in _DEMO_REPLIES:
        if any(k in q for k in keys):
            return ans + "\n\n*(Demo mode: add a Gemini key for full answers.)*"
    return ("I'm in demo mode with limited answers. Ask about concrete mix, curing, steel, cracks or PPE, "
            "or add a Gemini API key.")


def parse_json(text: str) -> dict:
    text = re.sub(r"^```(?:json)?|```$", "", text.strip(), flags=re.M).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        m = re.search(r"\{.*\}", text, re.S)
        if not m:
            raise
        return json.loads(m.group(0))


def _model(api_key, model_name, system=None):
    import google.generativeai as genai
    genai.configure(api_key=api_key)
    return genai.GenerativeModel(model_name, system_instruction=system)


def analyze_image(api_key, model_name, prompt, image) -> dict:
    resp = _model(api_key, model_name).generate_content(
        [prompt, image], generation_config={"response_mime_type": "application/json", "temperature": 0.2})
    return parse_json(resp.text)


def chat_reply(api_key, model_name, history, question, weather="Normal") -> str:
    """history: list of (role, text) with role in {'user','assistant'}."""
    model = _model(api_key, model_name, CHAT_SYSTEM + f" Current site weather: {weather}.")
    hist = [{"role": "user" if r == "user" else "model", "parts": [m]} for r, m in history]
    return model.start_chat(history=hist).send_message(question).text
