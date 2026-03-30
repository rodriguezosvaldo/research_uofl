from ..variables import variables_to_extract
from .common import normalize_label, normalize_time_to_hms


def parse(table):
    expected_variables = set(variables_to_extract["Clinical Impression"])
    alias_map = {
        # PDF uses apostrophe; variable does not
        "patientslevelofdistress": "Patient Level of Distress",
    }
    normalized_expected = {normalize_label(v): v for v in expected_variables}
    extracted = {}
    last_duration_field = None

    for row in table[1:]:  # Skip title row
        if not row:
            continue

        for idx in range(0, len(row), 2):
            key = row[idx] if idx < len(row) else ""
            value = row[idx + 1] if idx + 1 < len(row) else ""
            key_text = (key or "").strip()
            value_text = " ".join(str(value or "").split())

            if not key_text:
                continue

            normalized_key = normalize_label(key_text)

            # "Units" label maps to Duration Units or Secondary Duration Units
            if normalized_key == "units":
                if last_duration_field == "Duration":
                    extracted["Duration Units"] = value_text
                elif last_duration_field == "Secondary Duration":
                    extracted["Secondary Duration Units"] = value_text
                continue

            canonical = alias_map.get(normalized_key) or normalized_expected.get(normalized_key)

            if canonical is None:
                continue

            # "Duration" appears twice in the PDF; first → Duration, second → Secondary Duration
            if canonical == "Duration" and "Duration" in extracted:
                canonical = "Secondary Duration"

            if canonical in expected_variables:
                if canonical in {"Onset Time", "Last Known Well"}:
                    value_text = normalize_time_to_hms(value_text)
                extracted[canonical] = value_text
                if canonical in {"Duration", "Secondary Duration"}:
                    last_duration_field = canonical

    return extracted
