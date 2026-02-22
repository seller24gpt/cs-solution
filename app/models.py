from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


class CallRecord(Base):
    __tablename__ = "call_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    caller_number: Mapped[str] = mapped_column(String(30), index=True)
    ivr_choice: Mapped[str] = mapped_column(String(5), default="1")
    inbound_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    recording_url: Mapped[str] = mapped_column(String(255), default="")
    transcript_text: Mapped[str] = mapped_column(Text, default="")
    summary_text: Mapped[str] = mapped_column(Text, default="")

    processing_status: Mapped[str] = mapped_column(String(20), default="unprocessed", index=True)
    response_channel: Mapped[str] = mapped_column(String(30), default="")
    response_note: Mapped[str] = mapped_column(Text, default="")
    action_note: Mapped[str] = mapped_column(Text, default="")
    resolver_name: Mapped[str] = mapped_column(String(100), default="")
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    follow_up_required: Mapped[bool] = mapped_column(Boolean, default=False)
    follow_up_due_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
