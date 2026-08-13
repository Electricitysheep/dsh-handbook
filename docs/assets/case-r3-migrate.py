#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
migrate.py — Migrate data.csv (synthetic employee data) into SQLite (employees.db).

Data-quality policy (explicit, per requirement #3):

  SKIP-AND-WARN  (rows that cannot be fixed without inventing data, or that would
                  still violate a table constraint after cleaning):
    * negative salary ............... skipped  (would violate CHECK salary >= 0)
    * department not in whitelist ... skipped  (would violate CHECK department IN (...))
    * duplicate id .................. skipped  (second+ occurrence; first one wins)
    * blank name .................... skipped  (name TEXT NOT NULL)
    * blank / non-integer id ........ skipped  (id INTEGER PRIMARY KEY)

  CLEAN-AND-KEEP  (rows where a safe, lossless transformation exists):
    * salary   '12,345.00' ......... -> 12345.00   (strip thousand-separator commas)
    * salary   empty ................ -> NULL
    * is_active yes/no/true/false/1/0 -> 1 / 0     (case-insensitive)
    * hire_date DD/MM/YYYY, YYYY/MM/DD -> YYYY-MM-DD (normalised to ISO, real calendar check)
    * hire_date invalid (2024/02/30) . -> NULL      (row kept, warned)
    * bonus    empty / non-numeric .. -> NULL
    * email    missing / malformed .. -> NULL       (row kept, warned)

Every category is counted and reported in the migration summary printed at the end.
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
DATE_FORMATS = ("%Y-%m-%d", "%d/%m/%Y", "%Y/%m/%d")

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS employees (
    id         INTEGER PRIMARY KEY,
    name       TEXT    NOT NULL,
    department TEXT    CHECK (department IN ('engineering','sales','finance','hr','ops')),
    salary     REAL    CHECK (salary >= 0),
    hire_date  TEXT,
    is_active  INTEGER,
    email      TEXT,
    bonus      REAL
);
"""


def new_stats():
    return {
        "total_rows": 0,
        "inserted": 0,
        "salary_comma": 0,
        "salary_empty": 0,
        "salary_negative": 0,   # -> skipped
        "salary_bad": 0,        # non-numeric -> NULL
        "is_active_raw": {},
        "is_active_unknown": 0,
        "hire_date_convert": 0, # DD/MM/YYYY or YYYY/MM/DD -> ISO
        "hire_date_invalid": 0, # e.g. 2024/02/30 -> NULL
        "hire_date_unparsed": 0,
        "hire_date_empty": 0,
        "bonus_empty": 0,
        "bonus_bad": 0,
        "email_missing": 0,
        "email_invalid": 0,
        "name_blank": 0,
        "skip_duplicate": 0,
        "skip_department": 0,
        "skip_negative_salary": 0,
        "skip_blank_name": 0,
        "skip_bad_id": 0,
        "skip_integrity": 0,
    }


def parse_salary(raw, stats, warnings, line):
    raw = (raw or "").strip()
    if raw == "":
        stats["salary_empty"] += 1
        return None, True
    cleaned = raw.replace(",", "")
    if cleaned != raw:
        stats["salary_comma"] += 1
    try:
        val = float(cleaned)
    except ValueError:
        stats["salary_bad"] += 1
        warnings.append(f"line {line}: salary '{raw}' is not numeric -> NULL")
        return None, True
    if val < 0:
        stats["salary_negative"] += 1
        return val, False  # skip
    return val, True


def parse_is_active(raw, stats, warnings, line):
    v = (raw or "").strip().lower()
    stats["is_active_raw"][v] = stats["is_active_raw"].get(v, 0) + 1
    if v in ("yes", "true", "1"):
        return 1
    if v in ("no", "false", "0"):
        return 0
    stats["is_active_unknown"] += 1
    warnings.append(f"line {line}: is_active '{raw}' unrecognised -> NULL")
    return None


def parse_hire_date(raw, stats, warnings, line):
    raw = (raw or "").strip()
    if raw == "":
        stats["hire_date_empty"] += 1
        return None
    for fmt in DATE_FORMATS:
        try:
            dt = datetime.strptime(raw, fmt)
        except ValueError:
            continue
        if fmt != "%Y-%m-%d":
            stats["hire_date_convert"] += 1
        return dt.strftime("%Y-%m-%d")
    if len(raw) == 10 and raw[4] == "/":
        stats["hire_date_invalid"] += 1
        warnings.append(f"line {line}: hire_date '{raw}' is not a real calendar date -> NULL")
    else:
        stats["hire_date_unparsed"] += 1
        warnings.append(f"line {line}: hire_date '{raw}' unrecognised format -> NULL")
    return None


def parse_bonus(raw, stats, warnings, line):
    raw = (raw or "").strip()
    if raw == "":
        stats["bonus_empty"] += 1
        return None
    try:
        return float(raw)
    except ValueError:
        stats["bonus_bad"] += 1
        warnings.append(f"line {line}: bonus '{raw}' is not numeric -> NULL")
        return None


def parse_email(raw, stats, warnings, line):
    raw = (raw or "").strip()
    if raw == "":
        stats["email_missing"] += 1
        return None
    if not EMAIL_RE.match(raw):
        stats["email_invalid"] += 1
        warnings.append(f"line {line}: email '{raw}' malformed -> NULL")
        return None
    return raw


def main():
    stats = new_stats()
    warnings = []
    skipped = []  # (id, reason)

    with open(CSV_PATH, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    stats["total_rows"] = len(rows)

    # --- fresh, reproducible database -----------------------------------
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute("DROP TABLE IF EXISTS employees")
        conn.execute(CREATE_TABLE_SQL)
        conn.commit()

        seen_ids = set()
        for i, row in enumerate(rows):
            line = i + 2  # 1-based line number inside the CSV (header is line 1)

            raw_id = (row.get("id") or "").strip()
            try:
                rid = int(raw_id)
            except ValueError:
                skipped.append((raw_id, "blank / non-integer id (INTEGER PRIMARY KEY)"))
                stats["skip_bad_id"] += 1
                continue

            # ---- clean first (count every transformation) ----
            name = (row.get("name") or "").strip()
            if name == "":
                stats["name_blank"] += 1
            salary, salary_ok = parse_salary(row.get("salary"), stats, warnings, line)
            is_active = parse_is_active(row.get("is_active"), stats, warnings, line)
            hire_date = parse_hire_date(row.get("hire_date"), stats, warnings, line)
            bonus = parse_bonus(row.get("bonus"), stats, warnings, line)
            email = parse_email(row.get("email"), stats, warnings, line)
            department = (row.get("department") or "").strip().lower()

            # ---- duplicate id: first occurrence wins ----
            if rid in seen_ids:
                skipped.append((rid, f"duplicate id (first occurrence kept; row '{name}')"))
                stats["skip_duplicate"] += 1
                continue
            seen_ids.add(rid)

            # ---- hard constraint checks ----
            if not salary_ok:  # negative salary
                skipped.append((rid, f"salary {row.get('salary')!r} is negative (CHECK salary >= 0)"))
                stats["skip_negative_salary"] += 1
                continue
            if name == "":
                skipped.append((rid, "name is blank (NOT NULL)"))
                stats["skip_blank_name"] += 1
                continue
            if department not in ALLOWED_DEPARTMENTS:
                skipped.append((rid, f"department '{row.get('department')}' not in "
                                     f"('engineering','sales','finance','hr','ops')"))
                stats["skip_department"] += 1
                continue

            # ---- insert (safety net: catch any unexpected constraint error) ----
            try:
                conn.execute(
                    "INSERT INTO employees (id, name, department, salary, hire_date,"
                    " is_active, email, bonus) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (rid, name, department, salary, hire_date, is_active, email, bonus),
                )
            except sqlite3.IntegrityError as exc:
                skipped.append((rid, f"integrity error: {exc}"))
                stats["skip_integrity"] += 1
                continue
            stats["inserted"] += 1

        conn.commit()
        db_count = conn.execute("SELECT COUNT(*) FROM employees").fetchone()[0]
    finally:
        conn.close()

    # ---- summary --------------------------------------------------------
    iso = stats["is_active_raw"]
    iso_breakdown = ", ".join(f"{k}={iso[k]}" for k in sorted(iso)) if iso else "none"
    print("=" * 68)
    print("MIGRATION SUMMARY  (data.csv -> employees.db)")
    print("=" * 68)
    print(f"CSV source            : {CSV_PATH.name}")
    print(f"SQLite database       : {DB_PATH.name}")
    print(f"Total CSV rows read   : {stats['total_rows']}")
    print(f"Rows inserted         : {stats['inserted']}")
    print(f"Rows skipped          : {stats['total_rows'] - stats['inserted']}")
    print(f"Rows confirmed in DB  : {db_count}")
    print()
    print("-- Cleaning applied (CLEAN-AND-KEEP) ----------------------------")
    print(f"salary  thousand-separator commas removed      : {stats['salary_comma']}")
    print(f"salary  empty -> NULL                          : {stats['salary_empty']}")
    print(f"salary  non-numeric -> NULL                    : {stats['salary_bad']}")
    print(f"is_active normalised to 0/1 (raw breakdown: {iso_breakdown}) : "
          f"{sum(iso.values())}")
    print(f"hire_date DD/MM/YYYY or YYYY/MM/DD -> ISO      : {stats['hire_date_convert']}")
    print(f"hire_date invalid date -> NULL                 : {stats['hire_date_invalid']}")
    print(f"hire_date unrecognised -> NULL                 : {stats['hire_date_unparsed']}")
    print(f"bonus    empty -> NULL                         : {stats['bonus_empty']}")
    print(f"bonus    non-numeric -> NULL                   : {stats['bonus_bad']}")
    print(f"email    missing -> NULL                       : {stats['email_missing']}")
    print(f"email    malformed -> NULL                     : {stats['email_invalid']}")
    print()
    print("-- Rows skipped (SKIP-AND-WARN) --------------------------------")
    print(f"negative salary (CHECK salary >= 0)            : {stats['skip_negative_salary']}")
    print(f"department outside whitelist (CHECK)           : {stats['skip_department']}")
    print(f"duplicate id (PRIMARY KEY, first kept)         : {stats['skip_duplicate']}")
    print(f"blank name (NOT NULL)                          : {stats['skip_blank_name']}")
    print(f"blank / non-integer id                         : {stats['skip_bad_id']}")
    print(f"unexpected integrity error                     : {stats['skip_integrity']}")
    if skipped:
        print("  skipped rows:")
        for rid, reason in skipped:
            print(f"    - id={rid!r}: {reason}")
    if warnings:
        print()
        print("-- Warnings (non-fatal, cleaned to NULL) ------------------------")
        for w in warnings:
            print(f"  WARN {w}")
    print("=" * 68)
    return 0


if __name__ == "__main__":
    sys.exit(main())
