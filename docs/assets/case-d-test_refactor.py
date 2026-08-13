# -*- coding: utf-8 -*-
"""
test_refactor.py
================
对比 legacy_orders.py（过程式）与 orders_refactored.py（面向对象重构版）的行为一致性。

覆盖内容：
1. format_report() 输出逐字符一致（固定时间戳后比较）
2. export_json() 导出结果一致（原始文本 + 解析后的数据）
3. 各查询函数返回结果一致（get_customer_orders / get_product_sales /
   get_region_summary / get_pending_orders / calc_order_total 边界情况）
4. 以脚本方式整体运行两者，对比生成的 report.txt（忽略时间戳）与 orders.json

测试结果追加写入同目录 case4-output.txt。
"""

import io
import json
import os
import re
import shutil
import subprocess
import sys
import traceback
from contextlib import redirect_stdout
from datetime import datetime

import legacy_orders
import orders_refactored

# 报告中包含实时时间戳，比较时统一归一化
TS_RE = re.compile(r"^生成时间: .*$", re.MULTILINE)

# 临时目录建在工作区内（沙箱只允许写工作区文件）
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_TMP_BASE = os.path.join(_SCRIPT_DIR, ".test_tmp")


class _FakeDatetime:
    """固定 now()，使 format_report() 中的时间戳可确定性比较。"""

    FIXED = datetime(2024, 8, 10, 12, 30, 0)

    @classmethod
    def now(cls):
        return cls.FIXED


_results = []
_passed = 0
_total = 0


def check(name, ok, detail=""):
    global _passed, _total
    _total += 1
    if ok:
        _passed += 1
    line = f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" | {detail}" if detail else "")
    _results.append(line)
    print(line)


def _first_diff(a, b):
    la, lb = a.splitlines(), b.splitlines()
    for i in range(max(len(la), len(lb))):
        x = la[i] if i < len(la) else "<EOF>"
        y = lb[i] if i < len(lb) else "<EOF>"
        if x != y:
            return f"第 {i + 1} 行: legacy={x!r} ref={y!r}"
    return f"行数不同: legacy={len(la)} ref={len(lb)}"


def _run():
    # ---- 0) 加载数据 ----
    legacy_orders.load_data()
    orders_refactored.load_data()

    # ---- 1) format_report() 对比（固定时间戳） ----
    old_legacy_dt, old_ref_dt = legacy_orders.datetime, orders_refactored.datetime
    try:
        legacy_orders.datetime = _FakeDatetime
        orders_refactored.datetime = _FakeDatetime
        legacy_report = legacy_orders.format_report()
        ref_report = orders_refactored.format_report()
    finally:
        legacy_orders.datetime = old_legacy_dt
        orders_refactored.datetime = old_ref_dt

    same_report = legacy_report == ref_report
    check("format_report() 输出完全一致", same_report,
          "" if same_report else _first_diff(legacy_report, ref_report))

    # ---- 2) export_json() 对比 ----
    # 注意：不用 tempfile.mkdtemp/TemporaryDirectory（其 0700 目录 ACL 在沙箱下不可写），
    # 改用手动 os.makedirs 建目录（继承正常 ACL）并手动清理。
    export_tmp = os.path.join(_TMP_BASE, "export_cmp")
    shutil.rmtree(export_tmp, ignore_errors=True)
    os.makedirs(export_tmp, exist_ok=True)
    try:
        leg_path = os.path.join(export_tmp, "legacy_orders.json")
        ref_path = os.path.join(export_tmp, "refactored_orders.json")
        with redirect_stdout(io.StringIO()):
            legacy_orders.export_json(leg_path)
            orders_refactored.export_json(ref_path)
        with open(leg_path, "r", encoding="utf-8") as f:
            leg_text = f.read()
        with open(ref_path, "r", encoding="utf-8") as f:
            ref_text = f.read()
        check("export_json() 文本完全一致", leg_text == ref_text)
        check("export_json() 解析后数据一致", json.loads(leg_text) == json.loads(ref_text))
    finally:
        shutil.rmtree(export_tmp, ignore_errors=True)

    # ---- 3) 查询函数对比 ----
    for cid in legacy_orders.customers:
        check(f"get_customer_orders({cid}) 一致",
              legacy_orders.get_customer_orders(cid) == orders_refactored.get_customer_orders(cid))
    for pid in legacy_orders.products:
        check(f"get_product_sales({pid}) 一致",
              legacy_orders.get_product_sales(pid) == orders_refactored.get_product_sales(pid))
    check("get_region_summary() 一致",
          legacy_orders.get_region_summary() == orders_refactored.get_region_summary())
    leg_pending = legacy_orders.get_pending_orders()
    ref_pending = [o.to_dict() for o in orders_refactored.get_pending_orders()]
    check("get_pending_orders() 一致（序列化后）", leg_pending == ref_pending)
    check("calc_order_total(未知ID) 均返回 0.0",
          legacy_orders.calc_order_total("NOPE") == orders_refactored.calc_order_total("NOPE") == 0.0)

    # ---- 4) 以脚本方式整体运行，对比产物 ----
    run_tmp = os.path.join(_TMP_BASE, "run_cmp")
    shutil.rmtree(run_tmp, ignore_errors=True)
    os.makedirs(run_tmp, exist_ok=True)
    try:
        outputs = {}
        for key, script in (("legacy", "legacy_orders.py"), ("refactored", "orders_refactored.py")):
            subprocess.run(
                [sys.executable, os.path.join(_SCRIPT_DIR, script)],
                cwd=run_tmp, check=True,
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            )
            with open(os.path.join(run_tmp, "report.txt"), "r", encoding="utf-8") as f:
                report_text = f.read()
            with open(os.path.join(run_tmp, "orders.json"), "r", encoding="utf-8") as f:
                json_data = json.load(f)
            outputs[key] = {
                "report": TS_RE.sub("生成时间: <TS>", report_text),
                "json": json_data,
            }
        check("脚本整体运行: report.txt 一致（忽略时间戳）",
              outputs["legacy"]["report"] == outputs["refactored"]["report"])
        check("脚本整体运行: orders.json 一致",
              outputs["legacy"]["json"] == outputs["refactored"]["json"])
    finally:
        shutil.rmtree(run_tmp, ignore_errors=True)

    # ---- 5) 汇总并追加写入 case4-output.txt ----
    output_path = os.path.join(_SCRIPT_DIR, "case4-output.txt")
    with open(output_path, "a", encoding="utf-8") as f:
        f.write("\n")
        f.write("=== CASE4 REFACTOR TEST START ===\n")
        f.write(f"运行时间: {datetime.now().isoformat()}\n")
        f.write("被测模块: legacy_orders.py vs orders_refactored.py\n")
        for line in _results:
            f.write(line + "\n")
        f.write(f"结果: {_passed}/{_total} 项通过\n")
        f.write("结论: 重构前后行为完全一致\n" if _passed == _total else "结论: 存在不一致，请检查重构\n")
        f.write("=== CASE4 REFACTOR TEST END ===\n")

    # 清理工作区内的临时目录
    shutil.rmtree(_TMP_BASE, ignore_errors=True)

    return _passed == _total


def main():
    try:
        ok = _run()
    except Exception:
        traceback.print_exc()
        ok = False
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
