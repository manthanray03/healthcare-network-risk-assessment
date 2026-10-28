"""Scores a third-party vendor's answers against the security questionnaire.

Yes = full points, Partial = half, No = none. Questions marked must_have = Y
decide the rating on their own: one "No" there makes the vendor High risk.
"""

POINTS = {"Yes": 1.0, "Partial": 0.5, "No": 0.0}


def assess(questions, responses):
    answers = {r["question_id"]: r for r in responses}
    total_weight = 0
    earned = 0.0
    rows = []

    for q in questions:
        weight = int(q["weight"])
        response = answers.get(q["question_id"], {})
        answer = response.get("answer", "")
        if answer == "N/A":
            rows.append({**q, "answer": answer, "evidence": response.get("evidence", ""), "points": None})
            continue
        if answer not in POINTS:
            answer = "No"
            response = {"evidence": "No answer given"}
        total_weight += weight
        earned += weight * POINTS[answer]
        rows.append({**q, "answer": answer, "evidence": response.get("evidence", ""), "points": weight * POINTS[answer]})

    percent = round(100 * earned / total_weight, 1) if total_weight else 0.0
    must_fail = [r for r in rows if r["must_have"] == "Y" and r["answer"] == "No"]
    must_partial = [r for r in rows if r["must_have"] == "Y" and r["answer"] == "Partial"]
    gaps = [r for r in rows if r["answer"] in ("No", "Partial")]

    if must_fail or percent < 70:
        risk = "High"
    elif must_partial or percent < 85:
        risk = "Medium"
    else:
        risk = "Low"

    return {
        "rows": rows,
        "earned": earned,
        "total_weight": total_weight,
        "percent": percent,
        "must_fail": must_fail,
        "must_partial": must_partial,
        "gaps": gaps,
        "risk": risk,
    }


def decision(result):
    if result["must_fail"]:
        return "Do not approve yet. At least one must-have requirement is not met."
    if result["risk"] == "Medium":
        return "Approve only with contract conditions that close the gaps below."
    if result["risk"] == "High":
        return "Do not approve. The overall score is below 70%."
    return "Approve. Review again in 12 months or when the service changes."


def render_markdown(result, vendor, service, as_of):
    lines = [
        f"# Vendor security assessment: {vendor}",
        "",
        f"Service: {service}  ",
        f"Assessed: {as_of.isoformat()}  ",
        f"Score: {result['percent']}% ({result['earned']:g} of {result['total_weight']} weighted points)  ",
        f"Vendor risk: **{result['risk']}**",
        "",
        f"Recommendation: {decision(result)}",
        "",
        "## Must-have requirements",
        "",
        "| ID | Requirement | Answer | Evidence |",
        "|---|---|---|---|",
    ]
    for r in result["rows"]:
        if r["must_have"] == "Y":
            lines.append(f"| {r['question_id']} | {r['question']} | {r['answer']} | {r['evidence']} |")

    lines += ["", "## Gaps to close", ""]
    if result["gaps"]:
        lines += ["| ID | Domain | Question | Answer | Evidence | Reference |", "|---|---|---|---|---|---|"]
        for r in sorted(result["gaps"], key=lambda r: (r["answer"] != "No", r["must_have"] != "Y", r["question_id"])):
            lines.append(f"| {r['question_id']} | {r['domain']} | {r['question']} | {r['answer']} | "
                         f"{r['evidence']} | {r['reference']} |")
    else:
        lines.append("None.")

    lines += ["", "## All answers", "", "| ID | Domain | Weight | Answer | Points |", "|---|---|---|---|---|"]
    for r in result["rows"]:
        points = "n/a" if r["points"] is None else f"{r['points']:g}"
        lines.append(f"| {r['question_id']} | {r['domain']} | {r['weight']} | {r['answer']} | {points} |")

    lines += ["", "Scoring: Yes = full weight, Partial = half, No = 0. A must-have answered No makes the vendor "
              "High risk. Otherwise 85% or more is Low, 70-84% is Medium, below 70% is High.", ""]
    return "\n".join(lines)
