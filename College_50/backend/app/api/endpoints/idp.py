from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
import uuid
import json
from backend.app.db.session import get_db
from backend.app.db.models import ProcessedDocument
from backend.app.ml.inference_engine import idp_engine
from backend.app.core.websocket_manager import ws_manager

router = APIRouter()

class DocumentProcessRequest(BaseModel):
    document_type: str = "MEDICAL_INTAKE_FORM"
    simulate_cursive_unclear: bool = False

@router.get("/documents")
def get_documents(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    docs = db.query(ProcessedDocument).order_by(ProcessedDocument.timestamp.desc()).offset(skip).limit(limit).all()
    return {"count": len(docs), "documents": docs}

@router.post("/process")
async def process_document(req: DocumentProcessRequest, db: Session = Depends(get_db)):
    res = idp_engine.process_form(req.document_type, req.simulate_cursive_unclear)

    doc = ProcessedDocument(
        doc_id=f"DOC-2026-{uuid.uuid4().hex[:6].upper()}",
        document_type=req.document_type,
        patient_or_client_name=res["patient_or_client_name"],
        date_field=res["date_field"],
        id_number=res["id_number"],
        total_amount=res["total_amount"],
        signature_verified=res["signature_verified"],
        mean_confidence=res["mean_confidence"],
        human_review_required=res["human_review_required"],
        extracted_json_payload=json.dumps(res)
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    await ws_manager.broadcast({"event": "DOCUMENT_PROCESSED", "data": res})
    return {"document": doc, "metrics": res}
