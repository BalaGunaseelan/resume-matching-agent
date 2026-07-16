# Azure Foundry Integration Research: Backend Model Invocation for Resume Matching

## Research Metadata
- Date: 2026-07-16
- Scope: Backend integration architecture for Azure Foundry model invocation in a resume-matching application
- Status: Complete

## Research Questions
1. What is the technical integration pattern from backend service to Azure Foundry (auth, endpoint configuration, prompt/version management, response handling, retries, cost telemetry)?
2. What security posture, observability pattern, and failure modes are recommended?
3. What language-specific guidance exists for Java and Python SDK/client options?

## Findings (In Progress)

## Findings

### 1) Technical integration pattern: backend service -> Azure Foundry

#### Recommended endpoint and client pattern
- Use the Foundry project endpoint as the primary backend integration surface for resume-matching inference, especially when you need Foundry features beyond raw OpenAI compatibility.
	- Project endpoint format: `https://<resource-name>.services.ai.azure.com/api/projects/<project-name>`.
	- Foundry SDK exposes:
		- Project client (project-native operations: setup/config/connections/tracing).
		- OpenAI-compatible client (Responses API style model invocation on project endpoint `/openai`).
- Use direct Azure OpenAI endpoint (`https://<resource>.openai.azure.com/openai/v1`) selectively when you need full OpenAI surface or embeddings path with best compatibility/latency.
	- Important nuance from Foundry SDK overview: embeddings currently are not routed via project endpoint in that guidance.

#### Authentication and authorization flow
- Preferred for production: Microsoft Entra ID token auth with scope `https://ai.azure.com/.default`.
- Use `DefaultAzureCredential` chain for local dev + cloud runtime portability.
- In Azure hosting, use managed identity (system-assigned or user-assigned), then assign least-privilege Foundry RBAC role.
- API keys are supported, but only recommended for rapid prototyping or isolated non-production usage due to coarse-grained access and audit limitations.

#### Endpoint configuration pattern
- For Foundry-native integration:
	- Keep a single project endpoint in backend config.
	- Derive OpenAI-compatible client from project client for runtime inference.
- For direct Azure OpenAI usage:
	- Configure resource endpoint and deployment name separately.
	- Use deployment name as model identifier in requests.
- Validate endpoint shape early during startup and fail-fast on malformed URLs to avoid runtime 404s.

#### Prompt and version management pattern
- Treat prompts as versioned artifacts in source control (prompt ID, version, owner, evaluation score metadata).
- Use model deployment names and maintain explicit mapping:
	- `task -> model deployment -> prompt version`.
- For safe rollouts:
	- Blue/green or canary route at gateway or service layer.
	- Keep same model+version across failover backends to avoid behavior drift.
- For resume-matching specifically:
	- Maintain stable JSON schema outputs (match score, rationale, missing skills, confidence).
	- Use contract tests for output schema compatibility during prompt/model updates.

#### Response handling pattern
- Parse and validate structured output before committing downstream decisions.
- Persist request/response metadata for traceability:
	- request ID (`x-request-id` / SDK request id field), model deployment, token usage, latency, outcome class.
- Handle content filtering and policy blocks as first-class outcomes (not generic failures).
- Enforce idempotency key for retry-safe business operations around model invocation.

#### Retries and resilience pattern
- Retry transient errors only:
	- 408, 429, 5xx, connection errors.
- Honor `Retry-After` semantics for throttling.
- Use exponential backoff with bounded attempts and bounded total retry duration.
- Add circuit breaker for repeated throttling or backend failures.
- For multi-backend/gateway topologies, keep backend pool health and temporarily evict unhealthy routes.

#### Cost and usage telemetry pattern
- Capture both app-level and platform-level token/latency metrics:
	- App-level: per-request input/output/total tokens, business context (tenant/job id), success/failure class.
	- Azure Monitor metrics: `InputTokens`, `OutputTokens`, `TotalTokens`, `AzureOpenAIRequests`, `AzureOpenAITimeToResponse`, `AzureOpenAIAvailabilityRate`, plus deployment/model dimensions.
- Build per-tenant/per-feature chargeback from dimensions (deployment/model/operation/region/consumer key).
- Add token budget alerts and anomaly detection on sudden token-per-request spikes.

### 2) Recommended security posture, observability, and failure modes

#### Security posture (recommended baseline)
- Identity:
	- Production backend -> managed identity -> Foundry resource/project via RBAC.
	- Avoid static API keys in production call path.
- Authorization:
	- Use least privilege built-in roles (`Foundry User` where possible); use custom roles when built-ins are too broad.
- Secret handling:
	- If keys/secrets are unavoidable (legacy/external), store in Azure Key Vault.
	- Never place credentials in prompts, traces, or logs.
- Network:
	- Prefer private networking with gateway + Private Link where enterprise posture requires it.
	- Prevent backend bypass when introducing a gateway.
- Governance:
	- Use Azure Policy for deployment consistency across regions/environments.

#### Observability pattern
- Foundry tracing:
	- Connect Application Insights to Foundry project for server-side traces (no code changes for supported hosted scenarios).
- Distributed tracing:
	- Use OpenTelemetry semantic conventions for GenAI spans.
- Operational dashboards:
	- Track token usage, latency, run success rate, evaluation scores, red-team outcomes.
- Logging model:
	- Structured logs with request id, correlation id, model deployment, prompt version, retry count, status code, and latency buckets.
- Data controls:
	- Redact PII and sensitive fields before telemetry export.
	- Apply role-scoped access to App Insights/Log Analytics data.

#### Failure modes and handling
- 401 Unauthorized:
	- Wrong token scope, expired token, or invalid key.
	- Fix: ensure `https://ai.azure.com/.default`, validate credential chain.
- 403 Forbidden:
	- Missing RBAC role or insufficient dataActions.
	- Fix: assign proper Foundry role at correct scope.
- 404 Not Found:
	- Wrong endpoint path or deployment/model name mismatch.
	- Fix: validate endpoint format and deployment names at startup.
- 429 Too Many Requests:
	- Quota/TPM saturation.
	- Fix: honor Retry-After, backoff, token quotas at gateway, spillover strategy if designed.
- >=500 / connectivity errors:
	- Transient backend or network faults.
	- Fix: bounded retries + circuit breaker + failover route.
- Content policy rejection / filtered output:
	- Prompt or input violates policy.
	- Fix: classify as handled business outcome; return safe fallback.
- Observability blind spot:
	- Missing trace links between backend and Foundry calls.
	- Fix: propagate correlation IDs and instrument all hops.

### 3) Language-specific notes: Java and Python

#### Python options
- Foundry SDK path:
	- Package: `azure-ai-projects>=2.0.0`.
	- Auth: `azure-identity` with `DefaultAzureCredential`.
	- Pattern: `AIProjectClient(endpoint, credential)` then `project_client.get_openai_client()`.
- OpenAI-compatible direct path:
	- Package: `openai`.
	- Auth options: Entra token provider (`get_bearer_token_provider`) or API key.
	- Base URL: `https://<resource>.openai.azure.com/openai/v1/`.
- Retry notes:
	- Azure SDK retry policy defaults to exponential backoff and retries transient status codes including 429/5xx.
	- OpenAI Python client docs indicate automatic retries for connection/408/429/>=500 by default.

#### Java options
- Foundry SDK path:
	- Packages: `azure-ai-projects`, `azure-ai-agents` (per Foundry SDK guidance).
	- Auth: `com.azure:azure-identity` with `DefaultAzureCredentialBuilder`.
	- Pattern: `ProjectsClientBuilder().credential(...).endpoint(...).buildClient()` then `getOpenAIClient()`.
- OpenAI-compatible direct path:
	- Package: `com.openai:openai-java`.
	- Entra auth via bearer token supplier from `DefaultAzureCredential`; base URL points to `/openai/v1/`.
- Retry notes:
	- Azure Java core `RetryPolicy` uses exponential backoff by default and supports response header based retry delay (`Retry-After` or `x-ms-retry-after-ms`) when configured.

## Official References

### Core Foundry and SDK
- Microsoft Foundry documentation hub: https://learn.microsoft.com/en-us/azure/foundry/
- Get started with Foundry SDKs and endpoints: https://learn.microsoft.com/en-us/azure/foundry/how-to/develop/sdk-overview
- Authentication and authorization in Foundry: https://learn.microsoft.com/en-us/azure/foundry/concepts/authentication-authorization-foundry

### Inference APIs and language support
- Azure OpenAI reference (Foundry): https://learn.microsoft.com/en-us/azure/foundry/openai/reference
- Azure OpenAI supported languages (includes Python/Java examples and retry/error notes): https://learn.microsoft.com/en-us/azure/foundry/openai/supported-languages

### Security/auth foundations
- Python Azure SDK authentication overview: https://learn.microsoft.com/en-us/azure/developer/python/sdk/authentication/overview
- Java managed identity guidance (Azure-hosted apps): https://learn.microsoft.com/en-us/azure/developer/java/sdk/authentication/system-assigned-managed-identity

### Retry/resilience and gateway patterns
- Python SDK HTTP pipeline retries: https://learn.microsoft.com/en-us/azure/developer/python/sdk/fundamentals/http-pipeline-retries
- Java RetryPolicy class reference: https://learn.microsoft.com/en-us/java/api/com.azure.core.http.policy.retrypolicy?view=azure-java-stable
- Gateway architecture for Foundry model deployments: https://learn.microsoft.com/en-us/azure/architecture/ai-ml/guide/azure-openai-gateway-multi-backend
- API Management AI gateway capabilities: https://learn.microsoft.com/en-us/azure/api-management/genai-gateway-capabilities

### Observability and cost telemetry
- Set up tracing in Foundry: https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/trace-agent-setup
- Monitor agents dashboard: https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/how-to-monitor-agents-dashboard
- Azure Monitor metrics for Cognitive Services/Foundry/OpenAI: https://learn.microsoft.com/en-us/azure/azure-monitor/reference/supported-metrics/microsoft-cognitiveservices-accounts-metrics

## Minimal Integration Blueprint

### Logical flow (backend-centric)
1. API receives resume + job profile.
2. Backend normalizes inputs and assigns correlation ID.
3. Backend retrieves prompt template/version and target model deployment mapping.
4. Backend obtains Entra token via managed identity (`DefaultAzureCredential`).
5. Backend calls Foundry/OpenAI endpoint with bounded timeout + retry policy.
6. Backend validates structured response contract and policy status.
7. Backend persists decision + telemetry (tokens, latency, request id, model, prompt version).
8. Backend returns scored match response and trace id.

### Suggested component layout
- Resume Matching API (Python FastAPI or Java Spring Boot).
- Prompt Registry (versioned files or config service).
- Foundry Client Adapter (single abstraction for endpoint/auth/retry/parsing).
- Telemetry Adapter (OpenTelemetry + App Insights dimensions).
- Optional AI Gateway (API Management) for quota/routing/governance.

### Reference pseudocode (language-neutral)
```text
load config (project_endpoint | openai_endpoint, deployment, prompt_version)
credential = DefaultAzureCredential()
token_scope = "https://ai.azure.com/.default"

request = build_model_request(resume, job, prompt_version)

for attempt in bounded_retries:
	response = invoke_model(request, credential, timeout)
	if success: break
	if status in [429, 408, 5xx]: wait_with_backoff_and_retry_after(response)
	else: fail_fast

validated = validate_schema(response)
emit_metrics(tokens=response.usage, latency, status, deployment, prompt_version)
return validated
```

## Configuration Checklist

### Identity and access
- [ ] Foundry resource uses custom subdomain (required for token auth).
- [ ] Managed identity enabled on hosting service.
- [ ] Managed identity assigned least-privilege Foundry role at proper scope.
- [ ] Local dev identity path works (`az login` + role assignment).

### Endpoint and model config
- [ ] Project endpoint or `/openai/v1` endpoint configured per scenario.
- [ ] Deployment names stored in environment-specific config.
- [ ] Prompt version pinned and traceable.
- [ ] Startup validation checks endpoint format and deployment reachability.

### Reliability and performance
- [ ] Retry policy enabled only for transient faults.
- [ ] `Retry-After` honored for 429.
- [ ] Circuit breaker thresholds defined.
- [ ] Timeout budgets defined (connect/read/overall operation).
- [ ] Optional gateway routing/failover policy tested with same model/version parity.

### Security
- [ ] No API keys in source code or logs.
- [ ] Any required secrets stored in Key Vault.
- [ ] Private networking and backend bypass prevention reviewed.
- [ ] Prompt/response logging redaction policy in place.

### Observability and cost control
- [ ] App Insights connected to Foundry project.
- [ ] Correlation IDs propagated end-to-end.
- [ ] Token, request, latency, and failure metrics collected by deployment/model.
- [ ] Cost dashboards and budget alerts configured.
- [ ] Evaluation and safety monitoring enabled for production traffic samples.

## Implementation-Ready Recommendations (Concise)
- Prefer Entra ID + managed identity for production backend-to-Foundry calls.
- Use Foundry project endpoint as default integration surface; use direct `/openai/v1` for embedding-heavy or strict OpenAI compatibility paths.
- Standardize a reusable client adapter that enforces: auth, timeouts, transient retries, retry-after handling, schema validation, telemetry emission.
- Introduce API Management AI gateway when you need centralized quota enforcement, multi-backend routing, or cross-team governance.
- Track token and latency at both app and Azure Monitor layers, and bind costs to model deployment + consumer dimensions.

## Open Questions
- Which hosting target is planned for backend runtime (App Service, AKS, Container Apps, Functions)? This affects managed identity and private networking details.
- Is strict data residency/geography isolation required for candidate data? This impacts single vs multi-region gateway topology.
- Is there a requirement to support embeddings in same service path now, or can embeddings be separated into a dedicated endpoint adapter?

## Official References

## Minimal Integration Blueprint (Draft)

## Configuration Checklist (Draft)

## Open Questions
- None at this time.
