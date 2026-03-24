from ..variables import variables_to_extract
from .common import normalize_label


def parse(table):
    expected = set(variables_to_extract["Insurance Details"])
    normalized_expected = {normalize_label(v): v for v in expected}

    # PDF labels that differ from variables_to_extract
    alias_map = {
        "insuredsname": "Insured Name",
        "insuredname": "Insured Name",
        "insuredssn": "Insured SSN",
        "insureddob": "Insured DOB",
    }

    extracted = {}
    secondary_section = False

    def map_key(key_text):
        nonlocal secondary_section
        nk = normalize_label(key_text)

        if nk == normalize_label("Secondary Ins"):
            secondary_section = True

        if nk == normalize_label("Policy #"):
            return (
                "Secondary Insurance Policy #"
                if secondary_section
                else "Primary Insurance Policy #"
            )
        if nk in (normalize_label("Group #"), normalize_label("Group#")):
            return (
                "Secondary Insurance Group #"
                if secondary_section
                else "Primary Insurance Group #"
            )

        if nk in alias_map:
            return alias_map[nk]
        return normalized_expected.get(nk)

    for row in table[1:]:  # Skip title row
        if not row:
            continue

        for idx in range(0, len(row), 2):
            key = row[idx] if idx < len(row) else ""
            value = row[idx + 1] if idx + 1 < len(row) else ""
            key_text = str(key or "").strip()
            value_text = " ".join(str(value or "").split())

            if not key_text:
                continue

            canonical = map_key(key_text)
            if canonical and canonical in expected:
                extracted[canonical] = value_text

    return extracted
