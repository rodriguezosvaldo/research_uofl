import pdfplumber
import re
from parsers import table_to_dict




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
    # sections will have the following structure:
    # {section_name: table_of_that_section} 
    # (e.g. {"Patient Information": [['Patient Information', None, None, ...]], 
    #       "Medications/Allergies/History/Immunizations": [['Medications/Allergies/History/Immunizations', None, None, ...]], etc.)
    for table in all_tables:
        if not table:
            continue
        first_row = table[0]
        title = first_row[0] if first_row else None
        if title in (
            "Patient Information",
            "Medications/Allergies/History/Immunizations",
            "Specialty Patient - CPR",
            "Incident Details",
            "Insurance Details",
            "Mileage",
            "Specialty Patient - Motor Vehicle Collision",
            "Specialty Patient - Trauma Criteria",
            "Specialty Patient - CDC 2011 Trauma Criteria",
            "Transfer Details",
            "Patient Transport Details",
            "Patient Refusal",
            # Tables type 2:
            "Vital Signs",
            "Vitals Calculations",
            "Flow Chart",
            "Specialty Patient - Advanced Airway",
            "Specialty Patient - Spinal Immobilization",
            "ECG",
            # Tables type 3:
            "Assessments",
            # Tables type 4:
            "Narrative",
            # Tables type 5:
            "Consumables",
        ):
            if title in sections:
                duplicates.setdefault(title, []).append(table)
            else:
                sections[title] = table 
        
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
    return incident_dict

incident_number, incident_date, all_tables = structured_extraction('./pdfs/test.pdf')
tables_dict_format(all_tables)

