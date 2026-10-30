"""주문 관리 유틸리티(orders.py) 단위 테스트 스위트.

모든 함수(add, average_amount, add_tag, get_page)에 대해
정상 작동(Normal), 오작동/오류(Error/Bug), 엣지 케이스(Edge)를 검증합니다.
명세 기반 TDD 원칙에 따라 이 테스트 코드는 작성 후 변경하지 않습니다.
"""

import pytest

from warmup.orders import add, add_tag, average_amount, get_page

# ==============================================================================
# 1. add(sum1, sum2) 테스트
# ==============================================================================


@pytest.mark.parametrize(
    ("a", "b", "expected"),
    [
        (2, 3, 5),
        (-2, 3, 1),
        (-5, -7, -12),
        (100, 200, 300),
    ],
)
def test_add_normal(a, b, expected):
    """[정상] 두 정수를 더한 올바른 합을 반환하는지 검증."""
    assert add(a, b) == expected


@pytest.mark.parametrize(
    ("a", "b", "expected"),
    [
        (0, 0, 0),
        (0, 10, 10),
        (-10, 0, -10),
    ],
)
def test_add_edge_zeros(a, b, expected):
    """[엣지] 0이 포함된 덧셈(덧셈의 항등원)을 올바르게 처리하는지 검증."""
    assert add(a, b) == expected


def test_add_edge_floats():
    """[엣지] 부동소수점 덧셈 시 부동소수점 오차 범위를 고려해 검증."""
    assert add(0.1, 0.2) == pytest.approx(0.3)


def test_add_edge_large_numbers():
    """[엣지] 매우 큰 정수의 덧셈이 정상 동작하는지 검증."""
    large_num = 10**18
    assert add(large_num, large_num) == 2 * 10**18


@pytest.mark.parametrize(
    ("a", "b"),
    [
        (10, "20"),
        ("hello", 5),
        (None, 5),
    ],
)
def test_add_invalid_type_raises_type_error(a, b):
    """[오작동] 지원되지 않는 타입(문자열과 숫자, None 등) 연산 시 TypeError 발생 검증."""
    with pytest.raises(TypeError):
        add(a, b)


# ==============================================================================
# 2. average_amount(amounts) 테스트
# ==============================================================================


@pytest.mark.parametrize(
    ("amounts", "expected"),
    [
        ([1000, 2000, 3000], 2000.0),
        ([100, 200], 150.0),
        ([10, 20, 24], 18.0),
    ],
)
def test_average_amount_normal(amounts, expected):
    """[정상] 여러 주문 금액의 산술 평균을 올바르게 계산하는지 검증."""
    assert average_amount(amounts) == pytest.approx(expected)


def test_average_amount_edge_single_item():
    """[엣지] 주문 금액이 단 1건만 주어졌을 때 해당 금액이 그대로 반환되는지 검증."""
    assert average_amount([750]) == pytest.approx(750.0)


@pytest.mark.parametrize(
    ("amounts", "expected"),
    [
        ([0, 0, 0], 0.0),
        ([-100, 100], 0.0),
        ([-50, -150], -100.0),
    ],
)
def test_average_amount_edge_zeros_and_negatives(amounts, expected):
    """[엣지] 0 또는 음수가 포함된 주문 금액 목록의 평균을 올바르게 계산하는지 검증."""
    assert average_amount(amounts) == pytest.approx(expected)


def test_average_amount_edge_floats():
    """[엣지] 소수점 금액이 포함된 경우 부동소수점 오차를 고려해 검증."""
    assert average_amount([10.5, 20.5, 30.5]) == pytest.approx(20.5)


def test_average_amount_error_empty_list_raises_zero_division():
    """[오작동/예외] 빈 리스트가 전달되면 ZeroDivisionError가 발생하는지 검증."""
    with pytest.raises(ZeroDivisionError):
        average_amount([])


def test_average_amount_error_invalid_elements_raise_type_error():
    """[오작동/예외] 금액 리스트에 숫자가 아닌 요소가 포함된 경우 TypeError 발생 검증."""
    with pytest.raises(TypeError):
        average_amount([1000, "2000원", 3000])


# ==============================================================================
# 3. add_tag(order, tag, tags=[]) 테스트
# ==============================================================================


def test_add_tag_normal_single_order():
    """[정상] 태그가 없는 주문에 새 태그를 추가하고 기존 주문 객체를 반환하는지 검증."""
    order = {"id": 1}
    result = add_tag(order, "gift")

    assert result is order
    assert order["tags"] == ["gift"]


def test_add_tag_normal_order_with_existing_tags():
    """[정상] 이미 tags를 가지고 있는 주문에 새 태그를 추가했을 때 기존 태그가 유지되는지 검증."""
    order = {"id": 1, "tags": ["vip"]}
    add_tag(order, "urgent")

    assert order["tags"] == ["vip", "urgent"]


def test_add_tag_normal_with_explicit_tags_argument():
    """[정상] 호출 시 tags 파라미터를 명시적으로 전달했을 때 해당 리스트를 사용하는지 검증."""
    order = {"id": 1}
    custom_tags = ["custom1"]
    add_tag(order, "custom2", tags=custom_tags)

    assert order["tags"] == ["custom1", "custom2"]
    assert custom_tags == ["custom1", "custom2"]


def test_add_tag_edge_empty_string_tag():
    """[엣지] 빈 문자열 태그가 추가될 때 정상 반영되는지 검증."""
    order = {"id": 100}
    add_tag(order, "")
    assert order["tags"] == [""]


def test_add_tag_edge_duplicate_tag():
    """[엣지] 동일한 태그가 중복 추가될 때 리스트에 누적되는지 검증."""
    order = {"id": 100, "tags": ["sale"]}
    add_tag(order, "sale")
    assert order["tags"] == ["sale", "sale"]


def test_add_tag_bug_independent_orders_do_not_share_default_tags():
    """[오작동/버그 포착] 독립적인 주문 객체 간에 기본 인자 리스트(tags=[])가 공유되지 않는지 검증.

    파이썬의 가변 기본 인자 버그가 존재하면 이전 호출의 태그가 새 주문에 누적됩니다.
    """
    order1 = {"id": 1}
    order2 = {"id": 2}

    add_tag(order1, "gift")
    add_tag(order2, "urgent")

    assert order1["tags"] == ["gift"]
    assert order2["tags"] == ["urgent"]


# ==============================================================================
# 4. get_page(orders, page, size=10) 테스트
# ==============================================================================


def test_get_page_normal_first_page():
    """[정상] 1페이지(1부터 시작) 요청 시 0번 인덱스부터 size개 만큼 반환하는지 검증."""
    orders = list(range(1, 21))  # 1 ~ 20
    assert get_page(orders, page=1, size=5) == [1, 2, 3, 4, 5]


def test_get_page_normal_middle_page():
    """[정상] 2번째 및 3번째 페이지를 정확히 슬라이싱하는지 검증."""
    orders = list(range(1, 21))  # 1 ~ 20
    assert get_page(orders, page=2, size=5) == [6, 7, 8, 9, 10]
    assert get_page(orders, page=3, size=5) == [11, 12, 13, 14, 15]


def test_get_page_normal_default_size():
    """[정상] size 인자를 생략했을 때 기본값 10이 적용되어 10개가 반환되는지 검증."""
    orders = list(range(1, 25))  # 1 ~ 24
    assert get_page(orders, page=1) == list(range(1, 11))


def test_get_page_edge_empty_orders():
    """[엣지] 주문 목록이 비어있을 때 빈 리스트가 반환되는지 검증."""
    assert get_page([], page=1, size=5) == []


def test_get_page_edge_last_partial_page():
    """[엣지] 마지막 페이지의 주문 수가 size보다 적을 때(남은 개수만) 올바르게 반환하는지 검증."""
    orders = list(range(1, 6))  # 5개
    assert get_page(orders, page=2, size=3) == [4, 5]


def test_get_page_edge_exact_multiple():
    """[엣지] 전체 주문 개수가 size의 정확한 배수일 때 마지막 페이지가 올바르게 반환되는지 검증."""
    orders = list(range(1, 7))  # 6개
    assert get_page(orders, page=2, size=3) == [4, 5, 6]


def test_get_page_edge_size_larger_than_orders():
    """[엣지] 전체 주문 수보다 size가 더 큰 경우 전체 목록이 반환되는지 검증."""
    orders = [1, 2, 3]
    assert get_page(orders, page=1, size=10) == [1, 2, 3]


def test_get_page_edge_past_last_page():
    """[엣지] 전체 페이지 수를 초과한 page 번호 요청 시 빈 리스트가 반환되는지 검증."""
    orders = list(range(1, 6))
    assert get_page(orders, page=5, size=2) == []
