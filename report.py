"""Checks the risk register and builds the KRI dashboard.

    python report.py                      # report as of today
    python report.py --as-of 2026-10-28   # report as of a set date
    python report.py --strict             # exit with an error if the data has problems

Writes to reports/: dashboard.html, risk_summary.md and owner_followups.csv
"""

import argparse
import csv
import sys
from datetime import date
from pathlib import Path

from grc import checks, dashboard, data, kri

ROOT = Path(__file__).resolve().parent


def write_followups(path, results):
    """One row per action an owner needs to chase: overdue first, then due in the next 14 days."""
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["owner", "action_id", "risk_id", "action", "due_date", "status", "flag", "days"])
        rows = [(a, "Overdue", a["days_overdue"]) for a in results["overdue_actions"]]
        rows += [(a, "Due soon", a["days_left"]) for a in results["due_soon_actions"]]
        rows.sort(key=lambda item: (item[0]["owner"], item[1] != "Overdue", item[0]["due_date"]))
        for a, flag, days in rows:
            writer.writerow([a["owner"], a["action_id"], a["risk_id"], a["action"], a["due_date"], a["status"], flag, days])
    return len(rows)


def main():
    parser = argparse.ArgumentParser(description="Check the risk register and build the KRI dashboard.")
    parser.add_argument("--register", default=ROOT / "data" / "risk_register.csv", type=Path)
    parser.add_argument("--actions", default=ROOT / "data" / "remediation_actions.csv", type=Path)
    parser.add_argument("--out", default=ROOT / "reports", type=Path)
    parser.add_argument("--as-of", default=date.today().isoformat(), help="report date, YYYY-MM-DD (default: today)")
    parser.add_argument("--strict", action="store_true", help="exit with code 1 if any data errors are found")
    args = parser.parse_args()

    try:
        as_of = date.fromisoformat(args.as_of)
    except ValueError:
        parser.error("--as-of must be a date like 2026-10-28")

    risks = data.read_csv(args.register)
    actions = data.read_csv(args.actions)

    issues = checks.check_all(risks, actions, as_of)
    errors = [i for i in issues if i.severity == "error"]
    warnings = [i for i in issues if i.severity == "warning"]

    con = data.build_db(risks, actions)
    results = kri.run(con, data.load_queries(), as_of)
    indicators = kri.build(results)

    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "dashboard.html").write_text(
        dashboard.render_html(results, indicators, issues, as_of, len(risks), len(actions)), encoding="utf-8")
    (args.out / "risk_summary.md").write_text(
        dashboard.render_markdown(results, indicators, issues, as_of, len(risks), len(actions)), encoding="utf-8")
    n_followups = write_followups(args.out / "owner_followups.csv", results)

    print(f"Risk report as of {as_of}: {len(risks)} risks, {len(actions)} actions")
    print(f"Data checks: {len(errors)} errors, {len(warnings)} warnings")
    for issue in issues:
        print(f"  {issue.severity.upper():7} {issue.record} {issue.field}: {issue.problem}")
    print()
    for k in indicators:
        print(f"  [{k.status:5}] {k.name}: {k.value} (target {k.target})")
    print()
    print(f"Wrote {args.out / 'dashboard.html'}")
    print(f"Wrote {args.out / 'risk_summary.md'}")
    print(f"Wrote {args.out / 'owner_followups.csv'} ({n_followups} follow-ups)")

    if args.strict and errors:
        sys.exit(1)


if __name__ == "__main__":
    main()
