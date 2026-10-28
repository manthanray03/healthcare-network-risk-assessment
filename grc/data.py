"""Reads the CSV files and loads them into an in-memory SQLite database."""

import csv
import re
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCHEMA = ROOT / "sql" / "schema.sql"
QUERIES = ROOT / "sql" / "kri_queries.sql"

RISK_INT_FIELDS = [
    "inherent_likelihood", "inherent_impact",
    "residual_likelihood", "residual_impact",
    "target_likelihood", "target_impact",
]


def read_csv(path):
    with open(path, newline="", encoding="utf-8") as f:
        return [{k: (v or "").strip() for k, v in row.items()} for row in csv.DictReader(f)]


def _to_int(text):
    return int(text) if text.isdigit() else None


def build_db(risks, actions, schema_path=SCHEMA):
    con = sqlite3.connect(":memory:")
    con.row_factory = sqlite3.Row
    con.executescript(Path(schema_path).read_text(encoding="utf-8"))

    risk_cols = [
        "risk_id", "title", "asset", "threat", "vulnerability", "existing_controls",
        "csf_function", "csf_refs", "iso_refs", *RISK_INT_FIELDS,
        "treatment", "owner", "status", "last_reviewed", "accepted_by", "accepted_on",
    ]
    for r in risks:
        values = [_to_int(r.get(c, "")) if c in RISK_INT_FIELDS else (r.get(c) or None) for c in risk_cols]
        # OR IGNORE: a duplicate id is reported by checks.py, so skip it here instead of crashing
        con.execute(
            f"INSERT OR IGNORE INTO risks ({', '.join(risk_cols)}) VALUES ({', '.join('?' * len(risk_cols))})",
            values,
        )

    action_cols = ["action_id", "risk_id", "action", "owner", "due_date", "status", "completed_date"]
    for a in actions:
        con.execute(
            f"INSERT OR IGNORE INTO actions ({', '.join(action_cols)}) VALUES ({', '.join('?' * len(action_cols))})",
            [a.get(c) or None for c in action_cols],
        )
    con.commit()
    return con


def load_queries(path=QUERIES):
    """Splits kri_queries.sql into {name: sql} using the '-- name:' lines."""
    text = Path(path).read_text(encoding="utf-8")
    queries = {}
    for block in re.split(r"^-- name:\s*", text, flags=re.MULTILINE)[1:]:
        name, _, sql = block.partition("\n")
        queries[name.strip()] = sql.strip()
    return queries
