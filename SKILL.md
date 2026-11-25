# SKILL: Document Parser

Local service for extracting text from documents. No external APIs.

## Purpose
Accepts a file, extracts its text and returns:
full text, character count, sentence count,
top-10 keywords, and a brief summary (3 most informative sentences).

## Supported formats
- .pdf  — via pypdf
- .docx — via python-docx (paragraph text + tables)
- .xlsx — via openpyxl (all sheets, all cells)
- .rtf  — via striprtf
- .pptx — via python-pptx (text of all slides, [Slide N] markup)
- .csv, .txt, .md — plain text with UTF-8 decoding

## Running
1. Install dependencies: pip install -r requirements.txt
2. Start the server: python -m uvicorn main:app --reload
3. Service: http://127.0.0.1:8000 — Swagger docs: http://127.0.0.1:8000/docs

## API
POST /analyze/ — multipart/form-data, field: file.

## Response format (JSON)
- filename — uploaded file name
- format — file extension
- characters_extracted — number of extracted characters
- sentences_count — number of sentences
- keywords — top-10 keywords (list)
- summary — brief overview (3 sentences)
- full_text — full extracted text

## Requirements
- Python 3.9+
- Windows / Linux / macOS
