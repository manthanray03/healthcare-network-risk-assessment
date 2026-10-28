from datetime import date

from grc import checks, data
from grc.data import ROOT

AS_OF = date(2026, 10, 28)


def sample():
    risks = data.read_csv(ROOT / "data" / "risk_register.csv")
    actions = data.read_csv(ROOT / "data" / "remediation_actions.csv")
    return risks, actions


def problems(issues, record, field):
    return [i for i in issues if i.record == record and i.field == field]


def test_sample_data_has_no_errors():
    risks, actions = sample()
    issues = checks.check_all(risks, actions, AS_OF)
    assert [i for i in issues if i.severity == "error"] == []


def test_bad_likelihood_is_an_error():
    risks, actions = sample()
    risks[0]["residual_likelihood"] = "7"
    issues = checks.check_all(risks, actions, AS_OF)
    assert problems(issues, "R01", "residual_likelihood")


def test_missing_owner_is_an_error():
    risks, actions = sample()
    risks[2]["owner"] = ""
    issues = checks.check_risks(risks)
    assert problems(issues, "R03", "owner")


def test_duplicate_risk_id():
    risks, _ = sample()
    risks.append(dict(risks[0]))
    issues = checks.check_risks(risks)
    assert any(i.problem == "duplicate id" for i in issues)


def test_bad_framework_references():
    risks, _ = sample()
    risks[0]["csf_refs"] = "PR.AC-1"       # CSF 1.1 style, not 2.0
    risks[0]["iso_refs"] = "A.8.40"        # Annex A theme 8 stops at 8.34
    issues = checks.check_risks(risks)
    assert problems(issues, "R01", "csf_refs")
    assert problems(issues, "R01", "iso_refs")


def test_accepted_risk_needs_sign_off():
    risks, _ = sample()
    r04 = next(r for r in risks if r["risk_id"] == "R04")
    r04["accepted_by"] = ""
    issues = checks.check_risks(risks)
    assert problems(issues, "R04", "accepted_by")


def test_action_for_unknown_risk():
    risks, actions = sample()
    actions[0]["risk_id"] = "R99"
    issues = checks.check_actions(actions, risks, AS_OF)
    assert problems(issues, "A01", "risk_id")


def test_done_action_needs_a_completed_date():
    risks, actions = sample()
    actions[0]["status"] = "Done"
    issues = checks.check_actions(actions, risks, AS_OF)
    assert problems(issues, "A01", "completed_date")


def test_completed_date_in_the_future():
    risks, actions = sample()
    a11 = next(a for a in actions if a["action_id"] == "A11")
    a11["completed_date"] = "2026-12-01"
    issues = checks.check_actions(actions, risks, AS_OF)
    assert problems(issues, "A11", "completed_date")


def test_closed_risk_with_open_action():
    risks, actions = sample()
    r01 = next(r for r in risks if r["risk_id"] == "R01")
    r01["status"] = "Closed"
    issues = checks.check_actions(actions, risks, AS_OF)
    assert problems(issues, "R01", "status")
