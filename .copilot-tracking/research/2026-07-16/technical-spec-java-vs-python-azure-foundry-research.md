<!-- markdownlint-disable-file -->
# Task Research: Technical Specification for Resume Matching App (Java vs Python, Azure Foundry)

Research to determine the technical components required to build the Contoso HR resume-matching application, evaluate Java and Python implementation approaches, and recommend one architecture with Azure Foundry model integration.

## Task Implementation Requests

* Identify required technical components across frontend, backend, storage, AI integration, security, observability, and deployment
* Compare Java and Python as backend implementation options for the v1 scope
* Define Azure Foundry integration approach for model calls and prompt orchestration
* Produce a technical specification suitable for moving into implementation planning

## Scope and Success Criteria

* Scope: Application architecture, runtime stack, service boundaries, Azure services, model integration pattern, security and operations baseline for v1
* Assumptions:
  * v1 input format is UTF-8 TXT for both resumes and requirement documents
  * Recruiter remains final decision authority in decision workflow
  * Azure Foundry is available for model inferencing from backend
* Success Criteria:
  * Technical components are explicitly enumerated and mapped to responsibilities
  * Java and Python alternatives are evaluated with trade-offs and one selected approach
  * Selected approach contains implementation-ready architecture and component decisions

## Outline

1. Existing Project and Artifact Findings
2. Technical Components Inventory
3. Azure Foundry Integration Design
4. Java vs Python Comparative Analysis
5. Selected Approach and Technical Specification
6. Implementation Risks and Next Steps

## Potential Next Research

* Azure Foundry SDK and runtime integration specifics by language
  * Reasoning: Select concrete implementation path and libraries
  * Reference: Azure AI Foundry documentation
* Production deployment options for low-complexity v1
  * Reasoning: Ensure realistic hosting recommendation
  * Reference: Azure App Service / Container Apps guidance

## Research Executed

### File Analysis

* docs/brds/contoso-hr-resume-matching-brd.md
  * v1 scope is internal employee resume upload, skills extraction, matching, and recruiter review
* docs/prds/contoso-hr-resume-matching.md
  * Includes FR and NFR set with telemetry and security expectations
* docs/backlog/contoso-hr-resume-matching-backlog.md
  * Provides epic and story decomposition for implementation order
* docs/decisions/2026-07-15-v1-txt-only-input-format-v01.md
  * Confirms v1 TXT-only input decision and v2 expansion strategy

### Code Search Results

* "resume", "matching", "azure", "foundry"
  * Repository currently contains planning docs and no application code implementation yet

### External Research

* runSubagent: Architecture components and operational controls
  * Source file: .copilot-tracking/research/subagents/2026-07-16/architecture-components-research.md
* runSubagent: Java vs Python decision matrix
  * Source file: .copilot-tracking/research/subagents/2026-07-16/java-vs-python-research.md
* runSubagent: Azure Foundry backend integration
  * Source file: .copilot-tracking/research/subagents/2026-07-16/azure-foundry-integration-research.md

### Project Conventions

* Standards referenced: markdown planning artifacts and ADR-driven decision capture
* Instructions followed: Task Researcher phased workflow and repository planning artifacts

## Key Discoveries

### Project Structure

The repository currently contains planning artifacts and no application source implementation. Existing artifacts define business scope, product requirements, backlog decomposition, and one accepted ADR for v1 TXT-only ingestion.

Key artifacts:

* docs/brds/contoso-hr-resume-matching-brd.md
* docs/prds/contoso-hr-resume-matching.md
* docs/backlog/contoso-hr-resume-matching-backlog.md
* docs/decisions/2026-07-15-v1-txt-only-input-format-v01.md

### Implementation Patterns

Required v1 component boundaries:

* Experience boundary: employee upload and recruiter review UI
* Access policy boundary: OIDC auth, RBAC authorization, audit events
* Intake boundary: TXT validation, encoding checks, metadata state transitions
* Extraction boundary: async skill extraction worker
* Matching boundary: requirement parsing, ranking, rationale generation
* Review boundary: decision capture and persistence
* Data boundary: object storage + structured persistence + KPI read model
* Platform boundary: telemetry, alerting, rollout controls, CI/CD checks

### Complete Examples

```text
Ingestion state model (v1)

Uploaded -> Validated -> ReadyForProcessing -> Extracted
         -> ReadyForMatching -> Ranked -> Reviewed

Rejection path:
Uploaded -> Rejected(type|encoding|size)
```

### API and Schema Documentation

Recommended API slices:

* POST /api/resumes/upload
* POST /api/requirements/upload
* GET /api/matches/{requestId}
* POST /api/matches/{requestId}/decisions
* GET /api/processing/{artifactId}/status

Recommended rationale payload schema:

* candidateId
* rank
* score
* matchedSkills[]
* missingCriticalSkills[]
* confidence
* modelDeployment
* promptVersion

### Configuration Examples

```text
Runtime configuration

AZURE_FOUNDRY_PROJECT_ENDPOINT=https://<resource>.services.ai.azure.com/api/projects/<project>
AZURE_CLIENT_ID=<managed-identity-client-id-optional>
MODEL_DEPLOYMENT_SKILL_EXTRACTION=<deployment-name>
MODEL_DEPLOYMENT_MATCHING=<deployment-name>
PROMPT_VERSION_SKILL_EXTRACTION=v1.0.0
PROMPT_VERSION_MATCHING=v1.0.0
MAX_UPLOAD_SIZE_BYTES=1048576
ALLOWED_FILE_FORMAT=txt
```

## Technical Scenarios

### Scenario A: Java Backend with Azure Foundry Integration

Description:

Implement v1 with Java (Spring Boot), async workers, and Foundry client adapter.

Requirements:

* Must satisfy FR-001 through FR-006 and NFR-001 through NFR-005
* Must enforce TXT-only validation and 1 MB limit
* Must provide full auditability and traceability

Preferred approach:

* Use Spring Boot API + worker pattern
* Use Azure identity and Foundry Java SDK/OpenAI-compatible client
* Use strict contract schemas for rationale and decisions

Advantages:

* Strong compile-time contracts and enterprise governance
* Mature operational and testing patterns

Limitations:

* Slower v1 AI iteration loop compared with Python
* Higher initial implementation overhead for PoC speed target

### Scenario B: Python Backend with Azure Foundry Integration

Description:

Implement v1 with Python (FastAPI), async workers, and Foundry client adapter.

Requirements:

* Must satisfy FR-001 through FR-006 and NFR-001 through NFR-005
* Must enforce TXT-only validation and 1 MB limit
* Must provide full auditability and traceability

Preferred approach:

* FastAPI API service + worker queue for extraction and matching
* Azure identity + Foundry project endpoint with OpenAI-compatible client path
* Structured response schema validation and correlation-ID observability

Advantages:

* Highest delivery velocity for AI-centric PoC
* Strong AI integration ecosystem and lower iteration friction
* Best alignment with v1 scope and schedule pressure

Limitations:

* Requires strict lint/type/test discipline to avoid architecture drift

### Scenario C: Hybrid Service Split (Python AI services + Java core API)

Description:

Split services by language to optimize for strengths.

Preferred approach:

* Java for core API/governance, Python for extraction/matching

Advantages:

* Can leverage existing Java platform and Python AI agility

Limitations:

* Over-complex for v1 team size and timeline
* Adds inter-service coordination and operational overhead early

#### Considered Alternatives

Alternative A (Java primary) was not selected for v1 due to slower AI feature iteration and time-to-value risk.

Alternative C (hybrid) was not selected due to architecture and operations complexity that is disproportionate for a v1 PoC.

## Comparative Decision Matrix

Weighted outcome from subagent analysis:

* Python: 4.18
* Java: 3.82

Highest-weight differentiators:

* Development speed for PoC delivery
* AI integration velocity and ecosystem fit
* Implementation cost-to-value under v1 constraints

## Selected Approach and Technical Specification

Selected approach: Python backend with Azure Foundry integration, plus explicit architecture controls for security, observability, and governance.

### Technical Specification

System style:

* Modular monolith for v1 with async worker boundaries

Primary services/components:

* Web UI (employee upload, recruiter review)
* Backend API (FastAPI)
* Ingestion validator (TXT/UTF-8/size)
* Extraction worker (Foundry model call)
* Requirement parser and matching worker
* Recommendation/rationale builder
* Decision and audit store
* Telemetry pipeline (traces, metrics, logs)

Data stores:

* Object storage for raw TXT artifacts
* Relational/document DB for extracted skills, requirements, rankings, decisions
* KPI read model for cycle time, acceptance rate, and rationale visibility

Security baseline:

* Microsoft Entra ID auth with managed identity for backend to Foundry
* RBAC with role-scoped endpoint access
* 403 on unauthorized access and audit event per denial

Azure Foundry integration pattern:

* Use Foundry project endpoint as default backend surface
* Use Entra token scope https://ai.azure.com/.default
* Track model deployment and prompt version on all extraction/matching outputs
* Retry transient failures only (408, 429, 5xx) with Retry-After support

Observability baseline:

* Correlation ID required across all flows
* Event telemetry for upload, extraction, matching, and review
* KPI dashboards and cost dashboards with token and latency metrics

Operational envelope:

* Pilot deployment with internal-only access
* Rollback/feature disable switch for recommendation display
* CI/CD gates for tests, policy checks, and artifact integrity

### Implementation Details

```text
Suggested service modules

/api
  /upload
  /matching
  /review
/workers
  /extract_skills
  /parse_requirements
  /rank_candidates
/domain
  /schemas
  /policies
  /rationale
/platform
  /identity
  /telemetry
  /foundry_client
```

```text
Minimum acceptance gates before pilot

1) TXT-only validation with UTF-8 checks and explicit errors
2) End-to-end traceability with correlation IDs
3) 403 + audit behavior validated on restricted endpoints
4) Top-5 ranking contract and rationale schema regression tests
5) KPI and token-cost dashboards active
```

## Risks and Mitigations

* Risk: Input conversion quality affects extraction
  * Mitigation: strict validation and upload guidance template
* Risk: Prompt/model drift affects recommendation trust
  * Mitigation: prompt versioning, output contract tests, controlled rollouts
* Risk: Cost growth despite TXT-only scope
  * Mitigation: token budget alerts and weekly cost review
* Risk: Security gaps on read endpoints
  * Mitigation: centralized authorization middleware and audit checks

## Potential Next Research

* Hosting target selection deep dive (App Service vs Container Apps vs AKS)
  * Reasoning: finalize deployment topology and managed identity details
  * Reference: Azure hosting options and platform policy
* KPI baseline capture design
  * Reasoning: reduce uncertainty in pilot success measurement
  * Reference: PRD metrics section and telemetry plan
* v2 format expansion strategy (PDF/DOCX)
  * Reasoning: prepare controlled expansion path with quality gates
  * Reference: ADR v2 criteria

## Key Discoveries

### Project Structure

To be updated after subagent execution.

### Implementation Patterns

To be updated after subagent execution.

### Complete Examples

```text
Pending
```

### API and Schema Documentation

To be updated after subagent execution.

### Configuration Examples

```text
Pending
```

## Technical Scenarios

### Scenario A: Java Backend with Azure Foundry Integration

Pending evaluation.

### Scenario B: Python Backend with Azure Foundry Integration

Pending evaluation.

### Scenario C: Hybrid Service Split

Pending evaluation.
