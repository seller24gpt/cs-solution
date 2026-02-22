def summarize_transcript(text: str) -> str:
    normalized = " ".join(text.strip().split())
    if not normalized:
        return "전사 내용이 아직 없습니다."

    short = normalized[:180]
    return f"요약: {short}" if len(normalized) <= 180 else f"요약: {short}..."
