#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
log_analyzer.py — 仅使用 Python 标准库的日志分析脚本（零第三方依赖）。

功能:
  1. 统计日志总行数与各级别(DEBUG/INFO/WARN/ERROR)计数及占比
  2. 计算错误率(ERROR 数 / 总行数)
  3. 按错误类型前缀(如 DatabaseError、ConnectionTimeout)归类 TOP 错误类型
  4. 按小时统计错误趋势
  5. 识别异常模式: 用滑动时间窗口找出错误集中爆发的时间窗口

用法:
  python log_analyzer.py --log app.log --output log-report.md

参数:
  --log <path>            日志文件路径(默认 app.log)
  --output <path>         Markdown 报告输出路径(默认 log-report.md)
  --window-minutes <n>    爆发检测滑动窗口时长(分钟, 默认 10)
  --burst-min-errors <n>  爆发窗口最少错误数下限(默认 3)
  --burst-multiplier <m>  爆发窗口错误数需达到期望值的倍数(默认 2.0)
  --top-n <n>             TOP 错误类型数量(默认 10)
"""

import argparse
import bisect
import datetime as dt
import math
import re
import sys
from collections import Counter, namedtuple
from pathlib import Path

Entry = namedtuple("Entry", ["ts", "level", "component", "message"])

# 形如: 2026-08-13 09:00:10,461 [INFO] [db] message
LINE_RE = re.compile(
    r"^(?P<ts>\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2}),\d{3}\s*"
    r"\[(?P<level>[A-Za-z]+)\]\s*\[(?P<component>[^\]]+)\]\s*(?P<message>.*)$"
)
LEVEL_ORDER = ("DEBUG", "INFO", "WARN", "ERROR")
TS_FMT = "%Y-%m-%d %H:%M:%S"


def parse_log(path):
    """解析日志文件，返回 (entries, skipped)。无法匹配格式的行计入 skipped。"""
    entries, skipped = [], 0
    # utf-8-sig: 自动去除文件开头的 UTF-8 BOM，避免首行被误判为格式错误
    with open(path, "r", encoding="utf-8-sig", errors="replace") as fh:
        for raw in fh:
            line = raw.rstrip("\r\n")
            m = LINE_RE.match(line)
            if not m:
                skipped += 1
                continue
            try:
                ts = dt.datetime.strptime(m.group("ts").replace("T", " "), TS_FMT)
            except ValueError:
                skipped += 1
                continue
            entries.append(Entry(
                ts=ts,
                level=m.group("level").upper(),
                component=m.group("component"),
                message=m.group("message"),
            ))
    return entries, skipped


def error_type(message):
    """按冒号前的类型前缀归类，如 'DatabaseError: ...' -> 'DatabaseError'。"""
    if ":" in message:
        head = message.split(":", 1)[0].strip()
        if head:
            return head
    tokens = message.split()
    return tokens[0] if tokens else "(empty)"


def detect_bursts(error_times, span_seconds, window_minutes, min_errors, multiplier):
    """
    滑动窗口爆发检测。

    对每个错误时间点 t0, 统计 [t0, t0 + window] 内的错误数;
    只有当错误数 >= max(min_errors, ceil(multiplier * 期望值)) 时视为爆发候选窗口;
    对互相重叠的候选窗口去重(区间调度: 优先保留错误数更多、开始更早的窗口)。

    返回 (bursts, threshold, expected)。
    bursts: [(count, start, end), ...] 按开始时间升序。
    """
    if not error_times:
        return [], 0, 0.0
    times = sorted(error_times)
    window = dt.timedelta(minutes=window_minutes)
    expected = len(times) * window.total_seconds() / span_seconds if span_seconds > 0 else 0.0
    threshold = max(min_errors, int(math.ceil(multiplier * expected)))

    candidates = []
    for i, t0 in enumerate(times):
        t1 = t0 + window
        j = bisect.bisect_right(times, t1)
        cnt = j - i
        if cnt >= threshold:
            candidates.append((cnt, t0, t1))

    selected = []
    for cnt, start, end in sorted(candidates, key=lambda x: (-x[0], x[1])):
        if any(not (end <= s2 or start >= e2) for _, s2, e2 in selected):
            continue
        selected.append((cnt, start, end))
    selected.sort(key=lambda x: x[1])
    return selected, threshold, expected


def pct(num, den):
    """百分比格式化，保留 1 位小数。"""
    return f"{num / den * 100:.1f}%" if den else "0.0%"


def bar(count, max_count, width=24):
    """生成与 count/max_count 成比例的 '#' 分布图。"""
    if max_count <= 0 or count <= 0:
        return ""
    return "#" * max(1, round(width * count / max_count))


def analyze(entries, args):
    """汇总统计，返回包含全部结果的 dict。"""
    total = len(entries)
    level_counts = Counter(e.level for e in entries)
    errors = [e for e in entries if e.level == "ERROR"]
    error_count = len(errors)

    type_counter = Counter(error_type(e.message) for e in errors)
    hour_total = Counter(e.ts.hour for e in entries)
    hour_error = Counter(e.ts.hour for e in errors)
    hours = sorted(set(hour_total) | set(hour_error))

    if entries:
        span_start = min(e.ts for e in entries)
        span_end = max(e.ts for e in entries)
        span_seconds = max((span_end - span_start).total_seconds(), 1.0)
    else:
        span_start = span_end = None
        span_seconds = 0.0

    error_times = [e.ts for e in errors]
    bursts, burst_threshold, burst_expected = detect_bursts(
        error_times, span_seconds, args.window_minutes, args.burst_min_errors, args.burst_multiplier
    )

    # 小时级异常: 错误数 >= 每小时均值的 2 倍(且至少 2 条)
    hour_anomalies = []
    if hours and error_count:
        hour_mean = error_count / len(hours)
        for h in hours:
            if hour_error[h] >= max(2, 2 * hour_mean):
                hour_anomalies.append(h)

    burst_details = []
    for cnt, start, end in bursts:
        in_win = Counter(error_type(e.message) for e in errors if start <= e.ts <= end)
        burst_details.append({
            "start": start,
            "end": end,
            "count": cnt,
            "top": in_win.most_common(3),
        })

    return {
        "total": total,
        "level_counts": level_counts,
        "error_count": error_count,
        "type_counter": type_counter,
        "hours": hours,
        "hour_total": hour_total,
        "hour_error": hour_error,
        "span_start": span_start,
        "span_end": span_end,
        "bursts": bursts,
        "burst_threshold": burst_threshold,
        "burst_expected": burst_expected,
        "hour_anomalies": hour_anomalies,
        "burst_details": burst_details,
    }


def print_summary(stats, skipped, args):
    """在控制台打印统计摘要。"""
    s = stats
    print("=" * 48)
    print("日志分析摘要 (log_analyzer.py)")
    print("=" * 48)
    print(f"日志文件     : {args.log}")
    if s["span_start"]:
        print(f"时间范围     : {s['span_start']:%Y-%m-%d %H:%M:%S} ~ {s['span_end']:%Y-%m-%d %H:%M:%S}")
    print(f"总行数       : {s['total']} (解析失败/跳过: {skipped})")
    level_str = "  ".join(
        f"{lv}={s['level_counts'].get(lv, 0)}({pct(s['level_counts'].get(lv, 0), s['total'])})"
        for lv in LEVEL_ORDER
    )
    print(f"级别分布     : {level_str}")
    print(f"错误率       : {s['error_count']} / {s['total']} = {pct(s['error_count'], s['total'])}")
    top_types = ", ".join(f"{t}={c}" for t, c in s["type_counter"].most_common(args.top_n))
    print(f"TOP 错误类型 : {top_types}")
    hour_str = "  ".join(f"{h:02d}:00={s['hour_error'].get(h, 0)}" for h in s["hours"])
    print(f"按小时错误   : {hour_str}")
    if s["bursts"]:
        burst_str = "  ".join(
            f"{b['start']:%H:%M:%S}~{b['end']:%H:%M:%S}({b['count']}条)" for b in s["burst_details"]
        )
        print(f"异常爆发窗口 : {burst_str}")
    else:
        print("异常爆发窗口 : 未检测到")
    print(f"分析报告     : {args.output}")
    print("=" * 48)


def write_report(stats, skipped, args, out_path):
    """生成 Markdown 分析报告。"""
    s = stats
    now = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    L = []
    A = L.append

    A("# 应用日志分析报告")
    A("")
    A(f"> 生成工具: `log_analyzer.py`（仅使用 Python 标准库，零第三方依赖）  ")
    A(f"> 分析时间: {now}  ")
    A(f"> 日志文件: `{args.log}`  ")
    A("")

    A("## 0. 概览")
    A("")
    A("| 项目 | 值 |")
    A("| --- | --- |")
    A(f"| 日志文件 | `{args.log}` |")
    A(f"| 总行数 | {s['total']} |")
    A(f"| 解析失败/跳过行数 | {skipped} |")
    if s["span_start"]:
        A(f"| 时间范围 | {s['span_start']:%Y-%m-%d %H:%M:%S} ~ {s['span_end']:%Y-%m-%d %H:%M:%S} |")
    A(f"| ERROR 行数 | {s['error_count']} |")
    A(f"| 错误率 | {s['error_count']} / {s['total']} = **{pct(s['error_count'], s['total'])}** |")
    A("")

    A("## 1. 日志级别分布")
    A("")
    A("| 级别 | 数量 | 占比 |")
    A("| --- | ---: | ---: |")
    for lv in list(LEVEL_ORDER) + sorted(set(s["level_counts"]) - set(LEVEL_ORDER)):
        cnt = s["level_counts"].get(lv, 0)
        A(f"| {lv} | {cnt} | {pct(cnt, s['total'])} |")
    A("")

    A("## 2. 错误率")
    A("")
    A(f"- ERROR 行数: {s['error_count']}")
    A(f"- 总行数: {s['total']}")
    A(f"- **错误率 = ERROR 数 / 总行数 = {pct(s['error_count'], s['total'])}**")
    A("")

    A("## 3. TOP 错误类型")
    A("")
    A("按错误消息中冒号前的类型前缀归类（如 `DatabaseError: ...` → `DatabaseError`）。")
    A("")
    A("| 排名 | 错误类型 | 数量 | 占 ERROR 比例 |")
    A("| ---: | --- | ---: | ---: |")
    for i, (t, c) in enumerate(s["type_counter"].most_common(args.top_n), 1):
        A(f"| {i} | `{t}` | {c} | {pct(c, s['error_count'])} |")
    if not s["type_counter"]:
        A("| - | 无 ERROR 日志 | 0 | - |")
    A("")

    A("## 4. 按小时错误趋势")
    A("")
    A("| 小时 | 总行数 | ERROR 数 | 错误率 | 分布图（# 与最大小时错误数成比例） |")
    A("| --- | ---: | ---: | ---: | --- |")
    max_h = max((s["hour_error"].get(h, 0) for h in s["hours"]), default=0)
    for h in s["hours"]:
        et = s["hour_error"].get(h, 0)
        tt = s["hour_total"].get(h, 0)
        A(f"| {h:02d}:00 | {tt} | {et} | {pct(et, tt)} | {bar(et, max_h)} |")
    A("")

    A("## 5. 异常模式：错误爆发时间窗口")
    A("")
    A(f"判定规则：以 {args.window_minutes:g} 分钟为滑动窗口，窗口内错误数 ≥ max("
      f"{args.burst_min_errors}, {args.burst_multiplier:g} × 期望值 {s['burst_expected']:.2f}) = "
      f"{s['burst_threshold']} 视为爆发窗口；互相重叠的窗口仅保留错误数最多者。")
    A("")
    if s["bursts"]:
        A("| # | 窗口开始 | 窗口结束 | 错误数 | 占 ERROR 比例 | 窗口内主要错误类型 |")
        A("| ---: | --- | --- | ---: | ---: | --- |")
        for i, b in enumerate(s["burst_details"], 1):
            top = ", ".join(f"`{t}`×{c}" for t, c in b["top"]) or "-"
            A(f"| {i} | {b['start']:%Y-%m-%d %H:%M:%S} | {b['end']:%Y-%m-%d %H:%M:%S} | "
              f"{b['count']} | {pct(b['count'], s['error_count'])} | {top} |")
    else:
        A("未检测到满足条件的错误爆发窗口。")
    A("")
    if s["hour_anomalies"]:
        mean = s["error_count"] / len(s["hours"]) if s["hours"] else 0
        hrs = ", ".join(f"{h:02d}:00" for h in s["hour_anomalies"])
        A(f"小时级观察：{hrs} 的错误数达到每小时均值（{mean:.1f} 条）的 2 倍以上，属于错误集中时段。")
        A("")

    A("## 6. 结论与建议")
    A("")
    err_ratio = s["error_count"] / s["total"] if s["total"] else 0
    A(f"- 本日志共 {s['total']} 行，错误率 {pct(s['error_count'], s['total'])}。"
      + ("错误率偏高（>5%），建议优先处理。" if err_ratio > 0.05 else "错误率处于可接受范围。"))
    if s["type_counter"]:
        top_t, top_c = s["type_counter"].most_common(1)[0]
        A(f"- 最频繁错误类型为 `{top_t}`（{top_c} 条，占 ERROR 的 "
          f"{pct(top_c, s['error_count'])}），建议优先排查。")
    if s["bursts"]:
        b = s["burst_details"][0]
        A(f"- 错误最集中的时段为 {b['start']:%Y-%m-%d %H:%M:%S} ~ {b['end']:%Y-%m-%d %H:%M:%S}"
          f"（{b['count']} 条，占 ERROR 的 {pct(b['count'], s['error_count'])}），"
          "建议检查该窗口对应的发布、任务或依赖服务状态。")
    if s["hours"] and s["error_count"]:
        top_h = max(s["hours"], key=lambda h: s["hour_error"].get(h, 0))
        A(f"- 错误集中在 {top_h:02d}:00 时段（{s['hour_error'].get(top_h, 0)} 条，"
          f"占 ERROR 的 {pct(s['hour_error'].get(top_h, 0), s['error_count'])}）。")
    A("")

    A("## 附录：方法与复现")
    A("")
    A("- 解析规则：`YYYY-MM-DD HH:MM:SS,mmm [LEVEL] [component] message`（标准库正则）。")
    A("- 错误类型归类：取错误消息中冒号 `:` 前的前缀作为类型；无冒号时取首个空白分隔词。")
    A("- 爆发检测：滑动窗口时长、最少错误数、期望倍数均可通过命令行参数调整，默认 "
      f"{args.window_minutes:g} 分钟 / {args.burst_min_errors} 条 / {args.burst_multiplier:g} 倍。")
    A("- 复现命令：")
    A("")
    A("```bash")
    A(f"python log_analyzer.py --log {args.log} --output {args.output}")
    A("```")
    A("")
    A("- 依赖：仅 Python 标准库（`argparse`/`bisect`/`collections`/`datetime`/`math`/`re`/`pathlib`），"
      "无需安装任何第三方包；相同输入下统计结果完全确定。")
    A("")

    out_path.write_text("\n".join(L), encoding="utf-8")


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="零第三方依赖的日志分析脚本：统计级别分布、错误率、错误类型、小时趋势并识别错误爆发窗口。"
    )
    parser.add_argument("--log", default="app.log", help="日志文件路径（默认: app.log）")
    parser.add_argument("--output", default="log-report.md", help="Markdown 报告输出路径（默认: log-report.md）")
    parser.add_argument("--window-minutes", type=float, default=10.0,
                        help="爆发检测滑动窗口时长（分钟，默认 10）")
    parser.add_argument("--burst-min-errors", type=int, default=3,
                        help="爆发窗口最少错误数下限（默认 3）")
    parser.add_argument("--burst-multiplier", type=float, default=2.0,
                        help="爆发窗口错误数需达到期望值的倍数（默认 2.0）")
    parser.add_argument("--top-n", type=int, default=10, help="TOP 错误类型数量（默认 10）")
    args = parser.parse_args(argv)

    if args.window_minutes <= 0 or args.burst_min_errors < 1 or args.burst_multiplier < 1:
        print("[错误] 参数不合法: --window-minutes>0, --burst-min-errors>=1, --burst-multiplier>=1",
              file=sys.stderr)
        return 2

    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass

    log_path = Path(args.log)
    if not log_path.is_file():
        print(f"[错误] 日志文件不存在: {log_path}", file=sys.stderr)
        return 2

    entries, skipped = parse_log(log_path)
    if not entries:
        print("[警告] 未解析到任何符合格式的日志行，无法分析。", file=sys.stderr)
        return 1

    stats = analyze(entries, args)
    print_summary(stats, skipped, args)

    out_path = Path(args.output)
    write_report(stats, skipped, args, out_path)
    print(f"[完成] 分析报告已生成: {out_path.resolve()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
