---
title: ADR 0001 - V1 TXT-Only Input Format for Resume and Requirement Processing
description: Decision record for selecting UTF-8 TXT as the only v1 input format to optimize cost, scope, and delivery speed
author: Bala Gunaseelan
ms.date: 2026-07-15
ms.topic: overview
---

## Status

Accepted

## Date

2026-07-15

## Decision Scope

This ADR applies to v1 ingestion for:

* Internal employee resume uploads
* Project requirement document uploads

## Context

Contoso HR is building a v1 PoC to match internal employee skills to project needs using AI. The v1 scope emphasizes low delivery risk and low AI operating cost. Earlier planning artifacts define the workflow and KPI targets, including shortlist cycle-time improvement and recommendation quality.

The ingestion format has direct impact on token volume, extraction reliability, implementation complexity, and release timeline.

## Decision Drivers

* Cost control for LLM processing
* Delivery speed for v1 PoC
* Lower ingestion complexity and operational risk
* Clear migration path to v2 format expansion

## Options Considered

### Option A: Support PDF, DOCX, and TXT in v1

Pros:

* Better immediate user convenience
* Supports current document habits without conversion

Cons:

* Wider parser and extraction failure surface
* Increased engineering and test effort
* More variable token and processing cost

### Option B: Support UTF-8 TXT only in v1

Pros:

* Most predictable and lowest processing cost
* Simplest ingestion, validation, and parsing path
* Higher confidence in meeting PoC timeline

Cons:

* Users must convert files before upload
* Temporary usability trade-off until v2

## Decision

Adopt Option B for v1.

The system will accept only UTF-8 TXT files for both resumes and project requirement documents in v1. File size limit for both inputs is 1 MB.

## Architecture Implications

* Single ingestion validator for encoding, file type, and size
* Shared TXT parsing path for resume and requirement streams
* Lower variance in extraction and matching pipeline behavior
* Simpler telemetry and cost attribution model

## Consequences

Positive:

* Lower token consumption and better cost predictability
* Faster implementation and testing
* Reduced operational complexity in pilot

Negative:

* User pre-conversion overhead
* Potential conversion quality issues from source documents

Mitigation plan:

* Publish TXT conversion guidance for users
* Enforce strict upload validation and clear error messages
* Add v2 roadmap epic for PDF and DOCX support

## Guardrails

* Recruiters remain final decision makers
* Access control is mandatory for all uploaded and derived HR data
* Event telemetry must capture upload, extraction, matching, and review actions

## v2 Exit and Expansion Criteria

Format expansion to PDF and DOCX is allowed when all criteria are met:

* v1 pilot demonstrates stable KPI trend for one full review cycle
* Sponsor approves processing cost envelope for expanded formats
* Quality and reliability tests pass for PDF and DOCX parsing and extraction

## Related Decisions

No prior ADRs in repository.

## References

* docs/brds/contoso-hr-resume-matching-brd.md
* docs/prds/contoso-hr-resume-matching.md
* docs/backlog/contoso-hr-resume-matching-backlog.md
