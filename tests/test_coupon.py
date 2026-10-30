"""쿠폰 발급 API(/v1/coupons/issue) 테스트 — SPEC_COUPON.md 기준."""

import re

import pytest

from app.coupon import clear_coupon_history


@pytest.fixture(autouse=True)
def reset_coupon_history():
    clear_coupon_history()


def test_same_review_twice_same_code(make_client):
    """실습 4-2 필수 테스트: 같은 리뷰 번호로 두 번 요청해도 쿠폰 번호가 같아야 함."""
    client = make_client(0.2)  # 점수 상관없는 테스트, 기본 점수 아무거나 넣습니다
    body = {"review_id": "r2", "text": "배송 최악"}
    first = client.post("/v1/coupons/issue", json=body).json()
    second = client.post("/v1/coupons/issue", json=body).json()
    assert first["code"] is not None
    assert first["code"] == second["code"]


# SPEC_COUPON.md 예시표 c1 ~ c6 (초회 발급 케이스)
COUPON_INITIAL_CASES = [
    pytest.param(
        "c1", "r101", "배송이 너무 늦고 파손되어 왔어요", 0.12, True, "APOLOGY", 5000,
        id="c1_r101_apology_boundary"
    ),
    pytest.param(
        "c2", "r102", "완전 별로", 0.25, True, "APOLOGY", 5000,
        id="c2_r102_apology"
    ),
    pytest.param(
        "c3", "r103", "배송도 정말 빠르고 상품 마감 품질도 아주 만족스럽습니다!", 0.88, True, "THANKS", 2000,
        id="c3_r103_thanks_boundary"
    ),
    pytest.param(
        "c4", "r104", "정말 최고로 마음에 쏙 들어요 ㅎㅎ!", 0.75, True, "THANKS", 2000,
        id="c4_r104_thanks"
    ),
    pytest.param(
        "c5", "r105", "좋아요 만족합니다", 0.85, False, None, None,
        id="c5_r105_no_issue_short"
    ),
    pytest.param(
        "c6", "r106", "굿", 0.60, False, None, None,
        id="c6_r106_no_issue_short"
    ),
]


@pytest.mark.parametrize(
    "case_id, review_id, text, score, expected_issued, expected_type, expected_amount",
    COUPON_INITIAL_CASES,
)
def test_coupon_issue_initial(
    make_client, case_id, review_id, text, score, expected_issued, expected_type, expected_amount
):
    client = make_client(score)
    body = {"review_id": review_id, "text": text}
    res = client.post("/v1/coupons/issue", json=body)
    assert res.status_code == 200
    data = res.json()
    assert data["issued"] == expected_issued
    assert data["coupon_type"] == expected_type
    assert data["amount"] == expected_amount
    if expected_issued:
        assert data["code"] is not None
        assert data["code"].startswith(f"{expected_type}-")
    else:
        assert data["code"] is None


def test_coupon_duplicate_request_c7(make_client):
    """c7: 이미 발급된 리뷰(r101) 재요청 시 이전과 동일한 쿠폰 정보 및 코드 반환 (R4)."""
    client = make_client(0.12)
    body = {"review_id": "r101", "text": "배송이 너무 늦고 파손되어 왔어요"}
    res1 = client.post("/v1/coupons/issue", json=body)
    assert res1.status_code == 200
    first = res1.json()

    res2 = client.post("/v1/coupons/issue", json=body)
    assert res2.status_code == 200
    second = res2.json()

    assert first["issued"] is True
    assert second["issued"] is True
    assert first["coupon_type"] == second["coupon_type"] == "APOLOGY"
    assert first["amount"] == second["amount"] == 5000
    assert first["code"] is not None
    assert first["code"] == second["code"]


def test_coupon_duplicate_unissued_request_c8(make_client):
    """c8: 미발급된 리뷰(r105) 재요청 시 동일하게 미발급(False) 반환 (R5)."""
    client = make_client(0.85)
    body = {"review_id": "r105", "text": "좋아요 만족합니다"}
    res1 = client.post("/v1/coupons/issue", json=body)
    assert res1.status_code == 200
    assert res1.json()["issued"] is False

    res2 = client.post("/v1/coupons/issue", json=body)
    assert res2.status_code == 200
    assert res2.json()["issued"] is False


def test_coupon_validation_error_c9(make_client):
    """c9: 본문이 비어있거나 누락된 경우 422 상태 코드 반환 (R7)."""
    client = make_client(0.5)
    # 빈 문자열 (c9)
    res_empty = client.post("/v1/coupons/issue", json={"review_id": "r107", "text": ""})
    assert res_empty.status_code == 422

    # review_id 누락
    res_no_id = client.post("/v1/coupons/issue", json={"text": "배송 최악"})
    assert res_no_id.status_code == 422


COUPON_STANDARD_CASES = [
    pytest.param(
        f"standard-{index:03d}",
        score,
        text,
        expected_type,
        expected_amount,
        id=f"standard_{index:03d}_{expected_type or 'no_coupon'}",
    )
    for index, (score, text, expected_type, expected_amount) in enumerate(
        [
            *[
                (score, f"불만 리뷰 {index}", "APOLOGY", 5000)
                for index, score in enumerate(
                    (0.0, 0.1, 0.2, 0.3, 0.4, 0.4999, 0.49, 0.25, 0.05, 0.45,
                     0.01, 0.15, 0.35, 0.48, 0.499, 0.11, 0.22, 0.33, 0.44, 0.06,
                     0.16, 0.26, 0.36, 0.46, 0.07, 0.17, 0.27, 0.37, 0.47, 0.08,
                     0.18, 0.28, 0.38, 0.498)
                )
            ],
            *[
                (score, f"만족스러운 리뷰입니다. 충분한 내용입니다. {index:02d}", "THANKS", 2000)
                for index, score in enumerate(
                    (0.5, 0.51, 0.6, 0.7, 0.8, 0.9, 1.0, 0.55, 0.65, 0.75,
                     0.85, 0.95, 0.5001, 0.52, 0.62, 0.72, 0.82, 0.92, 0.53, 0.63,
                     0.73, 0.83, 0.93, 0.54, 0.64, 0.74, 0.84, 0.94, 0.56, 0.66,
                     0.76, 0.86, 0.96)
                )
            ],
            *[
                (score, f"짧은 리뷰 {index}", None, None)
                for index, score in enumerate(
                    (0.5, 0.51, 0.6, 0.7, 0.8, 0.9, 1.0, 0.55, 0.65, 0.75,
                     0.85, 0.95, 0.5001, 0.52, 0.62, 0.72, 0.82, 0.92, 0.53, 0.63,
                     0.73, 0.83, 0.93, 0.54, 0.64, 0.74, 0.84, 0.94, 0.56, 0.66,
                     0.76, 0.86, 0.96)
                )
            ],
        ]
    )
]


@pytest.mark.parametrize(
    "review_id, score, text, expected_type, expected_amount",
    COUPON_STANDARD_CASES,
)
def test_coupon_standard_cases(
    make_client, review_id, score, text, expected_type, expected_amount
):
    response = make_client(score).post(
        "/v1/coupons/issue",
        json={"review_id": review_id, "text": text},
    )

    assert response.status_code == 200
    result = response.json()
    assert result["issued"] is (expected_type is not None)
    assert result["coupon_type"] == expected_type
    assert result["amount"] == expected_amount
    if expected_type is None:
        assert result["code"] is None
    else:
        assert re.fullmatch(rf"{expected_type}-[A-Z0-9]{{8}}", result["code"])


COUPON_EDGE_VALID_CASES = [
    (
        f"edge-boundary-{score_index}-{length}",
        score,
        "x" * length,
        ("APOLOGY", 5000) if score < 0.5 else (("THANKS", 2000) if length >= 20 else (None, None)),
    )
    for score_index, score in enumerate((0.0, 0.4999, 0.5, 0.5001, 1.0))
    for length in (1, 19, 20, 500)
] + [
    ("edge-whitespace-text", 0.5, " " + "x" * 18 + " ", (None, None)),
    ("edge-unicode-19", 0.5, "한" * 19, (None, None)),
    ("edge-unicode-20", 0.5, "한" * 20, ("THANKS", 2000)),
    ("edge-emoji-19", 0.5, "🙂" * 19, (None, None)),
    ("edge-emoji-20", 0.5, "🙂" * 20, ("THANKS", 2000)),
]

COUPON_EDGE_INVALID_BODIES = [
    ("edge-null-body", None),
    ("edge-array-body", []),
    ("edge-string-body", "not-an-object"),
    ("edge-number-body", 7),
    ("edge-bool-body", True),
    ("edge-missing-review-id", {"text": "유효한 텍스트"}),
    ("edge-missing-text", {"review_id": "missing-text"}),
    ("edge-null-review-id", {"review_id": None, "text": "유효한 텍스트"}),
    ("edge-empty-review-id", {"review_id": "", "text": "유효한 텍스트"}),
    ("edge-blank-review-id", {"review_id": "   ", "text": "유효한 텍스트"}),
    ("edge-integer-review-id", {"review_id": 123, "text": "유효한 텍스트"}),
    ("edge-float-review-id", {"review_id": 1.5, "text": "유효한 텍스트"}),
    ("edge-bool-review-id", {"review_id": True, "text": "유효한 텍스트"}),
    ("edge-array-review-id", {"review_id": [], "text": "유효한 텍스트"}),
    ("edge-object-review-id", {"review_id": {}, "text": "유효한 텍스트"}),
    ("edge-null-text", {"review_id": "null-text", "text": None}),
    ("edge-empty-text", {"review_id": "empty-text", "text": ""}),
    ("edge-blank-text", {"review_id": "blank-text", "text": "   "}),
    ("edge-text-length-501", {"review_id": "too-long-text", "text": "x" * 501}),
    ("edge-text-length-1000", {"review_id": "much-too-long-text", "text": "x" * 1000}),
    ("edge-integer-text", {"review_id": "integer-text", "text": 123}),
    ("edge-float-text", {"review_id": "float-text", "text": 1.5}),
    ("edge-bool-text", {"review_id": "bool-text", "text": True}),
    ("edge-array-text", {"review_id": "array-text", "text": []}),
    ("edge-object-text", {"review_id": "object-text", "text": {}}),
]

COUPON_EDGE_CASES = [
    pytest.param("valid", score, {"review_id": case_id, "text": text}, expected, id=f"valid-{case_id}")
    for case_id, score, text, expected in COUPON_EDGE_VALID_CASES
] + [
    pytest.param("invalid", 0.5, body, None, id=case_id)
    for case_id, body in COUPON_EDGE_INVALID_BODIES
]


@pytest.mark.parametrize("kind, score, body, expected", COUPON_EDGE_CASES)
def test_coupon_edge_cases(make_client, kind, score, body, expected):
    response = make_client(score).post("/v1/coupons/issue", json=body)

    if kind == "invalid":
        assert response.status_code == 422
        return

    assert response.status_code == 200
    result = response.json()
    expected_type, expected_amount = expected
    assert result["issued"] is (expected_type is not None)
    assert result["coupon_type"] == expected_type
    assert result["amount"] == expected_amount
    if expected_type is None:
        assert result["code"] is None
    else:
        assert re.fullmatch(rf"{expected_type}-[A-Z0-9]{{8}}", result["code"])
