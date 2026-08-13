"""buggy_calculator.py 的完整单元测试。

覆盖每个函数的正常路径、边界情况和异常路径。
运行方式：python -m pytest test_calculator.py -v
"""
import pytest

from buggy_calculator import (
    add,
    subtract,
    multiply,
    divide,
    factorial,
    format_money,
)


# ---------------------------------------------------------------- add

@pytest.mark.parametrize(
    "a, b, expected",
    [
        (1, 2, 3),                 # 正常正整数
        (0, 0, 0),                 # 全零
        (5, 0, 5),                 # 加零
        (-1, -2, -3),              # 双负数
        (-5, 3, -2),               # 一正一负
        (1.5, 2.25, 3.75),         # 浮点数
        (0.1, 0.2, 0.30000000000000004),  # 浮点精度（原始值）
    ],
)
def test_add(a, b, expected):
    assert add(a, b) == expected


def test_add_commutative():
    assert add(7, 9) == add(9, 7)


# ------------------------------------------------------------ subtract

@pytest.mark.parametrize(
    "a, b, expected",
    [
        (5, 3, 2),                 # 正常正整数
        (3, 5, -2),                # 结果为负
        (0, 0, 0),                 # 全零
        (0, 7, -7),                # 零减正数
        (7, 0, 7),                 # 减零
        (-4, -6, 2),               # 双负数
        (5.5, 2.25, 3.25),         # 浮点数
    ],
)
def test_subtract(a, b, expected):
    assert subtract(a, b) == expected


# ------------------------------------------------------------ multiply

@pytest.mark.parametrize(
    "a, b, expected",
    [
        (3, 4, 12),                # 正常正整数
        (-3, 4, -12),              # 一负一正
        (-3, -4, 12),              # 双负
        (0, 5, 0),                 # 乘零
        (1.5, 2, 3.0),             # 浮点数
        (0.5, 0.5, 0.25),          # 小数相乘
    ],
)
def test_multiply(a, b, expected):
    assert multiply(a, b) == expected


# -------------------------------------------------------------- divide

@pytest.mark.parametrize(
    "a, b, expected",
    [
        (10, 2, 5),                # 整除
        (7, 2, 3.5),               # 非整除 → 浮点
        (-6, 3, -2),               # 一负一正
        (6, -3, -2),
        (-6, -3, 2),               # 双负
        (0, 5, 0.0),               # 零除以非零
        (5.0, 2.0, 2.5),           # 浮点数
    ],
)
def test_divide(a, b, expected):
    assert divide(a, b) == expected


@pytest.mark.parametrize("b", [0, 0.0])
def test_divide_by_zero_raises(b):
    """除以零必须抛 ZeroDivisionError，而不是静默返回 0。"""
    with pytest.raises(ZeroDivisionError):
        divide(10, b)


# ------------------------------------------------------------ factorial

@pytest.mark.parametrize(
    "n, expected",
    [
        (0, 1),                    # 边界：0! = 1
        (1, 1),                    # 边界：1! = 1
        (2, 2),
        (3, 6),
        (5, 120),
        (10, 3628800),             # 稍大数值
    ],
)
def test_factorial(n, expected):
    assert factorial(n) == expected


@pytest.mark.parametrize("n", [-1, -5, -100])
def test_factorial_negative_raises(n):
    """负数阶乘必须抛 ValueError，而不是静默返回 -1。"""
    with pytest.raises(ValueError):
        factorial(n)


def test_factorial_non_integer_raises():
    """非整数输入（正数）无法被 range 接受，应抛 TypeError。"""
    with pytest.raises(TypeError):
        factorial(2.5)


# --------------------------------------------------------- format_money

@pytest.mark.parametrize(
    "amount, expected",
    [
        (5, "$5.00"),              # 整数 → 两位小数
        (3.5, "$3.50"),            # 一位小数 → 补零
        (0, "$0.00"),              # 零
        (1234.567, "$1234.57"),    # 四舍五入
        (1234567.891, "$1234567.89"),  # 大数
        (0.1 + 0.2, "$0.30"),      # 浮点累加误差下的四舍五入
        (1, "$1.00"),
    ],
)
def test_format_money(amount, expected):
    assert format_money(amount) == expected


def test_format_money_negative():
    """负数按 Python 格式化为 $-x.xx（保持与 f-string 一致的行为）。"""
    assert format_money(-2.5) == "$-2.50"


def test_format_money_returns_string():
    result = format_money(42)
    assert isinstance(result, str)
    assert result.startswith("$")
