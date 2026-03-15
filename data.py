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
            tables = page.extract_tables()
            print(tables)

structured_extraction('./pdfs/test.pdf')