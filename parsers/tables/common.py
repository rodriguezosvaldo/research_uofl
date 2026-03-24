import re

from ..variables import variables_to_extract


def normalize_label(text):
    return re.sub(r"[^a-z0-9]", "", str(text or "").lower())


def extract_type_1_by_variables(table, variable_names):
    extracted = {}
    for row in table[1:]:  # Skip title row
        if not row:
            continue
        for variable in variable_names:
            for idx, cell in enumerate(row):
                if re.search(variable, str(cell or "")):
                    value = row[idx + 1] if idx + 1 < len(row) else ""
                    extracted[variable] = (value or "").strip()
                    break
    return extracted


def extract_patient_information(table):
    expected_variables = set(variables_to_extract["Patient Information"])
    extracted = {}
    last_duration_field = None

    alias_map = {
        "signssymptoms": "Signs Symptoms",
        "medicaltrauma": "Medical Trauma",
        "alcoholdrugs": "Alcohol Drugs",
        "weight": "__WEIGHT__",
        "height": "__HEIGHT__",
    }
    normalized_expected = {
        normalize_label(variable): variable for variable in expected_variables
    }

    for row in table[1:]:  # Skip title row
        if not row:
            continue

        for idx in range(0, len(row), 2):
            key = row[idx] if idx < len(row) else ""
            value = row[idx + 1] if idx + 1 < len(row) else ""
            key_text = (key or "").strip()
            value_text = (value or "").strip()

            if not key_text:
                continue

            normalized_key = normalize_label(key_text)
            canonical = alias_map.get(normalized_key) or normalized_expected.get(normalized_key)

            if canonical in expected_variables:
                extracted[canonical] = value_text
                if canonical in {"Duration", "Secondary Duration"}:
                    last_duration_field = canonical
                continue

            if normalized_key == "units":
                if last_duration_field == "Duration":
                    extracted["Duration Units"] = value_text
                elif last_duration_field == "Secondary Duration":
                    extracted["Secondary Duration Units"] = value_text
                continue

            if canonical == "__WEIGHT__":
                pounds_match = re.search(r"([0-9]*\.?[0-9]+)\s*lbs?", value_text, re.IGNORECASE)
                kg_match = re.search(r"([0-9]*\.?[0-9]+)\s*kg", value_text, re.IGNORECASE)
                if pounds_match:
                    extracted["Weight-lbs"] = pounds_match.group(1)
                if kg_match:
                    extracted["Weight-kg"] = kg_match.group(1)
                continue

            if canonical == "__HEIGHT__":
                feet_match = re.search(r"([0-9]*\.?[0-9]+)\s*ft", value_text, re.IGNORECASE)
                cm_match = re.search(r"([0-9]*\.?[0-9]+)\s*cm", value_text, re.IGNORECASE)
                if feet_match:
                    extracted["Height-ft"] = feet_match.group(1)
                if cm_match:
                    extracted["Height- cm"] = cm_match.group(1)
                continue

    return extracted


def extract_medications_allergies_history_immunizations(table):
    expected_variables = set(variables_to_extract["Medications/Allergies/History/Immunizations"])
    normalized_expected = {
        normalize_label(variable): variable for variable in expected_variables
    }
    extracted = {}

    for row in table[1:]:  # Skip title row
        if not row:
            continue

        for idx in range(0, len(row), 2):
            key = row[idx] if idx < len(row) else ""
            value = row[idx + 1] if idx + 1 < len(row) else ""
            key_text = (key or "").strip()
            value_text = (value or "").strip()

            if not key_text:
                continue

            canonical = normalized_expected.get(normalize_label(key_text))
            if canonical:
                extracted[canonical] = value_text

    return extracted


def extract_type_2_rows(table):
    records = []
    if len(table) < 2:
        return records

    headers = table[1]
    for row in table[2:]:  # Skip title row and header row
        if not row:
            continue
        record = {}
        for idx, cell in enumerate(row):
            if cell and idx < len(headers):
                record[headers[idx]] = cell
        if record:
            records.append(record)
    return records


def extract_narrative(table):
    return {"Narrative": table[1][0] if len(table) > 1 and table[1] else ""}
