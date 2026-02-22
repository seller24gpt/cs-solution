# CS Voice Intake MVP

`010 업무폰 -> 070 IVR 착신 -> 녹취/STT/요약 -> 처리 대시보드` 흐름을 구현한 FastAPI 기반 MVP입니다.

## 기능
- 인바운드 콜 webhook 등록 API (`/api/calls/inbound`)
- 인입 목록 조회 API (`/api/calls`)
- 인입 상세 조회 API (`/api/calls/{id}`)
- 처리 상태 업데이트 API (`/api/calls/{id}`)
- 처리완료(`done`) 시 답변 내용(`response_note`) 필수 검증
- 메인 대시보드 KPI: 일별 인입수 / 처리수 / 미처리수 / 처리율
- 웹 UI:
  - 인입 목록 테이블
  - 행 클릭 시 전사/요약/녹취URL 상세 보기
  - 처리 상태/답변/메모 업데이트

## 실행파일(런처)
아래 중 하나만 실행하면 됩니다.

### 1) Python 실행파일 (권장, OS 공통)
```bash
python run.py
```

### 2) Linux/macOS 셸 실행파일
```bash
./scripts/run.sh
```

### 3) Windows 배치 실행파일
```bat
scripts\run.bat
```

### 4) Windows 단일 실행 앱(.exe) 만들기
```bat
scripts\build_windows_exe.bat
```

빌드가 끝나면 `dist\CSVoiceIntake.exe` 파일이 생성됩니다.
해당 exe를 실행하면 서버가 `http://127.0.0.1:8000`에서 동작합니다.

모든 실행파일이 자동으로 처리하는 작업:
1. `.venv` 가 없으면 생성
2. 가상환경 활성화/사용
3. `requirements.txt` 설치
4. `uvicorn app.main:app` 실행

브라우저에서 `http://127.0.0.1:8000` 접속.

## 수동 실행
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## 예시: 인입 데이터 생성
```bash
curl -X POST http://127.0.0.1:8000/api/calls/inbound \
  -H "Content-Type: application/json" \
  -d '{
    "caller_number": "01025717669",
    "ivr_choice": "1",
    "recording_url": "https://example.com/recordings/abc.wav",
    "transcript_text": "배송이 아직 도착하지 않았고 송장 확인 부탁드립니다"
  }'
```

## 실행 참고 문서
- 아톡비즈 전환 실무 패키지: `docs/atalk-execution-pack.md`
