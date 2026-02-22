from fastapi.testclient import TestClient

from app.database import SessionLocal
from app.main import app
from app.models import CallRecord

client = TestClient(app)


def setup_function():
    db = SessionLocal()
    db.query(CallRecord).delete()
    db.commit()
    db.close()


def test_create_and_dashboard():
    res = client.post(
        "/api/calls/inbound",
        json={
            "caller_number": "01011112222",
            "ivr_choice": "1",
            "recording_url": "https://example.com/a.wav",
            "transcript_text": "환불 문의드립니다",
        },
    )
    assert res.status_code == 200
    body = res.json()
    assert body["processing_status"] == "unprocessed"

    dash = client.get("/api/dashboard/daily")
    assert dash.status_code == 200
    metrics = dash.json()
    assert metrics["inbound_count"] == 1
    assert metrics["unprocessed_count"] == 1
    assert metrics["processed_rate"] == 0.0


def test_done_requires_response_note_and_sets_resolved_at():
    create = client.post(
        "/api/calls/inbound",
        json={"caller_number": "01000000000", "ivr_choice": "1", "transcript_text": "교환 원합니다"},
    )
    call_id = create.json()["id"]

    fail = client.patch(
        f"/api/calls/{call_id}",
        json={
            "processing_status": "done",
            "response_channel": "콜백",
            "response_note": "",
            "action_note": "",
            "resolver_name": "관리자",
            "follow_up_required": False,
            "follow_up_due_at": None,
        },
    )
    assert fail.status_code == 400

    ok = client.patch(
        f"/api/calls/{call_id}",
        json={
            "processing_status": "done",
            "response_channel": "콜백",
            "response_note": "배송 지연 사유 안내 및 내일 재연락 약속",
            "action_note": "콜백 예약",
            "resolver_name": "관리자",
            "follow_up_required": False,
            "follow_up_due_at": None,
        },
    )
    assert ok.status_code == 200
    updated = ok.json()
    assert updated["processing_status"] == "done"
    assert updated["resolved_at"] is not None


def test_get_call_detail():
    create = client.post(
        "/api/calls/inbound",
        json={
            "caller_number": "01099998888",
            "ivr_choice": "2",
            "recording_url": "https://example.com/r.wav",
            "transcript_text": "콜백 부탁드립니다",
        },
    )
    call_id = create.json()["id"]

    detail = client.get(f"/api/calls/{call_id}")
    assert detail.status_code == 200
    assert detail.json()["caller_number"] == "01099998888"
