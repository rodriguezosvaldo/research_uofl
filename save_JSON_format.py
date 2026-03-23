from data import structured_extraction, tables_dict_format
import json
from classDef import Incident

# TESTING:
# This script extracts selected tables from test.pdf and saves them to a JSON file in the JSON folder
# The goal is to see if the format of the JSON file fits the requirements of the project

incident_number, incident_date, all_tables = structured_extraction('./pdfs/test.pdf')
incident_structured_dict = tables_dict_format(all_tables)
incident = Incident(incident_number=incident_number, incident_date=incident_date)
for table_name, table_data in incident_structured_dict.items():
    incident.add_table(table_name, table_data)

for table_name, table_data in incident.tables.items():

    for table_name, table_data in table_data.items():
        print(table_name)
        for key, value in table_data.items():
            print(f"{key}: {value}")
        print("--------------------------------")
