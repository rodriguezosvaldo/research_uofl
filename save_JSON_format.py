from data import structured_extraction, tables_dict_format
from class_def import Incident
import json
import os
import glob

PDF_DIR = './pdfs'
OUTPUT_DIR = './output'
JSON_DIR = os.path.join(OUTPUT_DIR, 'JSON')

os.makedirs(JSON_DIR, exist_ok=True)

pdf_files = sorted(glob.glob(os.path.join(PDF_DIR, '*.pdf')))
total = len(pdf_files)

for i, pdf_path in enumerate(pdf_files, start=1):
    incident_number, incident_date, all_tables = structured_extraction(pdf_path)
    incident_structured_dict = tables_dict_format(all_tables)

    incident = Incident(incident_number=incident_number, incident_date=incident_date)
    for table_name, table_data in incident_structured_dict.items():
        incident.add_table(table_name, table_data)

    pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]
    output_path = os.path.join(JSON_DIR, f'{pdf_name}.json')

    payload = {
        'incident_number': incident.incident_number,
        'incident_date': incident.incident_date,
        'tables': incident.tables,
    }

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)

    print(f'Done {i}/{total}')
