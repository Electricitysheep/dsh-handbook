"""test_data_utils — data_utils 模块（5 个工具函数）的完整 pytest 单元测试。

覆盖范围：
- parse_duration：组合单位、大小写、空白、超大值、Unicode、非法格式 / None / 空串
- chunk_list：整分 / 余块 / 空列表 / 块大于列表 / 单元素块、size 非法值
- fibonacci：0/1 起始语义、边界、大 n、负数与非法类型
- is_valid_email：合法格式、空 local/domain、多 @、无 TLD、TLD 过短、空白、Unicode、非字符串
- calculate_interest：复利数值、0 值边界、小数年限、浮点精度（approx）、溢出 inf、负数与非法类型
"""

import math

import pytest

from data_utils import (
    calculate_interest,
    chunk_list,
    fibonacci,
    is_valid_email,
    parse_duration,
)


# ---------------------------------------------------------------------------
# parse_duration
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "duration,expected",
    [
        ("30s", 30),                       # 单单位
        ("1h30m", 5400),                   # 组合单位
        ("2d", 172800),                    # 天
        ("1d12h", 129600),                 # 跨单位组合
        ("1h30m2s", 5402),                 # 三种单位组合
        ("0s", 0),                         # 零值
        (" 1h30m ", 5400),                 # 首尾空白字符
        ("1H30M", 5400),                   # 大小写不敏感
        ("999999999d", 86_399_999_913_600),  # 超大值（Python int 无溢出）
    ],
    ids=[
        "single_unit_s",
        "combined_h_m",
        "single_unit_d",
        "combined_d_h",
        "combined_h_m_s",
        "zero_value",
        "outer_whitespace",
        "case_insensitive",
        "huge_value",
    ],
)
def test_parse_duration_valid(duration, expected):
    assert parse_duration(duration) == expected


@pytest.mark.parametrize(
    "duration",
    [
        None,          # None
        "",            # 空字符串
        "   ",         # 纯空白
        "h",           # 缺数值
        "10",          # 缺单位
        "1h30",        # 尾部残留数字
        "abc",         # 完全非法
        "1h 30m",      # 内部空白字符
        "1.5h",        # 小数不支持
        "-1h",         # 负号
        "1h30x",       # 未知单位
        "1\u0434",     # Unicode（西里尔字母）非法单位
    ],
    ids=[
        "none",
        "empty",
        "only_whitespace",
        "missing_number",
        "missing_unit",
        "trailing_digits",
        "garbage",
        "inner_whitespace",
        "fractional_number",
        "negative_number",
        "unknown_unit",
        "unicode_unit",
    ],
)
def test_parse_duration_invalid_raises_value_error(duration):
    with pytest.raises(ValueError):
        parse_duration(duration)


def test_parse_duration_none_error_message():
    with pytest.raises(ValueError, match="must not be None"):
        parse_duration(None)


def test_parse_duration_empty_error_message():
    with pytest.raises(ValueError, match="must not be empty"):
        parse_duration("   ")


# ---------------------------------------------------------------------------
# chunk_list
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "items,size,expected",
    [
        ([1, 2, 3, 4, 5, 6], 2, [[1, 2], [3, 4], [5, 6]]),   # 整除
        ([1, 2, 3, 4, 5], 2, [[1, 2], [3, 4], [5]]),         # 余块
        ([], 3, []),                                         # 空列表
        ([1, 2, 3], 5, [[1, 2, 3]]),                         # size > 长度
        ([1, 2, 3], 1, [[1], [2], [3]]),                     # size = 1
        ([1, 2, 3], 3, [[1, 2, 3]]),                         # size = 长度
        (["a", "b", "c", "d"], 2, [["a", "b"], ["c", "d"]]), # 非数字元素
    ],
    ids=[
        "exact_division",
        "remainder_chunk",
        "empty_list",
        "size_greater_than_len",
        "size_one",
        "size_equal_len",
        "string_items",
    ],
)
def test_chunk_list_valid(items, size, expected):
    assert chunk_list(items, size) == expected


def test_chunk_list_does_not_mutate_original():
    items = [1, 2, 3, 4, 5]
    chunk_list(items, 2)
    assert items == [1, 2, 3, 4, 5]


@pytest.mark.parametrize(
    "size",
    [0, -1, -100],
    ids=["zero", "negative_one", "negative_large"],
)
def test_chunk_list_non_positive_size_raises_value_error(size):
    with pytest.raises(ValueError, match="size must be > 0"):
        chunk_list([1, 2, 3], size)


@pytest.mark.parametrize(
    "size",
    [1.5, "2", None, [2], 2 + 3j],
    ids=["float", "str", "none", "list", "complex"],
)
def test_chunk_list_non_int_size_raises_type_error(size):
    with pytest.raises(TypeError, match="size must be an int"):
        chunk_list([1, 2, 3], size)


@pytest.mark.parametrize(
    "size",
    [True, False],
    ids=["bool_true", "bool_false"],
)
def test_chunk_list_bool_size_raises_type_error(size):
    # bool 是 int 的子类，但按文档语义应视为非法类型
    with pytest.raises(TypeError, match="size must be an int"):
        chunk_list([1, 2, 3], size)


# ---------------------------------------------------------------------------
# fibonacci
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "n,expected",
    [
        (0, 0),                              # 边界：第 0 项
        (1, 1),                              # 边界：第 1 项
        (2, 1),
        (5, 5),
        (10, 55),
        (20, 6765),
        (100, 354224848179261915075),        # 大 n
    ],
    ids=["n0", "n1", "n2", "n5", "n10", "n20", "n100"],
)
def test_fibonacci_valid(n, expected):
    assert fibonacci(n) == expected


def test_fibonacci_monotonic_growth():
    seq = [fibonacci(n) for n in range(15)]
    assert seq == sorted(seq)
    assert seq[0] == 0 and seq[1] == 1


@pytest.mark.parametrize(
    "n",
    [-1, -100],
    ids=["negative_one", "negative_large"],
)
def test_fibonacci_negative_raises_value_error(n):
    with pytest.raises(ValueError, match="n must be >= 0"):
        fibonacci(n)


@pytest.mark.parametrize(
    "n",
    [1.5, "5", None, [5], 5 + 0j],
    ids=["float", "str", "none", "list", "complex"],
)
def test_fibonacci_non_int_raises_type_error(n):
    with pytest.raises(TypeError, match="n must be an int"):
        fibonacci(n)


@pytest.mark.parametrize(
    "n",
    [True, False],
    ids=["bool_true", "bool_false"],
)
def test_fibonacci_bool_raises_type_error(n):
    # bool 是 int 的子类，但按文档语义应视为非法类型
    with pytest.raises(TypeError, match="n must be an int"):
        fibonacci(n)


# ---------------------------------------------------------------------------
# is_valid_email
# ---------------------------------------------------------------------------

@pytest.fixture
def valid_email_samples():
    """一组符合宽松正则语义的合法邮箱样本。"""
    return [
        "user@example.com",
        "first.last@sub.example.co.uk",
        "USER@EXAMPLE.COM",
        "a_b%+-x@example.com",
        "x@y.abc",
    ]


def test_is_valid_email_fixture_samples(valid_email_samples):
    for email in valid_email_samples:
        assert is_valid_email(email) is True


@pytest.mark.parametrize(
    "email",
    [
        "user@example.com",                  # 常规
        "first.last@sub.example.co.uk",      # 子域 + 多级 TLD
        "USER@EXAMPLE.COM",                  # 大写
        "a_b%+-x@example.com",               # local 部分特殊字符
        "x@y.abc",                           # 三字母 TLD
    ],
    ids=["normal", "subdomain", "uppercase", "special_chars", "three_letter_tld"],
)
def test_is_valid_email_valid(email):
    assert is_valid_email(email) is True


@pytest.mark.parametrize(
    "email",
    [
        None,                                  # None
        123,                                   # int
        3.14,                                  # float
        b"user@example.com",                   # bytes
        "",                                    # 空串
        "   ",                                 # 纯空白
        "user@",                               # 空 domain
        "@example.com",                        # 空 local
        "user@example",                        # 无 TLD
        "user@example.c",                      # TLD 过短
        "a b@c.com",                           # local 含空白
        "user@exa mple.com",                   # domain 含空白
        "user@@example.com",                   # 多个 @
        "\u7528\u6237@example.com",            # Unicode local（中文）
        "user@\u4f8b.com",                     # Unicode domain（中文）
        "user@.com",                           # domain 以点开头
    ],
    ids=[
        "none", "int", "float", "bytes", "empty", "whitespace",
        "empty_domain", "empty_local", "no_tld", "short_tld",
        "space_in_local", "space_in_domain", "double_at",
        "unicode_local", "unicode_domain", "dot_leading_domain",
    ],
)
def test_is_valid_email_invalid(email):
    assert is_valid_email(email) is False


def test_is_valid_email_returns_bool_type():
    result = is_valid_email("user@example.com")
    assert isinstance(result, bool)


# ---------------------------------------------------------------------------
# calculate_interest
# ---------------------------------------------------------------------------

@pytest.fixture
def interest_case():
    """复利基准用例：本金 1000、年利率 5%、3 年。"""
    return {"principal": 1000.0, "rate": 0.05, "years": 3.0, "expected": 1157.625}


def test_calculate_interest_fixture_case(interest_case):
    result = calculate_interest(
        interest_case["principal"],
        interest_case["rate"],
        interest_case["years"],
    )
    assert result == pytest.approx(interest_case["expected"])


@pytest.mark.parametrize(
    "principal,rate,years,expected",
    [
        (1000, 0.1, 1, 1100.0),                     # 基本复利
        (100, 0.05, 2, 110.25),                     # 多年复利
        (100, 0.5, 0.5, 122.4744871391589),         # 小数年限
        (1000, 0.1, 0, 1000.0),                     # years = 0
        (1000, 0.0, 5, 1000.0),                     # rate = 0
        (0, 0.1, 5, 0.0),                           # principal = 0
        (0.1, 0.2, 1, 0.12),                        # 小数值浮点精度
    ],
    ids=[
        "basic_compound",
        "multi_year",
        "fractional_year",
        "zero_years",
        "zero_rate",
        "zero_principal",
        "float_precision",
    ],
)
def test_calculate_interest_values(principal, rate, years, expected):
    assert calculate_interest(principal, rate, years) == pytest.approx(expected)


def test_calculate_interest_returns_float():
    assert isinstance(calculate_interest(1000, 0.1, 1), float)


def test_calculate_interest_overflow_to_inf():
    # 极大数值溢出为 inf（浮点边界行为）
    assert calculate_interest(1e308, 0.1, 100) == pytest.approx(math.inf)


@pytest.mark.parametrize(
    "principal,rate,years",
    [
        (-100, 0.1, 1),      # 负本金
        (100, -0.1, 1),      # 负利率
        (100, 0.1, -1),      # 负年限
        (-1, -1, -1),        # 全负
    ],
    ids=["negative_principal", "negative_rate", "negative_years", "all_negative"],
)
def test_calculate_interest_negative_raises_value_error(principal, rate, years):
    with pytest.raises(ValueError):
        calculate_interest(principal, rate, years)


@pytest.mark.parametrize(
    "principal,rate,years",
    [
        ("1000", 0.1, 1),     # 字符串本金
        (1000, "0.1", 1),     # 字符串利率
        (1000, 0.1, "1"),     # 字符串年限
        (None, 0.1, 1),       # None 本金
        ([100], 0.1, 1),      # 列表本金
    ],
    ids=["str_principal", "str_rate", "str_years", "none_principal", "list_principal"],
)
def test_calculate_interest_non_numeric_raises_type_error(principal, rate, years):
    with pytest.raises(TypeError):
        calculate_interest(principal, rate, years)
