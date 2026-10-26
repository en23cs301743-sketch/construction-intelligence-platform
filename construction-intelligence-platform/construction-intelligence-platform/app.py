"""Multimodal Construction Intelligence Platform (Skill Wallet Capstone Project 1).
Run: streamlit run app.py
"""
import json
import urllib.parse

import streamlit as st
from PIL import Image

from core import ai
from core.contracts import normalize_crack, normalize_ppe
from core.cost import MILESTONES, RATE, TIER_COST, calculate_project, inr
from core.weather import WEATHER

st.set_page_config(page_title="Construction Intelligence Platform", page_icon="🏗️", layout="wide")

st.markdown("""
<style>
.block-container{padding-top:1.5rem}
.hero{background:linear-gradient(120deg,#0f2027,#203a43,#2c5364);color:#fff;padding:1.2rem 1.6rem;border-radius:14px;margin-bottom:1rem}
.hero h1{margin:0;font-size:1.7rem;color:#fff}.hero p{margin:.2rem 0 0;opacity:.85}
.card{background:#f6f8fa;border:1px solid #e1e4e8;border-radius:12px;padding:.9rem 1.1rem;text-align:center}
.card .v{font-size:1.5rem;font-weight:700;color:#0b3d5c}.card .l{font-size:.78rem;color:#586069;text-transform:uppercase;letter-spacing:.04em}
.pill{display:inline-block;padding:.15rem .7rem;border-radius:999px;font-size:.8rem;font-weight:600;color:#fff}
.Low,.pass{background:#2da44e}.Medium,.warn{background:#b8860b}.High{background:#e5731a}.Critical,.fail{background:#cf222e}
@media (prefers-color-scheme: dark){.card{background:#1c2128;border-color:#30363d}.card .v{color:#79c0ff}.card .l{color:#8b949e}}
</style>
""", unsafe_allow_html=True)


# ------------------------------------------------------------ helpers
def card(label, value):
    st.markdown(f'<div class="card"><div class="v">{value}</div><div class="l">{label}</div></div>',
                unsafe_allow_html=True)


def pill(text, cls=None):
    return f'<span class="pill {cls or text}">{text}</span>'


def default_key():
    try:
        return st.secrets.get("GEMINI_API_KEY", "")
    except Exception:
        return ""


def run_analysis(image, prompt, demo, normalizer):
    """Live Gemini analysis with graceful fallback to demo data. Returns (result, is_demo)."""
    key = st.session_state.api_key
    if not key:
        return normalizer(demo), True
    try:
        return normalizer(ai.analyze_image(key, st.session_state.model_name, prompt, image)), False
    except Exception as e:
        st.warning(f"Live analysis failed ({type(e).__name__}: {str(e)[:120]}). Showing demonstration output.")
        return normalizer(demo), True


def upload_image(key):
    f = st.file_uploader("Upload site photo (JPG/PNG)", type=["jpg", "jpeg", "png"], key=key)
    if not f:
        return None
    try:
        img = Image.open(f).convert("RGB")
        img.thumbnail((1600, 1600))
        return img
    except Exception:
        st.error("Could not read that image. Please upload a valid JPG or PNG.")
        return None


# ------------------------------------------------------------ sidebar
for k, v in {"api_key": default_key(), "model_name": "gemini-2.5-flash", "chat": []}.items():
    st.session_state.setdefault(k, v)

with st.sidebar:
    st.title("🏗️ Control Panel")
    st.session_state.api_key = st.text_input(
        "Google Gemini API key", type="password", value=st.session_state.api_key,
        help="Leave empty to run in demonstration mode.").strip()
    st.session_state.model_name = st.selectbox("Model", ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash"])
    (st.success if st.session_state.api_key else st.info)(
        "Live mode: Gemini connected" if st.session_state.api_key else "Demonstration mode (no key)")
    st.markdown("---")
    st.subheader("Architecture")
    st.markdown("- **UI**: Streamlit\n- **Vision/LLM**: Gemini multimodal → JSON contracts\n- **Imaging**: Pillow\n"
                "- **Concept art**: Pollinations (Flux)\n- **Cost engine**: rule-based, INR\n- **State**: session only, no database")
    st.subheader("Features")
    st.markdown("1. PPE safety audit\n2. Crack diagnostics\n3. Cost & valuation\n4. Weather advisory & chatbot")
    st.caption("AI output is advisory. Have a licensed engineer verify structural decisions.")

st.markdown('<div class="hero"><h1>🏗️ Multimodal Construction Intelligence Platform</h1>'
            '<p>Safety auditing · Structural diagnostics · Cost & valuation · Weather-aware site assistant</p></div>',
            unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs(["🦺 Safety & PPE Audit", "🧱 Crack Diagnostics",
                                  "💰 Planning & Valuation", "🌦️ Site Assistant"])

# ------------------------------------------------------------ tab 1
with tab1:
    st.subheader("Site Safety & PPE Compliance Audit")
    img = upload_image("ppe_up")
    if img:
        c1, c2 = st.columns([1, 1.3])
        c1.image(img, caption="Site photo", use_container_width=True)
        if c2.button("Run safety audit", type="primary"):
            with st.spinner("Analyzing PPE compliance..."):
                st.session_state.ppe, st.session_state.ppe_demo = run_analysis(
                    img, ai.PPE_PROMPT, ai.DEMO_PPE, normalize_ppe)
    r = st.session_state.get("ppe")
    if r:
        if st.session_state.get("ppe_demo"):
            st.caption("⚠️ Demonstration data")
        score = r["safety_score"]
        scls = "pass" if score >= 80 else "warn" if score >= 60 else "fail"
        m = st.columns(3)
        with m[0]: card("Safety score", f"{score}/100")
        with m[1]: card("Workers detected", r["workers_detected"])
        with m[2]: card("Overall status", pill(r["overall_status"], scls))
        st.progress(score / 100)
        st.markdown("#### PPE checklist")
        for item, d in r["ppe_detection"].items():
            cls = {"Detected": "pass", "Missing": "fail"}.get(d["status"], "warn")
            st.markdown(f"**{item.replace('_', ' ').title()}** {pill(d['status'], cls)} {d['note']}",
                        unsafe_allow_html=True)
        st.markdown("#### Identified hazards")
        for h in r["hazards"]:
            st.markdown(f"{pill(h['severity'])} **{h['hazard']}**<br>↳ _Remedy:_ {h['remedy']}",
                        unsafe_allow_html=True)
        st.info(r["summary"])
        st.download_button("⬇️ Download JSON report", json.dumps(r, indent=2), "safety_report.json", "application/json")

# ------------------------------------------------------------ tab 2
with tab2:
    st.subheader("Crack Diagnostics & Structural Integrity")
    img = upload_image("crack_up")
    if img:
        c1, c2 = st.columns([1, 1.3])
        c1.image(img, caption="Surface photo", use_container_width=True)
        if c2.button("Diagnose defect", type="primary"):
            with st.spinner("Analyzing structural defect..."):
                st.session_state.crack, st.session_state.crack_demo = run_analysis(
                    img, ai.CRACK_PROMPT, ai.DEMO_CRACK, normalize_crack)
    r = st.session_state.get("crack")
    if r:
        if st.session_state.get("crack_demo"):
            st.caption("⚠️ Demonstration data")
        m = st.columns(4)
        with m[0]: card("Defect type", r["defect_type"])
        with m[1]: card("Severity score", f"{r['severity_score']}/100")
        with m[2]: card("Est. width", f"{r['estimated_width_mm']} mm")
        with m[3]: card("Urgency", pill(r["urgency"]))
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("#### Root causes")
            for x in r["root_causes"]: st.markdown(f"- {x}")
        with c2:
            st.markdown("#### Recommended repairs")
            for x in r["recommended_repairs"]: st.markdown(f"- {x}")
        st.warning(f"**Monitoring:** {r['monitoring_advice']}")
        st.info(r["summary"])
        st.download_button("⬇️ Download JSON report", json.dumps(r, indent=2), "crack_report.json", "application/json")

# ------------------------------------------------------------ tab 3
with tab3:
    st.subheader("Project Planning & Real Estate Valuation")
    c1, c2, c3 = st.columns(3)
    stype = c1.selectbox("Structure type", list(RATE))
    area = c2.number_input("Built-up area (sqft)", 200, 500000, 2000, step=100)
    tier = c3.selectbox("Location tier", list(TIER_COST), format_func=lambda t: f"{t} city")
    pct = st.slider("Completion %", 0, 100, 40)
    p = calculate_project(stype, area, tier, pct)

    m = st.columns(4)
    with m[0]: card("Total project budget", inr(p["budget"]))
    with m[1]: card("Capex incurred", inr(p["capex"]))
    with m[2]: card("Current asset value", inr(p["current_value"]))
    with m[3]: card("Value on completion", inr(p["full_value"]))
    m = st.columns(3)
    with m[0]: card("Steel required", f"{p['steel_tonnes']:,.1f} tonnes")
    with m[1]: card("Cement required", f"{p['cement_bags']:,.0f} bags")
    with m[2]: card("Remaining spend", inr(p["remaining"]))

    st.markdown("#### Milestone progress")
    st.progress(pct / 100)
    for col, (th, name) in zip(st.columns(len(MILESTONES)), MILESTONES):
        col.markdown(f"{'✅' if pct >= th else '⬜'} **{th}%**<br><small>{name}</small>", unsafe_allow_html=True)
    st.caption("Estimates use indicative per-sqft rates; actual costs vary with specifications and local rates.")

    st.markdown("#### 🎨 Conceptual 3D rendering (Pollinations AI)")
    style = st.text_input("Style notes", "modern, glass facade, landscaped entrance, golden hour")
    prompt = (f"photorealistic 3D architectural rendering of a {stype.lower()} in an Indian {tier.lower()} city, "
              f"{area} sqft, {style}, high detail")
    st.code(prompt, language=None)
    if st.button("Generate rendering"):
        url = ("https://image.pollinations.ai/prompt/" + urllib.parse.quote(prompt)
               + "?width=1024&height=640&nologo=true&model=flux")
        st.image(url, caption="AI concept render (illustrative only)", use_container_width=True)

# ------------------------------------------------------------ tab 4
with tab4:
    st.subheader("Daily Site Assistant & Weather-Aware Advisory")
    wx = st.radio("Today's weather", list(WEATHER), horizontal=True)
    icon, cls, alerts = WEATHER[wx]
    st.markdown(f"### {icon} {wx} protocol {pill('Alert' if wx != 'Normal' else 'Clear', cls)}",
                unsafe_allow_html=True)
    for a in alerts:
        (st.success if wx == "Normal" else st.error if cls == "fail" else st.warning)(a)

    st.markdown("---")
    st.markdown("#### 💬 Construction engineering assistant")
    for role, msg in st.session_state.chat:
        with st.chat_message(role):
            st.markdown(msg)
    q = st.chat_input("Ask about mixes, curing, codes, safety, scheduling...")
    if q:
        history = list(st.session_state.chat)
        st.session_state.chat.append(("user", q))
        with st.chat_message("user"):
            st.markdown(q)
        with st.chat_message("assistant"):
            if not st.session_state.api_key:
                ans = ai.demo_reply(q)
            else:
                try:
                    ans = ai.chat_reply(st.session_state.api_key, st.session_state.model_name, history, q, wx)
                except Exception as e:
                    ans = f"Live assistant error ({type(e).__name__}). Fallback: {ai.demo_reply(q)}"
            st.markdown(ans)
        st.session_state.chat.append(("assistant", ans))
    if st.session_state.chat and st.button("Clear conversation"):
        st.session_state.chat = []
        st.rerun()
