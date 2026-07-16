---
title: ADR Draft - V1 TXT-Only Input Format for Resume and Requirement Processing
description: Working draft ADR for selecting UTF-8 TXT as the single v1 input format to optimize AI processing cost and delivery speed
author: Bala Gunaseelan
ms.date: 2026-07-15
ms.topic: overview
---

## Decision Summary

For v1, the system accepts only UTF-8 TXT files for both resume inputs and project requirement inputs.

## Context

Contoso HR is building a v1 PoC for internal talent matching with the following flow:

* Internal employees upload resumes
* AI extracts skills
* AI matches skills to project requirements
* Recruiters review and finalize recommendations

The team prioritized fast time-to-value, lower implementation complexity, and lower model processing cost.

## Decision Drivers

* Minimize token consumption and LLM processing cost
* Reduce ingestion and parsing complexity in v1
* Improve operational predictability for a pilot release
* Preserve a clear path to broader file format support in v2

## Options Considered

### Option A: Multi-format support in v1 (PDF, DOCX, TXT)

Pros:

* Better user convenience on day one
* Less pre-conversion burden on uploaders

Cons:

* Higher extraction complexity and error handling
* Higher run-time and token cost variability
* Larger v1 scope and delivery risk

### Option B: TXT-only in v1 for both resumes and requirements

Pros:

* Lowest ingestion complexity
* Better token efficiency and cost control
* Faster delivery for PoC timeline

Cons:

* User pre-processing required for non-TXT source files
* Potential early adoption friction

## Decision

Choose Option B.

The product accepts only UTF-8 TXT files for resumes and project requirement documents in v1, each limited to 1 MB.

## Consequences

Positive consequences:

* Predictable and lower AI processing cost
* Reduced engineering effort for ingestion and parsing
* Faster pilot execution and iteration cycle

Negative consequences:

* Manual conversion needed for users with PDF or DOCX files
* Potential quality loss if conversion is done poorly

Mitigations:

* Provide upload guidance and a conversion checklist
* Validate UTF-8 encoding and file quality at upload
* Include format expansion as a v2 milestone

## v2 Transition Criteria

Enable PDF and DOCX support when:

* v1 KPI stability is demonstrated for at least one pilot cycle
* Cost envelope is approved by sponsor
* Ingestion quality tests for PDF and DOCX pass agreed thresholds

## Related Artifacts

* docs/brds/contoso-hr-resume-matching-brd.md
* docs/prds/contoso-hr-resume-matching.md
* docs/backlog/contoso-hr-resume-matching-backlog.md
