"""data_utils — 5 个合成工具函数（供单测生成案例使用）。

覆盖字符串解析、列表分块、数值递推、邮箱校验、金融计算五个领域，
每个函数都包含刻意设计的边界与异常语义，供单元测试充分覆盖。
"""

import re


def parse_duration(s: str) -> int:
    """解析紧凑时长字符串为秒数。

    支持单位：d(天) h(小时) m(分钟) s(秒)，可组合如 '1h30m'、'2d'、'1d12h'。
    - 空字符串 / None / 非法格式（如 '1h30'、'abc'、'10'）→ ValueError
    - 大小写不敏感（'1H30M' 合法），返回 int 秒数
    """
    if s is None:
        raise ValueError("duration must not be None")
    s = str(s).strip().lower()
    if not s:
        raise ValueError("duration must not be empty")
    units = {"d": 86400, "h": 3600, "m": 60, "s": 1}
    total = 0
    pos = 0
    for m in re.finditer(r"(\d+)([dhms])", s):
        if m.start() != pos:
            raise ValueError(f"invalid duration format: {s!r}")
        total += int(m.group(1)) * units[m.group(2)]
        pos = m.end()
    if pos != len(s):
        raise ValueError(f"invalid duration format: {s!r}")
    return total


def chunk_list(items: list, size: int) -> list:
    """将列表按 size 分块，返回子列表的列表。

    - size <= 0 → ValueError
    - size 非 int（含 bool）→ TypeError
    - size > len(items) → 返回单个完整块；空列表 → []
    """
    if isinstance(size, bool) or not isinstance(size, int):
        raise TypeError("size must be an int")
    if size <= 0:
        raise ValueError("size must be > 0")
    return [items[i:i + size] for i in range(0, len(items), size)]


def fibonacci(n: int) -> int:
    """返回第 n 个斐波那契数（0 起始：fib(0)=0, fib(1)=1）。

    - n 非 int（含 bool）→ TypeError
    - n < 0 → ValueError
    - 迭代实现，无递归深度限制，大 n 亦可计算
    """
    if isinstance(n, bool) or not isinstance(n, int):
        raise TypeError("n must be an int")
    if n < 0:
        raise ValueError("n must be >= 0")
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a


_EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")


def is_valid_email(email: str) -> bool:
    """基础邮箱格式校验（宽松正则）。

    - 非字符串输入 → False（不抛异常）
    - 空串、无 '@'、多个 '@'、local/domain 为空、无 TLD（如 'a@b'）、
      含空白字符（如 'a b@c.com'）、TLD 过短（'a@b.c'）→ False
    - 合法格式（含子域、大写域名）→ True
    """
    if not isinstance(email, str):
        return False
    return bool(_EMAIL_RE.match(email))


def calculate_interest(principal: float, rate: float, years: float) -> float:
    """复利计算：principal * (1 + rate) ** years。

    - principal / rate / years < 0 → ValueError
    - years 支持小数（如 0.5），返回 float（可能因浮点产生精度差异，测试用 approx）
    - 极大数值可能溢出为 inf（边界行为，测试应覆盖）
    """
    if principal < 0:
        raise ValueError("principal must be >= 0")
    if rate < 0:
        raise ValueError("rate must be >= 0")
    if years < 0:
        raise ValueError("years must be >= 0")
    return principal * (1 + rate) ** years
