import os
import json
import uuid
import hashlib
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

from backend.app.db.session import get_db
from backend.app.db.models import ProcessedDocument, AuditLedger
from backend.app.ml.inference_engine import idp_engine
from backend.app.core.websocket_manager import ws_manager

router = APIRouter()

class DocumentProcessRequest(BaseModel):
    document_type: str = "HOSPITAL_CLINICAL_INTAKE"
    patient_or_client_name: str = "Dr. Jonathan Hayes"
    primary_diagnosis_or_purpose: str = "Acute Bronchitis"
    date_field: str = "2026-10-12"
    id_number: str = "MED-8842"
    total_amount: str = "$350.00"
    simulate_cursive_unclear: bool = False
    custom_features: Optional[Dict[str, float]] = None

def doc_to_dict(doc: ProcessedDocument) -> dict:
    return {
        "id": doc.id,
        "document_id": doc.doc_id,
        "doc_id": doc.doc_id,
        "document_type": doc.document_type,
        "patient_or_client_name": doc.patient_or_client_name,
        "extracted_patient_name": doc.patient_or_client_name,
        "primary_diagnosis_or_purpose": doc.primary_diagnosis_or_purpose,
        "extracted_diagnosis": doc.primary_diagnosis_or_purpose,
        "date_field": doc.date_field,
        "id_number": doc.id_number,
        "total_amount": doc.total_amount,
        "contrast_ratio": doc.contrast_ratio,
        "stroke_variance": doc.stroke_variance,
        "background_snr": doc.background_snr,
        "quality_score": doc.quality_score,
        "lexical_confidence": doc.lexical_confidence,
        "confidence": doc.lexical_confidence,
        "character_error_rate": doc.character_error_rate,
        "word_error_rate": doc.word_error_rate,
        "signature_verified": doc.signature_verified,
        "human_review_required": doc.human_review_required,
        "evidence_hash": doc.evidence_hash,
        "timestamp": doc.timestamp.isoformat() if doc.timestamp else ""
    }

def audit_to_dict(b: AuditLedger) -> dict:
    return {
        "block_index": b.block_index,
        "timestamp": b.timestamp,
        "event_type": b.event_type,
        "doc_id": b.doc_id,
        "evidence_hash": b.evidence_hash,
        "previous_hash": b.previous_hash,
        "block_hash": b.block_hash
    }

@router.get("/documents")
def get_documents(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    document_type: Optional[str] = None,
    review_required: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    query = db.query(ProcessedDocument)
    if document_type:
        query = query.filter(ProcessedDocument.document_type == document_type)
    if review_required is not None:
        query = query.filter(ProcessedDocument.human_review_required == review_required)

    total = query.count()
    docs = query.order_by(ProcessedDocument.id.desc()).offset(skip).limit(limit).all()
    return {
        "count": len(docs),
        "total": total,
        "documents": [doc_to_dict(d) for d in docs]
    }

@router.get("/records")
def get_ocr_records(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    """Frontend compatibility endpoint."""
    docs = db.query(ProcessedDocument).order_by(ProcessedDocument.id.desc()).offset(skip).limit(limit).all()
    return {
        "total": len(docs),
        "records": [doc_to_dict(d) for d in docs]
    }

@router.get("/presets")
def get_document_presets():
    return {
        "presets": [
            {
                "id": "hayes_intake",
                "label": "Dr. Jonathan Hayes — Hospital Clinical Intake (Clean SOTA)",
                "document_type": "HOSPITAL_CLINICAL_INTAKE",
                "patient_or_client_name": "Dr. Jonathan Hayes",
                "primary_diagnosis_or_purpose": "Acute Bronchitis",
                "date_field": "2026-10-12",
                "id_number": "MED-8842",
                "total_amount": "$350.00",
                "simulate_cursive_unclear": False
            },
            {
                "id": "global_supplies_invoice",
                "label": "Global Supplies Ltd — Handwritten Commercial Invoice",
                "document_type": "BANK_KYC_LOAN_APPLICATION",
                "patient_or_client_name": "Global Supplies Ltd",
                "primary_diagnosis_or_purpose": "Working Capital Line $250k",
                "date_field": "2026-10-10",
                "id_number": "INV-1094",
                "total_amount": "$1,450.00",
                "simulate_cursive_unclear": False
            },
            {
                "id": "pendelton_claim",
                "label": "Arthur Pendelton — Insurance Claim Reimbursement",
                "document_type": "INSURANCE_CLAIM_REIMBURSEMENT",
                "patient_or_client_name": "Arthur Pendelton",
                "primary_diagnosis_or_purpose": "Emergency ER Consultation",
                "date_field": "2026-10-15",
                "id_number": "CLM-4491",
                "total_amount": "$2,850.00",
                "simulate_cursive_unclear": False
            },
            {
                "id": "anonymous_survey",
                "label": "Anonymous Respondent #42 — Survey Sheet (Degraded Cursive)",
                "document_type": "LEGAL_AFFIDAVIT_ATTESTATION",
                "patient_or_client_name": "Anonymous Respondent #42",
                "primary_diagnosis_or_purpose": "Property Title Attestation",
                "date_field": "2026-10-08",
                "id_number": "SURV-77",
                "total_amount": "N/A",
                "simulate_cursive_unclear": True
            }
        ]
    }

@router.post("/process")
async def process_document(req: DocumentProcessRequest, db: Session = Depends(get_db)):
    res = idp_engine.process_form(
        document_type=req.document_type,
        patient_or_client_name=req.patient_or_client_name,
        primary_diagnosis_or_purpose=req.primary_diagnosis_or_purpose,
        date_field=req.date_field,
        id_number=req.id_number,
        total_amount=req.total_amount,
        simulate_cursive_unclear=req.simulate_cursive_unclear,
        custom_features=req.custom_features
    )

    doc_id = f"DOC-2026-{uuid.uuid4().hex[:6].upper()}"

    doc = ProcessedDocument(
        doc_id=doc_id,
        document_type=res["document_type"],
        patient_or_client_name=res["patient_or_client_name"],
        primary_diagnosis_or_purpose=res["primary_diagnosis_or_purpose"],
        date_field=res["date_field"],
        id_number=res["id_number"],
        total_amount=res["total_amount"],
        contrast_ratio=res["contrast_ratio"],
        stroke_variance=res["stroke_variance"],
        background_snr=res["background_snr"],
        quality_score=res["quality_score"],
        lexical_confidence=res["lexical_confidence"],
        character_error_rate=res["character_error_rate"],
        word_error_rate=res["word_error_rate"],
        signature_verified=res["signature_verified"],
        human_review_required=res["human_review_required"],
        evidence_hash=res["evidence_hash"],
        extracted_json_payload=json.dumps(res),
        timestamp=datetime.now(timezone.utc)
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    # Cryptographic block append
    last_block = db.query(AuditLedger).order_by(AuditLedger.block_index.desc()).first()
    prev_hash = last_block.block_hash if last_block else "0000000000000000000000000000000000000000000000000000000000000000"
    b_idx = (last_block.block_index + 1) if last_block else 0
    b_ts = datetime.now(timezone.utc).isoformat()
    ev_type = "HUMAN_REVIEW_FLAGGED" if res["human_review_required"] else "DOCUMENT_OCR_TRANSCRIBED"
    raw_payload = f"{b_idx}|{b_ts}|{ev_type}|{doc_id}|{res['evidence_hash']}|{prev_hash}"
    b_hash = hashlib.sha256(raw_payload.encode()).hexdigest()

    new_block = AuditLedger(
        block_index=b_idx,
        timestamp=b_ts,
        event_type=ev_type,
        doc_id=doc_id,
        evidence_hash=res["evidence_hash"],
        previous_hash=prev_hash,
        block_hash=b_hash
    )
    db.add(new_block)
    db.commit()
    db.refresh(new_block)

    res["block_index"] = b_idx
    res["block_hash"] = b_hash
    res["document_id"] = doc_id

    try:
        await ws_manager.broadcast({"event": "DOCUMENT_PROCESSED", "data": res})
    except Exception:
        pass

    return {
        "document": doc_to_dict(doc),
        "metrics": res,
        "audit_block": audit_to_dict(new_block)
    }

@router.post("/extract")
async def extract_document_compat(req: DocumentProcessRequest, db: Session = Depends(get_db)):
    """Frontend compatibility endpoint."""
    return await process_document(req, db)

@router.get("/audit-logs")
def get_audit_logs(limit: int = 50, db: Session = Depends(get_db)):
    blocks = db.query(AuditLedger).order_by(AuditLedger.block_index.desc()).limit(limit).all()
    # Check chain integrity
    all_blocks = db.query(AuditLedger).order_by(AuditLedger.block_index.asc()).all()
    chain_valid = True
    for i in range(1, len(all_blocks)):
        if all_blocks[i].previous_hash != all_blocks[i-1].block_hash:
            chain_valid = False
            break

    return {
        "chain_valid": chain_valid,
        "total_blocks": len(all_blocks),
        "blocks": [audit_to_dict(b) for b in blocks]
    }
