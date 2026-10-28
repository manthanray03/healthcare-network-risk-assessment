# Risk method

How risks in this project are scored, rated, treated and reviewed. The scales are written for a health authority, so impact looks at patient care and personal health information first.

## Three scores per risk

| Score | What it means |
|---|---|
| Inherent | The risk if none of the controls in the network design existed |
| Residual | The risk today, with the controls that are actually in place |
| Target | The risk expected once the planned remediation actions are done |

Each score is likelihood x impact on a 5 x 5 matrix, so it runs from 1 to 25. Keeping all three shows what the current design already buys, and what the remaining work is worth.

## Likelihood

| Rating | Label | Guide |
|---|---|---|
| 1 | Rare | Could happen, but no known cases in similar organizations |
| 2 | Unlikely | Has happened elsewhere; not expected here in the next 3 years |
| 3 | Possible | Could happen in the next 1 to 3 years |
| 4 | Likely | Expected within a year, or has happened here before |
| 5 | Almost certain | Expected within months, or already happening |

## Impact

The highest column that applies sets the rating.

| Rating | Label | Patient care | Health information | Service |
|---|---|---|---|---|
| 1 | Minor | No effect | No records exposed | Under 1 hour at one site |
| 2 | Moderate | Small delays, workarounds in place | A few records seen by staff without a need | 1 to 4 hours at one site |
| 3 | Significant | Appointments moved or delayed | Records for one clinic or department exposed | Up to a day at one site, or hours at several |
| 4 | Major | Care delayed at a hospital | Thousands of records exposed or altered | Days at one hospital or several clinics |
| 5 | Severe | Patient harm possible | Records for most of the authority exposed | Authority-wide outage of clinical systems |

## Rating bands

| Score | Rating | What has to happen |
|---|---|---|
| 20 to 25 | Critical | Tell the Director of IT Operations within 1 business day; treatment plan within 2 weeks |
| 10 to 16 | High | Treatment plan with owners and dates within 30 days |
| 5 to 9 | Medium | Treat, or the Director of IT Operations can accept it in writing |
| 1 to 4 | Low | Risk owner can accept it; check at the next review |

Scores of 17 to 19 can't happen on a 5 x 5 matrix, which is why the bands jump from 16 to 20.

## Treatment options

- Mitigate: add or improve controls (most risks here).
- Accept: live with the residual risk. Needs a named person and a date in `accepted_by` and `accepted_on`.
- Transfer: move part of the risk to someone else, for example through a contract or insurance.
- Avoid: stop doing the thing that creates the risk.

## Reviews

Every risk that isn't closed gets reviewed at least every 90 days, or sooner if something changes (a new system, an incident, a vendor change). The dashboard lists any risk whose `last_reviewed` date is older than that.

## Key risk indicators

| Indicator | Green | Amber | Red |
|---|---|---|---|
| Critical risks open | 0 | n/a | 1 or more |
| High and critical risks open | 3 or fewer | 4 to 6 | 7 or more |
| Overdue remediation actions | 0 | 1 to 3 | 4 or more |
| Actions completed on time | 90% or more | 75% to 89% | Below 75% |
| Risks past their 90-day review | 0 | 1 to 2 | 3 or more |

"Exposure reduced by current controls" is shown for information only: (total inherent score - total residual score) / total inherent score, across risks that aren't closed.

## Frameworks

- NIST Cybersecurity Framework (CSF) 2.0: each risk names its main function (Govern, Identify, Protect, Detect, Respond, Recover) and the subcategories its controls support, such as PR.AA-05 for least-privilege access.
- ISO/IEC 27001:2022 Annex A: the controls that apply, such as A.8.22 for segregation of networks.
- Saskatchewan's Health Information Protection Act (HIPA), section 16: trustees must keep administrative, technical and physical safeguards for personal health information. The TRA groups findings under those three headings.
