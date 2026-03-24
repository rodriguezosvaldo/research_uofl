from ..variables import variables_to_extract
from .common import normalize_label


def parse(table):
    expected = set(variables_to_extract["Transfer Details"])
    normalized_expected = {normalize_label(v): v for v in expected}

    # PDF may split one variable label across rows/cells
    label_alias = {
        normalize_label("Prior Authorization Code"): "Prior Authorization Code Payer",
        normalize_label("Payer"): "Prior Authorization Code Payer",
    }

    extracted = {}

    def set_field(canonical, value_text):
        if canonical not in expected:
            return
        cleaned = " ".join(value_text.split())
        if not cleaned:
            current = extracted.get(canonical, "")
            if not current:
                extracted[canonical] = ""
            return
        current = extracted.get(canonical, "")
        if not current:
            extracted[canonical] = cleaned
        elif cleaned != current and cleaned not in current:
            extracted[canonical] = f"{current}; {cleaned}"

    for row in table[1:]:  # Skip title row
        if not row:
            continue

        for idx in range(0, len(row) - 1, 2):
            key_text = str(row[idx] or "").strip()
            value_text = str(row[idx + 1] or "").strip()

            if not key_text:
                continue

            nk = normalize_label(key_text)
            canonical = label_alias.get(nk) or normalized_expected.get(nk)
            if canonical:
                set_field(canonical, value_text)

    return extracted
