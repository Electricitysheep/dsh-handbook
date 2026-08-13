#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
verify.py — Verify employees.db after the migration performed by migrate.py.

Checks performed:
  1. Schema matches the specification (column names/types, PRIMARY KEY,
     NOT NULL on name, CHECK constraints present).
  2. Total row count matches the expected count, recomputed *independently*
     from data.csv using the documented skip policy (negative salary,
     invalid department, blank name, duplicate id -> skipped).
  3. id uniqueness: no NULL ids, COUNT(DISTINCT id) == COUNT(*).
  4. Constraint validity over ALL rows:
       - name   NOT NULL / non-blank
       - department in ('engineering','sales','finance','hr','ops')
       - salary is NULL or >= 0
       - is_active in (0, 1) or NULL
       - email is NULL or matches a sane address pattern
       - hire_date is NULL or a real ISO date (YYYY-MM-DD)
       - bonus is NULL or numeric
  5. Spot checks of representative rows (clean rows, cleaned rows, and rows
     that must be ABSENT because they were skipped).

Prints PASS/FAIL per check and a final conclusion; exit code 0 = all passed.
"""

import csv
import re
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
CSV_PATH = BASE_DIR / "data.csv"
DB_PATH = BASE_DIR / "employees.db"

ALLOWED_DEPARTMENTS = {"engineering", "sales", "finance", "hr", "ops"}
EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")

results = []  # (name, ok, detail)


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f"  -- {detail}" if detail else ""))


def expected_inserted_ids(rows):
    """Independently recompute which ids SHOULD be in the DB (skip policy)."""
    ids, seen = [], set()
    for row in rows:
        raw = (row.get("id") or "").strip()
        if not raw.isdigit():
            continue
        rid = int(raw)
        if rid in seen:
            continue  # duplicate -> skipped
        try:
            sal = float(row.get("salary", "").strip().replace(",", ""))
        except ValueError:
            sal = None
        raw_sal = (row.get("salary") or "").strip()
        if raw_sal and sal is not None and sal < 0:
            continue  # negative salary -> skipped
        if (row.get("department") or "").strip().lower() not in ALLOWED_DEPARTMENTS:
            continue  # invalid department -> skipped
        if not (row.get("name") or "").strip():
            continue  # blank name -> skipped
        seen.add(rid)
        ids.append(rid)
    return ids


def read_csv_rows():
    with open(CSV_PATH, newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def main():
    rows = read_csv_rows()
    print("=" * 68)
    print("VERIFICATION  (employees.db after migration)")
    print("=" * 68)

    if not DB_PATH.exists():
        check("database file exists", False, f"{DB_PATH} not found")
        finish()
        return 1

    conn = sqlite3.connect(DB_PATH)
    try:
        # ---- 1. schema ----
        cols = {r[1]: r for r in conn.execute("PRAGMA table_info(employees)")}
        expected_cols = {
            "id": "INTEGER", "name": "TEXT", "department": "TEXT",
            "salary": "REAL", "hire_date": "TEXT", "is_active": "INTEGER",
            "email": "TEXT", "bonus": "REAL",
        }
        ok_schema = set(cols) == set(expected_cols) and all(
            cols[c][2].upper() == t for c, t in expected_cols.items()
        )
        check("schema: columns and types match specification", ok_schema,
              ", ".join(f"{c}:{t}" for c, t in expected_cols.items()))
        pk = [c for c in cols.values() if c[5] > 0]
        check("schema: id is INTEGER PRIMARY KEY", len(pk) == 1 and pk[0][1] == "id")
        check("schema: name is NOT NULL", cols["name"][3] == 1)
        ddl = conn.execute(
            "SELECT sql FROM sqlite_master WHERE type='table' AND name='employees'"
        ).fetchone()[0]
        check("schema: CHECK constraints present",
              "CHECK (department IN" in ddl and "CHECK (salary >= 0)" in ddl,
              ddl.replace("\n", " ")[:160] + "...")

        total = conn.execute("SELECT COUNT(*) FROM employees").fetchone()[0]
        expected_ids = expected_inserted_ids(rows)
        check("row count matches expected",
              total == len(expected_ids),
              f"actual={total}, expected={len(expected_ids)}")

        # ---- 2. id uniqueness ----
        null_ids = conn.execute("SELECT COUNT(*) FROM employees WHERE id IS NULL").fetchone()[0]
        check("no NULL ids", null_ids == 0, f"NULL ids={null_ids}")
        distinct = conn.execute("SELECT COUNT(DISTINCT id) FROM employees").fetchone()[0]
        check("ids unique (COUNT(DISTINCT id) == COUNT(*))",
              distinct == total, f"distinct={distinct}, total={total}")

        actual_ids = sorted(r[0] for r in conn.execute("SELECT id FROM employees"))
        check("inserted id set equals expected id set",
              actual_ids == sorted(expected_ids),
              f"missing={sorted(set(expected_ids) - set(actual_ids))} "
              f"unexpected={sorted(set(actual_ids) - set(expected_ids))}")

        # ---- 3. constraint validity over all rows ----
        bad_name = conn.execute(
            "SELECT COUNT(*) FROM employees WHERE name IS NULL OR trim(name)=''"
        ).fetchone()[0]
        check("constraint: name NOT NULL / non-blank", bad_name == 0, f"violations={bad_name}")

        bad_dept = conn.execute(
            f"SELECT COUNT(*) FROM employees WHERE department NOT IN "
            f"({','.join('?' * len(ALLOWED_DEPARTMENTS))})",
            tuple(sorted(ALLOWED_DEPARTMENTS)),
        ).fetchone()[0]
        check("constraint: department in whitelist", bad_dept == 0, f"violations={bad_dept}")

        bad_sal = conn.execute("SELECT COUNT(*) FROM employees WHERE salary < 0").fetchone()[0]
        check("constraint: salary IS NULL or >= 0", bad_sal == 0, f"violations={bad_sal}")

        bad_act = conn.execute(
            "SELECT COUNT(*) FROM employees WHERE is_active NOT IN (0, 1)"
        ).fetchone()[0]
        check("constraint: is_active in (0, 1) or NULL", bad_act == 0, f"violations={bad_act}")

        all_rows = conn.execute(
            "SELECT id, name, department, salary, hire_date, is_active, email, bonus "
            "FROM employees"
        ).fetchall()
        bad_email = [r[0] for r in all_rows
                     if r[6] is not None and not EMAIL_RE.match(r[6])]
        check("constraint: email NULL or valid pattern", not bad_email, f"violations={bad_email}")

        bad_date = []
        for r in all_rows:
            hd = r[4]
            if hd is None:
                continue
            try:
                if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", hd):
                    raise ValueError
                datetime.strptime(hd, "%Y-%m-%d")
            except ValueError:
                bad_date.append(r[0])
        check("constraint: hire_date NULL or real ISO date", not bad_date, f"violations={bad_date}")

        bad_bonus = [r[0] for r in all_rows
                     if r[7] is not None and not isinstance(r[7], (int, float))]
        check("constraint: bonus NULL or numeric", not bad_bonus, f"violations={bad_bonus}")

        # ---- 4. spot checks ----
        # (id, field, expected) — None expected means SQL NULL; 'ABSENT' means row skipped.
        spot = [
            (1, "name", "Alice Chen"), (1, "department", "sales"),
            (1, "salary", 8350.13), (1, "hire_date", "2022-10-09"),
            (1, "is_active", 1), (1, "email", "alice.chen@example.com"),
            (1, "bonus", 1075.37),
            (3, "salary", 14150.64),        # "14,150.64" -> comma stripped
            (3, "email", None),             # 'carol.wang@example' malformed -> NULL
            (5, "hire_date", None),         # 2024/02/30 not a real date -> NULL
            (5, "is_active", 0),            # 'no' -> 0
            (12, "hire_date", "2024-03-15"),# 15/03/2024 -> ISO
            (12, "salary", 12640.34),       # "12,640.34" -> comma stripped
            (12, "bonus", None),            # empty -> NULL
            (17, "salary", None),           # empty -> NULL
            (22, "email", None),            # 'vince pan@example.com' malformed -> NULL
            (31, "email", None),            # missing -> NULL
            (9, None, "ABSENT"),            # skipped: negative salary
            (40, None, "ABSENT"),           # skipped: department 'marketing'
            (7, "name", "Grace Zhao"),      # first occurrence kept
            (21, "name", "Uma Qiao"),       # first occurrence kept
            ("__no_duplicate_copy__", "name", "Grace Zhao Copy"),   # must be absent
            ("__no_duplicate_copy__", "name", "Vince Pan Copy"),    # must be absent
        ]
        row_by_id = {r[0]: r for r in all_rows}
        spot_fail = []
        for sid, field, expected in spot:
            if expected == "ABSENT":
                if sid in row_by_id:
                    spot_fail.append(f"id {sid} should be ABSENT but is present")
                continue
            if sid == "__no_duplicate_copy__":
                present = any(r[1] == expected for r in all_rows)
                if present:
                    spot_fail.append(f"duplicate-copy name '{expected}' should be absent")
                continue
            rec = row_by_id.get(sid)
            if rec is None:
                spot_fail.append(f"id {sid} missing")
                continue
            idx = {c[1]: i for i, c in enumerate(conn.execute("PRAGMA table_info(employees)"))}
            actual = rec[idx[field]]
            if expected is None:
                if actual is not None:
                    spot_fail.append(f"id {sid} {field}: expected NULL, got {actual!r}")
            elif isinstance(expected, float):
                if actual is None or abs(float(actual) - expected) > 1e-9:
                    spot_fail.append(f"id {sid} {field}: expected {expected}, got {actual!r}")
            elif actual != expected:
                spot_fail.append(f"id {sid} {field}: expected {expected!r}, got {actual!r}")
        check("spot checks: sample row values correct", not spot_fail,
              "; ".join(spot_fail[:6]) if spot_fail else f"{len(spot)} checks passed")

        # ---- 5. department distribution (informational) ----
        dist = dict(conn.execute(
            "SELECT department, COUNT(*) FROM employees GROUP BY department ORDER BY department"
        ).fetchall())
        print(f"INFO department distribution: {dist}")
    finally:
        conn.close()

    finish()
    return 0 if all(r[1] for r in results) else 1


def finish():
    passed = sum(1 for _, ok, _ in results if ok)
    failed = len(results) - passed
    print("-" * 68)
    print(f"CONCLUSION: {passed}/{len(results)} checks passed, {failed} failed "
          f"-> {'VERIFICATION PASSED' if failed == 0 else 'VERIFICATION FAILED'}")
    print("=" * 68)


if __name__ == "__main__":
    sys.exit(main())
