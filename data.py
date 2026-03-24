import pdfplumber
import pandas as pd
import re
from classDef import Incident




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
                duplicates[title] = table
            else:
                sections[title] = table 
        
    if duplicates:
        for duplicate_title, table in duplicates.items():
            sections[duplicate_title].extend(table[1:]) 
    
    # Debugging:
    for table_name, table in sections.items():
        print(table_name)
        print(table)
        print("--------------------------------")
    
    incident_dict = {}
    for table_name, table in sections.items():
        incident_dict[table_name] = table_to_dict(table_name, table)
    return incident_dict

def table_to_dict(table_name, table):
    #Converts a table into a dictionary
    #Type 1 tables example: converts from "Patient Information": [['Patient Information', None, None, ...]] to "Patient Information": {last: value, first: value, ...}
    #Type 2 tables example: converts from "Vital Signs": [['Time', 'AVPU', 'Side', ...]] to "Vital Signs": 0: {time: value, avpu: value, side: value, ...}, 1: {time: value, avpu: value, side: value, ...}, etc.
    #Type 3 tables example: converts from "Assessments": [['Time', 'Category', 'Category Comments', 'Subcategory', 'Subcategory Comments', 'Subcategory Comments Status']] to "Assessments": 0: {time: value, category: value, category_comments: value, subcategory: value, subcategory_comments: value, subcategory_comments_status: value}, 1: {time: value, category: value, category_comments: value, subcategory: value, subcategory_comments: value, subcategory_comments_status: value}, etc.
    incident_dict = {}
    tables_type_1 = [
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
        "Patient Refusal"
    ]
    tables_type_2 = [
        "Vital Signs",
        "Vitals Calculations",
        "Flow Chart",
        "Specialty Patient - Advanced Airway",
        "Specialty Patient - Spinal Immobilization",
        "ECG",
    ]
    # tables_type_3 = [
    #     "Assessments",
    # ]
    tables_type_4 = [
        "Narrative",
    ]
    tables_type_5 = [
        "Consumables",
    ]

    
    if table_name in tables_type_1:
        incident_dict[table_name] = {}
        for row in table[1:]: # skip the title row (e.g. 'Patient Information')
            if not row:
                continue
            #THIS APPROACH ITERATES OVER THE ROWS JUMPING 2 COLUMNS AT A TIME, EXTRACTING THE KEY AND THE VALUE
            # for i in range(0, len(row), 2):
            #     key = (row[i] or "").strip()
            #     if not key:
            #         continue
            #     val = (row[i+1] or "").strip() if i + 1 < len(row) else ""
            #     kv[key] = val

            #THIS APPROACH USES REGULAR EXPRESSIONS TO MATCH THE KEY AND THE VALUE
            for variable in variables_to_extract[table_name]:
                for idx, cell in enumerate(row):
                    if re.search(variable, str(cell or "")):
                        value = row[idx + 1] 
                        incident_dict[table_name][variable] = value.strip()
                        break

    elif table_name in tables_type_2:
        incident_dict[table_name] = []
        headers = table[1]
        for row in table[2:]: # skip the title row (e.g. 'Vital Signs') and the headers row
            if not row:
                continue
            record = {}
            for idx, cell in enumerate(row):
                if cell:
                    record[headers[idx]] = cell if cell else "" 
            incident_dict[table_name].append(record)

    elif table_name in tables_type_4:
        incident_dict[table_name] = {}
        incident_dict[table_name]["Narrative"] = table[1][0] if table[1] else ""

    elif table_name in tables_type_5:
        incident_dict[table_name] = []
        for row in table[2:]:  # Saltar título y headers
            if not row:
                continue
            for i in range(0, len(row), 2):
                if i + 1 >= len(row):
                    break
                num = (i // 2) + 1  # 1, 2, 3, ...
                description = (row[i] or "").strip()
                qty = (row[i + 1] or "").strip()
                if description or qty:
                    incident_dict[table_name].append({
                        f"Description {num}": description,
                        f"Qty {num}": qty
                    })
    return incident_dict


variables_to_extract = {
    # Tables type 1 variables:
    "Patient Information": [
        "Last",
        "First",
        "Middle",
        "Name Suffix",
        "Sex",
        "Gender",
        "DOB",
        "Age",
        "Weight-lbs",
        "Weight-kg",
        "Height-ft",
        "Height- cm",
        "Pedi Color",
        "SSN",
        "Advance Directives",
        "Resident Status",
        "Patient Resides in Service Area",
        "Temporary Residence Type",
        "Address",
        "Address 2",
        "City",
        "State",
        "Zip",
        "Country",
        "Tel",
        "Physician",
        "Phys. Tel",
        "Ethnicity",
        "Race",
        # Clinical Impression
        "Primary Impression",
        "Secondary Impression",
        "Protocols Used",
        "Local Protocol Provided",
        "Care Level",
        "Anatomic Position",
        "Onset Time",
        "Last Known Well",
        "Chief Complaint",
        "Duration",
        "Duration Units",
        "Secondary Complaint",
        "Secondary Duration",
        "Secondary Duration Units",
        "Patient Level of Distress",
        "Signs Symptoms",
        "Injury",
        "Additional Injury",
        "Mechanism of Injury",
        "Medical Trauma",
        "Barriers of Care",
        "Alcohol Drugs",
        "Pregnancy",
        "Initial Patient Acuity",
        "Final Patient Acuity",
        "Patient Activity",
    ],
    "Medications/Allergies/History/Immunizations": [
        "Medications",
        "Allergies",
        "History",
        "Immunizations",
    ],
    "Specialty Patient - CPR": [
        "Cardiac Arrest",
        "Cardiac Arrest Etiology",
        "Estimated Time of Arrest",
        "Est Time Collapse to 911",
        "Est Time Collapse to CPR",
        "Arrest Witnessed By",
        "CPR Initiated By",
        "Time 1st CPR",
        "CPR Feedback",
        "ITD Used",
        "Applied AED",
        "Applied By",
        "Defibrillated",
        "CPR Type",
        "Prearrival CPR Instructions",
        "First Defibrillated By",
        "Time of First Defib",
        "Initial ECG Rhythm",
        "Rhythm at Destination",
        "Hypothermia",
        "End of Event",
        "ROSC",
        "ROSC Time",
        "ROSC Occurred",
        "Resuscitation Discontinued",
        "Discontinued Reason",
        "Resuscitation",
        "Expired",
        "Time", 
        "Date",
        "Physician",
    ],
    "Incident Details": [
        "Location Type",
        "Location",
        "Address",
        "Address 2",
        "Mile Marker",
        "City",
        "County",
        "State",
        "Zip",
        "Country",
        "Medic Unit",
        "Medic Vehicle",
        "Run Type",
        "Response Mode",
        "Response Mode Descriptors",
        "Shift",
        "Zone",
        "Level of Service",
        "EMD Complaint",
        "EMD Card Number",
        "Dispatch Priority",
        # Destination Details
        "Disposition",
        "Unit Disposition",
        "Patient Evaluation and/or Care Disposition",
        "Crew Disposition",
        "Transport Disposition",
        "Transport Mode",
        "Reason for Refusal or Release",
        "Transport Mode Descriptors",
        "Transport Due To",
        "Transported To",
        "Requested By",
        "Transferred To",
        "Transferred Unit",
        "Destination",
        "Department",
        "Address",
        "Address 2",
        "City",
        "County",
        "State",
        "Zip",
        "Country",
        "Zone",
        "Condition at Destination",
        "State Wristband",
        "Destination Record",
        "Trauma Registry ID",
        "STEMI Registry ID",
        "Stroke Registry ID",
        # Incident Times
        "PSAP Call",
        "Dispatch Notified",
        "Call Received",
        "Dispatched",
        "En Route",
        "Staged",
        "Resp on Scene",
        "On Scene",
        "At Patient",
        "Care Transferred",
        "Depart Scene",
        "At Destination",
        "Pt. Transferred",
        "Call Closed",
        "In District",
        "At Landing Area",
    ],
    "Insurance Details": [
        "Insured Name",
        "Relationship",
        "Insured SSN",
        "Insured DOB",
        "Address1",
        "Address2",
        "Address3",
        "City",
        "State",
        "Zip",
        "Country",
        "Primary Payer",
        "Medicare",
        "Medicaid",
        "Primary Insurance",
        "Primary Insurance Policy #",
        "Primary Insurance Group Name",
        "Primary Insurance Group #",
        "Secondary Ins",
        "Secondary Insurance Policy #",
        "Secondary Insurance Group Name",
        "Secondary Insurance Group #",
        "Dispatch Nature",
        "Response Urgency",
        "Job Related Injury",
        "Employer",
        "Contact",
        "Phone",
        "Mileage to Closest Hospital",
    ],
    "Mileage": [
        "Scene",
        "Destination",
        "Loaded Miles",
        "Start",
        "End",
        "Total Miles",
        # Delays
        "Dispatch Delays",
        "Response Delays",
        "Scene Delays",
        "Transport Delays",
        "Turn Around Delays",
        # Additional
        "Additional Agencies",
    ],
    "Specialty Patient - Motor Vehicle Collision": [
        "Patient Injured",
        "Vehicle Type",
        "Position In Vehicle",
        "Seat Row",
        "Number Of Vehicles",
        "Weather",
        "Extrication Required",
        "Estimated Speed",
        "Exterior Damage",
        "Law Enforcement Case #",
        "Collision Indicators",
        "Damage Location",
        "Airbag Deployment",
        "Safety Devices",
        "Extrication Comments",
        "Extrication Time",
    ],
    "Specialty Patient - Trauma Criteria": [
        "Anatomic",
        "Physiologic",
        "Mechanical",
        "Other Conditions",
        "Trauma Activation",
        "Time",
        "Date",
        "Trauma level",
        "Reason Not Activated",
    ],
    "Specialty Patient - CDC 2011 Trauma Criteria": [
        "Vital Signs",
        "Anatomy of Injury",
        "Mechanism of Injury",
        "Special Considerations",
        "Trauma Activation",
        "Time",
        "Date",
        "level",
        "Reason Not Activated",
    ],
    "Transfer Details": [
        "PAN",
        "Prior Authorization Code Payer",
        "PCS",
        "Interfacility Transfer or Medical Transport Reason",
        "ABN",
        "CMS Service Level",
        "ICD-9 Code",
        "Transport Assessment",
        "Specialty Care Transport Provider",
        "Transfer Reason",
        "Justification for Transfer",
        "Other/Services",
        "Medical Necessity",
        "Sending Physician",
        "Sending Record #",
        "Receiving Physician",
        "Condition Code",
        "Condition Code Modifiers",
    ],
    "Patient Transport Details": [
        "How was Patient Moved To Stretcher",
        "How was Patient Moved From Ambulance",
        "Condition of Patient at Destination",
        "How was Patient Moved To Ambulance",
        "Patient Position During Transport",
    ],
    "Patient Refusal": [
        "Signed By"
    ],

    # Tables type 2 variables:
    "Vital Signs": [
        "AVPU",
        "Side",
        "POS",
        "BP",
        "Pulse",
        "RR",
        "SPO2",
        "ETCO2",
        "CO",
        "BG",
        "Temp",
        "Pain",
    ],
    "Vitals Calculations": [
        "GCS Qualifiers",
        "RASS",
        "BARS",
        "RTS",
        "PTS",
        "MAP",
        "Shock Index",
    ],
    "Flow Chart": [
        "Time",
        "Treatment",
        "Description",
    ],
    "ECG": [
        "Time",
        "Type",
        "Rhythm",
        "Notes",
    ],
    "Specialty Patient - Advanced Airway": [
        "Airway",
        "Indications",
        "Monitoring Devices",
        "Rescue Devices",
        "Reasons Failed Intubation",
    ],
    "Specialty Patient - Spinal Immobilization": [
        "Immobilization Recommended?",
        "Altered Mental Status",
        "Evidence of Alcohol/Drug Impairment",
        "Distracting Injury",
        "Neurologic Deficit",
        "Spinal Pain/Tenderness",
    ],
    # Tables type 4 variables:
    "Narrative": [
        "Narrative",
    ],
    # Tables type 5 variables:
    "Consumables": [
        "Description",
        "Qty",
    ],
}


incident_number, incident_date, all_tables = structured_extraction('./pdfs/test.pdf')
tables_dict_format(all_tables)

