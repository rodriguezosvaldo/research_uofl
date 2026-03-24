from ..variables import variables_to_extract
from .common import normalize_label


def parse(table):
    expected = set(variables_to_extract["Patient Transport Details"])
    normalized_expected = {normalize_label(v): v for v in expected}
    extracted = {}

    for row in table[1:]:  # Skip title row
        if not row:
            continue

        # Layout: label, value, label, value (four columns per row)
        for idx in range(0, len(row) - 1, 2):
            key_text = str(row[idx] or "").strip()
            value_text = " ".join(str(row[idx + 1] or "").split())

            if not key_text:
                continue

            canonical = normalized_expected.get(normalize_label(key_text))
            if canonical:
                extracted[canonical] = value_text

    return extracted
