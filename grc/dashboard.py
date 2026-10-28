"""Builds the HTML dashboard and the Markdown summary from the KRI results.

The HTML is one self-contained file (no JavaScript, no external CSS) so it opens
from disk and can be attached to an email.
"""

from html import escape

from grc.kri import active_counts
from grc.scoring import RATING_ORDER, rating

STATUS_COLOURS = {"Green": "#2e7d32", "Amber": "#b26a00", "Red": "#c62828", "Info": "#1f5fa8"}
BAND_COLOURS = {"Low": "#e3f1df", "Medium": "#fdf1c7", "High": "#fbd9b4", "Critical": "#f6c1c1"}

CSS = """
* { box-sizing: border-box; }
body { margin: 0; font-family: "Segoe UI", Roboto, Helvetica, Arial, sans-serif; color: #1d2733; background: #f3f5f8; }
header { background: #16324f; color: #fff; padding: 20px 28px; }
header h1 { margin: 0 0 4px; font-size: 22px; font-weight: 600; }
header p { margin: 0; color: #c9d6e3; font-size: 14px; }
main { max-width: 1180px; margin: 0 auto; padding: 20px 16px 8px; }
.tiles { display: grid; grid-template-columns: repeat(auto-fit, minmax(170px, 1fr)); gap: 12px; margin-bottom: 16px; }
.tile { background: #fff; border-radius: 6px; padding: 12px 14px; border-left: 6px solid; box-shadow: 0 1px 2px rgba(0,0,0,.08); }
.tile .label { font-size: 13px; color: #4a5868; }
.tile .value { font-size: 24px; font-weight: 600; margin: 4px 0; }
.tile .target { font-size: 12px; color: #6b7a8a; }
.grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(340px, 1fr)); gap: 16px; }
.card { background: #fff; border-radius: 6px; padding: 14px 16px; margin-bottom: 16px; box-shadow: 0 1px 2px rgba(0,0,0,.08); overflow-x: auto; }
.card h2 { font-size: 16px; margin: 0 0 10px; }
.card h3 { font-size: 14px; margin: 16px 0 8px; color: #33414f; }
table { border-collapse: collapse; width: 100%; font-size: 13px; }
th, td { text-align: left; padding: 6px 8px; border-bottom: 1px solid #e3e8ee; vertical-align: top; }
th { background: #f7f9fb; color: #4a5868; font-weight: 600; }
td.num, th.num { text-align: right; white-space: nowrap; }
td.date { white-space: nowrap; }
.pill { display: inline-block; padding: 1px 8px; border-radius: 10px; font-size: 12px; font-weight: 600; }
.heat { width: auto; margin: 0 auto; }
.heat td { width: 52px; height: 44px; text-align: center; font-size: 16px; font-weight: 600; border: 2px solid #fff; }
.heat th { background: none; text-align: center; font-weight: 500; border: none; }
.axis { text-align: center; font-size: 12px; color: #4a5868; margin-top: 6px; }
.bar-row { display: flex; align-items: center; gap: 8px; margin: 6px 0; font-size: 13px; }
.bar-row .name { width: 120px; flex: none; }
.bar-row .track { flex: 1; background: #eef1f5; border-radius: 3px; height: 16px; }
.bar-row .fill { height: 16px; border-radius: 3px; background: #2f6fa7; }
.bar-row .count { width: 44px; text-align: right; flex: none; }
.muted { color: #6b7a8a; font-size: 13px; }
footer { max-width: 1180px; margin: 0 auto; padding: 4px 16px 24px; font-size: 12px; color: #6b7a8a; }
"""


def _pill(text, colour, background):
    return f'<span class="pill" style="color:{colour};background:{background}">{escape(text)}</span>'


def _rating_pill(name):
    return _pill(name, "#1d2733", BAND_COLOURS[name])


def _table(headers, rows, numeric=(), dates=("Due", "Last reviewed")):
    head = "".join(f'<th class="num">{escape(h)}</th>' if h in numeric else f"<th>{escape(h)}</th>" for h in headers)
    body = []
    for row in rows:
        cells = []
        for h, cell in zip(headers, row):
            cls = ' class="num"' if h in numeric else ' class="date"' if h in dates else ""
            cells.append(f"<td{cls}>{cell}</td>")
        body.append("<tr>" + "".join(cells) + "</tr>")
    return f"<table><thead><tr>{head}</tr></thead><tbody>{''.join(body)}</tbody></table>"


def _bars(items, colour="#2f6fa7"):
    biggest = max((v for _, v in items), default=0) or 1
    out = []
    for name, value in items:
        width = round(100 * value / biggest)
        out.append(
            f'<div class="bar-row"><span class="name">{escape(str(name))}</span>'
            f'<span class="track"><span class="fill" style="display:block;width:{width}%;background:{colour}"></span></span>'
            f'<span class="count">{value}</span></div>'
        )
    return "".join(out)


def _heatmap(results):
    cells = {(row["likelihood"], row["impact"]): row["risks"] for row in results["heatmap"]}
    rows = []
    for likelihood in range(5, 0, -1):
        tds = []
        for impact in range(1, 6):
            band = rating(likelihood * impact)
            count = cells.get((likelihood, impact), "")
            tds.append(f'<td style="background:{BAND_COLOURS[band]}" title="{band}: L{likelihood} x I{impact}">{count}</td>')
        rows.append(f"<tr><th>{likelihood}</th>{''.join(tds)}</tr>")
    impact_row = "<tr><th></th>" + "".join(f"<th>{i}</th>" for i in range(1, 6)) + "</tr>"
    return (
        '<table class="heat"><tbody>' + "".join(rows) + impact_row + "</tbody></table>"
        '<p class="axis">Impact (1 = minor, 5 = severe) across, likelihood (1 = rare, 5 = almost certain) up. '
        "Open, in-treatment and accepted risks.</p>"
    )


def render_html(results, kris, issues, as_of, n_risks, n_actions):
    tiles = []
    for k in kris:
        colour = STATUS_COLOURS[k.status]
        tiles.append(
            f'<div class="tile" style="border-left-color:{colour}">'
            f'<div class="label">{escape(k.name)}</div>'
            f'<div class="value" style="color:{colour}">{escape(k.value)}</div>'
            f'<div class="target">Target: {escape(k.target)} &middot; {escape(k.status)}</div></div>'
        )

    counts = active_counts(results)
    rating_bars = "".join(
        f'<div class="bar-row"><span class="name">{_rating_pill(name)}</span>'
        f'<span class="track"><span class="fill" style="display:block;width:{round(100 * counts[name] / (max(counts.values()) or 1))}%;'
        f'background:#5b7b99"></span></span><span class="count">{counts[name]}</span></div>'
        for name in RATING_ORDER
    )
    function_bars = _bars([(r["csf_function"], r["risks"]) for r in results["by_function"]])

    top = _table(
        ["ID", "Risk", "Owner", "Status", "Inherent", "Residual", "Target", "Rating"],
        [[escape(r["risk_id"]), escape(r["title"]), escape(r["owner"]), escape(r["status"]),
          r["inherent_score"], r["residual_score"], r["target_score"], _rating_pill(r["residual_rating"])]
         for r in results["top_risks"]],
        numeric=("Inherent", "Residual", "Target"),
    )

    overdue_rows = results["overdue_actions"]
    overdue = _table(
        ["Action", "Risk", "Owner", "Due", "Days late"],
        [[f"{escape(a['action_id'])}: {escape(a['action'])}", escape(a["risk_id"]), escape(a["owner"]),
          escape(a["due_date"]), a["days_overdue"]] for a in overdue_rows],
        numeric=("Days late",),
    ) if overdue_rows else '<p class="muted">No overdue actions.</p>'

    soon_rows = results["due_soon_actions"]
    soon = _table(
        ["Action", "Risk", "Owner", "Due", "Days left"],
        [[f"{escape(a['action_id'])}: {escape(a['action'])}", escape(a["risk_id"]), escape(a["owner"]),
          escape(a["due_date"]), a["days_left"]] for a in soon_rows],
        numeric=("Days left",),
    ) if soon_rows else '<p class="muted">Nothing due in the next 14 days.</p>'

    owners = _table(
        ["Owner", "Open actions", "Overdue"],
        [[escape(o["owner"]), o["open_actions"],
          _pill(str(o["overdue"]), "#fff", STATUS_COLOURS["Red"]) if o["overdue"] else "0"]
         for o in results["actions_by_owner"]],
        numeric=("Open actions", "Overdue"),
    )

    totals = results["score_totals"][0]
    exposure = _bars(
        [("Inherent", totals["inherent"] or 0), ("Residual (now)", totals["residual"] or 0),
         ("Target", totals["target"] or 0)],
        colour="#8a5a9e",
    )

    accepted = _table(
        ["ID", "Risk", "Residual", "Rating"],
        [[escape(r["risk_id"]), escape(r["title"]), r["residual_score"], _rating_pill(r["residual_rating"])]
         for r in results["accepted_risks"]],
        numeric=("Residual",),
    ) if results["accepted_risks"] else '<p class="muted">No accepted risks.</p>'

    stale = _table(
        ["ID", "Risk", "Owner", "Last reviewed", "Days"],
        [[escape(r["risk_id"]), escape(r["title"]), escape(r["owner"]), escape(r["last_reviewed"]),
          r["days_since_review"]] for r in results["stale_reviews"]],
        numeric=("Days",),
    ) if results["stale_reviews"] else '<p class="muted">Every risk was reviewed in the last 90 days.</p>'

    if issues:
        quality = _table(
            ["Severity", "Record", "Field", "Problem"],
            [[escape(i.severity), escape(i.record), escape(i.field), escape(i.problem)] for i in issues],
        )
    else:
        quality = '<p class="muted">No data quality issues found in either file.</p>'

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Healthcare Network Risk Dashboard</title>
<style>{CSS}</style>
</head>
<body>
<header>
<h1>Healthcare Network Risk Dashboard</h1>
<p>Fictional provincial health authority &middot; data as of {as_of.isoformat()} &middot; {n_risks} risks &middot; {n_actions} remediation actions</p>
</header>
<main>
<section class="tiles">{''.join(tiles)}</section>
<div class="grid">
<section class="card"><h2>Residual risk heatmap</h2>{_heatmap(results)}</section>
<section class="card"><h2>Active risks by rating</h2>{rating_bars}
<h3>Active risks by NIST CSF function</h3>{function_bars}</section>
</div>
<section class="card"><h2>Top 5 active risks</h2>{top}</section>
<div class="grid">
<section class="card"><h2>Overdue actions</h2>{overdue}</section>
<section class="card"><h2>Due in the next 14 days</h2>{soon}</section>
</div>
<div class="grid">
<section class="card"><h2>Open actions by owner</h2>{owners}</section>
<section class="card"><h2>Total risk score: inherent, residual, target</h2>{exposure}
<p class="muted">Sum of likelihood x impact across all risks that aren't closed.</p></section>
</div>
<div class="grid">
<section class="card"><h2>Accepted risks</h2>{accepted}</section>
<section class="card"><h2>Reviews overdue (more than 90 days)</h2>{stale}</section>
</div>
<section class="card"><h2>Data quality checks</h2>{quality}</section>
</main>
<footer>Built by report.py from data/risk_register.csv and data/remediation_actions.csv. Learning project: the organization, people and findings are fictional.</footer>
</body>
</html>
"""


def _md_table(headers, rows):
    lines = ["| " + " | ".join(headers) + " |", "|" + "|".join("---" for _ in headers) + "|"]
    for row in rows:
        lines.append("| " + " | ".join(str(c).replace("|", "/") for c in row) + " |")
    return "\n".join(lines)


def render_markdown(results, kris, issues, as_of, n_risks, n_actions):
    out = [
        "# Risk summary",
        "",
        f"Data as of {as_of.isoformat()}: {n_risks} risks and {n_actions} remediation actions. "
        "Generated by `report.py`; open `dashboard.html` for the full view.",
        "",
        "## Key risk indicators",
        "",
        _md_table(["Indicator", "Value", "Target", "Status"], [[k.name, k.value, k.target, k.status] for k in kris]),
        "",
        "## Top 5 active risks",
        "",
        _md_table(
            ["ID", "Risk", "Owner", "Inherent", "Residual", "Target", "Rating"],
            [[r["risk_id"], r["title"], r["owner"], r["inherent_score"], r["residual_score"],
              r["target_score"], r["residual_rating"]] for r in results["top_risks"]],
        ),
        "",
        "## Overdue actions",
        "",
    ]
    if results["overdue_actions"]:
        out.append(_md_table(
            ["Action", "Risk", "Owner", "Due", "Days late"],
            [[f"{a['action_id']}: {a['action']}", a["risk_id"], a["owner"], a["due_date"], a["days_overdue"]]
             for a in results["overdue_actions"]],
        ))
    else:
        out.append("None.")
    out += ["", "## Accepted risks", ""]
    if results["accepted_risks"]:
        out.append(_md_table(
            ["ID", "Risk", "Residual", "Rating"],
            [[r["risk_id"], r["title"], r["residual_score"], r["residual_rating"]] for r in results["accepted_risks"]],
        ))
    else:
        out.append("None.")
    out += ["", "## Data quality", ""]
    if issues:
        out.append(_md_table(["Severity", "Record", "Field", "Problem"],
                             [[i.severity, i.record, i.field, i.problem] for i in issues]))
    else:
        out.append("No issues found in either file.")
    out.append("")
    return "\n".join(out)
