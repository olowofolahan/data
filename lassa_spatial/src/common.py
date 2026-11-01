"""Shared helpers: canonical state names and paths for the Lassa spatial project."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
EXTERNAL = ROOT / "data" / "external"
PROCESSED = ROOT / "data" / "processed"
OUTPUTS = ROOT / "outputs"
for _p in (PROCESSED, OUTPUTS):
    _p.mkdir(parents=True, exist_ok=True)

# The 37 surveillance units (36 states + FCT) exactly as spelled in State_Weekly.
CANON_STATES = [
    "Abia", "Adamawa", "Akwa Ibom", "Anambra", "Bauchi", "Bayelsa", "Benue",
    "Borno", "Cross River", "Delta", "Ebonyi", "Edo", "Ekiti", "Enugu", "FCT",
    "Gombe", "Imo", "Jigawa", "Kaduna", "Kano", "Katsina", "Kebbi", "Kogi",
    "Kwara", "Lagos", "Nasarawa", "Niger", "Ogun", "Ondo", "Osun", "Oyo",
    "Plateau", "Rivers", "Sokoto", "Taraba", "Yobe", "Zamfara",
]

# Map alternate spellings (Natural Earth, NBS, DHS, etc.) -> canonical.
NAME_FIXES = {
    "Federal Capital Territory": "FCT",
    "Abuja": "FCT",
    "Abuja Federal Capital Territory": "FCT",
    "Fct, Abuja": "FCT",
    "FCT, Abuja": "FCT",
    "Fct": "FCT",
    "Nassarawa": "Nasarawa",
    "Akwa-Ibom": "Akwa Ibom",
    "Cross-River": "Cross River",
    "Cross-river": "Cross River",
}


def canon(name: str) -> str:
    n = str(name).strip()
    return NAME_FIXES.get(n, n)
