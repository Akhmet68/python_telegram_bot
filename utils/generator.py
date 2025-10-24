import json, random
from pathlib import Path

PROMPTS_DIR = Path(__file__).resolve().parent.parent / "prompts"

def load_task(level: str) -> dict:
    mapping = {
        "beginner": "beginner.json",
        "intermediate": "intermediate.json",
        "advanced": "advanced.json"
    }
    name = mapping.get(level, "beginner.json")
    with open(PROMPTS_DIR / name, "r", encoding="utf-8") as f:
        data = json.load(f)
    return random.choice(data)
