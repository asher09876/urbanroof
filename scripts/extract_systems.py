import os
import json
import sys
from typing import Any
from dotenv import load_dotenv
from openai import OpenAI


MODEL_NAME = "gpt-4o-mini"



def load_api():
    load_dotenv()
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        raise ValueError("[ERROR] OPENAI_API_KEY is missing.")
    return OpenAI(api_key=key)


def read_text(path: str) -> str:
    if not os.path.exists(path):
        raise FileNotFoundError(f"[ERROR] File not found: {path}")

    with open(path, "r", encoding="utf-8") as f:
        text = f.read()

    if not text.strip():
        raise ValueError("[ERROR] Empty inspection text.")

    return text


def build_prompt(text: str) -> str:
    return f"""
You are a building diagnostics engineer with over 10 years of experience.

Extract ONLY system-level issues from the inspection text.

Return STRICT JSON in this exact structure:

{{
  "bathroom_issues": {{
    "tile_joint_gaps": "Yes | No | Not Available",
    "nahani_trap_damage": "Yes | No | Not Available",
    "concealed_plumbing": "Yes | No | Not Available"
  }},
  "external_wall": {{
    "cracks_present": "Yes | No | Not Available",
    "vegetation": "Yes | No | Not Available",
    "internal_dampness": "Yes | No | Not Available"
  }},
  "terrace": {{
    "surface_cracks": "Yes | No | Not Available",
    "hollow_sound": "Yes | No | Not Available",
    "slope_disturbance": "Yes | No | Not Available"
  }},
  "parking": {{
    "ceiling_leakage": "Yes | No | Not Available"
  }}
}}

Rules:
- Use ONLY provided text.
- Do NOT infer or create new data.
- Missing → "Not Available".
- Return valid JSON only.
- Do not add any commentary.

Inspection Text:
----------------
{text}
"""


ALLOWED = {"Yes", "No", "Not Available"}

EXPECTED_SCHEMA = {
    "bathroom_issues": ["tile_joint_gaps", "nahani_trap_damage", "concealed_plumbing"],
    "external_wall": ["cracks_present", "vegetation", "internal_dampness"],
    "terrace": ["surface_cracks", "hollow_sound", "slope_disturbance"],
    "parking": ["ceiling_leakage"]
}


def validate(data: Any):
    for section, fields in EXPECTED_SCHEMA.items():
        if section not in data:
            raise ValueError(f"[ERROR] Missing section: {section}")

        for field in fields:
            if field not in data[section]:
                raise ValueError(f"[ERROR] Missing field {field} in {section}")

            value = data[section][field]

            if value not in ALLOWED:
                raise ValueError(
                    f"[ERROR] Invalid value '{value}' for {section}.{field}"
                )



def extract_systems(text: str) -> dict:
    client = load_api()

    prompt = build_prompt(text)

    response = client.chat.completions.create(
        model=MODEL_NAME,
        temperature=0,
        messages=[
            {"role": "system", "content": "Return strict JSON only."},
            {"role": "user", "content": prompt}
        ],
    )

    raw = response.choices[0].message.content.strip()

    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        raise ValueError("[ERROR] LLM did not return valid JSON.")

    validate(parsed)

    return parsed


# -----------------------------
# Save
# -----------------------------

def save(data: dict, path: str):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    print(f"[SUCCESS] Systems extracted → {path}")


# -----------------------------
# Main
# -----------------------------

def main():
    if len(sys.argv) != 3:
        print("Usage: python extract_systems.py <inspection_txt> <systems_json>")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2]

    print("[INFO] Reading inspection text...")
    text = read_text(input_path)

    print("[INFO] Extracting system-level issues...")
    systems = extract_systems(text)

    save(systems, output_path)

    print("[DONE] System extraction complete.\n")


if __name__ == "__main__":
    main()
