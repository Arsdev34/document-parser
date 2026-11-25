# Document Parser

A local FastAPI service for extracting text, keywords, and summaries from documents. No external APIs, no rate limits, no subscription fees.

## Key Features

- **Multi-format support**: PDF, DOCX, XLSX, RTF, PPTX, CSV, TXT, MD.
- **No external dependencies**: All parsing is done locally with open-source libraries.
- **Structured output**: full text, character count, sentence count, top-10 keywords, 3-sentence summary.
- **Fast and simple**: one command to run; Swagger UI included.

## Supported Formats

| Format | Library | Notes |
|--------|---------|-------|
| .pdf   | pypdf | Text extraction from pages |
| .docx  | python-docx | Text + tables |
| .xlsx  | openpyxl | All sheets and cells |
| .rtf   | striprtf | Plain text conversion |
| .pptx  | python-pptx | Slide text + tables |
| .csv, .txt, .md | built-in | UTF-8 decoding |
## Quick Start

1. Install dependencies:

   pip install -r requirements.txt

2. Run the server:

   python -m uvicorn main:app --reload

   Service: http://127.0.0.1:8000  |  Swagger docs: http://127.0.0.1:8000/docs

3. Test with curl:

   curl -X POST "http://127.0.0.1:8000/analyze/" -F "file=@test.pdf"

## API

POST /analyze/ — multipart/form-data, field: file.

Example response:

  {
    "filename": "report.pdf",
    "format": ".pdf",
    "characters_extracted": 4321,
    "sentences_count": 37,
    "keywords": ["revenue", "growth", "market"],
    "summary": ["Revenue grew by 18% YoY.", "Q3 margin forecast: +12%.", "Key driver: digital transformation."],
    "full_text": "Full extracted text goes here..."
  }

## Why This Project

- Ready to deploy: minimal setup, documented API.
- No cloud costs: no third-party API keys or quotas.
- Extensible: easy to add formats or integrate into pipelines.

## Requirements

- Python 3.9+
- Windows / Linux / macOS

## License

MIT License - free to use, modify, and sell.
