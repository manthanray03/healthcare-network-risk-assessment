# Vendor security assessment: Prairie Imaging Cloud

Service: Cloud PACS and teleradiology reading (fictional vendor)  
Assessed: 2026-10-21  
Score: 73.5% (25 of 34 weighted points)  
Vendor risk: **High**

Recommendation: Do not approve yet. At least one must-have requirement is not met.

## Must-have requirements

| ID | Requirement | Answer | Evidence |
|---|---|---|---|
| V02 | Can the vendor provide a current SOC 2 Type II report or ISO 27001 certificate that covers the service and region we would use? | Partial | SOC 2 Type II (2026) covers the US-East region only |
| V03 | Is personal health information stored and processed only in Canada? | No | Primary storage in Toronto; disaster recovery replica in US-East |
| V04 | Is data encrypted at rest with AES-256 or equivalent? | Yes | AES-256 at rest with keys in the cloud provider's KMS |
| V05 | Are all connections protected with TLS 1.2 or higher? | Yes | TLS 1.2 minimum enforced; checked with an external TLS scan |
| V06 | Do vendor staff need MFA to reach customer data? | Yes | MFA required for all support staff |
| V09 | Will the vendor notify us of a confirmed breach within 24 hours? | Partial | Contract says "without undue delay" with no hour limit |

## Gaps to close

| ID | Domain | Question | Answer | Evidence | Reference |
|---|---|---|---|---|---|
| V03 | Data residency | Is personal health information stored and processed only in Canada? | No | Primary storage in Toronto; disaster recovery replica in US-East | A.5.23; A.5.34 |
| V02 | Assurance | Can the vendor provide a current SOC 2 Type II report or ISO 27001 certificate that covers the service and region we would use? | Partial | SOC 2 Type II (2026) covers the US-East region only | GV.SC-07; A.5.22 |
| V09 | Incident response | Will the vendor notify us of a confirmed breach within 24 hours? | Partial | Contract says "without undue delay" with no hour limit | GV.SC-05; A.5.20; A.5.24 |
| V07 | Access control | Can our users sign in with SSO and be given role-based access? | Partial | SAML SSO supported; only two built-in roles | PR.AA-05; A.5.15 |
| V08 | Logging | Are access logs for our data kept for at least 1 year and available on request? | Partial | Logs kept 90 days; longer retention is an extra cost | PR.PS-04; A.8.15 |
| V12 | Subprocessors | Does the vendor publish its subprocessors and give notice before adding new ones? | Partial | Subprocessor list is public; no advance notice of changes | GV.SC-07; A.5.21 |

## All answers

| ID | Domain | Weight | Answer | Points |
|---|---|---|---|---|
| V01 | Governance | 2 | Yes | 2 |
| V02 | Assurance | 3 | Partial | 1.5 |
| V03 | Data residency | 3 | No | 0 |
| V04 | Data protection | 3 | Yes | 3 |
| V05 | Data protection | 3 | Yes | 3 |
| V06 | Access control | 3 | Yes | 3 |
| V07 | Access control | 2 | Partial | 1 |
| V08 | Logging | 2 | Partial | 1 |
| V09 | Incident response | 3 | Partial | 1.5 |
| V10 | Vulnerability management | 2 | Yes | 2 |
| V11 | Business continuity | 2 | Yes | 2 |
| V12 | Subprocessors | 2 | Partial | 1 |
| V13 | Data lifecycle | 2 | Yes | 2 |
| V14 | People | 1 | Yes | 1 |
| V15 | People | 1 | Yes | 1 |

Scoring: Yes = full weight, Partial = half, No = 0. A must-have answered No makes the vendor High risk. Otherwise 85% or more is Low, 70-84% is Medium, below 70% is High.
