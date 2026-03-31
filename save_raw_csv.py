import glob
import os
import pdfplumber
import re


def extract_all_to_csv(pdf_path, output_folder='./output/raw_csv'):
    values = []

    with pdfplumber.open(pdf_path) as pdf:
        page = pdf.pages[0]
        cropped = page.crop((0, 0, page.width, 80))
        text = cropped.extract_text()
        match_incident_number = re.search(r'Incident #:\s*(\S+)', text)
        if match_incident_number:
            incident_number = match_incident_number.group()
        else:
            incident_number = 'Incident:Unknown'

        header = '\n'.join(page.extract_text().split('\n')[0:3])
        values.append(header + '\n')

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
    output_path = os.path.join(output_folder, f'{filename}.csv')

    with open(output_path, 'w', encoding='utf-8') as csv_file:
        csv_file.write(csv_text)


def process_all_pdfs(pdf_folder='./pdfs', output_folder='./output/raw_csv'):
    pdf_files = sorted(glob.glob(os.path.join(pdf_folder, '*.pdf')))

    if not pdf_files:
        print(f"No PDF files found in: {pdf_folder}")
        return

    os.makedirs(output_folder, exist_ok=True)

    for i, pdf_path in enumerate(pdf_files, start=1):
        try:
            extract_all_to_csv(pdf_path, output_folder)
            print(f"PDF #{i} procesado: {os.path.basename(pdf_path)}")
        except Exception as exc:
            print(f"PDF #{i} - ERROR en {os.path.basename(pdf_path)}: {exc}")

    print("\nTodos los PDFs han sido procesados.")


if __name__ == "__main__":
    process_all_pdfs()