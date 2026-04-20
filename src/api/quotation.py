# src/api/quotation.py

import os
from fastapi import APIRouter, Response, HTTPException

BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../")
)

QUOTATION_DIR = os.path.join(BASE_DIR, "public", "quotations")

def load_pdf_from_disk(qid: str) -> bytes:
    file_path = os.path.join(QUOTATION_DIR, f"quotation_{qid}.pdf")

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Quotation not found: {qid}")

    with open(file_path, "rb") as f:
        return f.read()

router = APIRouter(prefix="/thcm-agentic-poc/api", tags=["Quotation"])

@router.get("/quotation/{qid}.pdf")
def get_quotation(qid: str):
    try:
        pdf_bytes = load_pdf_from_disk(qid)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Quotation not found")

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'inline; filename="quotation_{qid}.pdf"'
        },
    )