import os
import io
from fastapi import FastAPI, UploadFile, File, HTTPException
from pypdf import PdfReader
from openai import OpenAI

app = FastAPI(
    title="AI Document Analyzer",
    description="Extracts text from PDFs and uses LLM to analyze scientific claims."
)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY", "your-api-key-here"))

def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    reader = PdfReader(io.BytesIO(pdf_bytes))
    text = ""
    for page in reader.pages:
        extracted = page.extract_text()
        if extracted:
            text += extracted + "\n"
    return text.strip()

@app.post("/analyze/")
async def analyze_document(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
    try:
        pdf_bytes = await file.read()
        extracted_text = extract_text_from_pdf(pdf_bytes)
        if not extracted_text:
            raise HTTPException(status_code=400, detail="Could not extract text from PDF.")
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that summarizes scientific documents."},
                {"role": "user", "content": f"Summarize this document:\n\n{extracted_text[:3000]}"}
            ],
            max_tokens=300
        )
        summary = response.choices[0].message.content
        return {
            "filename": file.filename,
            "characters_extracted": len(extracted_text),
            "summary": summary
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
