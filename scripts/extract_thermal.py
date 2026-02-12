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
        raise ValueError("[ERROR] OPENAI_API_KEY missing.")
    return OpenAI(api_key=key)


def read_text(path: str) -> str:
    if not os.path.exists(path):
        raise FileNotFoundError(f"[ERROR] File not found: {path}")

    with open(path, "r", encoding="utf-8") as f:
        text = f.read()

    if not text.strip():
        raise ValueError("[ERROR] Thermal text is empty.")

    return text


def build_prompt(text: str) -> str:
    return f"""
You are a thermal diagnostics specialist with over 15 years of experience.

Extract thermal readings from the text.

Return STRICT JSON in this exact structure:

{{
  "thermal_readings": [
    {{
      "image_name": "string",
      "hotspot_temp": number,
      "coldspot_temp": number,
      "temperature_difference": number,
      "moisture_indicator": "Yes | No",
      "area_reference": "string or Not Available",
      "confidence": "High | Medium | Low"
    }}
  ]
}}

Rules:
- temperature_difference = hotspot_temp - coldspot_temp
- moisture_indicator = "Yes" if temperature_difference >= 3°C
- If area not explicitly mentioned → "Not Available"
- Do NOT invent areas.
- Return valid JSON only.
- No commentary.

Thermal Text:
--------------
{text}
"""



def validate(data: Any):
    if "thermal_readings" not in data:
        raise ValueError("[ERROR] Missing 'thermal_readings' key.")

    if not isinstance(data["thermal_readings"], list):
        raise ValueError("[ERROR] thermal_readings must be a list.")

    for idx, item in enumerate(data["thermal_readings"]):
        required = {
            "image_name",
            "hotspot_temp",
            "coldspot_temp",
            "temperature_difference",
            "moisture_indicator",
            "area_reference",
            "confidence"
        }

        missing = required - item.keys()
        if missing:
            raise ValueError(f"[ERROR] Missing keys in reading {idx}: {missing}")

        if not isinstance(item["hotspot_temp"], (int, float)):
            raise ValueError(f"[ERROR] Invalid hotspot_temp at index {idx}")

        if not isinstance(item["coldspot_temp"], (int, float)):
            raise ValueError(f"[ERROR] Invalid coldspot_temp at index {idx}")

        computed_diff = round(
            item["hotspot_temp"] - item["coldspot_temp"], 2
        )

        if abs(computed_diff - item["temperature_difference"]) > 0.1:
            raise ValueError(
                f"[ERROR] Incorrect temperature_difference at index {idx}"
            )

        if item["moisture_indicator"] not in {"Yes", "No"}:
            raise ValueError(
                f"[ERROR] Invalid moisture_indicator at index {idx}"
            )



def extract_thermal(text: str) -> dict:
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



def save(data: dict, path: str):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    print(f"[SUCCESS] Thermal data saved → {path}")



def main():
    if len(sys.argv) != 3:
        print("Usage: python extract_thermal.py <thermal_txt> <thermal_json>")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2]

    print("[INFO] Reading thermal text...")
    text = read_text(input_path)

    print("[INFO] Extracting thermal readings...")
    thermal_data = extract_thermal(text)

    print(f"[INFO] Extracted {len(thermal_data['thermal_readings'])} readings.")

    save(thermal_data, output_path)

    print("[DONE] Thermal extraction complete.\n")


if __name__ == "__main__":
    main()
