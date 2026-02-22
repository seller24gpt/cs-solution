from datetime import datetime

from pydantic import BaseModel, Field


class InboundCallCreate(BaseModel):
    caller_number: str = Field(..., examples=["01012341234"])
    ivr_choice: str = Field(default="1", pattern="^[12]$")
    recording_url: str = ""
    transcript_text: str = ""


class CallProcessUpdate(BaseModel):
    processing_status: str = Field(..., pattern="^(unprocessed|in_progress|done|reopened)$")
    response_channel: str = ""
    response_note: str = ""
    action_note: str = ""
    resolver_name: str = ""
    follow_up_required: bool = False
    follow_up_due_at: datetime | None = None


class CallRecordOut(BaseModel):
    id: int
    caller_number: str
    ivr_choice: str
    inbound_at: datetime
    recording_url: str
    transcript_text: str
    summary_text: str
    processing_status: str
    response_channel: str
    response_note: str
    action_note: str
    resolver_name: str
    resolved_at: datetime | None
    follow_up_required: bool
    follow_up_due_at: datetime | None

    class Config:
        from_attributes = True
