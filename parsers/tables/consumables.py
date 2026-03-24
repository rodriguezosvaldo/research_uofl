import re


def _clean(value):
    return re.sub(r"\s+", " ", str(value or "")).strip()


def parse(table):
    """
    Type-2 style: many records. Each row may repeat Description/Qty pairs horizontally;
    multiple data rows stack more records.
    Each item is one dict with uniform keys for downstream use.
    """
    if len(table) < 2:
        return []

    records = []
    for row in table[2:]:  # Skip title row and header row
        if not row:
            continue

        for i in range(0, len(row) - 1, 2):
            description = _clean(row[i])
            qty = _clean(row[i + 1])
            if description or qty:
                records.append({"Description": description, "Qty": qty})

    return records
