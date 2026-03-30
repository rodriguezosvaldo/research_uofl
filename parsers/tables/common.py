import re

from ..variables import variables_to_extract


def normalize_label(text):
    return re.sub(r"[^a-z0-9]", "", str(text or "").lower())


_TIME_FIELDS_TO_NORMALIZE = {
    "Onset Time",
    "Last Known Well",
    "Time 1st CPR",
    "Time of First Defib",
    "ROSC Time",
    "Resuscitation Discontinued",
    "Time",
    "Extrication Time",
    "PSAP Call",
    "Dispatch Notified",
    "Call Received",
    "Dispatched",
    "En Route",
    "Staged",
    "Resp on Scene",
    "On Scene",
    "At Patient",
    "Care Transferred",
    "Depart Scene",
    "At Destination",
    "Pt. Transferred",
    "Call Closed",
    "In District",
    "At Landing Area",
}

_TIME_RE = re.compile(r"\b(\d{1,2}):(\d{2})(?::(\d{2}))?\s*([AaPp][Mm])?\b")


def normalize_time_to_hms(value_text):
    """
    Extract time and return HH:MM:SS.
    Keeps original text if no time pattern is found.
    """
    text = " ".join(str(value_text or "").split())
    if not text:
        return ""

    match = _TIME_RE.search(text)
    if not match:
        return text

    hour = int(match.group(1))
    minute = int(match.group(2))
    second = int(match.group(3) or "0")
    am_pm = (match.group(4) or "").lower()

    if am_pm == "pm" and hour < 12:
        hour += 12
    elif am_pm == "am" and hour == 12:
        hour = 0

    return f"{hour:02d}:{minute:02d}:{second:02d}"


def _extract_weight_lbs(value_text):
    """
    Normalize weight to pounds only.
    Examples:
      "110.0 lbs - 49.9 kg" -> "110.0"
      "110 lbs"             -> "110"
      "110.0"               -> "110.0"
    """
    text = str(value_text or "").strip()
    if not text:
        return ""

    lbs_part = text.split(" - ", 1)[0].strip()
    match = re.search(r"\d+(?:\.\d+)?", lbs_part)
    return match.group(0) if match else lbs_part


def extract_type_1_by_variables(table, variable_names):
    extracted = {}
    for row in table[1:]:  # Skip title row
        if not row:
            continue
        for variable in variable_names:
            for idx, cell in enumerate(row):
                if re.search(variable, str(cell or "")):
                    value = row[idx + 1] if idx + 1 < len(row) else ""
                    value_text = (value or "").strip()
                    if variable in _TIME_FIELDS_TO_NORMALIZE:
                        value_text = normalize_time_to_hms(value_text)
                    extracted[variable] = value_text
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

            # Some fields (e.g. SSN) span the full row width in the PDF, causing
            # pdfplumber to place their value at idx+2 instead of idx+1.
            # If value is empty, check if the next "key" slot holds the value.
            if canonical in expected_variables and not value_text and idx + 2 < len(row):
                candidate = str(row[idx + 2] or "").strip()
                candidate_normalized = normalize_label(candidate)
                if candidate_normalized not in normalized_expected and candidate_normalized not in alias_map:
                    value_text = candidate

            if canonical in expected_variables:
                if canonical == "Weight":
                    value_text = _extract_weight_lbs(value_text)
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
