from data import structured_extraction, tables_dict_format
import json
from classDef import Incident

# TESTING:
# This script extracts selected tables from test.pdf and saves them to a JSON file in the JSON folder
# The goal is to see if the format of the JSON file fits the requirements of the project

incident_number, incident_date, all_tables = structured_extraction('./pdfs/test.pdf')
incident_structured_dict = tables_dict_format(all_tables)
incident = Incident(incident_number=incident_number, incident_date=incident_date)
incident.add_table("Patient Information", incident_structured_dict["Patient Information"])
incident.add_table("Medications/Allergies/History/Immunizations", incident_structured_dict["Medications/Allergies/History/Immunizations"])
incident.add_table("Specialty Patient - CPR", incident_structured_dict["Specialty Patient - CPR"])
incident.add_table("Incident Details", incident_structured_dict["Incident Details"])
incident.add_table("Insurance Details", incident_structured_dict["Insurance Details"])
incident.add_table("Mileage", incident_structured_dict["Mileage"])

tables_type_1_json = {
    "Patient Information": incident.tables["Patient Information"],
    "Medications/Allergies/History/Immunizations": incident.tables["Medications/Allergies/History/Immunizations"],
    "Specialty Patient - CPR": incident.tables["Specialty Patient - CPR"],
    "Incident Details": incident.tables["Incident Details"],
    "Insurance Details": incident.tables["Insurance Details"],
    "Mileage": incident.tables["Mileage"],
}

with open("JSON/tables_type_1.json", "w", encoding="utf-8") as f:
    json.dump(tables_type_1_json, f, ensure_ascii=False, indent=2)