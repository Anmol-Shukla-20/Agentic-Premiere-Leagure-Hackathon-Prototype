"""Shared configuration and small domain-specific lookup tables.

Keeping these values in one place makes the scoring rules easier to explain
in a demo and easier to tune later if the matching behavior needs adjustment.
"""

DEFAULT_LOCATION_KEYWORDS = ["lucknow", "amausi"]
DEFAULT_OUTCOME_STAGES = ["applied", "shortlisted", "interview", "hired", "rejected"]

SKILL_SYNONYMS = {
    "3 phase wiring": "three phase wiring",
    "three phase": "three phase wiring",
    "ac": "alternating current",
    "motor rewinding": "motor winding",
    "rewinding": "motor winding",
    "panel board": "panel wiring",
    "electrical panel": "panel wiring",
    "preventive maintenance": "maintenance",
    "lathe machine": "lathe operation",
    "welding": "arc welding",
    "measurement": "multimeter use",
    "testing": "troubleshooting",
}

DEFAULT_TOP_K = 3