import subprocess
import sys
import os

SCRIPTS_DIR = "scripts"
DATA_DIR = "data"

INSPECTION_PDF = os.path.join(DATA_DIR, "Sample Report.pdf")
THERMAL_PDF = os.path.join(DATA_DIR, "Thermal Images.pdf")

INSPECTION_TXT = os.path.join(DATA_DIR, "inspection.txt")
THERMAL_TXT = os.path.join(DATA_DIR, "thermal.txt")

AREAS_JSON = os.path.join(DATA_DIR, "areas.json")
SYSTEMS_JSON = os.path.join(DATA_DIR, "systems.json")
THERMAL_JSON = os.path.join(DATA_DIR, "thermal.json")
DIAGNOSTIC_JSON = os.path.join(DATA_DIR, "diagnostic.json")


def run(cmd):
    print(f"\n PIPELINE Running: {' '.join(cmd)}")
    # Always use the current venv interpreter
    result = subprocess.run([sys.executable] + cmd)
    if result.returncode != 0:
        print("[PIPELINE ERROR] Step failed.")
        sys.exit(1)


def main():
    print("\n========== STARTING DDR PIPELINE ==========\n")

    # 1. Inspection OCR
    run([
        os.path.join(SCRIPTS_DIR, "extract_text.py"),
        INSPECTION_PDF,
        INSPECTION_TXT
    ])

    # 2. Thermal OCR
    run([
        os.path.join(SCRIPTS_DIR, "extract_text_ocr.py"),
        THERMAL_PDF,
        THERMAL_TXT
    ])

    # 3. Area Extraction
    run([
        os.path.join(SCRIPTS_DIR, "extract_areas.py"),
        INSPECTION_TXT,
        AREAS_JSON
    ])

    # 4. System Extraction
    run([
        os.path.join(SCRIPTS_DIR, "extract_systems.py"),
        INSPECTION_TXT,
        SYSTEMS_JSON
    ])

    # 5. Thermal Extraction
    run([
        os.path.join(SCRIPTS_DIR, "extract_thermal.py"),
        THERMAL_TXT,
        THERMAL_JSON
    ])

    # 6. Merge + Validate
    run([
        os.path.join(SCRIPTS_DIR, "merge.py"),
        AREAS_JSON,
        SYSTEMS_JSON,
        THERMAL_JSON,
        DIAGNOSTIC_JSON
    ])

    print("\n========== PIPELINE COMPLETE ==========\n")
    print(f"Final output → {DIAGNOSTIC_JSON}")


if __name__ == "__main__":
    main()
