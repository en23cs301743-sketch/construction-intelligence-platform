"""Weather-aware site protocols (Epic 5). level: pass / warn / fail (drives UI colour)."""

WEATHER = {
    "Normal": ("🌤️", "pass", ["Standard PPE and toolbox talk at shift start.",
                              "Normal crane & lifting operations permitted with daily inspection.",
                              "Cure fresh concrete 7+ days with wet hessian (IS 456 cl. 13.5)."]),
    "High Wind": ("💨", "fail", ["SUSPEND crane operations when wind exceeds ~36 km/h; lower booms.",
                                 "Secure scaffolding sheets, formwork and loose materials.",
                                 "Stop work at height; keep workers clear of unfinished edges.",
                                 "Delay concrete pouring on exposed decks."]),
    "Heavy Rain": ("🌧️", "fail", ["Electrical hazard: de-energise temporary supply, use RCCB-protected circuits only.",
                                  "Cover fresh concrete with tarpaulin; avoid pouring during downpour.",
                                  "Dewater excavations and check trench shoring for collapse risk.",
                                  "Slip hazard: restrict access to scaffolds and ramps until dry."]),
    "Extreme Heat": ("🔥", "warn", ["Shift heavy work to early morning/evening; mandatory hydration breaks (ORS).",
                                    "Concrete curing: pour in cool hours, use chilled water/retarders, cure continuously 10 days.",
                                    "Watch for heat exhaustion; provide shaded rest areas.",
                                    "Inspect hot-weather effects on steel (thermal expansion) and formwork."]),
}
