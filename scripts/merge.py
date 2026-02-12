import json
import sys
import os



def load_json(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"[ERROR] Missing file: {path}")

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(data, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    print(f"[SUCCESS] Diagnostic file written → {path}")



def attach_thermal(areas, thermal):
    readings = thermal.get("thermal_readings", [])

    for area in areas:
        area_name = area["area_name"].lower()

        matched = []

        for t in readings:
            ref = t["area_reference"].lower()

            if ref != "not available" and ref in area_name:
                matched.append(t)

        if matched:
            area["thermal_confirmation"] = "Moisture Detected"
        else:
            area["thermal_confirmation"] = "Not Available"

    return areas



def infer_root_causes(systems):
    causes = []

    if systems["bathroom_issues"]["tile_joint_gaps"] == "Yes":
        causes.append("Bathroom waterproofing failure")

    if systems["external_wall"]["cracks_present"] == "Yes":
        causes.append("External wall crack ingress")

    if systems["terrace"]["surface_cracks"] == "Yes":
        causes.append("Terrace surface deterioration")

    if systems["parking"]["ceiling_leakage"] == "Yes":
        causes.append("Vertical moisture migration")

    return list(set(causes))



def compute_severity(areas, systems):
    impacted = len(areas)

    bathroom = systems["bathroom_issues"]["tile_joint_gaps"] == "Yes"
    terrace = systems["terrace"]["surface_cracks"] == "Yes"
    external = systems["external_wall"]["cracks_present"] == "Yes"
    parking = systems["parking"]["ceiling_leakage"] == "Yes"

    if impacted >= 4 and (bathroom or terrace) and parking:
        return "High"

    if impacted >= 2 and (bathroom or external):
        return "Moderate"

    return "Low"


# -----------------------------
# Missing Data Detection
# -----------------------------

def detect_missing(areas, systems):
    missing = []

    for a in areas:
        for k, v in a.items():
            if v == "Not Available":
                missing.append(f"{a['area_name']}:{k}")

    for section, values in systems.items():
        for k, v in values.items():
            if v == "Not Available":
                missing.append(f"{section}:{k}")

    return missing


# -----------------------------
# Validation Phase (Phase 6)
# -----------------------------

def validate(diagnostic):
    if not diagnostic["areas"]:
        raise ValueError("[ERROR] No areas found.")

    if not diagnostic["overall"]["primary_root_causes"]:
        print("[WARNING] No root causes inferred.")

    if diagnostic["overall"]["severity"] not in {"Low", "Moderate", "High"}:
        raise ValueError("[ERROR] Invalid severity.")

    print("[VALIDATION] Areas:", len(diagnostic["areas"]))
    print("[VALIDATION] Root Causes:", diagnostic["overall"]["primary_root_causes"])
    print("[VALIDATION] Severity:", diagnostic["overall"]["severity"])
    print("[VALIDATION] Missing Fields:", len(diagnostic["overall"]["missing_information"]))



def main():
    if len(sys.argv) != 5:
        print("Usage: python merge.py areas.json systems.json thermal.json diagnostic.json")
        sys.exit(1)

    areas_path = sys.argv[1]
    systems_path = sys.argv[2]
    thermal_path = sys.argv[3]
    output_path = sys.argv[4]

    print("[INFO] Loading inputs...")
    areas_data = load_json(areas_path)
    systems = load_json(systems_path)
    thermal = load_json(thermal_path)

    areas = areas_data["areas"]

    print("[INFO] Attaching thermal...")
    areas = attach_thermal(areas, thermal)

    print("[INFO] Inferring root causes...")
    root_causes = infer_root_causes(systems)

    print("[INFO] Computing severity...")
    severity = compute_severity(areas, systems)

    print("[INFO] Detecting missing data...")
    missing = detect_missing(areas, systems)

    diagnostic = {
        "areas": areas,
        "bathroom_issues": systems["bathroom_issues"],
        "external_wall": systems["external_wall"],
        "terrace": systems["terrace"],
        "parking": systems["parking"],
        "overall": {
            "primary_root_causes": root_causes,
            "severity": severity,
            "missing_information": missing
        }
    }

    print("[INFO] Running validation...")
    validate(diagnostic)

    save_json(diagnostic, output_path)

    print("[DONE] Merge + validation complete.\n")


if __name__ == "__main__":
    main()
