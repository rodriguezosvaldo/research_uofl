import re

CHECKMARK_TOKENS = {"x", "X", "✓", "✔"}


def _clean_cell(value):
    text = re.sub(r"\s+", " ", str(value or "")).strip()
    return text


def _is_header_row(row):
    first = _clean_cell(row[0]) if len(row) > 0 else ""
    second = _clean_cell(row[1]) if len(row) > 1 else ""
    third = _clean_cell(row[2]) if len(row) > 2 else ""
    return (
        first.lower() == "category"
        and second.lower() == "comments"
        and third.lower() == "subcategory"
    )


def _parse_assessment_time(row):
    for cell in row:
        text = _clean_cell(cell)
        match = re.search(r"Assessment Time:\s*(.+)$", text, flags=re.IGNORECASE)
        if match:
            return match.group(1).strip()
    return None


def _extract_detail(row):
    detail_parts = []
    for cell in row[3:]:
        text = _clean_cell(cell)
        if not text or text in CHECKMARK_TOKENS:
            continue
        detail_parts.append(text)

    detail = " ".join(detail_parts).strip()
    if not detail and len(row) > 1:
        detail = _clean_cell(row[1])  # Comments column fallback
    return detail


def _normalize_detail(label, detail):
    text = detail.replace(" • ", "; ").replace("•", ";").strip(" ;")
    if label:
        prefix = f"{label}:"
        if text.lower().startswith(prefix.lower()):
            text = text[len(prefix):].strip(" ;")
    return text


def _unique_keep_order(values):
    seen = set()
    output = []
    for value in values:
        if value and value not in seen:
            seen.add(value)
            output.append(value)
    return output


def _build_category_text(category, rows):
    has_subcategories = any(subcategory for subcategory, _ in rows)
    multi_row = len(rows) > 1
    has_distinct_subcategory = any(
        subcategory and subcategory != category for subcategory, _ in rows
    )
    bullet_mode = has_subcategories and (multi_row or has_distinct_subcategory)

    if bullet_mode:
        subcategory_map = {}
        for subcategory, detail in rows:
            label = subcategory or category
            normalized_detail = _normalize_detail(label, detail)
            subcategory_map.setdefault(label, []).append(normalized_detail)

        lines = []
        for label, details in subcategory_map.items():
            normalized_details = _unique_keep_order(details)
            if normalized_details:
                lines.append(f"- {label}: {'; '.join(normalized_details)}")
            else:
                lines.append(f"- {label}:")
        return "\n".join(lines)
    else:
        details = []
        for _, detail in rows:
            normalized_detail = _normalize_detail(category, detail)
            if normalized_detail:
                details.append(normalized_detail)
        normalized_details = _unique_keep_order(details)
        return "; ".join(normalized_details)


def parse(table):
    # Collect category rows grouped by assessment time, preserving insertion order.
    # Multiple table sections with the same timestamp are merged under one key.
    assessment_map = {}
    assessment_order = []
    current_time = None
    current_category = ""

    for row in table[1:]:  # Skip title row
        if not row:
            continue

        assessment_time = _parse_assessment_time(row)
        if assessment_time is not None:
            if assessment_time not in assessment_map:
                assessment_map[assessment_time] = {}
                assessment_order.append(assessment_time)
            current_time = assessment_time
            current_category = ""
            continue

        if _is_header_row(row):
            continue

        if current_time is None:
            current_time = "Unknown"
            if current_time not in assessment_map:
                assessment_map[current_time] = {}
                assessment_order.append(current_time)

        category_cell = _clean_cell(row[0]) if len(row) > 0 else ""
        if category_cell:
            current_category = category_cell
        if not current_category:
            continue

        subcategory = _clean_cell(row[2]) if len(row) > 2 else ""
        detail = _extract_detail(row)

        category_rows = assessment_map[current_time].setdefault(current_category, [])
        category_rows.append((subcategory, detail))

    result = {}
    for time in assessment_order:
        key = f"Assessment time: {time}"
        result[key] = {
            category: _build_category_text(category, rows)
            for category, rows in assessment_map[time].items()
        }

    return result
