# Threat and risk assessment: provincial health network

| | |
|---|---|
| System | Network for a fictional provincial health authority (from [healthcare-network-design](https://github.com/manthanray03/healthcare-network-design)) |
| Assessment date | 2026-10-28 |
| Prepared by | Manthan Ray |
| Version | 1.0 |
| Register | [`data/risk_register.csv`](../data/risk_register.csv) and [`data/remediation_actions.csv`](../data/remediation_actions.csv) |

## Summary

The network design already cuts total risk by about 25%, mostly through VLAN segmentation, least-privilege ACLs and encrypted, SSH-only management. Even so, 13 of the 17 active risks are still rated High or Critical, so the design isn't ready to carry patient data yet.

The one Critical risk is vendor remote access to medical devices (R12): an always-on support tool with no approval step and no logging, and both actions to fix it are overdue. The next four are phishing (R10), ransomware reaching the EHR servers (R01), unpatched medical devices (R02) and logs that nobody reviews (R07).

If all 36 remediation actions are completed, no risk stays above Medium and the total score drops by 65%. Two risks are accepted as they are (R04 and R18), and one is already closed (R14).

## 1. Scope

In scope:

- The data centre, two hospitals and five rural clinics in the network design, including the WAN links and the IPsec backup path
- Network devices, the pfSense edge firewall, and the Windows (AD, DNS, DHCP) and Ubuntu (syslog) servers
- How staff, vendors and devices reach the network, and the personal health information that crosses it
- One third-party vendor, a cloud PACS and teleradiology service (assessed separately in [`reports/vendor_assessment_prairie_imaging_cloud.md`](../reports/vendor_assessment_prairie_imaging_cloud.md))

Out of scope: the EHR application's own code, medical device internals, and physical security at the hospitals beyond the network closets.

### Network segments

| VLAN | Name | What's on it | Allowed to reach |
|---|---|---|---|
| 10 | Clinical | Clinical workstations, EHR access | EHR and PACS servers |
| 20 | Admin | Business workstations | Business apps, internet |
| 30 | VoIP | Phones | Voice servers, with DSCP EF priority |
| 40 | Guest | Patient and visitor Wi-Fi | Internet only |
| 50 | Medical devices | Imaging modalities, pump gateways | PACS and the EHR interface engine only |
| 99 | Management | Device management interfaces | Reached only from addresses the ACLs allow (network team) |

### Controls already in place

Least-privilege ACLs between VLANs, a pfSense edge firewall, IPsec (AES-256/SHA-256) on the clinic backup path, SSH-only device management, SNMPv3, central syslog, dual cores with HSRP at the hospitals, and nightly config backups. Port security was added at the clinics in September 2026 (R14).

## 2. Assets

| Asset | Data or service | Most important property |
|---|---|---|
| EHR application and database servers | Patient records | Confidentiality and availability |
| PACS and teleradiology service | Diagnostic images and reports | Confidentiality and integrity |
| Networked medical devices | Imaging, infusion pump data | Integrity and availability (patient safety) |
| AD, DNS, DHCP | Logins and addressing at every site | Availability |
| Routers, switches, firewall | Everything above | Integrity and availability |
| Config backups | Device configurations and secrets | Confidentiality |
| Staff accounts and email | Access to all of the above | Confidentiality |

## 3. Method

Each risk was scored three times (inherent, residual, target) on a 5 x 5 likelihood and impact matrix. The full scales, bands and acceptance rules are in [methodology.md](methodology.md). Every risk is mapped to NIST CSF 2.0 and ISO/IEC 27001:2022 Annex A, and the control-by-control mapping is in [control-mapping.md](control-mapping.md).

Inputs were the design summary, IP plan, sample configs, firewall notes and test plan from the network design repository. Likelihood ratings are judgement calls based on that design and on common attacks against health organizations, not on incident history.

Threat sources considered:

- External attackers, including ransomware groups and credential phishing
- Insiders, both careless and curious
- Vendors and their remote access tools
- Equipment and carrier failures
- Physical access to network equipment

## 4. Findings

All 20 risks, highest residual score first. Scores are likelihood x impact (1 to 25).

| ID | Risk | Inherent | Residual | Target | Owner | Status |
|---|---|---|---|---|---|---|
| R12 | Vendor remote support access to medical devices is uncontrolled | 20 | 20 (Critical) | 6 | Vendor Management Lead | Open |
| R10 | Phishing leads to a compromised staff account | 20 | 16 (High) | 6 | Security Awareness Lead | In treatment |
| R01 | Ransomware spreads from an admin workstation to clinical servers | 20 | 15 (High) | 8 | Infrastructure Manager | In treatment |
| R02 | Unpatched medical devices on VLAN 50 are exploited | 20 | 12 (High) | 8 | Biomedical Engineering Lead | In treatment |
| R07 | Intrusion goes unnoticed because logs are not reviewed | 16 | 12 (High) | 6 | Security Operations Analyst | In treatment |
| R09 | Staff look up patient records without a clinical need | 16 | 12 (High) | 6 | Privacy Officer | Open |
| R20 | Known vulnerabilities on servers and network devices go unfound | 16 | 12 (High) | 6 | Security Operations Analyst | In treatment |
| R05 | Stolen or shared admin credentials used to change network devices | 15 | 12 (High) | 4 | Network Team Lead | In treatment |
| R17 | Loss of the directory server stops logins at all sites | 15 | 12 (High) | 4 | Infrastructure Manager | Open |
| R19 | No tested plan for responding to a network security incident | 15 | 12 (High) | 6 | Security Operations Analyst | Open |
| R11 | Single edge firewall fails and cuts internet and partner access | 12 | 12 (High) | 4 | Infrastructure Manager | Open |
| R13 | Teleradiology vendor keeps a copy of images outside Canada | 12 | 12 (High) | 4 | Vendor Management Lead | In treatment |
| R08 | Patient data intercepted between a clinic and the data centre | 15 | 10 (High) | 5 | Application Integration Lead | Open |
| R16 | Unreviewed changes weaken ACLs over time | 12 | 9 (Medium) | 4 | Network Team Lead | In treatment |
| R03 | Guest Wi-Fi user reaches internal systems through an ACL mistake | 12 | 8 (Medium) | 4 | Network Team Lead | Open |
| R06 | Config backups expose passwords or keys | 12 | 8 (Medium) | 3 | Network Team Lead | Open |
| R15 | Unauthorized physical access to clinic network equipment | 8 | 8 (Medium) | 4 | Facilities Manager | Open |
| R04 | Clinic loses its primary WAN link and cannot reach the EHR | 16 | 6 (Medium) | 6 | Director of IT Operations | Accepted |
| R14 | Unknown device plugged into a clinic network port | 9 | 3 (Low) | 3 | Network Team Lead | Closed |
| R18 | Management traffic such as SNMP is read or altered | 9 | 3 (Low) | 3 | Network Team Lead | Accepted |

### R12: Vendor remote support access to medical devices (Critical, 20)

The imaging vendor supports its equipment through a remote access tool that stays connected all the time. Nobody approves a session, and nothing records what the vendor's staff do. VLAN 50 isolation doesn't help here, because the tool runs on the device itself. A stolen vendor account would land an attacker on the most safety-sensitive segment in the network.

Recommendation: route vendor access through a jump host with per-session approval, MFA and session recording (A23), and put those terms in the vendor contract (A24). Both were due by mid-October and neither has started.

### R10: Phishing (High, 16)

MFA isn't enforced for every staff account and there is no awareness training, so one convincing email can hand over a working login. Email filtering at the provider catches some of it.

Recommendation: enforce MFA for all staff (A20) and run phishing training with quarterly simulations (A21, due October 31).

### R01: Ransomware reaching the EHR servers (High, 15)

Segmentation keeps most workstation traffic away from the clinical servers, but the admin VLAN still reaches a few server ports for business apps. Server backups exist, but they sit online on the data centre NAS, where ransomware can encrypt them too. Impact stays at 5 until there is a backup the attacker can't touch.

Recommendation: EDR on all workstations and servers (A01), immutable offline backups of the EHR servers (A02), and a timed restore test (A03).

### R02: Unpatched medical devices (High, 12)

Many devices run operating systems that only the vendor can patch, and there is no list of which devices run what. VLAN 50 and tight ACLs lower the likelihood, but a device that gets infected could still disrupt care.

Recommendation: build the device inventory with OS, firmware and support end dates (A04, overdue), agree patch windows with vendors (A05), and alert on any new outbound connection from VLAN 50 (A06).

### R07: Logs nobody reviews (High, 12)

Every router, switch and the firewall send logs to the central syslog server, but there are no alert rules yet. Log retention was raised from 30 days to a year in October, and weekly reviews started in September.

Recommendation: write alert rules for failed logins, config changes and firewall denies from clinical VLANs (A13).

## 5. Recommendations by priority

Next 30 days (by the end of November 2026):

1. Control vendor remote access to medical devices (A23, A24). This is the only Critical risk.
2. Enforce MFA for all staff and finish the phishing training (A20, A21).
3. Finish the medical device inventory (A04) and get monthly vulnerability scans running (A35).
4. Move network device logins to individual accounts through RADIUS (A09).

Next 90 days (by the end of January 2027):

5. Roll out EDR (A01) and the syslog alert rules (A13).
6. Start quarterly access reviews for the EHR (A18) and confirm TLS on every clinical app crossing the WAN (A16).
7. Get Canadian data residency and a Canadian-region SOC 2 report from the teleradiology vendor before renewal (A25, A26).
8. Require change tickets and compare nightly backups against the approved baseline (A30, A31). Encrypt the backup share (A12).

Within 6 months (by the end of April 2027):

9. Immutable backups and a restore test (A02, A03), a second domain controller (A32) and a second firewall (A22).
10. Write a network incident playbook and run a tabletop exercise with clinical managers (A33, A34).
11. Lockable racks at the clinics (A29) and TLS or IPsec for the legacy HL7 feed (A17).

## 6. Accepted risks

| ID | Risk | Residual | Accepted by | Why |
|---|---|---|---|---|
| R04 | Clinic loses its primary WAN link | 6 (Medium) | Director of IT Operations, 2026-10-26 | The IPsec backup path and OSPF rerouting keep clinics connected; a second carrier per clinic costs more than the remaining risk |
| R18 | Management traffic read or altered | 3 (Low) | Director of IT Operations, 2026-05-15 | SNMPv3 with encryption, VLAN 99 and SSH-only access leave little to gain. Review overdue since August |

## 7. HIPA safeguards

Section 16 of Saskatchewan's Health Information Protection Act requires trustees to keep administrative, technical and physical safeguards for personal health information. Grouping the findings that way shows where the gaps are:

| Safeguard | Risks | Main gap |
|---|---|---|
| Administrative | R09, R10, R12, R13, R16, R19 | No access reviews, no awareness training, weak vendor terms, no incident playbook |
| Technical | R01, R02, R03, R04, R05, R06, R07, R08, R11, R17, R18, R20 | MFA, EDR, offline backups, log alerting, vulnerability scanning |
| Physical | R14, R15 | Clinic equipment in shared rooms |

This is a learning exercise, not a legal opinion on HIPA compliance.

## 8. Assumptions and limitations

- The organization, vendor, people and findings are fictional. Owners are roles, not real people.
- Likelihood is a judgement based on the design documents. No penetration test or vulnerability scan was run.
- The lab only partly simulated the network in Packet Tracer and GNS3, so some controls are assessed from configs rather than tested behaviour.
- Costs and effort for each action haven't been estimated.
