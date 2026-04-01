# EMS Data Extraction — UofL Research Project

A pipeline to extract structured data from EMS incident reports PDFs, store it as CSV and JSON, and consolidate everything into a single Excel file for analysis.

---

## Tools & Dependencies

| Tool | Purpose |
|---|---|
| Python 3.10+ | Runtime (3.11 or 3.12 recommended) |
| [pdfplumber](https://github.com/jsvine/pdfplumber) | PDF text and table extraction |
| [openpyxl](https://openpyxl.readthedocs.io) | Writing and styling `.xlsx` files |

Install all dependencies with:

Recommended to use a virtual environment to install the dependencies.
```bash
python -m venv .venv
.venv\Scripts\activate      # Windows
# source .venv/bin/activate  # macOS / Linux
pip install -r requirements.txt
```

---

## Project Structure

```
data_extraction/
├── pdfs/                    # Input PDFs (place your files here)
├── output/
│   ├── JSON/                # Intermediate structured JSON (one file per PDF)
│   ├── raw_csv/             # Raw CSV output (one file per PDF)
│   └── output.xlsx          # Final consolidated Excel file
├── parsers/                 # Parsing logic split by section/table type
├── testing/
│   └── web/
│       ├── index.html       # Manual testing form UI
│       └── web_lookup.js    # Fetch logic for the local lookup server
├── README.md                # Project documentation
├── main.py                  # Interactive menu — the single entry point
├── save_JSON_format.py      # Converts PDFs → structured JSON files
├── save_raw_csv.py          # Converts PDFs → raw CSV files
├── dataframe.py             # Converts JSON files → consolidated Excel file
├── data.py                  # Orchestrates PDF parsing (calls parsers/)
├── class_def.py             # Incident data class definition
└── requirements.txt
```

---

## Files Overview

### `save_JSON_format.py`
Reads every PDF in `pdfs/`, extracts incident data through the structured parsers in `parsers/`, and writes one `.json` file per PDF to `output/JSON/`. Each JSON contains the incident number, date, and all parsed tables (Patient Information, Vital Signs, Flow Chart, CPR, etc.).

### `save_raw_csv.py`
Reads every PDF in `pdfs/` and dumps all detected table cells into a plain `.csv` file (one per PDF) in `output/raw_csv/`. No semantic structure is applied — this is useful for quick inspection or debugging raw extraction.

### `dataframe.py`
Reads all JSON files from `output/JSON/`, flattens each incident into a single row using `WORD_TO_DATA_MAP` (a mapping from column names to JSON locations), and exports the result to `output/output.xlsx`. The Excel file has a styled header row and auto-sized columns. It also computes derived fields such as first vascular access type, total epinephrine administrations, and final airway device from the Flow Chart data.

> **Note:** `dataframe.py` requires JSON files to already exist. Run `save_JSON_format.py` first.

---

## Running the Project

Everything can be run from a single interactive menu:

```bash
python main.py
```

The menu offers the following options:

```
  1. Create JSON files        →  runs save_JSON_format.py
  2. Create Excel file        →  runs dataframe.py
  3. Create CSV files         →  runs save_raw_csv.py
  5. Open manual testing form →  serves a local web UI for inspecting extracted values
  6. Exit
```

### Recommended workflow

1. Copy your PDF files into the `pdfs/` folder.
2. Run `python main.py` and select **option 1** to generate the JSON files.
3. Select **option 2** to produce the final `output/output.xlsx`.

### Alternative (raw CSV)

Select **option 3** to get unstructured CSV files — one per PDF — in `output/raw_csv/`.

---

## Manual Testing Form

Option 5 in the menu shows the instructions to open the manual testing form.

---

## Notes

- All scripts resolve paths relative to the project root, so they can be run from any working directory.
- If `dataframe.py` finds no JSON files it will print a reminder to run `save_JSON_format.py` first.
- The `parsers/` folder contains one module per table section (e.g. `vital_signs.py`, `specialty_patient_cpr.py`). Each module implements the extraction logic for its section.
