---
title: Contoso HR V1 ASCII Architecture Diagram
description: ASCII architecture diagram for the v1 TXT-only resume and requirement matching flow
author: Bala Gunaseelan
ms.date: 2026-07-15
ms.topic: overview
---

## V1 Architecture Diagram

```text
                   +--------------------------------------+
                   |         Internal Employee            |
                   |   Uploads UTF-8 TXT Resume (<=1MB)  |
                   +-------------------+------------------+
                                       |
                                       v
+-------------------+      +-----------+-----------+      +---------------------+
|  Project Requestor|----->|   Ingestion API       |<-----|      Recruiter      |
| Uploads UTF-8 TXT |      |  (TXT validation,     |      | Uploads Req TXT and |
| Requirement (<=1MB)|     |   auth, metadata)     |      | reviews outcomes    |
+-------------------+      +-----------+-----------+      +---------------------+
                                       |
                                       v
                           +-----------+-----------+
                           |  Document Store       |
                           | (TXT files + metadata)|
                           +-----------+-----------+
                                       |
                     +-----------------+------------------+
                     |                                    |
                     v                                    v
          +----------+-----------+             +----------+-----------+
          | Skill Extraction     |             | Requirement Parser   |
          | Service (AI)         |             | Service (AI/Rules)   |
          +----------+-----------+             +----------+-----------+
                     |                                    |
                     +-----------------+------------------+
                                       |
                                       v
                           +-----------+-----------+
                           | Matching Engine        |
                           | Rank candidates vs req |
                           +-----------+-----------+
                                       |
                                       v
                           +-----------+-----------+
                           | Recommendation API     |
                           | + Rationale Builder    |
                           +-----------+-----------+
                                       |
                                       v
                           +-----------+-----------+
                           | Recruiter Review UI    |
                           | Accept/Reject/Adjust   |
                           +-----------+-----------+
                                       |
                                       v
                           +-----------+-----------+
                           | Decision Store         |
                           | + Audit + Telemetry    |
                           +------------------------+

Cross-cutting controls:
- RBAC on upload, recommendation, and review endpoints
- Telemetry events for upload, extraction, matching, review
- Cost monitoring based on TXT token volume and run count
```

## Diagram Notes

* v1 enforces single-format UTF-8 TXT input for both resumes and requirements
* PDF and DOCX ingestion are explicitly deferred to v2
* Recruiters remain the final decision authority
