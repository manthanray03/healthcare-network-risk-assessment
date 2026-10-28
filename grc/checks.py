"""Data quality checks for the risk register and the remediation actions.

Errors are things that make the numbers wrong (a bad score, an action pointing at a
risk that doesn't exist). Warnings are things a reviewer should look at.
"""

import re
from collections import Counter
from dataclasses import dataclass
from datetime import date

RISK_STATUSES = {"Open", "In treatment", "Accepted", "Closed"}
TREATMENTS = {"Mitigate", "Accept", "Transfer", "Avoid"}
CSF_FUNCTIONS = {"Govern", "Identify", "Protect", "Detect", "Respond", "Recover"}
ACTION_STATUSES = {"Not started", "In progress", "Done"}

# NIST CSF 2.0 subcategory ids look like PR.AA-05
CSF_REF = re.compile(r"^(GV|ID|PR|DE|RS|RC)\.[A-Z]{2}-\d{2}$")
# ISO/IEC 27001:2022 Annex A controls run A.5.1-A.5.37, A.6.1-A.6.8, A.7.1-A.7.14, A.8.1-A.8.34
ISO_REF = re.compile(r"^A\.([5-8])\.(\d{1,2})$")
ISO_LAST = {5: 37, 6: 8, 7: 14, 8: 34}

RISK_REQUIRED = ["risk_id", "title", "asset", "threat", "vulnerability", "csf_function",
                 "treatment", "owner", "status", "last_reviewed"]
ACTION_REQUIRED = ["action_id", "risk_id", "action", "owner", "due_date", "status"]


@dataclass
class Issue:
    severity: str  # "error" or "warning"
    record: str
    field: str
    problem: str


def parse_date(text):
    try:
        return date.fromisoformat(text)
    except (TypeError, ValueError):
        return None


def split_refs(text):
    return [part.strip() for part in (text or "").split(";") if part.strip()]


def check_risks(risks):
    issues = []
    seen = set()

    for row_num, r in enumerate(risks, start=2):  # row 1 of the CSV is the header
        rid = r.get("risk_id") or f"row {row_num}"

        def add(severity, field, problem):
            issues.append(Issue(severity, rid, field, problem))

        for field in RISK_REQUIRED:
            if not r.get(field):
                add("error", field, "missing")

        if r.get("risk_id"):
            if not re.fullmatch(r"R\d{2,3}", r["risk_id"]):
                add("error", "risk_id", "should look like R01")
            if r["risk_id"] in seen:
                add("error", "risk_id", "duplicate id")
            seen.add(r["risk_id"])

        scores = {}
        for stage in ("inherent", "residual", "target"):
            parts = []
            for part in ("likelihood", "impact"):
                field = f"{stage}_{part}"
                value = r.get(field, "")
                if value.isdigit() and 1 <= int(value) <= 5:
                    parts.append(int(value))
                else:
                    add("error", field, f"must be a whole number from 1 to 5 (got '{value}')")
            if len(parts) == 2:
                scores[stage] = parts[0] * parts[1]

        if {"inherent", "residual"} <= scores.keys() and scores["residual"] > scores["inherent"]:
            add("warning", "residual", "residual score is higher than the inherent score")
        if {"residual", "target"} <= scores.keys() and scores["target"] > scores["residual"]:
            add("warning", "target", "target score is higher than the residual score")

        status = r.get("status", "")
        treatment = r.get("treatment", "")
        if status and status not in RISK_STATUSES:
            add("error", "status", f"'{status}' is not one of {sorted(RISK_STATUSES)}")
        if treatment and treatment not in TREATMENTS:
            add("error", "treatment", f"'{treatment}' is not one of {sorted(TREATMENTS)}")
        if r.get("csf_function") and r["csf_function"] not in CSF_FUNCTIONS:
            add("error", "csf_function", f"'{r['csf_function']}' is not a NIST CSF 2.0 function")
        if r.get("last_reviewed") and parse_date(r["last_reviewed"]) is None:
            add("error", "last_reviewed", "not a valid date (use YYYY-MM-DD)")

        csf = split_refs(r.get("csf_refs"))
        iso = split_refs(r.get("iso_refs"))
        if not csf:
            add("warning", "csf_refs", "no NIST CSF reference")
        if not iso:
            add("warning", "iso_refs", "no ISO 27001 reference")
        for ref in csf:
            if not CSF_REF.match(ref):
                add("error", "csf_refs", f"'{ref}' doesn't look like a CSF 2.0 subcategory id")
        for ref in iso:
            m = ISO_REF.match(ref)
            if not m or not 1 <= int(m.group(2)) <= ISO_LAST[int(m.group(1))]:
                add("error", "iso_refs", f"'{ref}' is not an ISO 27001:2022 Annex A control")

        if status == "Accepted":
            if treatment != "Accept":
                add("error", "treatment", "accepted risks should use the Accept treatment")
            if not r.get("accepted_by") or not r.get("accepted_on"):
                add("error", "accepted_by", "accepted risks need accepted_by and accepted_on")
            elif parse_date(r["accepted_on"]) is None:
                add("error", "accepted_on", "not a valid date (use YYYY-MM-DD)")
        elif treatment == "Accept" and status != "Closed":
            add("warning", "status", "treatment is Accept but nobody has signed off yet")

    return issues


def check_actions(actions, risks, as_of):
    issues = []
    seen = set()
    risk_ids = {r.get("risk_id") for r in risks}

    for row_num, a in enumerate(actions, start=2):
        aid = a.get("action_id") or f"row {row_num}"

        def add(severity, field, problem):
            issues.append(Issue(severity, aid, field, problem))

        for field in ACTION_REQUIRED:
            if not a.get(field):
                add("error", field, "missing")

        if a.get("action_id"):
            if not re.fullmatch(r"A\d{2,3}", a["action_id"]):
                add("error", "action_id", "should look like A01")
            if a["action_id"] in seen:
                add("error", "action_id", "duplicate id")
            seen.add(a["action_id"])

        if a.get("risk_id") and a["risk_id"] not in risk_ids:
            add("error", "risk_id", f"{a['risk_id']} is not in the risk register")

        status = a.get("status", "")
        if status and status not in ACTION_STATUSES:
            add("error", "status", f"'{status}' is not one of {sorted(ACTION_STATUSES)}")
        if a.get("due_date") and parse_date(a["due_date"]) is None:
            add("error", "due_date", "not a valid date (use YYYY-MM-DD)")

        completed = a.get("completed_date", "")
        if status == "Done":
            done_on = parse_date(completed)
            if done_on is None:
                add("error", "completed_date", "Done actions need a completed date")
            elif done_on > as_of:
                add("error", "completed_date", "completed date is in the future")
        elif completed:
            add("error", "completed_date", "has a completed date but the status isn't Done")

    # Cross-checks between the two files
    open_actions = Counter(a.get("risk_id") for a in actions if a.get("status") != "Done")
    for r in risks:
        rid = r.get("risk_id")
        if r.get("status") in ("Open", "In treatment") and r.get("treatment") == "Mitigate" and not open_actions[rid]:
            issues.append(Issue("warning", rid, "actions", "being mitigated but has no open actions"))
        if r.get("status") == "Closed" and open_actions[rid]:
            issues.append(Issue("error", rid, "status", "risk is closed but still has open actions"))

    return issues


def check_all(risks, actions, as_of):
    return check_risks(risks) + check_actions(actions, risks, as_of)
