from datetime import date

import pytest

from grc import data, kri, vendor
from grc.data import ROOT
from grc.scoring import rating, score

AS_OF = date(2026, 10, 28)


@pytest.fixture
def results():
    risks = data.read_csv(ROOT / "data" / "risk_register.csv")
    actions = data.read_csv(ROOT / "data" / "remediation_actions.csv")
    con = data.build_db(risks, actions)
    return kri.run(con, data.load_queries(), AS_OF)


@pytest.mark.parametrize("value, expected", [(1, "Low"), (4, "Low"), (5, "Medium"), (9, "Medium"),
                                             (10, "High"), (16, "High"), (20, "Critical"), (25, "Critical")])
def test_rating_bands(value, expected):
    assert rating(value) == expected


def test_score_rejects_out_of_range():
    with pytest.raises(ValueError):
        score(6, 2)


def test_python_and_sql_bands_agree(results):
    for row in results["top_risks"]:
        assert rating(row["residual_score"]) == row["residual_rating"]


def test_overdue_actions(results):
    overdue = {a["action_id"]: a["days_overdue"] for a in results["overdue_actions"]}
    assert overdue == {"A23": 28, "A35": 27, "A09": 18, "A04": 13, "A24": 13}


def test_due_soon_window(results):
    assert [a["action_id"] for a in results["due_soon_actions"]] == ["A21", "A30"]


def test_on_time_rate(results):
    totals = results["action_counts"][0]
    assert (totals["done"], totals["done_on_time"]) == (5, 3)


def test_stale_reviews(results):
    assert [r["risk_id"] for r in results["stale_reviews"]] == ["R18", "R15"]


def test_kri_statuses(results):
    statuses = {k.name: k.status for k in kri.build(results)}
    assert statuses["Critical risks open"] == "Red"
    assert statuses["Overdue remediation actions"] == "Red"
    assert statuses["Risks past their 90-day review"] == "Amber"


def test_vendor_must_have_failure_forces_high():
    questions = data.read_csv(ROOT / "data" / "vendor_questions.csv")
    responses = data.read_csv(ROOT / "data" / "vendor_responses_prairie_imaging.csv")
    result = vendor.assess(questions, responses)
    assert result["percent"] == 73.5
    assert result["risk"] == "High"
    assert [r["question_id"] for r in result["must_fail"]] == ["V03"]


def test_vendor_all_yes_is_low():
    questions = data.read_csv(ROOT / "data" / "vendor_questions.csv")
    responses = [{"question_id": q["question_id"], "answer": "Yes", "evidence": ""} for q in questions]
    assert vendor.assess(questions, responses)["risk"] == "Low"
