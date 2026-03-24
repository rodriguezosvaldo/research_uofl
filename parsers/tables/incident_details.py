from ..variables import variables_to_extract
from .common import normalize_label


def parse(table):
    expected_variables = set(variables_to_extract["Incident Details"])
    normalized_expected = {
        normalize_label(variable): variable for variable in expected_variables
    }
    extracted = {}

    for row in table[1:]:  # Skip title row
        if not row:
            continue

        # Incident Details table usually contains 3 side-by-side key/value sections.
        for idx in range(0, len(row), 2):
            key = row[idx] if idx < len(row) else ""
            value = row[idx + 1] if idx + 1 < len(row) else ""
            key_text = str(key or "").strip()
            value_text = " ".join(str(value or "").split())

            if not key_text:
                continue

            canonical = normalized_expected.get(normalize_label(key_text))
            if canonical:
                extracted[canonical] = value_text

    return extracted
