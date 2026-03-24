from ..variables import variables_to_extract
from .common import normalize_label


def parse(table):
    expected = set(variables_to_extract["Mileage"])
    normalized_expected = {normalize_label(v): v for v in expected}
    extracted = {}

    for row in table[1:]:  # Skip title row (e.g. "Mileage")
        if not row:
            continue

        for idx in range(0, len(row) - 1, 2):
            key_text = str(row[idx] or "").strip()
            value_text = " ".join(str(row[idx + 1] or "").split())

            if not key_text:
                continue

            nk = normalize_label(key_text)
            vn = normalize_label(value_text)
            if nk == normalize_label("Category") and vn == normalize_label("Delays"):
                continue

            canonical = normalized_expected.get(nk)
            if canonical:
                extracted[canonical] = value_text

    return extracted
