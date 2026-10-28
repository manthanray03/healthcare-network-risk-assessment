"""Runs the KRI queries and turns the numbers into Green / Amber / Red indicators."""

from dataclasses import dataclass

from grc.scoring import RATING_ORDER


@dataclass
class Kri:
    name: str
    value: str
    status: str   # Green, Amber, Red or Info
    target: str


def run(con, queries, as_of):
    params = {"as_of": as_of.isoformat()}
    results = {}
    for name, sql in queries.items():
        rows = con.execute(sql, params).fetchall()
        results[name] = [dict(row) for row in rows]
    return results


def _rag(value, green_max, amber_max):
    if value <= green_max:
        return "Green"
    if value <= amber_max:
        return "Amber"
    return "Red"


def active_counts(results):
    counts = {name: 0 for name in RATING_ORDER}
    for row in results["active_by_rating"]:
        counts[row["residual_rating"]] = row["risks"]
    return counts


def build(results):
    counts = active_counts(results)
    critical = counts["Critical"]
    high_plus = counts["Critical"] + counts["High"]
    overdue = len(results["overdue_actions"])
    stale = len(results["stale_reviews"])

    totals = results["action_counts"][0]
    done = totals["done"] or 0
    on_time = totals["done_on_time"] or 0
    if done:
        pct = round(100 * on_time / done)
        on_time_kri = Kri("Actions completed on time", f"{pct}% ({on_time} of {done})",
                          "Green" if pct >= 90 else "Amber" if pct >= 75 else "Red", "90% or more")
    else:
        on_time_kri = Kri("Actions completed on time", "none done yet", "Info", "90% or more")

    score = results["score_totals"][0]
    inherent, residual, target = score["inherent"] or 0, score["residual"] or 0, score["target"] or 0
    reduced_now = round(100 * (inherent - residual) / inherent) if inherent else 0
    reduced_planned = round(100 * (inherent - target) / inherent) if inherent else 0

    return [
        Kri("Critical risks open", str(critical), "Green" if critical == 0 else "Red", "0"),
        Kri("High and critical risks open", str(high_plus), _rag(high_plus, 3, 6), "3 or fewer"),
        Kri("Overdue remediation actions", str(overdue), _rag(overdue, 0, 3), "0"),
        on_time_kri,
        Kri("Risks past their 90-day review", str(stale), _rag(stale, 0, 2), "0"),
        Kri("Exposure reduced by current controls", f"{reduced_now}%", "Info",
            f"{reduced_planned}% once all actions are done"),
    ]
