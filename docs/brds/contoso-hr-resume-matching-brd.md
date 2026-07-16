---
title: Contoso HR Resume Matching BRD
description: Business requirements for a resume matching capability that extracts candidate skills and recommends project fit to recruiters
author: Bala Gunaseelan
ms.date: 2026-07-15
ms.topic: overview
---

## Business Context and Background

Contoso HR needs a consistent way to evaluate resumes against project requirements so recruiting teams can reduce manual screening effort and improve matching quality.

## Problem Statement and Business Drivers

### Problem Statement

Recruiters currently spend significant time manually reviewing resumes and mapping candidate skills to project requirements, which creates delays and inconsistent recommendations.

### Business Drivers

* Improve hiring throughput for project staffing
* Increase consistency of candidate-to-project matching decisions
* Reduce manual effort in recruiter screening workflows

## Business Objectives and Success Metrics

| Objective ID | Objective | Baseline | Target | Timeframe |
| --- | --- | --- | --- | --- |
| BO-001 | Reduce recruiter time spent on initial resume screening | 5 business days average time to shortlist | 2 business days average time to shortlist | Within 6 months of v1 rollout |
| BO-002 | Improve quality of shortlist recommendations | No measured acceptance baseline | Recruiters accept at least 70% of top-5 AI recommendations | Within 6 months of v1 rollout |
| BO-003 | Increase transparency of why a candidate is matched | Rationale captured inconsistently | 90% of recommendations include visible match rationale for recruiter review | Within 6 months of v1 rollout |

## Stakeholders and Roles

| Stakeholder | Role | Responsibility |
| --- | --- | --- |
| Contoso HR Leadership | Sponsor | Own business outcomes and approve scope |
| Recruiter | Primary user | Review AI recommendations and make final shortlist decisions |
| Internal Employee | Data contributor | Upload resume content for assessment |
| Project Requestor | Business consumer | Provide project requirements and consume shortlist outcomes |

## Scope

### In Scope

* Resume upload by internal employees as UTF-8 plain text files (TXT) in v1
* AI extraction of skills from resumes
* Project requirement document upload in token-efficient text format for v1 matching input
* AI matching against project requirement documents
* Recruiter review workflow for AI recommendations

### Out of Scope

* Automated hiring decisions without recruiter review
* Payroll, onboarding, or post-hire workflows
* External job board integrations in v1
* Direct integration to downstream project requirement systems in v1
* Resume upload support for PDF and DOCX in v1

## Business Requirements

| Requirement ID | Requirement | Linked Objective | Impacted Stakeholders | Acceptance Criteria | Priority |
| --- | --- | --- | --- | --- | --- |
| BR-001 | The system must allow internal employees to upload resumes as UTF-8 plain text files (TXT) in v1 to minimize token usage and processing cost | BO-001 | Internal Employee, Recruiter | Given a valid TXT resume file up to 1 MB, when uploaded, then the system stores it and marks it ready for processing | High |
| BR-002 | The system must extract skills from each uploaded resume using AI processing | BO-001 | Recruiter | Given a stored resume, when processing completes, then extracted skills are available for review | High |
| BR-003 | The system must allow project requestors or recruiters to upload project requirement documents as UTF-8 plain text files (TXT) in v1 to minimize token usage and processing cost | BO-001 | Recruiter, Project Requestor | Given a valid TXT project requirement file up to 1 MB, when uploaded, then the system stores and marks it available for matching | High |
| BR-004 | The system must match extracted skills against project requirement documents and produce ranked recommendations | BO-002 | Recruiter, Project Requestor | Given project requirement documents and processed resumes, when matching runs, then ranked internal employee recommendations are produced | High |
| BR-005 | The system must provide recruiters with a review interface to accept, reject, or adjust AI recommendations | BO-003 | Recruiter | Given ranked recommendations, when recruiter reviews them, then final recommendation decisions are captured with rationale | High |

## Current and Future Business Processes

### Current State

Recruiters manually read resumes, interpret skills, and compare candidates to project needs using ad hoc criteria and spreadsheet tracking.

### Future State

Internal employees upload token-efficient TXT resumes, project requestors or recruiters upload token-efficient TXT project requirement documents, AI extracts and matches skills, and recruiters make final decisions through a structured review step.

## Data and Reporting Requirements

* Store uploaded TXT resumes and extracted skills metadata
* Store uploaded TXT project requirement documents and extracted requirement metadata
* Capture recommendation rankings and recruiter final decisions
* Report on processing volume, recommendation acceptance rate, and time-to-shortlist

## Benefits and High-Level Economics

* Lower manual screening effort for recruiting teams
* Faster turnaround for staffing project requests
* Better consistency and auditability of recommendation decisions
* Expected cost and ROI details: TODO

## Risks, Assumptions, and Dependencies

### Risks

* Extracted skills quality may vary by resume format and writing style
* Matching recommendations may reflect incomplete or ambiguous project requirement documents
* Future integration to a source system may change requirement data structure and quality

### Assumptions

* Recruiters remain the final decision makers for shortlist selection
* Sufficient historical or curated data is available to evaluate matching quality
* v1 prioritizes token and processing cost efficiency over rich document formatting support
* v1 uses a single UTF-8 TXT format for both resumes and project requirement documents

### Dependencies

* AI service availability for skill extraction and matching
* Input from HR and project requestors to define measurable success metrics
* Availability of project requirement documents in agreed v1 format
* Availability of resume inputs in agreed v1 UTF-8 TXT format

## Approval and Sign-Off

| Approver | Role | Decision | Date |
| --- | --- | --- | --- |
| TODO | Sponsor | Pending | TODO |
