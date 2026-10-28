"""Scores a vendor's questionnaire answers and writes a short assessment report.

    python vendor_assessment.py data/vendor_responses_prairie_imaging.csv \
        --vendor "Prairie Imaging Cloud" --service "Cloud PACS and teleradiology reading"
"""

import argparse
import re
from datetime import date
from pathlib import Path

from grc import data, vendor

ROOT = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser(description="Score a vendor security questionnaire.")
    parser.add_argument("responses", type=Path, help="CSV with question_id, answer, evidence")
    parser.add_argument("--questions", type=Path, default=ROOT / "data" / "vendor_questions.csv")
    parser.add_argument("--vendor", required=True)
    parser.add_argument("--service", default="")
    parser.add_argument("--as-of", default=date.today().isoformat())
    parser.add_argument("--out", type=Path, default=ROOT / "reports")
    args = parser.parse_args()

    result = vendor.assess(data.read_csv(args.questions), data.read_csv(args.responses))
    as_of = date.fromisoformat(args.as_of)

    slug = re.sub(r"[^a-z0-9]+", "_", args.vendor.lower()).strip("_")
    args.out.mkdir(parents=True, exist_ok=True)
    out_file = args.out / f"vendor_assessment_{slug}.md"
    out_file.write_text(vendor.render_markdown(result, args.vendor, args.service, as_of), encoding="utf-8")

    print(f"{args.vendor}: {result['percent']}% -> {result['risk']} risk")
    for r in result["must_fail"]:
        print(f"  Must-have not met: {r['question_id']} {r['question']}")
    for r in result["must_partial"]:
        print(f"  Must-have only partly met: {r['question_id']} {r['question']}")
    print(f"Wrote {out_file}")


if __name__ == "__main__":
    main()
