import re

from ..variables import variables_to_extract
from .common import normalize_label


def _clean_cell(value):
    return re.sub(r"\s+", " ", str(value or "")).strip()


def parse(table):
    if len(table) < 2:
        return []

    headers = table[1] or []
    wanted_columns = ["Time"] + variables_to_extract["Flow Chart"]

    # Keep provider if present in PDF header, even if not listed in variables_to_extract.
    if any(normalize_label(header) == "provider" for header in headers):
        wanted_columns.append("Provider")

    normalized_to_original = {normalize_label(column): column for column in wanted_columns}

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

        # Reject page-header rows injected by pdfplumber at page breaks;
        # valid Flow Chart rows always have a HH:MM time in the Time column.
        time_value = record.get("Time", "")
        if has_any_value and re.match(r"^\d{2}:\d{2}$", time_value):
            records.append(record)

    return records
