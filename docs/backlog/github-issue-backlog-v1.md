---
title: GitHub Issue Backlog v1 Import Pack
description: GitHub-ready Epic Feature Story issue backlog generated from refined v1 backlog
author: Bala Gunaseelan
ms.date: 2026-07-16
ms.topic: how-to
---

## Purpose

This document provides a GitHub-ready backlog pack for repo issue creation.

It includes:

* Create order
* Labels and milestones
* Copy-paste issue title and body templates for Epics, Features, and Stories

## Recommended GitHub Setup

### Labels

* type:epic
* type:feature
* type:story
* priority:high
* priority:medium
* area:intake
* area:matching
* area:review
* area:platform
* milestone:m1
* milestone:m2
* milestone:m3
* milestone:m4

### Milestones

* M1 Intake complete
* M2 Matching complete
* M3 Review complete
* M4 Pilot ready

## Create Order

1. Create all Epics first
2. Create Features and link to parent Epic
3. Create Stories and link to parent Feature and Epic

## Epic Issues

### E-001 Intake and Document Normalization

Title:

`[Epic] E-001 Intake and Document Normalization`

Body:

```markdown
## Summary
Users can upload TXT resumes and TXT requirement documents into the system.

## Outcome
Enable v1 ingestion and validation flow for both resume and requirement documents.

## Scope
- Resume upload path (UTF-8 TXT, <=1 MB)
- Requirement upload path (UTF-8 TXT, <=1 MB)
- Input validation and persistence state transitions

## Linked Goals
- G-001

## Dependencies
- File storage
- Access control

## Child Features
- F-001 Resume Upload
- F-002 Requirement Document Upload
- F-003 Input Validation and Storage

## Exit Criteria
- TXT resume and requirement uploads work end to end
```

Labels:

* type:epic
* priority:high
* area:intake
* milestone:m1

### E-002 AI Extraction and Matching

Title:

`[Epic] E-002 AI Extraction and Matching`

Body:

```markdown
## Summary
The system extracts skills and generates ranked matches against requirement documents.

## Outcome
Deliver the core matching capability for v1.

## Scope
- Resume skill extraction
- Requirement text parsing
- Ranking and top-5 recommendation generation

## Linked Goals
- G-001
- G-002

## Dependencies
- E-001 complete
- AI service availability

## Child Features
- F-101 Resume Skill Extraction
- F-102 Requirement Text Parsing
- F-103 Candidate-to-Requirement Matching

## Exit Criteria
- Skills extraction and ranking produce usable recommendations
```

Labels:

* type:epic
* priority:high
* area:matching
* milestone:m2

### E-003 Recruiter Review and Rationale

Title:

`[Epic] E-003 Recruiter Review and Rationale`

Body:

```markdown
## Summary
Recruiters can inspect, accept, reject, or adjust recommendations with clear rationale.

## Outcome
Deliver human-in-the-loop decision workflow for v1.

## Scope
- Recommendation review screen
- Rationale visibility
- Decision capture with audit fields

## Linked Goals
- G-002
- G-003

## Dependencies
- E-002 complete

## Child Features
- F-201 Review Recommendations
- F-202 Recommendation Rationale
- F-203 Decision Capture

## Exit Criteria
- Recruiters can make final decisions with rationale capture
```

Labels:

* type:epic
* priority:high
* area:review
* milestone:m3

### E-004 Telemetry, Security, and Operations

Title:

`[Epic] E-004 Telemetry Security and Operations`

Body:

```markdown
## Summary
The pilot captures metrics, protects HR-sensitive data, and supports monitoring.

## Outcome
Ensure v1 operational readiness and governance.

## Scope
- Event telemetry and tracing
- RBAC and access-denial auditing
- Latency and availability monitoring
- Cost tracking for TXT processing

## Linked Goals
- G-001
- G-002
- G-003

## Dependencies
- E-001
- E-002
- E-003

## Child Features
- F-301 Event Telemetry
- F-302 Access Control
- F-303 Latency and Availability Monitoring
- F-304 Cost Efficiency Tracking

## Exit Criteria
- Telemetry, security, and monitoring are active
```

Labels:

* type:epic
* priority:high
* area:platform
* milestone:m4

## Feature Issues

### Template

```markdown
Title: [Feature] <FEATURE-ID> <FEATURE-NAME>

## Parent Epic
- <EPIC-ID>

## Summary
<FEATURE-DESCRIPTION>

## Linked Requirements
- <FR-IDs>

## Child Stories
- <STORY-IDs>

## Acceptance
- Feature behavior is implemented and verified by child stories
```

### Feature List

* `[Feature] F-001 Resume Upload` -> Epic E-001
* `[Feature] F-002 Requirement Document Upload` -> Epic E-001
* `[Feature] F-003 Input Validation and Storage` -> Epic E-001
* `[Feature] F-101 Resume Skill Extraction` -> Epic E-002
* `[Feature] F-102 Requirement Text Parsing` -> Epic E-002
* `[Feature] F-103 Candidate-to-Requirement Matching` -> Epic E-002
* `[Feature] F-201 Review Recommendations` -> Epic E-003
* `[Feature] F-202 Recommendation Rationale` -> Epic E-003
* `[Feature] F-203 Decision Capture` -> Epic E-003
* `[Feature] F-301 Event Telemetry` -> Epic E-004
* `[Feature] F-302 Access Control` -> Epic E-004
* `[Feature] F-303 Latency and Availability Monitoring` -> Epic E-004
* `[Feature] F-304 Cost Efficiency Tracking` -> Epic E-004

## Story Issues

### Template

```markdown
Title: [Story] <STORY-ID> <SHORT-TITLE>

## Parent Epic
- <EPIC-ID>

## Parent Feature
- <FEATURE-ID>

## User Story
<USER-STORY-TEXT>

## Acceptance Criteria
<ACCEPTANCE-CRITERIA>

## Dependencies
- <DEPENDENCY-STORY-IDs>
```

### Story Pack

#### E-001 Stories

Title:

`[Story] S-001 Upload TXT Resume`

Body:

```markdown
## Parent Epic
- E-001

## Parent Feature
- F-001

## User Story
As an internal employee, I want to upload my resume so that I can be considered for project matching.

## Acceptance Criteria
Given a UTF-8 TXT file up to 1 MB, when upload is submitted, then the file is stored and status is set to Ready for processing within 30 seconds.

## Dependencies
- None
```

Title:

`[Story] S-002 Upload Requirement TXT`

Body:

```markdown
## Parent Epic
- E-001

## Parent Feature
- F-002

## User Story
As a recruiter, I want to upload a requirement document so that matching uses the project description as input.

## Acceptance Criteria
Given a UTF-8 TXT file up to 1 MB, when upload is submitted, then the file is stored and status is set to Ready for matching.

## Dependencies
- None
```

Title:

`[Story] S-003 Enforce Input Validation`

Body:

```markdown
## Parent Epic
- E-001

## Parent Feature
- F-003

## User Story
As the platform, I want strict input validation so that unsupported files do not enter the pipeline.

## Acceptance Criteria
Given an invalid type, invalid encoding, or oversize file, when upload is submitted, then upload is rejected with a specific validation message and no processing job is created.

## Dependencies
- S-001
- S-002
```

#### E-002 Stories

Title:

`[Story] S-101 Extract Skills from Resume`

Body:

```markdown
## Parent Epic
- E-002

## Parent Feature
- F-101

## User Story
As the platform, I want to extract skills from a stored resume so that recruiters can review structured candidate data.

## Acceptance Criteria
Given a resume in Ready for processing state, when extraction completes, then skills are persisted to the candidate profile with extraction timestamp and source resume ID.

## Dependencies
- S-001
```

Title:

`[Story] S-102 Parse Requirement Text`

Body:

```markdown
## Parent Epic
- E-002

## Parent Feature
- F-102

## User Story
As the platform, I want to parse requirement text so that matching uses normalized requirement content.

## Acceptance Criteria
Given a requirement TXT file in Ready for matching state, when parsing completes, then normalized requirement terms are persisted and linked to the request ID.

## Dependencies
- S-002
```

Title:

`[Story] S-103 Generate Top-5 Ranked Recommendations`

Body:

```markdown
## Parent Epic
- E-002

## Parent Feature
- F-103

## User Story
As a recruiter, I want ranked recommendations so that I can quickly identify best-fit employees.

## Acceptance Criteria
Given extracted skills and parsed requirements, when matching runs, then a ranked top-5 list is returned with descending score and a unique candidate per rank.

## Dependencies
- S-101
- S-102
```

#### E-003 Stories

Title:

`[Story] S-201 Review Ranked Candidates`

Body:

```markdown
## Parent Epic
- E-003

## Parent Feature
- F-201

## User Story
As a recruiter, I want to review ranked candidates so that I can decide who should move forward.

## Acceptance Criteria
Given a completed matching run, when recommendations load, then each entry shows candidate name, rank, score, and key matched skills.

## Dependencies
- S-103
```

Title:

`[Story] S-202 View Recommendation Rationale`

Body:

```markdown
## Parent Epic
- E-003

## Parent Feature
- F-202

## User Story
As a recruiter, I want to see recommendation rationale so that I can trust and explain the result.

## Acceptance Criteria
Given a recommendation entry, when I open details, then rationale shows matched skills, missing critical skills, and confidence signal.

## Dependencies
- S-103
```

Title:

`[Story] S-203 Save Recruiter Decision with Audit Fields`

Body:

```markdown
## Parent Epic
- E-003

## Parent Feature
- F-203

## User Story
As a recruiter, I want to save my decision so that final shortlist outcomes are auditable.

## Acceptance Criteria
Given a recommendation entry, when I accept, reject, or adjust and submit rationale, then decision, rationale, reviewer ID, and timestamp are stored and retrievable.

## Dependencies
- S-201
- S-202
```

#### E-004 Stories

Title:

`[Story] S-301 Emit End-to-End Trace Events`

Body:

```markdown
## Parent Epic
- E-004

## Parent Feature
- F-301

## User Story
As an operator, I want upload and match events logged so that I can trace pipeline execution end to end.

## Acceptance Criteria
Given upload, extraction, matching, and review actions, when each action completes, then one trace event with correlation ID is recorded per action.

## Dependencies
- S-001
- S-101
- S-103
- S-203
```

Title:

`[Story] S-302 Enforce RBAC and Audit Denials`

Body:

```markdown
## Parent Epic
- E-004

## Parent Feature
- F-302

## User Story
As a security reviewer, I want role-based access controls enforced so that HR data remains protected.

## Acceptance Criteria
Given a user without required role, when file or recommendation data is requested, then access is denied with HTTP 403 and an audit event is recorded.

## Dependencies
- S-001
- S-002
- S-201
```

Title:

`[Story] S-303 Track Latency and Availability`

Body:

```markdown
## Parent Epic
- E-004

## Parent Feature
- F-303

## User Story
As a product owner, I want latency and availability tracking so that I can evaluate pilot readiness.

## Acceptance Criteria
Given pilot traffic, when dashboard is viewed, then processing p90 latency and service availability for the current week are displayed.

## Dependencies
- S-101
- S-103
```

Title:

`[Story] S-304 Track TXT Processing Cost`

Body:

```markdown
## Parent Epic
- E-004

## Parent Feature
- F-304

## User Story
As a TPM, I want cost tracking for TXT requirement processing so that v1 stays cost-efficient.

## Acceptance Criteria
Given processed requirement documents, when weekly metrics are generated, then average tokens per document and estimated processing cost are reported.

## Dependencies
- S-002
- S-102
```

## Traceability

* Source backlog: docs/backlog/contoso-hr-resume-matching-backlog.md
* Source PRD: docs/prds/contoso-hr-resume-matching.md
