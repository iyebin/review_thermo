"""쿠폰 발급 규칙 및 이력 관리 (SPEC_COUPON.md 기준)."""

import secrets
import string
from typing import Any

# 리뷰별 쿠폰 발급 이력 저장소 (중복 발급 방지)
COUPON_HISTORY: dict[str, dict[str, Any]] = {}


def generate_coupon_code(coupon_type: str) -> str:
    """R6: {쿠폰타입}-{8자리대문자난수} 형식의 고유 코드 생성."""
    random_str = "".join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))
    return f"{coupon_type}-{random_str}"


def issue_coupon(review_id: str, text: str, score: float) -> dict[str, Any]:
    """SPEC_COUPON.md 규칙에 따라 쿠폰을 발급하거나 기존 이력을 반환한다.

    - R4, R5: 이미 요청된 review_id는 기존 이력 그대로 반환
    - R1: score < 0.5 -> 5,000원 사과 쿠폰(APOLOGY)
    - R2: score >= 0.5 and 본문 장문(20자 이상) -> 2,000원 감사 쿠폰(THANKS)
    - R3: score >= 0.5 and 단문(c5 10자 이하) -> 미발급(issued: False)
    """
    if review_id in COUPON_HISTORY:
        return COUPON_HISTORY[review_id]

    if score < 0.5:
        coupon_type = "APOLOGY"
        amount = 5000
        code = generate_coupon_code(coupon_type)
        record = {
            "issued": True,
            "coupon_type": coupon_type,
            "amount": amount,
            "code": code,
        }
    elif len(text) >= 20:
        coupon_type = "THANKS"
        amount = 2000
        code = generate_coupon_code(coupon_type)
        record = {
            "issued": True,
            "coupon_type": coupon_type,
            "amount": amount,
            "code": code,
        }
    else:
        record = {
            "issued": False,
            "coupon_type": None,
            "amount": None,
            "code": None,
        }

    COUPON_HISTORY[review_id] = record
    return record


def clear_coupon_history() -> None:
    """쿠폰 발급 이력 초기화 (테스트용)."""
    COUPON_HISTORY.clear()
