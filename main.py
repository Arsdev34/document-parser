import os
import io
import re
import csv
from collections import Counter
from fastapi import FastAPI, UploadFile, File, HTTPException
from pypdf import PdfReader

app = FastAPI(
    title="Document Parser (PDF/DOCX/XLSX/RTF/PPTX/CSV/TXT/MD)",
    description="Extracts FULL text from documents + keywords + frequency summary. No external APIs."
)

STOPWORDS = {
    "the", "a", "an", "is", "are", "was", "were", "of", "to", "and", "in",
    "on", "for", "with", "that", "this", "it", "as", "at", "by", "from",
    "be", "or", "we", "you", "i", "not", "but", "have", "has", "can",
}

def extract_pdf(data: bytes) -> str:
    reader = PdfReader(io.BytesIO(data))
    text = ""
    for page in reader.pages:
        extracted = page.extract_text()
        if extracted:
            text += extracted + "\n"
    return text.strip()

def extract_docx(data: bytes) -> str:
    from docx import Document
    doc = Document(io.BytesIO(data))
    parts = [p.text for p in doc.paragraphs if p.text.strip()]
    for table in doc.tables:
        for row in table.rows:
            parts.append(" | ".join(cell.text.strip() for cell in row.cells))
    return "\n".join(parts).strip()

def extract_xlsx(data: bytes) -> str:
    from openpyxl import load_workbook
    wb = load_workbook(io.BytesIO(data), read_only=True, data_only=True)
    lines = []
    for sheet in wb.sheetnames:
        ws = wb[sheet]
        lines.append(f"[Sheet: {sheet}]")
        for row in ws.iter_rows(values_only=True):
            cells = [str(c) for c in row if c is not None]
            if cells:
                lines.append(" | ".join(cells))
    return "\n".join(lines).strip()

def extract_rtf(data: bytes) -> str:
    from striprtf.striprtf import rtf_to_text
    text = data.decode("utf-8", errors="replace")
    return rtf_to_text(text).strip()

def extract_pptx(data: bytes) -> str:
    from pptx import Presentation
    prs = Presentation(io.BytesIO(data))
    lines = []
    for i, slide in enumerate(prs.slides, start=1):
        lines.append(f"[Slide {i}]")
        for shape in slide.shapes:
            if shape.has_text_frame:
                for para in shape.text_frame.paragraphs:
                    t = "".join(run.text for run in para.runs).strip()
                    if t:
                        lines.append(t)
            if shape.has_table:
                for row in shape.table.rows:
                    cells = [cell.text.strip() for cell in row.cells]
                    if any(cells):
                        lines.append(" | ".join(cells))
    return "\n".join(lines).strip()

def extract_csv(data: bytes) -> str:
    text = data.decode("utf-8", errors="replace")
    lines = []
    for row in csv.reader(io.StringIO(text)):
        if any(c.strip() for c in row):
            lines.append(" | ".join(c.strip() for c in row))
    return "\n".join(lines).strip()

def extract_txt(data: bytes) -> str:
    return data.decode("utf-8", errors="replace").strip()

EXTRACTORS = {
    ".pdf": extract_pdf,
    ".docx": extract_docx,
    ".xlsx": extract_xlsx,
    ".rtf": extract_rtf,
    ".pptx": extract_pptx,
    ".csv": extract_csv,
    ".txt": extract_txt,
    ".md": extract_txt,
}

def split_sentences(text: str) -> list:
    parts = re.split(r"(?<=[.!?])\s+", text)
    return [s.strip() for s in parts if 20 < len(s.strip()) < 400]

def frequency_summary(text: str, max_sentences: int = 3) -> list:
    words = re.findall(r"[а-яёa-zA-Z]{3,}", text.lower())
    words = [w for w in words if w not in STOPWORDS]
    if not words:
        return []
    freq = Counter(words)
    max_freq = max(freq.values())
    sentences = split_sentences(text)
    scored = []
    for i, sent in enumerate(sentences):
        s_words = [w for w in re.findall(r"[а-яёa-zA-Z]{3,}", sent.lower()) if w not in STOPWORDS]
        if not s_words:
            continue
        score = sum(freq[w] / max_freq for w in s_words) / len(s_words)
        scored.append((i, score, sent))
    scored.sort(key=lambda x: x[1], reverse=True)
    top = sorted(scored[:max_sentences], key=lambda x: x[0])
    return [s for _, _, s in top]

@app.post("/analyze/")
async def analyze_document(file: UploadFile = File(...)):
    ext = os.path.splitext(file.filename.lower())[1]
    if ext not in EXTRACTORS:
        raise HTTPException(status_code=400, detail=f"Format {ext} not supported. Use: {', '.join(EXTRACTORS)}")
    try:
        data = await file.read()
        full_text = EXTRACTORS[ext](data)
        if not full_text:
            raise HTTPException(status_code=400, detail="Could not extract text from file.")
        summary = frequency_summary(full_text)
        keywords = [w for w, _ in Counter(
            [w for w in re.findall(r"[а-яёa-zA-Z]{3,}", full_text.lower()) if w not in STOPWORDS]
        ).most_common(10)]
        return {
            "filename": file.filename,
            "format": ext,
            "characters_extracted": len(full_text),
            "sentences_count": len(split_sentences(full_text)),
            "keywords": keywords,
            "summary": summary if summary else full_text[:500],
            "full_text": full_text
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
