# 🏗️ Multimodal Construction Intelligence Platform

**Skill Wallet Capstone – Project 1** · Generative AI | Real Estate Decision Support

An AI decision-support app that analyses construction-site photos to audit PPE compliance, diagnose concrete
cracks, estimate project cost and real-estate value in INR, and give weather-aware daily site protocols.

## Features
| Tab | Epic | What it does |
|---|---|---|
| 🦺 Safety & PPE Audit | 2 | Gemini vision checks helmet, hi-vis vest, steel-toe boots, harness (OSHA / IS 456). Safety score 0-100, hazards with severity (Low → Critical) + remedies, JSON download |
| 🧱 Crack Diagnostics | 2 | Classifies Hairline / Settlement / Structural Shear / Thermal Expansion / Spalling, width (mm), root causes, repairs (epoxy injection, re-grouting), urgency |
| 💰 Planning & Valuation | 3 | Budget, capex, current asset value (Lakh/Crore), steel & cement needs, milestone tracker, Pollinations/Flux 3D concept render |
| 🌦️ Site Assistant | 5 | Weather protocols (High Wind, Heavy Rain, Extreme Heat, Normal) + multi-turn engineering chatbot |

**Demo mode:** with no API key the app still works end-to-end using sample outputs, so it never crashes for reviewers.

## Architecture
```
app.py              Streamlit UI (4 tabs + sidebar)
core/ai.py          Gemini calls, prompts, demo fallbacks
core/contracts.py   JSON data contracts (Epic 4): validates/clamps model output
core/cost.py        Cost, valuation, material estimation (INR)
core/weather.py     Weather safety protocols
tests/              pytest unit + Streamlit AppTest smoke tests (Epic 6)
```
Model output → `parse_json` → `normalize_*` contract → UI. Invalid or partial JSON can't break the interface.

## Run locally
```bash
python -m venv venv && source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```
Paste a [Gemini API key](https://aistudio.google.com/app/apikey) in the sidebar (or set `GEMINI_API_KEY` in
`.streamlit/secrets.toml`, see `secrets.toml.example`).

## Tests
```bash
pip install -r requirements-dev.txt
python -m pytest -q
```

## Deploy on Streamlit Community Cloud (free)
1. Push this repo to GitHub.
2. Go to https://share.streamlit.io → **New app** → select repo, branch `main`, main file `app.py`.
3. (Optional) Settings → Secrets → `GEMINI_API_KEY = "your-key"`.
4. Deploy and copy the public URL for your submission.

## Notes & limitations
- Cost rates (₹/sqft), tier multipliers and steel/cement factors are indicative assumptions in `core/cost.py`.
- AI output is advisory; structural decisions need a licensed engineer.
- Gemini model names change over time; edit the model list in `app.py` if one is retired.
- Never commit your API key (`secrets.toml` is git-ignored).

## License
MIT
