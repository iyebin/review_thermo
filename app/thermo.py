"""리뷰 온도 규칙 3개. 규칙은 SPEC_REVIEW.md를 따릅니다."""


def to_label(score: float) -> str:
    """score를 "positive" / "negative" 로 바꾼다."""
    return "positive" if score >= 0.5 else "negative"


def to_temperature(score: float) -> float:
    """score를 리뷰 온도(0~100)로 바꾼다. 소수점 첫째 자리까지 반올림."""
    return round(score * 100, 1)


def is_mismatch(rating: int, label: str) -> bool:
    """별점과 내용이 반대인지 알려 준다.

    - 별점 4~5점인데 부정인 경우 True
    - 별점 1~2점인데 긍정인 경우 True
    - 별점 3점은 항상 일치(False)
    """
    if rating in (4, 5) and label == "negative":
        return True
    if rating in (1, 2) and label == "positive":
        return True
    return False

# © 2026 김연지. All rights reserved. 수강생 개인 학습용 · 무단 강의·복제·배포·수정 금지 (LICENSE.md)
