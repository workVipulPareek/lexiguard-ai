import os
import shutil
from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from graph.workflow import run_workflow
from rag.pdf_loader import extract_text_from_pdf

router = APIRouter()

UPLOAD_DIR = "data"
os.makedirs(UPLOAD_DIR, exist_ok=True)


class QueryRequest(BaseModel):
    question: str
    filename: str


@router.post("/upload")
async def upload_contract(file: UploadFile = File(...)):
    filename = file.filename

    if filename.endswith(".txt"):
        save_path = os.path.join(UPLOAD_DIR, filename)
        with open(save_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        saved_name = filename

    elif filename.endswith(".pdf"):
        raw_bytes = await file.read()
        text = extract_text_from_pdf(raw_bytes)

        if not text.strip():
            raise HTTPException(
                status_code=422,
                detail="PDF text extraction returned empty. File may be scanned/image-based."
            )

        saved_name = filename.replace(".pdf", ".txt")
        save_path = os.path.join(UPLOAD_DIR, saved_name)
        with open(save_path, "w", encoding="utf-8") as f:
            f.write(text)

    else:
        raise HTTPException(
            status_code=400,
            detail="Only .txt and .pdf files are supported."
        )

    return {
        "message": "File uploaded successfully.",
        "filename": saved_name,
        "original": filename
    }


@router.post("/query")
async def query_contract(request: QueryRequest):
    file_path = os.path.join(UPLOAD_DIR, request.filename)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Contract file not found.")

    result = run_workflow(
        question=request.question,
        file_path=file_path
    )

    return result