# Control mapping

Each control from the network design, plus the ones the remediation plan adds, mapped to the risks it reduces, NIST CSF 2.0 subcategories and ISO/IEC 27001:2022 Annex A controls.

## Controls in place

| Control | Where | Reduces | NIST CSF 2.0 | ISO 27001:2022 |
|---|---|---|---|---|
| VLAN segmentation (Clinical, Admin, VoIP, Guest, Medical devices, Management) | All sites | R01, R02, R03, R12 | PR.IR-01 | A.8.22 |
| Least-privilege ACLs between VLANs | Hospital distribution and clinic routers | R01, R02, R03, R05 | PR.AA-05, PR.IR-01 | A.8.20, A.8.22 |
| pfSense edge firewall | Data centre edge | R01, R03 | PR.IR-01 | A.8.20 |
| IPsec VPN (AES-256/SHA-256) | Clinic backup path | R04, R08 | PR.DS-02, PR.IR-03 | A.8.24, A.8.14 |
| SSH-only device management | All network devices | R05, R18 | PR.AA-03, PR.DS-02 | A.8.20 |
| SNMPv3 with authentication and encryption | All network devices | R18 | PR.DS-02 | A.8.21 |
| Management VLAN 99 | All sites | R05, R18 | PR.AA-05, PR.IR-01 | A.8.22 |
| Central syslog | Data centre | R07 | PR.PS-04 | A.8.15 |
| Weekly log review, 1-year retention | Security operations | R07 | DE.CM-01 | A.8.15, A.8.16 |
| Dual cores, EtherChannel, HSRP | Data centre and hospitals | Availability generally | PR.IR-03 | A.8.14 |
| Nightly config backups | All network devices | R11, R16 | PR.DS-11, PR.PS-01 | A.8.13, A.8.9 |
| Unused ports disabled, port security | Clinic access switches | R14 | PR.IR-01 | A.8.20 |
| Break-glass account kept in the password vault | All network devices | R05 | PR.AA-01 | A.5.17 |
| Role-based EHR access through AD groups | EHR | R09 | PR.AA-05 | A.5.15, A.5.18 |
| Email filtering | Mail provider | R10 | DE.CM-09 | A.8.7 |
| Vendor security questionnaire and scoring | Vendor management | R13 | GV.SC-07, ID.RA-10 | A.5.19, A.5.22 |

## Controls the remediation plan adds

| Control | Actions | Reduces | NIST CSF 2.0 | ISO 27001:2022 |
|---|---|---|---|---|
| Vendor access through a jump host, with per-session approval and recording | A23 | R12 | PR.AA-05, DE.CM-06 | A.8.2, A.8.15 |
| Security terms in vendor contracts (remote access, residency, breach notice) | A24, A25, A26 | R12, R13 | GV.SC-05 | A.5.20 |
| MFA for all staff, the VPN and the jump host | A10, A20 | R05, R10 | PR.AA-03 | A.8.5 |
| Individual device logins through RADIUS | A09 | R05 | PR.AA-01 | A.5.16, A.8.2 |
| Security awareness training and phishing simulations | A21 | R10 | PR.AT-01 | A.6.3 |
| Endpoint detection and response | A01 | R01 | DE.CM-09 | A.8.7 |
| Immutable offline backups and restore tests | A02, A03 | R01 | PR.DS-11 | A.8.13 |
| Medical device inventory and vendor patch windows | A04, A05 | R02 | ID.AM-01, PR.PS-02 | A.5.9, A.8.8 |
| Alerts on new outbound traffic from VLAN 50 | A06 | R02 | DE.CM-01 | A.8.16 |
| Monthly vulnerability scans with fix deadlines | A35, A36 | R20 | ID.RA-01 | A.8.8 |
| Syslog alert rules | A13 | R07 | DE.AE-02 | A.8.16 |
| Quarterly access reviews and EHR audit reports | A18, A19 | R09 | PR.AA-05, DE.CM-03 | A.5.18, A.8.15 |
| Change tickets and baseline comparison | A30, A31 | R16 | PR.PS-01, ID.RA-07 | A.8.9, A.8.32 |
| Quarterly guest ACL review and test case | A07, A08 | R03 | PR.AA-05 | A.8.20 |
| Encrypted backup share | A12 | R06 | PR.DS-01 | A.8.24 |
| TLS on every clinical app crossing the WAN | A16, A17 | R08 | PR.DS-02 | A.8.24 |
| Second domain controller, DHCP failover, second firewall | A32, A22 | R17, R11 | PR.IR-03 | A.8.14 |
| Network incident playbook and tabletop exercise | A33, A34 | R19 | RS.MA-01, RC.RP-01 | A.5.24, A.5.26 |
| Lockable racks and key log at clinics | A29 | R15 | PR.AA-06 | A.7.2, A.7.8 |

## Coverage by CSF function

| Function | Risks (main function) | Note |
|---|---|---|
| Protect | 13 | Expected for a network build |
| Govern | 2 | Both are vendor risks |
| Identify | 2 | No device inventory, no scanning |
| Detect | 1 | Logs are collected but nothing alerts yet |
| Respond | 1 | No playbook |
| Recover | 1 | Single directory server |

The design is strong on Protect and thin on Detect and Respond. Most of the 30-day and 90-day actions are there for that reason.
