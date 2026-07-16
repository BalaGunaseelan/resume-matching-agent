---
title: Contoso HR Resume Matching Backlog Breakdown
description: Prioritized backlog breakdown derived from the Contoso HR resume matching PRD
author: Bala Gunaseelan
ms.date: 2026-07-15
ms.topic: overview
---

## Backlog Overview

This backlog translates the approved product requirements into an implementation sequence for the v1 PoC.

### Planning Principles

* Keep internal employee resume intake and project requirement document processing as the first slice
* Deliver matching and recruiter review before expanding the product surface area
* Capture telemetry early so KPI trends are available during pilot
* Defer phase-2 integration and richer guardrails until the PoC proves value

## Epics

| Epic ID | Epic Name | Outcome | Linked Goals | Priority | Dependencies |
| --- | --- | --- | --- | --- | --- |
| E-001 | Intake and Document Normalization | Users can upload TXT resumes and TXT requirement documents into the system | G-001 | High | File storage, access control |
| E-002 | AI Extraction and Matching | The system extracts skills and generates ranked matches against requirement documents | G-001, G-002 | High | E-001, AI service availability |
| E-003 | Recruiter Review and Rationale | Recruiters can inspect, accept, reject, or adjust recommendations with clear reasoning | G-002, G-003 | High | E-002 |
| E-004 | Telemetry, Security, and Operations | The pilot captures metrics, protects HR-sensitive data, and supports monitoring | G-001, G-002, G-003 | High | E-001, E-002, E-003 |

## Epic Breakdown

### E-001 Intake and Document Normalization

| Feature ID | Feature | Linked FRs | Priority | Description |
| --- | --- | --- | --- | --- |
| F-001 | Resume Upload | FR-001 | High | Allow internal employees to upload UTF-8 TXT resumes up to 1 MB |
| F-002 | Requirement Document Upload | FR-003 | High | Allow recruiters or project requestors to upload UTF-8 TXT requirement documents up to 1 MB |
| F-003 | Input Validation and Storage | FR-001, FR-003 | High | Validate file type, size, and storage state before processing begins |

| Story ID | User Story | Acceptance Criteria | Depends On |
| --- | --- | --- | --- |
| S-001 | As an internal employee, I want to upload my resume so that I can be considered for project matching | Given a UTF-8 TXT file up to 1 MB, when upload is submitted, then the file is stored and status is set to Ready for processing within 30 seconds | None |
| S-002 | As a recruiter, I want to upload a requirement document so that matching uses the project description as input | Given a UTF-8 TXT file up to 1 MB, when upload is submitted, then the file is stored and status is set to Ready for matching | None |
| S-003 | As the platform, I want strict input validation so that unsupported files do not enter the pipeline | Given an invalid type, invalid encoding, or oversize file, when upload is submitted, then upload is rejected with a specific validation message and no processing job is created | S-001, S-002 |

### E-002 AI Extraction and Matching

| Feature ID | Feature | Linked FRs | Priority | Description |
| --- | --- | --- | --- | --- |
| F-101 | Resume Skill Extraction | FR-002 | High | Extract skills and related signals from uploaded resumes |
| F-102 | Requirement Text Parsing | FR-003 | High | Prepare TXT requirement documents for downstream matching |
| F-103 | Candidate-to-Requirement Matching | FR-004 | High | Rank internal employees against the requirement document |

| Story ID | User Story | Acceptance Criteria | Depends On |
| --- | --- | --- | --- |
| S-101 | As the platform, I want to extract skills from a stored resume so that recruiters can review structured candidate data | Given a resume in Ready for processing state, when extraction completes, then skills are persisted to the candidate profile with extraction timestamp and source resume ID | S-001 |
| S-102 | As the platform, I want to parse requirement text so that matching uses normalized requirement content | Given a requirement TXT file in Ready for matching state, when parsing completes, then normalized requirement terms are persisted and linked to the request ID | S-002 |
| S-103 | As a recruiter, I want ranked recommendations so that I can quickly identify best-fit employees | Given extracted skills and parsed requirements, when matching runs, then a ranked top-5 list is returned with descending score and a unique candidate per rank | S-101, S-102 |

### E-003 Recruiter Review and Rationale

| Feature ID | Feature | Linked FRs | Priority | Description |
| --- | --- | --- | --- | --- |
| F-201 | Review Recommendations | FR-005 | High | Allow recruiters to inspect the ranked list and make final decisions |
| F-202 | Recommendation Rationale | FR-006 | High | Show concise rationale for why a candidate was matched |
| F-203 | Decision Capture | FR-005 | High | Save accept, reject, and adjust actions with reviewer rationale |

| Story ID | User Story | Acceptance Criteria | Depends On |
| --- | --- | --- | --- |
| S-201 | As a recruiter, I want to review ranked candidates so that I can decide who should move forward | Given a completed matching run, when recommendations load, then each entry shows candidate name, rank, score, and key matched skills | S-103 |
| S-202 | As a recruiter, I want to see recommendation rationale so that I can trust and explain the result | Given a recommendation entry, when I open details, then rationale shows matched skills, missing critical skills, and confidence signal | S-103 |
| S-203 | As a recruiter, I want to save my decision so that final shortlist outcomes are auditable | Given a recommendation entry, when I accept, reject, or adjust and submit rationale, then decision, rationale, reviewer ID, and timestamp are stored and retrievable | S-201, S-202 |

### E-004 Telemetry, Security, and Operations

| Feature ID | Feature | Linked FRs and NFRs | Priority | Description |
| --- | --- | --- | --- | --- |
| F-301 | Event Telemetry | NFR-005 | High | Log key upload, extraction, matching, and review events |
| F-302 | Access Control | NFR-003 | High | Restrict access to HR-sensitive files and recruiter views |
| F-303 | Latency and Availability Monitoring | NFR-001, NFR-002 | Medium | Measure processing time and pilot availability |
| F-304 | Cost Efficiency Tracking | NFR-004 | High | Track token-efficient TXT usage and processing cost signals |

| Story ID | User Story | Acceptance Criteria | Depends On |
| --- | --- | --- | --- |
| S-301 | As an operator, I want upload and match events logged so that I can trace pipeline execution end to end | Given upload, extraction, matching, and review actions, when each action completes, then one trace event with correlation ID is recorded per action | S-001, S-101, S-103, S-203 |
| S-302 | As a security reviewer, I want role-based access controls enforced so that HR data remains protected | Given a user without required role, when file or recommendation data is requested, then access is denied with HTTP 403 and an audit event is recorded | S-001, S-002, S-201 |
| S-303 | As a product owner, I want latency and availability tracking so that I can evaluate pilot readiness | Given pilot traffic, when dashboard is viewed, then processing p90 latency and service availability for the current week are displayed | S-101, S-103 |
| S-304 | As a TPM, I want cost tracking for TXT requirement processing so that v1 stays cost-efficient | Given processed requirement documents, when weekly metrics are generated, then average tokens per document and estimated processing cost are reported | S-002, S-102 |

## Recommended Implementation Order

1. Build intake and validation first so the team can begin testing with real inputs.
2. Implement extraction and matching next because they produce the core product value.
3. Add recruiter review and rationale visibility before pilot usage.
4. Wire telemetry, access control, and monitoring throughout the build, not after.

## Delivery Milestones

| Milestone | Scope | Exit Criteria |
| --- | --- | --- |
| M-001 | Intake complete | TXT resume and TXT requirement uploads work end to end |
| M-002 | Matching complete | Skills extraction and ranking produce usable recommendations |
| M-003 | Review complete | Recruiters can make final decisions with rationale capture |
| M-004 | Pilot ready | Telemetry, security, and monitoring are active |

## Traceability

| PRD FR | Backlog Coverage |
| --- | --- |
| FR-001 | E-001 / F-001 / F-003 |
| FR-002 | E-002 / F-101 |
| FR-003 | E-001 / F-002 / F-003, E-002 / F-102 |
| FR-004 | E-002 / F-103 |
| FR-005 | E-003 / F-201 / F-203 |
| FR-006 | E-003 / F-202 |

## Open Items

* Confirm whether backlog should be converted into Azure DevOps work items next
* Confirm if phase-2 integration should be captured as a separate epic now or later
