# PDF Processing Pipeline (OCR + Extracted Text)

This project processes PDFs using two different flows depending on the PDF type:

- Scanned PDFs (images) are converted to images and passed through OCR.
- Selectable PDFs (text layer) are parsed directly without OCR.

## Python Dependencies

Add these to `requirements.txt`:

```
pdf2image>=1.17.0
pytesseract>=0.3.10
opencv-python>=4.8.0
pdfplumber>=0.10.3
Pillow>=10.0.0
```

Install them with:

```
pip install -r requirements.txt
```

## System Dependencies (Required)

These are not installed via `pip` and must be installed separately.

### Tesseract OCR

- **Linux**: `sudo apt install tesseract-ocr`
- **macOS**: `brew install tesseract`
- **Windows**: install the Tesseract binaries and add the install folder to `PATH`

### Poppler

Poppler is required by `pdf2image` for PDF to image conversion.

- **Linux**: `sudo apt install poppler-utils`
- **macOS**: `brew install poppler`
- **Windows**: install Poppler binaries and add the `bin` folder to `PATH`

## PDF Processing Flow

### 1) Scanned PDF (image-based)

**Flow**:

1. `pdf2image` converts each page to an image.
2. `OpenCV` preprocesses each image (e.g., grayscale, thresholding).
3. `pytesseract` runs OCR to extract text.

**Result**: text extracted from scanned pages.

### 2) Selectable PDF (text-based)

**Flow**:

1. `pdfplumber` opens the PDF and extracts text directly.
2. (Optional) use bounding boxes or tables from `pdfplumber` if needed.

**Result**: structured text extraction without OCR.

## Decision Logic

At runtime, choose the flow based on the PDF type:

- If the PDF has a text layer → use `pdfplumber`.
- If the PDF is image-only → use `pdf2image + OpenCV + pytesseract`.
