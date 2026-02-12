import os
import json
import sys
from typing import Any
from dotenv import load_dotenv
from openai import OpenAI


MODEL_NAME = "gpt-4o-mini"  

def load_api():
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("[ERROR] OPENAI_API_KEY not found in environment.")
    return OpenAI(api_key=api_key)


def read_text_file(path: str) -> str:
    if not os.path.exists(path):
        raise FileNotFoundError(f"[ERROR] Input file not found: {path}")

    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    if not content.strip():
        raise ValueError("[ERROR] Input file is empty.")

    return content



def build_prompt(inspection_text: str) -> str:
    return f"""
You are a building diagnostics expert with over 15 years of experience in diagnosing houses.

Extract impacted areas and observations from the inspection text.

Return a STRICT JSON only in this exact format:

{{
  "areas": [
    {{
      "area_name": "string",
      "negative_observation": "string",
      "positive_source": "string",
      "thermal_confirmation": "Not Available",
      "confidence": "High | Medium | Low"
    }}
  ]
}}

 make sure to follow these Rules:
- Only use information from provided text.
- Do NOT refer any other sources or create new data.
- If positive source not clearly stated, use "Not Available".
- Do NOT include comments.
- Return valid JSON only.

Inspection Text:
-----------------
{inspection_text}
"""

def validate_structure(data: Any):
    if "areas" not in data:
        raise ValueError("[ERROR] Missing 'areas' key in response.")

    if not isinstance(data["areas"], list):
        raise ValueError("[ERROR] 'areas' must be a list.")

    required_keys = {
        "area_name",
        "negative_observation",
        "positive_source",
        "thermal_confirmation",
        "confidence"
    }

    for idx, area in enumerate(data["areas"]):
        if not isinstance(area, dict):
            raise ValueError(f"[ERROR] Area index {idx} is not an object.")

        missing = required_keys - area.keys()
        extra = area.keys() - required_keys

        if missing:
            raise ValueError(f"[ERROR] Area index {idx} missing keys: {missing}")

        if extra:
            raise ValueError(f"[ERROR] Area index {idx} has unexpected keys: {extra}")

        if not area["area_name"].strip():
            raise ValueError(f"[ERROR] Area index {idx} has empty area_name.")

        if not area["negative_observation"].strip():
            raise ValueError(f"[ERROR] Area index {idx} has empty negative_observation.")



def extract_areas(inspection_text: str) -> dict:
    client = load_api()

    prompt = build_prompt(inspection_text)

    response = client.chat.completions.create(
        model=MODEL_NAME,
        temperature=0,
        messages=[
            {"role": "system", "content": "You output strict JSON only."},
            {"role": "user", "content": prompt}
        ],
    )

    raw_output = response.choices[0].message.content.strip()

    try:
        parsed = json.loads(raw_output)
    except json.JSONDecodeError:
        raise ValueError("[ERROR] Model did not return valid JSON.")

    validate_structure(parsed)

    return parsed



def save_json(data: dict, output_path: str):
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    print(f"[SUCCESS] Areas extracted and saved to {output_path}")



def main():
    if len(sys.argv) != 3:
        print("Usage: python extract_areas.py <inspection_txt> <output_json>")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2]

    print(f"[INFO] Reading inspection file: {input_path}")
    inspection_text = read_text_file(input_path)

    print("[INFO] Extracting areas using LLM...")
    areas_data = extract_areas(inspection_text)

    print(f"[INFO] Extracted {len(areas_data['areas'])} areas.")

    save_json(areas_data, output_path)

    print("[DONE] Area extraction complete.\n")


if __name__ == "__main__":
    main()
