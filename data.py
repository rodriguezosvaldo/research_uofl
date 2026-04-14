import pdfplumber
import re
from parsers import table_to_dict
from parsers.variables import variables_to_extract




def structured_extraction(pdf_path):
    incident_number = ''
    incident_date = ''
    all_tables = []
    with pdfplumber.open(pdf_path) as pdf:
        # Extract the incident number and date from the first page
        page = pdf.pages[0]
        cropped = page.crop((0, 0, page.width, 80))
        text = cropped.extract_text()
        match_incident_number = re.search(r'Incident #:\s*(\S+)', text)
        if match_incident_number:
            incident_number = match_incident_number.group()
        else:
            incident_number = 'Incident:Unknown'
        # Extract the incident date
        match_incident_date = re.search(r'Date:\s*(\S+)', text)
        if match_incident_date:
            incident_date = match_incident_date.group()
        else:
            incident_date = 'Date:Unknown'

        # Extract Information from Tables   
        for page in pdf.pages:
            all_tables.extend(page.extract_tables())
        
    return incident_number, incident_date, all_tables
            
def tables_dict_format(all_tables):
    # Returns the dictionary 'tables_dict_format' with the following structure:
    # tables_dict_format: {section_name: dictionary_of_that_section}
    # (e.g. {"Patient Information": {last: value, first: value, ...}, 
    #        "Medications/Allergies/History/Immunizations": {medications: value, allergies: value, ...}, etc.) 
    incident_dict = {}
    sections = {}
    duplicates = {}
    tables_type_2_titles = {
        "Vital Signs",
        "Vitals Calculations",
        "Flow Chart",
        "Specialty Patient - Advanced Airway",
        "Specialty Patient - Spinal Immobilization",
        "ECG",
    }
    known_titles = {
        "Patient Information",
        "Clinical Impression",
        "Medications/Allergies/History/Immunizations",
        "Specialty Patient - CPR",
        "Incident Details",
        "Destination Details",
        "Incident Times",
        "Insurance Details",
        "Mileage",
        "Delays",
        "Additional",
        "Specialty Patient - Motor Vehicle Collision",
        "Specialty Patient - Trauma Criteria",
        "Specialty Patient - CDC 2011 Trauma Criteria",
        "Transfer Details",
        "Patient Transport Details",
        "Patient Refusal",
        "Vital Signs",
        "Vitals Calculations",
        "Flow Chart",
        "Specialty Patient - Advanced Airway",
        "Specialty Patient - Spinal Immobilization",
        "ECG",
        "Assessments",
        "Narrative",
        "Consumables",
    }
    normalized_known_titles = {
        re.sub(r"[^a-z0-9]", "", title.lower()): title for title in known_titles
    }

    def _register(t_name, tbl):
        if t_name in sections:
            duplicates.setdefault(t_name, []).append(tbl)
        else:
            sections[t_name] = tbl

    def _find_embedded_type2_titles(table):
        """
        Some PDFs render a type-2 section title inside the body of a larger table
        (and may split that title across adjacent cells). Detect those rows by
        normalizing and concatenating the full row text.
        """
        matches = []
        for row_idx, row in enumerate(table):
            if not row:
                continue
            normalized_row = re.sub(
                r"[^a-z0-9]",
                "",
                "".join(str(cell or "") for cell in row).lower(),
            )
            if not normalized_row:
                continue

            for normalized_title, canonical_title in normalized_known_titles.items():
                if canonical_title not in tables_type_2_titles:
                    continue
                if normalized_title == normalized_row:
                    matches.append((row_idx, canonical_title))
                    break
        return matches

    # When a co-located title row lands on the bottom of a page, pdfplumber
    # splits the table in two: a title-only table on page N and a data-only
    # table (no title row) on page N+1. We carry the section_starts forward
    # so the data table can be associated with the correct sections.
    pending_co_located_section_starts = None

    # Maps a distinctive normalized column header to the table name for
    # type-2 tables whose title is rendered outside the table by some PDFs.
    headerless_signatures = {
        "treatment": "Flow Chart",
        "avpu": "Vital Signs",
        "gcse1m": "Vitals Calculations",  # normalize_label("GCS(E+V+M)/Qualifiers")
        "rhythm": "ECG",
        "airway": "Specialty Patient - Advanced Airway",
        "immobilizationrecommended": "Specialty Patient - Spinal Immobilization",
    }

    for table in all_tables:
        if not table:
            continue
        embedded_type2_titles = _find_embedded_type2_titles(table)
        for title_row_idx, embedded_title in embedded_type2_titles:
            if title_row_idx == 0 or title_row_idx + 1 >= len(table):
                continue

            virtual_table = [[embedded_title]]
            virtual_table.extend(table[title_row_idx + 1 :])
            _register(embedded_title, virtual_table)

        first_row = table[0]
        if not first_row:
            continue

        # Find all known section titles in the title row and their column positions.
        section_starts = [
            (idx, cell)
            for idx, cell in enumerate(first_row)
            if cell in known_titles
        ]

        if not section_starts:
            # Try headerless type-2 table detection (title rendered outside table).
            first_row_normalized = {
                re.sub(r"[^a-z0-9]", "", str(cell or "").lower())
                for cell in first_row
            }
            detected_title = next(
                (title for sig, title in headerless_signatures.items()
                 if sig in first_row_normalized),
                None,
            )
            if detected_title:
                _register(detected_title, [[detected_title]] + table)
                pending_co_located_section_starts = None
                continue

            # Try co-located page-break continuation: the previous table had
            # only the title row; this table has the data rows without a title.
            if pending_co_located_section_starts is not None:
                for i, (start_col, title) in enumerate(pending_co_located_section_starts):
                    end_col = (
                        pending_co_located_section_starts[i + 1][0]
                        if i + 1 < len(pending_co_located_section_starts)
                        else None
                    )
                    virtual_table = [[title]]
                    for row in table:  # include ALL rows — there is no title row to skip
                        if row:
                            virtual_table.append(list(row[start_col:end_col]))
                        else:
                            virtual_table.append(row)
                    _register(title, virtual_table)

            pending_co_located_section_starts = None
            continue

        # Determine whether this table actually contains data rows.
        # If not, the data is on the next page (page-break split); save the
        # context so the continuation table can be associated correctly.
        #
        # For type-2 single-section tables (Flow Chart, Vital Signs, ECG…)
        # row[1] is the column header, not data — so we check from row[2].
        # For co-located tables row[1] is already data, so we check from row[1].
        is_single_type_2 = (
            len(section_starts) == 1
            and section_starts[0][1] in tables_type_2_titles
        )
        data_check_start = 2 if is_single_type_2 else 1

        has_any_data = any(
            any(cell for cell in (row or []))
            for row in table[data_check_start:]
        )

        if not has_any_data and (len(section_starts) > 1 or is_single_type_2):
            pending_co_located_section_starts = section_starts
            if is_single_type_2:
                # Register the title+header table now so the parser has the
                # column headers; data rows will be merged from the next table.
                _register(section_starts[0][1], table)
            continue  # wait for the data continuation table
        else:
            pending_co_located_section_starts = None

        for i, (start_col, title) in enumerate(section_starts):
            end_col = section_starts[i + 1][0] if i + 1 < len(section_starts) else None

            if len(section_starts) == 1:
                # Single section: use the original table as-is to avoid any copying overhead.
                virtual_table = table
            else:
                # Co-located sections: build a virtual table containing only this
                # section's columns so parsers never see data from adjacent sections.
                virtual_table = [[title]]
                for row in table[1:]:
                    if row:
                        virtual_table.append(list(row[start_col:end_col]))
                    else:
                        virtual_table.append(row)

            _register(title, virtual_table)
        
    if duplicates:
        for duplicate_title, continuation_tables in duplicates.items():
            base_table = sections[duplicate_title]
            base_header = base_table[1] if len(base_table) > 1 else None

            for table in continuation_tables:
                if not table:
                    continue

                start_idx = 1  # Skip repeated title row by default
                if (
                    duplicate_title in tables_type_2_titles
                    and len(table) > 1
                    and base_header is not None
                    and table[1] == base_header
                ):
                    start_idx = 2  # Also skip repeated header row for table type 2

                base_table.extend(table[start_idx:]) 
    
    
    incident_dict = {}
    for table_name, table in sections.items():
        incident_dict[table_name] = table_to_dict(table_name, table)

    _fallback_empty_sections(incident_dict, all_tables)
    return incident_dict


def _fallback_empty_sections(incident_dict, all_tables):
    """
    For any key-value section that ended up empty after normal extraction,
    locate the pdfplumber table where the highest proportion of that
    section's expected variables appear as keys and extract from there.

    Requiring a supermajority match (MATCH_THRESHOLD) prevents false
    positives from sections that share a few variable names — e.g.
    Patient Information shares 'Address', 'City', 'State', 'Zip',
    'Country' with Incident Details (~25 %), but the real Incident
    Details table will match 70 %+ of its variables.
    """
    def _normalize(text):
        return re.sub(r"[^a-z0-9]", "", str(text or "").lower())

    # Minimum fraction of expected variables that must be present in a
    # pdfplumber table for it to be considered the correct source.
    MATCH_THRESHOLD = 0.35

    for section_name, section_data in incident_dict.items():
        if not isinstance(section_data, dict) or section_data:
            continue

        expected_variables = variables_to_extract.get(section_name, [])
        if not expected_variables:
            continue

        normalized_expected = {_normalize(v): v for v in expected_variables}

        # Score every pdfplumber table by how many of the section's expected
        # variable names appear as cell keys inside it.
        best_table = None
        best_score = 0.0

        for table in all_tables:
            if not table:
                continue

            table_keys = set()
            for row in table:
                if not row:
                    continue
                for idx in range(0, len(row), 2):
                    key_text = str(row[idx] or "").strip()
                    if key_text:
                        table_keys.add(_normalize(key_text))

            matches = sum(1 for nk in normalized_expected if nk in table_keys)
            score = matches / len(expected_variables)

            if score > best_score:
                best_score = score
                best_table = table

        if best_table is None or best_score < MATCH_THRESHOLD:
            continue

        # Extract key-value pairs from the best-matching table.
        # First occurrence of each variable wins (to avoid overwriting a
        # correct earlier value with an empty later one).
        recovered = {}
        for row in best_table:
            if not row:
                continue
            for idx in range(0, len(row) - 1, 2):
                key_text = str(row[idx] or "").strip()
                value_text = " ".join(str(row[idx + 1] or "").split())
                if not key_text:
                    continue
                nk = _normalize(key_text)
                canonical = normalized_expected.get(nk)
                if canonical and canonical not in recovered:
                    recovered[canonical] = value_text

        if recovered:
            incident_dict[section_name] = recovered


