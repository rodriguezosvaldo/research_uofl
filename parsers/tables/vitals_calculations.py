import re

from ..variables import variables_to_extract
from .common import normalize_label


def _clean_cell(value):
    return re.sub(r"\s+", " ", str(value or "")).strip()


def parse(table):
    if len(table) < 2:
        return []

    headers = table[1] or []
    wanted_columns = ["Time"] + variables_to_extract["Vitals Calculations"]

    normalized_to_original = {normalize_label(column): column for column in wanted_columns}
    # Handle visual header variants seen in PDFs.
    # Some PDFs render this header as "GCS Qualifiers" (or similar). Map those
    # variants back to the canonical JSON key we expect.
    normalized_to_original[normalize_label("GCS Qualifiers")] = "GCS(E+V+M)/Qualifiers"
    normalized_to_original[normalize_label("GCS Qualifier")] = "GCS(E+V+M)/Qualifiers"
    normalized_to_original[normalize_label("GCS")] = "GCS(E+V+M)/Qualifiers"

    index_map = {}
    for idx, header in enumerate(headers):
        canonical = normalized_to_original.get(normalize_label(header))
        if canonical:
            index_map[canonical] = idx

    records = []
    for row in table[2:]:  # Skip title and headers
        if not row:
            continue

        record = {}
        has_any_value = False
        for column in wanted_columns:
            idx = index_map.get(column)
            value = _clean_cell(row[idx]) if idx is not None and idx < len(row) else ""
            record[column] = value
            if value:
                has_any_value = True

        if has_any_value:
            records.append(record)

    return records
