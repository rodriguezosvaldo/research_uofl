import pdfplumber
import pandas as pd
import re
from classDef import Incident


# Extract all data from the PDF and save it to a CSV file (raw data, no formatting)
def extract_all_to_csv(pdf_path, output_path='./pdfs/raw_csv/{filename}.csv'):
    values = []
    
    with pdfplumber.open(pdf_path) as pdf:
        # Extract the incident number from the first page
        page = pdf.pages[0]
        cropped = page.crop((0, 0, page.width, 80))
        text = cropped.extract_text()
        match_incident_number = re.search(r'Incident #:\s*(\S+)', text)
        if match_incident_number:
            incident_number = match_incident_number.group()
        else:
            incident_number = 'Incident:Unknown'

        # Extract the information before the first table
        header = '\n'.join(page.extract_text().split('\n')[0:3])
        values.append(header + '\n')
        
        # Extract tables data from the rest of the pages
        for page in pdf.pages:
            tables = page.extract_tables()
            for table in tables:
                for row in table:
                    row_cells = []
                    for cell in row:
                        if cell: 
                            row_cells.append(str(cell).strip())
                        else:
                            row_cells.append('')
                    values.append(','.join(row_cells)) 
    
    csv_text = '\n'.join(values)
    filename = incident_number.replace(':', '_').replace('#', '_')
    complete_path = output_path.format(filename=filename)
    
    with open(complete_path, 'w', encoding='utf-8') as csv:
        csv.write(csv_text)

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

    sections = {} 
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
            "Vital Signs",
            "Vitals Calculations",
            "Flow Chart",
            "Assessments",
            "Narrative",
            "Specialty Patient - Advanced Airway",
            "Specialty Patient - CPR",
            "Incident Details",
            "Insurance Details",
            "Mileage",
        ):
            sections[title] = table

    tables_dict_format = {}
    for table_name, table in sections.items():
        tables_dict_format[table_name] = table_to_dict(table_name, table)
    return tables_dict_format

def table_to_dict(table_name, table):
    #Converts a table into a dictionary
    #Type 1 tables example: converts from "Patient Information": [['Patient Information', None, None, ...]] to "Patient Information": {last: value, first: value, ...}
    #Type 2 tables example: converts from "Vital Signs": [['Time', 'AVPU', 'Side', ...]] to "Vital Signs": 0: {time: value, avpu: value, side: value, ...}, 1: {time: value, avpu: value, side: value, ...}, etc.
    #Type 3 tables example: converts from "Assessments": [['Time', 'Category', 'Category Comments', 'Subcategory', 'Subcategory Comments', 'Subcategory Comments Status']] to "Assessments": 0: {time: value, category: value, category_comments: value, subcategory: value, subcategory_comments: value, subcategory_comments_status: value}, 1: {time: value, category: value, category_comments: value, subcategory: value, subcategory_comments: value, subcategory_comments_status: value}, etc.
    kv = {}
    tables_type_1 = [
        "Patient Information", 
        "Medications/Allergies/History/Immunizations", 
        "Narrative", 
        "Specialty Patient - CPR", 
        "Incident Details",
        "Insurance Details",
        "Mileage",
    ]
    tables_type_2 = [
        "Vital Signs",
        "Vitals Calculations",
        "Flow Chart",
        "Specialty Patient - Advanced Airway",
    ]
    tables_type_3 = [
        "Assessments",
    ]

    # skip the title row (e.g. 'Patient Information')
    if table_name in tables_type_1:
        for row in table[1:]:
            if not row:
                continue
            for i in range(0, len(row), 2):
                key = (row[i] or "").strip()
                if not key:
                    continue
                val = (row[i+1] or "").strip() if i + 1 < len(row) else ""
                kv[key] = val
    elif table_name in tables_type_2:
        headers = table[1]                    # ['Time', 'AVPU', ...]
        records = {}
        for idx, row in enumerate(table[2:]):    # skip the header row
            if not row:
                continue
            # match headers with values
            record_dict = dict(zip(headers, row))
            records[f"record{idx}"] = record_dict
        
    elif table_name in tables_type_3:
        headers = table[0]                    # ['Time', 'Category', ...]
        records = {}
        for idx, row in enumerate(table[1:]):    # skip the header row
            if not row:
                continue
            # match headers with values
            record_dict = dict(zip(headers, row))
            records[f"record{idx}"] = record_dict
    return kv






# Table variables: (DEFINIR LUEGO SI MOVERLO A UN ARCHIVO EXTERNO) DEBUGGIN IN PROCESS==================
# patient_information_clinical_impression_variables = {
#     "class_name": "patientInformationClinicalImpression",
#     "Last": "last",
#     "First": "first",
#     "Middle": "middle",
#     "Name Suffix": "name_suffix",
#     "Sex": "sex",
#     "Gender": "gender",
#     "DOB": "dob",
#     "Age": "age",
#     "Weight": "weight",
#     "Height": "height",
#     "Pedi Color": "pedi_color",
#     "SSN": "ssn",
#     "Advance Directives": "advance_directives",
#     "Resident Status": "resident_status",
#     "Patient Resides in Service Area": "patient_resides_in_service_area",
#     "Temporary Residence Type": "temporary_residence_type",
#     "Address": "address",
#     "Address 2": "address_2",
#     "City": "city",
#     "State": "state",
#     "Zip": "zip_code",
#     "Country": "country",
#     "Tel": "tel",
#     "Physician": "physician",
#     "Phys. Tel": "phys_tel",
#     "Ethnicity": "ethnicity",
#     "Race": "race",
#     # Clinical Impression
#     "Primary Impression": "primary_impression",
#     "Secondary Impression": "secondary_impression",
#     "Protocols Used": "protocols_used",
#     "Local Protocol Provided": "local_protocol_provided",
#     "Care Level": "care_level",
#     "Anatomic Position": "anatomic_position",
#     "Onset Time": "onset_time",
#     "Last Known Well": "last_known_well",
#     "Chief Complaint": "chief_complaint",
#     "Duration": "duration",
#     "Duration Units": "duration_units",
#     "Secondary Complaint": "secondary_complaint",
#     "Secondary Duration": "secondary_duration",
#     "Secondary Duration Units": "secondary_duration_units",
#     "Patient Level of Distress": "patient_level_of_distress",
#     "Signs Symptoms": "signs_symptoms",
#     "Injury": "injury",
#     "Additional Injury": "additional_injury",
#     "Mechanism of Injury": "mechanism_of_injury",
#     "Medical Trauma": "medical_trauma",
#     "Barriers of Care": "barriers_of_care",
#     "Alcohol Drugs": "alcohol_drugs",
#     "Pregnancy": "pregnancy",
#     "Initial Patient Acuity": "initial_patient_acuity",
#     "Final Patient Acuity": "final_patient_acuity",
#     "Patient Activity": "patient_activity",
# }

# medications_allergies_history_immunizations_variables = {
#     "class_name": "medicationsAllergiesHistoryImmunizations",
#     "Medications": "medications",
#     "Allergies": "allergies",
#     "History": "history",
#     "Immunizations": "immunizations",
#     "Last Oral Intake": "last_oral_intake",
# }

# narrative_variables = {
#     "class_name": "narrative",
#     "Narrative": "narrative",
# }

# specialty_patient_advanced_airway_variables = {
#     "class_name": "specialtyPatientAdvancedAirway",
#     "Airway": "airway",
#     "Indications": "indications",
#     "Monitoring Devices": "monitoring_devices",
#     "Rescue Devices": "rescue_devices",
#     "Reasons Failed Intubation": "reasons_failed_intubation",
# }

# specialty_patient_cpr_variables = {
#     "class_name": "specialtyPatientCPR",
#     "Cardiac Arrest": "cardiac_arrest",
#     "Cardiac Arrest Etiology": "cardiac_arrest_etiology",
#     "Estimated Time of Arrest": "estimated_time_of_arrest",
#     "Est Time Collapse to 911": "est_time_collapse_to_911",
#     "Est Time Collapse to CPR": "est_time_collapse_to_cpr",
#     "Arrest Witnessed By": "arrest_witnessed_by",
#     "CPR Initiated By": "cpr_initiated_by",
#     "Time 1st CPR": "time_1st_cpr",
#     "CPR Feedback": "cpr_feedback",
#     "ITD Used": "itd_used",
#     "Applied AED": "applied_aed",
#     "Applied By": "applied_by",
#     "Defibrillated": "defibrillated",
#     "CPR Type": "cpr_type",
#     "Prearrival CPR Instructions": "prearrival_cpr_instructions",
#     "First Defibrillated By": "first_defibrillated_by",
#     "Time of First Defib": "time_of_first_defib",
#     "Initial ECG Rhythm": "initial_ecg_rhythm",
#     "Rhythm at Destination": "rhythm_at_destination",
#     "Hypothermia": "hypothermia",
#     "End of Event": "end_of_event",
#     "ROSC": "rosc",
#     "ROSC Time": "rosc_time",
#     "ROSC Occurred": "rosc_occurred",
#     "Resuscitation Discontinued": "resuscitation_discontinued",
#     "Discontinued Reason": "discontinued_reason",
#     "Resuscitation": "resuscitation",
#     "In Field Pronouncement Expired": "in_field_pronouncement_expired",
#     "In Field Pronouncement Time": "in_field_pronouncement_time",
#     "In Field Pronouncement Date": "in_field_pronouncement_date",
#     "In Field Pronouncement Physician": "in_field_pronouncement_physician",
# }

# incident_details_destination_details_incident_times_variables = {
#     "class_name": "incidentDetailsDestinationDetailsIncidentTimes",
#     # Incident Details
#     "Location Type": "location_type",
#     "Location": "location",
#     "Address": "address",
#     "Address 2": "address_2",
#     "Mile Marker": "mile_marker",
#     "City": "city",
#     "County": "county",
#     "State": "state",
#     "Zip": "zip",
#     "Country": "country",
#     "Medic Unit": "medic_unit",
#     "Medic Vehicle": "medic_vehicle",
#     "Run Type": "run_type",
#     "Response Mode": "response_mode",
#     "Response Mode Descriptors": "response_mode_descriptors",
#     "Shift": "shift",
#     "Zone": "zone",
#     "Level of Service": "level_of_service",
#     "EMD Complaint": "emd_complaint",
#     "EMD Card Number": "emd_card_number",
#     "Dispatch Priority": "dispatch_priority",
#     # Destination Details
#     "Disposition": "disposition",
#     "Unit Disposition": "unit_disposition",
#     "Patient Evaluation Care Disposition": "patient_evaluation_care_disposition",
#     "Crew Disposition": "crew_disposition",
#     "Transport Disposition": "transport_disposition",
#     "Transport Mode": "transport_mode",
#     "Reason for Refusal or Release": "reason_for_refusal_or_release",
#     "Transport Mode Descriptors": "transport_mode_descriptors",
#     "Transport Due to": "transport_due_to",
#     "Transported To": "transported_to",
#     "Requested By": "requested_by",
#     "Transferred To": "transferred_to",
#     "Transferred Unit": "transferred_unit",
#     "Destination": "destination",
#     "Department": "department",
#     "Address": "address",
#     "Address 2": "address_2",
#     "City": "city",
#     "County": "county",
#     "State": "state",
#     "Zip": "zip",
#     "Country": "country",
#     "Zone": "zone",
#     "Condition at Destination": "condition_at_destination",
#     "State Wristband": "state_wristband",
#     "Destination Record": "destination_record",
#     "Trauma Registry ID": "trauma_registry_id",
#     "STEMI Registry ID": "stemi_registry_id",
#     "Stroke Registry ID": "stroke_registry_id",
#     # Incident Times
#     "PSAP Call": "psap_call",
#     "Dispatch Notified": "dispatch_notified",
#     "Call Received": "call_received",
#     "Dispatched": "dispatched",
#     "End Route": "end_route",
#     "Staged": "staged",
#     "Resp on Scene": "resp_on_scene",
#     "On Scene": "on_scene",
#     "At Patient": "at_patient",
#     "Care Transferred": "care_transferred",
#     "Depart Scene": "depart_scene",
#     "At Destination": "at_destination",
#     "PT Transferred": "pt_transferred",
#     "Call Closed": "call_closed",
#     "In District": "in_district",
#     "At Landing Area": "at_landing_area",
# }

# insurance_details_variables = {
#     "class_name": "insuranceDetails",
#     "Insured Name": "insured_name",
#     "Relationship": "relationship",
#     "Insured SSN": "insured_ssn",
#     "Insured DOB": "insured_dob",
#     "Address": "address",
#     "Address 2": "address_2",
#     "Address 3": "address_3",
#     "City": "city",
#     "State": "state",
#     "Zip": "zip",
#     "Country": "country",
#     "Primary Payer": "primary_payer",
#     "Medicare": "medicare",
#     "Medicaid": "medicaid",
#     "Primary Insurance": "primary_insurance",
#     "Policy Number": "policy_number",
#     "Primary Insurance Group Name": "primary_insurance_group_name",
#     "Group Number": "group_number",
#     "Secondary Ins": "secondary_ins",
#     "Secondary Policy Number": "secondary_policy_number",
#     "Secondary Insurance Group Name": "secondary_insurance_group_name",
#     "Group Number": "group_number",
#     "Dispatch Nature": "dispatch_nature",
#     "Response Urgency": "response_urgency",
#     "Job Related Injury": "job_related_injury",
#     "Employer": "employer",
#     "Contact": "contact",
#     "Phone": "phone",
#     "Mileage to Closest Hospital": "mileage_to_closest_hospital",
# }

# mileage_delays_additional_variables = {
#     "class_name": "mileageDelaysAdditional",
#     "Scene": "scene",
#     "Destination": "destination",
#     "Loaded Miles": "loaded_miles",
#     "Start": "start",
#     "End": "end",
#     "Total Miles": "total_miles",
#     # Delays
#     "Dispatch Delays": "dispatch_delays",
#     "Response Delays": "response_delays",
#     "Scene Delays": "scene_delays",
#     "Turn Around Delays": "turn_around_delays",
#     # Additional
#     "Additional Agencies": "additional_agencies",
# }
#==========================================================================================================
