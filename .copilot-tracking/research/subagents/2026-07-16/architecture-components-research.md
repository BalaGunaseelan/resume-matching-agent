---
title: Resume-Matching v1 Architecture Components Research
description: Source-backed technical component inventory, boundaries, data flow, and implementation guidance for the Contoso HR resume-matching v1 PoC
author: GitHub Copilot Researcher Subagent
ms.date: 2026-07-16
ms.topic: reference
---

## Metadata
* Date: 2026-07-16
* Status: Complete
* Scope: Enumerate technical components and architecture boundaries for v1 based on approved workspace artifacts.
* Output file: .copilot-tracking/research/subagents/2026-07-16/architecture-components-research.md

## Research Topics
1. What technical components are required for v1 across UI, API, ingestion, AI extraction, matching engine, persistence, auth/security, observability, deployment, CI/CD, and governance?
2. What component boundaries and data flow are recommended for a practical v1 implementation?
3. What implementation notes and pitfalls should be considered for delivery quality, risk reduction, and maintainability?

## Primary Workspace Evidence
* docs/brds/contoso-hr-resume-matching-brd.md
* docs/prds/contoso-hr-resume-matching.md
* docs/backlog/contoso-hr-resume-matching-backlog.md
* docs/decisions/2026-07-15-v1-txt-only-input-format-v01.md

## Source-Backed Findings

### 1. Required Technical Components for v1

#### 1.1 Client and UI Components
* Employee upload UI for resume TXT files (UTF-8, <=1 MB), aligned with BR-001 and FR-001.
* Recruiter and requestor upload UI for requirement TXT files (UTF-8, <=1 MB), aligned with BR-003 and FR-003.
* Recruiter review UI for ranked recommendations, rationale visibility, and decision capture (accept, reject, adjust), aligned with BR-005 and FR-005/FR-006.
* Validation UX for type, encoding, and file-size errors with explicit user messages, aligned with S-003.

Evidence:
* BRD In-Scope and Business Requirements BR-001 through BR-005.
* PRD Functional Requirements FR-001 through FR-006.
* Backlog E-001 and E-003 stories S-001, S-002, S-003, S-201, S-202, S-203.
* ADR decision enforces v1 TXT-only path.

#### 1.2 API Layer Components
* API gateway or backend-for-frontend endpoint surface for upload, processing status, recommendation retrieval, and recruiter decisions.
* Request validation and normalization layer enforcing UTF-8 TXT and 1 MB limit.
* Correlation ID propagation for end-to-end observability and auditable traceability (required by S-301).
* Standardized machine-readable error contract for client integration stability.

Evidence:
* PRD NFR-005 requires 100 percent event logging across upload, extraction, match, and review.
* Backlog S-301 requires trace events with correlation ID per action.
* Backlog S-302 requires explicit 403 behavior and audit logging.

#### 1.3 Ingestion Components
* Shared ingestion validator service (single path for resumes and requirements) for extension, encoding, and size checks.
* File storage service for original TXT artifacts and metadata state transitions (Ready for processing, Ready for matching).
* Metadata persistence for document identity, owner, timestamps, and processing state.

Evidence:
* ADR architecture implications specify a single ingestion validator and shared TXT parsing path.
* E-001/F-003 and stories S-001 through S-003 require strict validation and state updates.

#### 1.4 AI Extraction Components
* Resume skill extraction worker or service that runs asynchronously on stored resumes.
* Skill schema normalizer for extracted skill canonicalization (for consistent matching quality).
* Extraction result store with provenance fields: source resume ID and extraction timestamp.

Evidence:
* BR-002, FR-002, S-101 explicitly require persisted extracted skills with timestamps and source link.
* PRD risks R-001 and dependencies identify quality variance and AI service dependency risk.

#### 1.5 Matching Engine Components
* Requirement parsing and term normalization component for requirement TXT.
* Candidate-to-requirement ranking engine producing top-5 unique candidates with descending scores.
* Rationale generator producing matched skills, missing critical skills, and confidence indicators.

Evidence:
* BR-004, FR-004, S-102, S-103, S-202.
* KPI target G-002 requires recruiter acceptance of top-5 recommendations.
* G-003 and FR-006 require visible rationale for trust.

#### 1.6 Persistence Components
* Object storage for raw uploaded TXT artifacts.
* Relational or document store for:
	* candidate profiles and extracted skills,
	* requirement normalization outputs,
	* matching outputs and scores,
	* recruiter decisions and rationale,
	* telemetry correlation identifiers.
* Reporting store or materialized views for KPI dashboards (time-to-shortlist, acceptance rate, rationale visibility).

Evidence:
* BRD Data and Reporting Requirements list required stored entities.
* PRD instrumentation and metrics tables define events and KPI sources.

#### 1.7 Auth and Security Components
* Central identity provider integration using OIDC-based SSO for authenticated access.
* Role-based authorization enforcement for employee, recruiter, and requestor actions.
* Access-control middleware returning 403 for unauthorized requests and emitting audit events.
* Data protection controls for HR-sensitive data in transit and at rest.

Evidence:
* PRD NFR-003 requires 100 percent authenticated access and HR-sensitive data protection.
* Backlog S-302 defines authorization testable behavior (HTTP 403 + audit event).
* ADR guardrails require mandatory access control for uploaded and derived HR data.

Relevant official guidance:
* OIDC Core defines interoperable identity layer on OAuth 2.0 and ID token validation requirements.
	* https://openid.net/specs/openid-connect-core-1_0.html

#### 1.8 Observability Components
* Distributed tracing with correlation IDs across ingestion, extraction, matching, and review workflows.
* Metrics pipeline for latency, availability, throughput, and cost indicators.
* Structured logs and audit events for security and governance traceability.
* Alerting for processing failures and availability degradations.

Evidence:
* PRD NFR-001, NFR-002, NFR-005 and Operational Considerations (monitoring and alerting).
* Backlog S-301 and S-303.

Relevant official guidance:
* OpenTelemetry signal model supports traces, metrics, logs, and baggage for correlated observability.
	* https://opentelemetry.io/docs/concepts/signals/

#### 1.9 Deployment Components
* Controlled pilot environment with internal-only access.
* Separate app runtime, storage, and telemetry resources with environment-specific configuration.
* Feature flags or kill switch to disable matching display while preserving manual workflow fallback.

Evidence:
* PRD Operational Considerations specify pilot-only controlled access and rollback switch.
* PRD rollout milestones M1 through M4.

#### 1.10 CI/CD Components
* Build and release pipeline with:
	* linting and tests,
	* security checks (dependencies, IaC where used),
	* signed provenance and artifact integrity checks,
	* environment promotion controls and rollback.
* Automated policy checks for upload constraints and auth assertions in test suites.

Evidence:
* High priority operations and security scope in E-004.
* NFR-003, NFR-005, and pilot reliability requirements imply release discipline.

Relevant official guidance:
* SLSA Build levels define provenance maturity from L1 (provenance exists) to L3 (hardened builds).
	* https://slsa.dev/spec/v1.0/levels

#### 1.11 Governance Components
* Prompt and model governance for extraction and matching prompt versions, tuning notes, and change history.
* Decision auditability for recruiter override and rationale capture.
* AI risk management controls covering transparency, bias checks, and risk treatment workflow.
* Data lifecycle controls for retention, access monitoring, and deletion policy alignment.

Evidence:
* BRD objective BO-003 and PRD G-003/FR-006 require rationale transparency.
* PRD privacy and threat considerations mandate restricted handling of HR-sensitive data.
* Open questions in PRD imply governance continuity into phase-2 integration.

Relevant official guidance:
* NIST AI RMF provides voluntary framework to manage AI risk and trustworthiness across design, development, use, and evaluation.
	* https://www.nist.gov/itl/ai-risk-management-framework

### 2. Recommended Component Boundaries

Recommended v1 bounded components:

1. Experience Boundary
* Web UI for employees, recruiters, and requestors.
* No direct data-store access.
* Uses API contracts only.

2. Access and Policy Boundary
* Authentication and authorization middleware.
* Role checks and scope checks.
* Centralized denial and audit logic.

3. Intake Boundary
* Upload handlers and input validation.
* TXT-only rules and state machine.
* Raw storage handoff.

4. Extraction Boundary
* Async AI extraction pipeline.
* Output schema normalization.
* Quality and retry handling.

5. Matching Boundary
* Requirement parsing and normalized term generation.
* Ranking algorithm and score model.
* Explanation and confidence output generation.

6. Review and Decision Boundary
* Recommendation retrieval optimized for recruiter workflow.
* Decision write path with rationale and reviewer identity.

7. Data Boundary
* Persistent stores for artifacts, metadata, results, decisions.
* Read models for KPI and operations dashboards.

8. Platform Operations Boundary
* Telemetry ingestion and dashboards.
* Alerting and incident hooks.
* Deployment and release controls.

Why these boundaries are recommended:
* They mirror the backlog epic decomposition E-001 through E-004.
* They reduce change coupling between ingestion constraints (ADR TXT-only) and AI logic.
* They support phase-2 expansion (PDF or DOCX, external system integrations) with minimal blast radius.

### 3. Recommended v1 Data Flow

1. Employee uploads resume TXT via UI.
2. Intake API validates extension, encoding, and size.
3. System stores raw TXT and metadata status = Ready for processing.
4. Extraction worker consumes ready resumes and persists normalized skill profile.
5. Recruiter or requestor uploads requirement TXT.
6. Intake API validates requirement file and sets status = Ready for matching.
7. Requirement parser normalizes terms and persists requirement model.
8. Matching engine computes ranked top-5 unique candidates with scores and rationale.
9. Recruiter review UI displays rank, score, matched and missing skills, confidence signal.
10. Recruiter submits accept, reject, adjust decisions with rationale.
11. System persists decisions and emits telemetry and audit events.
12. KPI reporting aggregates cycle time, acceptance rate, and rationale visibility.

Cross-cutting behavior through all steps:
* AuthN and AuthZ checks on every endpoint.
* Correlation ID propagation for each transaction.
* Structured logs, traces, and metrics emissions.

### 4. Practical Implementation Notes

#### 4.1 Input and Ingestion
* Enforce allowlist of file extension and validate actual content assumptions for TXT.
* Validate UTF-8 decode before persistence and reject invalid encodings with explicit user errors.
* Avoid trusting client content-type header as authoritative.
* Use generated internal object IDs and decouple from user-provided filenames.
* Keep upload processing async after minimal synchronous validation to protect API responsiveness.

Relevant official guidance:
* OWASP File Upload Cheat Sheet: extension allowlist, content-type skepticism, size limits, auth checks, storage isolation, and defense-in-depth.
	* https://cheatsheetseries.owasp.org/cheatsheets/File_Upload_Cheat_Sheet.html

#### 4.2 API and Error Contracts
* Use stable API contracts for uploads, status, recommendations, and decisions.
* Use machine-readable problem responses (Problem Details for HTTP APIs) for validation and policy errors.
* Include operation IDs and correlation IDs in error payloads for supportability.

Relevant official guidance:
* RFC 7807 (obsoleted by RFC 9457) defines problem detail format and `application/problem+json` media type.
	* https://www.rfc-editor.org/rfc/rfc7807

#### 4.3 Extraction and Matching Quality
* Version prompts and extraction templates; store prompt version with extraction output.
* Build representative test corpus for resume and requirement variability.
* Track extraction confidence and missingness signals to guide recruiter trust and tuning.
* Keep matching logic deterministic for a fixed extraction output to aid debugging and acceptance analysis.

#### 4.4 Security and Privacy
* Use OIDC enterprise SSO for identity and role claims.
* Enforce least-privilege data access with role scopes.
* Encrypt data in transit and at rest.
* Avoid logging raw resume or requirement content in operational logs.
* Emit immutable audit events for review decisions and access denials.

#### 4.5 Observability and Operations
* Instrument each pipeline stage with traces, metrics, and logs.
* Track p90 processing latency to align with NFR-001 target.
* Alert on extraction and matching failure-rate spikes.
* Capture cost telemetry (tokens or model call cost estimates) to validate NFR-004 cost goals.

#### 4.6 CI/CD and Supply Chain
* Generate build provenance and sign artifacts in CI.
* Gate releases on test, security scan, and policy checks.
* Use environment promotion with explicit approvals for pilot stages.
* Prefer hosted hardened builds over local ad hoc releases.

### 5. Pitfalls and Failure Modes

1. Hidden format drift in input data
* Risk: Teams upload pseudo-TXT or badly converted files that pass extension checks but degrade extraction.
* Mitigation: strict UTF-8 decoding, quality checks, user guidance, and rejection feedback.

2. Prompt and model drift without traceability
* Risk: recommendation behavior changes silently and breaks recruiter trust.
* Mitigation: versioned prompts, model version logging, regression evaluation set.

3. Weak rationale quality
* Risk: recommendations become hard to approve, reducing acceptance KPI.
* Mitigation: explicit rationale schema with matched and missing skills, confidence indicators.

4. Authorization gaps in read endpoints
* Risk: unauthorized exposure of HR-sensitive content.
* Mitigation: centralized policy middleware, endpoint-level tests, audit event assertions.

5. Overloaded synchronous APIs
* Risk: high upload latency and timeout under pilot load.
* Mitigation: async processing with queue or worker model and clear status model.

6. Missing correlation IDs
* Risk: impossible end-to-end troubleshooting during incidents.
* Mitigation: mandatory correlation ID propagation and validation in middleware.

7. Unmanaged cost growth
* Risk: token or compute costs increase despite TXT-only strategy.
* Mitigation: cost metrics dashboard, prompt efficiency reviews, document-size checks.

### 6. Recommended v1 Target Architecture Summary

Minimum viable architecture for v1 PoC:

* UI: internal web app with role-based views.
* API: REST service with OIDC auth integration and policy middleware.
* Ingestion: TXT validator + object storage + state metadata.
* Async processing: extraction worker and matching worker.
* Data: persistent stores for skills, requirements, rankings, decisions.
* Observability: traces + metrics + logs + audit events.
* Ops: pilot deployment with rollback switch and alerts.
* CI/CD: provenance-aware release pipeline with security checks.
* Governance: rationale transparency, prompt and model versioning, AI risk controls.

This architecture is directly aligned to BRD scope, PRD FR and NFR targets, backlog epics and stories, and ADR TXT-only constraints.

## Official Documentation References

1. OpenID Connect Core 1.0
* https://openid.net/specs/openid-connect-core-1_0.html

2. OWASP File Upload Cheat Sheet
* https://cheatsheetseries.owasp.org/cheatsheets/File_Upload_Cheat_Sheet.html

3. OpenTelemetry Signals
* https://opentelemetry.io/docs/concepts/signals/

4. Problem Details for HTTP APIs (RFC 7807, obsoleted by RFC 9457)
* https://www.rfc-editor.org/rfc/rfc7807

5. SLSA Security Levels (Build Track)
* https://slsa.dev/spec/v1.0/levels

6. NIST AI Risk Management Framework
* https://www.nist.gov/itl/ai-risk-management-framework

## Assumptions

* v1 remains internal-only pilot with controlled access.
* Resume and requirement inputs remain strictly UTF-8 TXT <=1 MB for v1.
* Recruiters remain final decision-makers and AI only assists.
* Existing identity provider can supply role claims for authorization.
* Team can stand up asynchronous workers for extraction and matching.

## Open and Clarifying Questions

1. Identity and role model
* Which exact RBAC roles and permissions are required at API endpoint granularity?

2. Data retention and deletion
* What are retention windows for raw resumes, extracted skills, and recruiter decisions?

3. Matching method details
* Is v1 ranking purely rules-based, embedding-based, LLM-scored, or hybrid?

4. KPI baselining
* How will baseline capture be operationalized during the first pilot weeks for accurate before and after comparison?

5. Integration roadmap
* Which downstream system is phase-2 target, and what contract constraints should v1 APIs preserve now?

6. Security controls depth
* Are additional controls required for antivirus or malware scanning even for TXT uploads in the pilot?

## Top Recommendations

1. Implement strict TXT ingestion boundary first, with explicit validation and failure messaging, then freeze contract.
2. Build extraction and matching as asynchronous bounded services with durable state transitions.
3. Treat rationale generation as a first-class output schema, not a display afterthought.
4. Enforce centralized authorization and audit logging across all read and write endpoints.
5. Instrument traces, metrics, and logs from day one with mandatory correlation IDs.
6. Establish model and prompt governance with versioned artifacts before pilot launch.
7. Use provenance-aware CI/CD controls to reduce release and supply chain risk.

## Recommended Follow-On Research (Not Executed in This Session)

* Select concrete tech stack options (for example, minimal Java or Python service blueprint) and map to team skills.
* Define canonical skill taxonomy and requirement term ontology for matching stability.
* Draft API contract shapes and example Problem Details payloads.
* Define non-functional test strategy for NFR-001 through NFR-005 validation.
* Create pilot operations runbook for alerts, incident triage, and rollback criteria.
