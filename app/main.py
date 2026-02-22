from datetime import date, datetime, time
from pathlib import Path
import sys

from fastapi import Depends, FastAPI, HTTPException, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import func
from sqlalchemy.orm import Session

from .database import Base, SessionLocal, engine
from .models import CallRecord
from .schemas import CallProcessUpdate, CallRecordOut, InboundCallCreate
from .services import summarize_transcript

Base.metadata.create_all(bind=engine)

BASE_DIR = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parents[1]))

app = FastAPI(title="CS Voice Intake Dashboard")
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/api/calls/inbound", response_model=CallRecordOut)
def create_inbound_call(payload: InboundCallCreate, db: Session = Depends(get_db)):
    summary = summarize_transcript(payload.transcript_text)
    row = CallRecord(
        caller_number=payload.caller_number,
        ivr_choice=payload.ivr_choice,
        recording_url=payload.recording_url,
        transcript_text=payload.transcript_text,
        summary_text=summary,
        processing_status="unprocessed",
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@app.get("/api/calls", response_model=list[CallRecordOut])
def list_calls(status: str | None = None, db: Session = Depends(get_db)):
    query = db.query(CallRecord).order_by(CallRecord.inbound_at.desc())
    if status:
        query = query.filter(CallRecord.processing_status == status)
    return query.all()


@app.get("/api/calls/{call_id}", response_model=CallRecordOut)
def get_call(call_id: int, db: Session = Depends(get_db)):
    row = db.get(CallRecord, call_id)
    if not row:
        raise HTTPException(status_code=404, detail="Call record not found")
    return row


@app.patch("/api/calls/{call_id}", response_model=CallRecordOut)
def update_call(call_id: int, payload: CallProcessUpdate, db: Session = Depends(get_db)):
    row = db.get(CallRecord, call_id)
    if not row:
        raise HTTPException(status_code=404, detail="Call record not found")

    if payload.processing_status == "done" and not payload.response_note.strip():
        raise HTTPException(status_code=400, detail="response_note is required when marking done")

    row.processing_status = payload.processing_status
    row.response_channel = payload.response_channel
    row.response_note = payload.response_note
    row.action_note = payload.action_note
    row.resolver_name = payload.resolver_name
    row.follow_up_required = payload.follow_up_required
    row.follow_up_due_at = payload.follow_up_due_at
    row.resolved_at = datetime.utcnow() if payload.processing_status == "done" else None

    db.commit()
    db.refresh(row)
    return row


@app.get("/api/dashboard/daily")
def daily_dashboard(
    target_date: date = Query(default_factory=date.today),
    db: Session = Depends(get_db),
):
    start = datetime.combine(target_date, time.min)
    end = datetime.combine(target_date, time.max)

    total = (
        db.query(func.count(CallRecord.id))
        .filter(CallRecord.inbound_at >= start, CallRecord.inbound_at <= end)
        .scalar()
    )
    processed = (
        db.query(func.count(CallRecord.id))
        .filter(
            CallRecord.inbound_at >= start,
            CallRecord.inbound_at <= end,
            CallRecord.processing_status == "done",
        )
        .scalar()
    )
    in_progress = (
        db.query(func.count(CallRecord.id))
        .filter(
            CallRecord.inbound_at >= start,
            CallRecord.inbound_at <= end,
            CallRecord.processing_status == "in_progress",
        )
        .scalar()
    )
    unprocessed = total - processed

    return {
        "date": str(target_date),
        "inbound_count": total,
        "processed_count": processed,
        "in_progress_count": in_progress,
        "unprocessed_count": unprocessed,
        "processed_rate": round((processed / total) * 100, 1) if total else 0.0,
    }
