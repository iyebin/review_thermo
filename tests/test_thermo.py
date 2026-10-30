"""SPEC_REVIEW.md 예시표 기반 thermo 단위 테스트.

to_label, to_temperature, is_mismatch 3개 함수를 검증합니다.
"""

import pytest

from app.thermo import is_mismatch, to_label, to_temperature

# SPEC_REVIEW.md 5장 예시표 기반 테스트 케이스 목록
# (text, rating, score, label, temperature, mismatch)

LABEL_CASES = [
    pytest.param(0.9521, "positive", id="0.9521_positive"),
    pytest.param(0.1204, "negative", id="0.1204_negative"),
    pytest.param(0.8810, "positive", id="0.8810_positive"),
    pytest.param(0.2500, "negative", id="0.2500_negative"),
    pytest.param(0.6000, "positive", id="0.6000_positive"),
    pytest.param(0.5000, "positive", id="0.5000_positive_boundary"),
    pytest.param(0.4999, "negative", id="0.4999_negative_boundary"),
    pytest.param(0.5000001, "positive", id="0.5000001_positive_micro_edge"),
    pytest.param(0.4999999, "negative", id="0.4999999_negative_micro_edge"),
    pytest.param(0.0000, "negative", id="0.0000_negative_min"),
    pytest.param(1.0000, "positive", id="1.0000_positive_max"),
    pytest.param(0.7000, "positive", id="0.7000_positive"),
    pytest.param(0.4000, "negative", id="0.4000_negative"),
    pytest.param(0.3000, "negative", id="0.3000_negative"),
    pytest.param(0.7500, "positive", id="0.7500_positive"),
    pytest.param(0.1500, "negative", id="0.1500_negative"),
    pytest.param(0.8500, "positive", id="0.8500_positive"),
    pytest.param(0.8735, "positive", id="0.8735_positive_round_up"),
    pytest.param(0.8732, "positive", id="0.8732_positive_round_down"),
    pytest.param(0.9999, "positive", id="0.9999_positive_high_edge"),
    pytest.param(0.0005, "negative", id="0.0005_negative_low_edge"),
    pytest.param(0.9000, "positive", id="0.9000_positive_multiline"),
]

TEMPERATURE_CASES = [
    pytest.param(0.9521, 95.2, id="0.9521_temp_95.2"),
    pytest.param(0.1204, 12.0, id="0.1204_temp_12.0"),
    pytest.param(0.8810, 88.1, id="0.8810_temp_88.1"),
    pytest.param(0.2500, 25.0, id="0.2500_temp_25.0"),
    pytest.param(0.6000, 60.0, id="0.6000_temp_60.0"),
    pytest.param(0.5000, 50.0, id="0.5000_temp_50.0"),
    pytest.param(0.4999, 50.0, id="0.4999_temp_50.0_rounded"),
    pytest.param(0.5000001, 50.0, id="0.5000001_temp_50.0_micro"),
    pytest.param(0.4999999, 50.0, id="0.4999999_temp_50.0_micro"),
    pytest.param(0.0000, 0.0, id="0.0000_temp_0.0_min"),
    pytest.param(1.0000, 100.0, id="1.0000_temp_100.0_max"),
    pytest.param(0.7000, 70.0, id="0.7000_temp_70.0"),
    pytest.param(0.4000, 40.0, id="0.4000_temp_40.0"),
    pytest.param(0.3000, 30.0, id="0.3000_temp_30.0"),
    pytest.param(0.7500, 75.0, id="0.7500_temp_75.0"),
    pytest.param(0.1500, 15.0, id="0.1500_temp_15.0"),
    pytest.param(0.8500, 85.0, id="0.8500_temp_85.0"),
    pytest.param(0.8735, 87.4, id="0.8735_temp_87.4_round_up"),
    pytest.param(0.8732, 87.3, id="0.8732_temp_87.3_round_down"),
    pytest.param(0.9999, 100.0, id="0.9999_temp_100.0_upper_round"),
    pytest.param(0.0005, 0.1, id="0.0005_temp_0.1_lower_round"),
    pytest.param(0.9000, 90.0, id="0.9000_temp_90.0"),
]

MISMATCH_CASES = [
    pytest.param(1, "positive", True, id="rating1_positive_mismatch"),
    pytest.param(1, "negative", False, id="rating1_negative_match"),
    pytest.param(2, "positive", True, id="rating2_positive_mismatch"),
    pytest.param(2, "negative", False, id="rating2_negative_match"),
    pytest.param(3, "positive", False, id="rating3_positive_neutral_match"),
    pytest.param(3, "negative", False, id="rating3_negative_neutral_match"),
    pytest.param(4, "positive", False, id="rating4_positive_match"),
    pytest.param(4, "negative", True, id="rating4_negative_mismatch"),
    pytest.param(5, "positive", False, id="rating5_positive_match"),
    pytest.param(5, "negative", True, id="rating5_negative_mismatch"),
]


@pytest.mark.parametrize("score,expected_label", LABEL_CASES)
def test_to_label(score: float, expected_label: str) -> None:
    """점수에 따른 긍정/부정 라벨을 검증한다."""
    assert to_label(score) == expected_label


@pytest.mark.parametrize("score,expected_temp", TEMPERATURE_CASES)
def test_to_temperature(score: float, expected_temp: float) -> None:
    """점수에 따른 리뷰 온도를 검증한다."""
    assert to_temperature(score) == expected_temp


@pytest.mark.parametrize("rating,label,expected_mismatch", MISMATCH_CASES)
def test_is_mismatch(rating: int, label: str, expected_mismatch: bool) -> None:
    """별점과 감성 라벨에 따른 불일치 여부를 검증한다."""
    assert is_mismatch(rating, label) == expected_mismatch
