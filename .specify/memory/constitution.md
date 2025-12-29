<!--
Sync Impact Report:
- Version: 0.0.0 → 1.0.0 (Initial constitution creation)
- Principles Added: 7 core principles established
- Sections Added: Performance Standards, Quality Gates, Governance
- Templates Status:
  ✅ plan-template.md - Constitution Check section aligns
  ✅ spec-template.md - Requirements align with principles
  ✅ tasks-template.md - Task categories support principles
- Follow-up: None - all placeholders resolved
-->

# Multi-Agent Conversation System Constitution

## Core Principles

### I. Agent Modularity (NON-NEGOTIABLE)

Each agent MUST be independently testable with clear input/output contracts. Agents operate as specialized modules with single responsibilities:
- **Planner Agent**: Strategist and coordinator only
- **Timesheet Agent**: Tool executor only (51 Harvest API tools)
- **Branding Agent**: Channel-specific formatter only
- **Quality Agent**: Validator only (scorecard-based evaluation)

**Rationale**: Modularity enables parallel development, isolated testing, and clear failure boundaries. Violations create coupling that prevents independent agent evolution and makes debugging impossible.

### II. Quality-First Response Generation

All responses MUST pass quality validation before delivery. The Quality Agent validates against scorecard criteria with automatic refinement (max 1 attempt). If refinement fails, send graceful failure message.

**Requirements**:
- Scorecard-based validation with explicit criteria
- LLM-powered criterion evaluation
- Automatic refinement loop (single attempt)
- Graceful failure fallback with user-friendly messages
- Comprehensive failure logging for debugging

**Rationale**: Quality validation is the primary value proposition preventing bad responses from reaching users. This is non-negotiable for production readiness.

### III. Channel-Specific Formatting

Responses MUST be formatted appropriately for each channel's capabilities and constraints:
- **SMS**: Plain text only, no markdown, <1600 chars, intelligent splitting
- **Email**: Full markdown, unlimited length, rich formatting
- **WhatsApp**: Limited markdown (bold, italic), <4000 chars
- **Teams**: Adaptive cards (future)

**Rationale**: Channel-appropriate formatting prevents user frustration and ensures messages are readable on all platforms. Markdown in SMS or oversized messages create poor UX.

### IV. Contract-Driven Development

All agent interactions MUST follow documented contracts in `specs/[feature]/contracts/`. Contracts define:
- Input schema (required/optional fields, types, validation)
- Output schema (guaranteed fields, error formats)
- Error handling (expected errors, retry behavior)
- Performance targets (latency, throughput)

**Rationale**: Contracts enable independent development, prevent integration bugs, and serve as executable documentation. Changes to contracts require migration plans.

### V. Performance Accountability

All components MUST meet documented performance targets:
- End-to-end: <10s (95th percentile)
- Quality validation: <1s (99th percentile)
- Branding formatting: <500ms (99th percentile)
- Cost per conversation: ~$0.003-0.005 (with caching)

**Enforcement**: Performance regressions block deployment. All changes must include performance impact analysis.

**Rationale**: Performance directly impacts user experience and operational costs. Gradual degradation without accountability leads to unusable systems.

### VI. Observability & Debugging

All agent actions MUST be logged with sufficient context for debugging:
- Request ID tracking across all agents
- Input/output logging at agent boundaries
- Validation failures with scorecard details
- Refinement attempts with feedback
- Performance metrics (latency, token usage)

**Requirements**:
- Structured logging (JSON format)
- Correlation IDs for distributed tracing
- Error context (stack traces, agent state)
- Metrics export to monitoring systems

**Rationale**: Multi-agent systems are complex. Without comprehensive logging, debugging failures is impossible and quality improvements cannot be measured.

### VII. Graceful Degradation

System MUST maintain user experience even during failures:
- Partial data responses when some tools fail
- Graceful failure messages (never raw errors to users)
- Automatic retry with exponential backoff
- Circuit breakers for failing dependencies
- Fallback responses when refinement fails

**Rationale**: Production systems fail. Graceful degradation ensures users receive helpful responses even when components fail, maintaining trust and usability.

### VIII. PII Protection & Data Sanitization (NON-NEGOTIABLE)

All logging and monitoring MUST sanitize personally identifiable information (PII):
- **Automatic sanitization**: All agent logs sanitize PII fields before logging
- **Redaction list**: phone_number, email, access_token, api_key, password, secret, credential, ssn, address
- **Nested sanitization**: Recursively sanitize dictionaries and lists
- **Structured logging**: Use JSON format with sanitized fields marked as `[REDACTED]`
- **Configuration control**: `log_prompts` and `log_responses` flags default to `False` to prevent PII leakage

**Implementation**:
```python
class BaseAgent:
    def _sanitize_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        # Check if key contains PII field names
        if any(pii in key.lower() for pii in pii_fields):
            sanitized[key] = "[REDACTED]"
```

**Rationale**: PII in logs creates legal liability (GDPR, CCPA), security risks, and compliance violations. Automatic sanitization prevents accidental PII exposure.

### IX. Lazy Loading & Resource Efficiency

All expensive resources MUST be lazy-loaded to optimize startup time and memory:
- **LLM providers**: Load only when first chat completion is called
- **Rate limiters**: Initialize only when needed
- **Opik tracker**: Load only if `opik_enabled=True`
- **Memory managers**: Cache per tenant, load on first use
- **Vector stores**: Initialize only when RAG is accessed

**Pattern**:
```python
@property
def provider(self):
    """Lazy load provider"""
    if self._provider is None:
        from llm.providers.openai import OpenAIProvider
        self._provider = OpenAIProvider(self.config)
    return self._provider
```

**Rationale**: Lazy loading reduces startup time, memory footprint, and allows graceful degradation when optional dependencies are missing.

### X. Centralized LLM Client

All LLM interactions MUST go through the centralized `LLMClient`:
- **Single entry point**: No direct OpenAI/Anthropic API calls
- **Built-in features**: Rate limiting, caching, error handling, Opik tracing, cost tracking
- **Multi-tenant support**: Tenant-specific API keys via `TenantKeyManager`
- **Provider abstraction**: Switch providers without changing agent code
- **JSON minification**: Automatic token savings for large payloads

**Usage**:
```python
from llm.client import LLMClient

client = LLMClient(config)
response = await client.chat_completion(
    messages=[{"role": "user", "content": "Hello"}],
    tenant_id="tenant-123",
    user_id="user-456"
)
```

**Rationale**: Centralization ensures consistent behavior, prevents rate limit violations, enables cost attribution, and simplifies monitoring.

### XI. Structured Data Flow

Agents MUST pass structured data (dicts), not formatted strings:
- **Timesheet Agent**: Returns `{"data": {...}, "metadata": {...}, "success": bool}`
- **Planner Agent**: Receives structured data, composes natural language
- **Branding Agent**: Formats structured responses for channels
- **No premature formatting**: Data stays structured until final formatting step

**Anti-pattern**:
```python
# ❌ BAD: Timesheet Agent returns formatted string
return "You've logged 32/40 hours this week..."

# ✅ GOOD: Timesheet Agent returns structured data
return {
    "data": {"hours_logged": 32, "hours_target": 40},
    "success": True
}
```

**Rationale**: Structured data enables agent coordination, allows multiple formatting strategies, and prevents information loss during processing.

### XII. Multi-Tenant Isolation

All data access MUST enforce tenant isolation:
- **Memory isolation**: Mem0 queries filtered by `tenant_id` and `user_id`
- **API key isolation**: Each tenant uses separate API keys (OpenRouter provisioning)
- **Conversation isolation**: Supabase queries filtered by `tenant_id`
- **Test coverage**: Dedicated tests verify no cross-tenant data leakage

**Enforcement**:
```python
# All memory operations require tenant_id
memory.add_conversation(
    user_message=msg,
    ai_response=response,
    tenant_id=tenant_id,  # REQUIRED
    user_id=user_id
)
```

**Rationale**: Multi-tenant isolation prevents data breaches, ensures compliance, and enables per-tenant billing and rate limiting.

## Security Standards

### PII Handling Requirements

**MUST implement**:
- Automatic PII sanitization in all logs
- Configuration flags for sensitive data logging (`log_prompts=False`, `log_responses=False`)
- Recursive sanitization for nested data structures
- Clear `[REDACTED]` markers for sanitized fields

**MUST test**:
- Verify no PII in production logs
- Test sanitization with nested objects and arrays
- Verify configuration flags prevent PII logging

### Multi-Tenant Security

**MUST enforce**:
- Tenant ID in all database queries
- User ID in all memory operations
- API key isolation per tenant
- Test coverage for cross-tenant isolation

**MUST monitor**:
- Failed authentication attempts
- Cross-tenant access attempts
- API key usage per tenant

## Resource Management

### Lazy Loading Requirements

**MUST lazy-load**:
- LLM providers (OpenAI, Anthropic, Azure)
- Rate limiters (v1, v2)
- Opik tracker (only if enabled)
- Memory managers (per tenant)
- Vector stores (only if RAG enabled)
- Embeddings providers (only if needed)

**Benefits measured**:
- Startup time <5s (vs >30s with eager loading)
- Memory footprint <500MB (vs >2GB with eager loading)
- Graceful degradation when optional dependencies missing

### Centralized Services

**MUST centralize**:
- LLM client (all AI interactions)
- Memory manager (all RAG operations)
- Error handler (all retry logic)
- Rate limiter (all API throttling)

**MUST NOT**:
- Make direct API calls to OpenAI/Anthropic
- Implement custom retry logic in agents
- Create per-agent rate limiters
- Duplicate caching logic

## Performance Standards

### Latency Requirements

| Component | Target | Measurement |
|-----------|--------|-------------|
| Planner analysis | <2s | 95th percentile |
| Timesheet data fetch | <3s | 95th percentile |
| Response composition | <2s | 95th percentile |
| Quality validation | <1s | 99th percentile |
| Branding formatting | <500ms | 99th percentile |
| End-to-end | <10s | 95th percentile |

### Cost Efficiency

- Target: $0.003-0.005 per conversation
- Enforce response caching where applicable
- Monitor token usage per agent
- Alert on cost anomalies (>2x baseline)

### Reliability

- Uptime: 99.9% (excluding planned maintenance)
- Error rate: <1% of requests
- Quality validation pass rate: >95%
- Graceful failure rate: <5% of requests

## Testing Standards

### Test Categories (REQUIRED)

**Unit Tests** (`tests/unit/`):
- Agent logic (Planner, Timesheet, Branding, Quality)
- LLM client features (rate limiting, caching, error handling)
- Utility functions (JSON minification, sanitization)
- Target: ≥80% code coverage

**Integration Tests** (`tests/integration/`):
- Multi-agent workflows
- Temporal activity execution
- Mem0 + Qdrant memory operations
- Harvest MCP tool integration
- Target: All critical paths covered

**API Tests** (`tests/api/`):
- Webhook endpoints (SMS, Email, WhatsApp)
- Health check endpoints
- Manual trigger endpoints
- Target: All endpoints tested

**E2E Tests** (`tests/e2e/`):
- Complete conversation flows
- Quality validation with refinement
- Channel-specific formatting
- Graceful failure scenarios
- Target: All user scenarios covered

**Performance Tests** (`tests/performance/`):
- Latency benchmarks per agent
- Concurrent user load testing
- Memory leak detection
- Cost per conversation measurement
- Target: Meet performance standards

### Test Data Management

**MUST use**:
- Fixtures for common test data (`tests/fixtures/`)
- Mock objects for external dependencies
- Separate test tenants/users
- Cleanup after test execution

**MUST NOT**:
- Use production data in tests
- Leave test data in production databases
- Hard-code API keys in tests
- Skip cleanup in test teardown

## Deployment Standards

### Docker Image Requirements

**MUST include**:
- Multi-stage builds (builder + runtime)
- Non-root user (appuser, UID 1000)
- Health check endpoint
- Minimal base image (python:3.11-slim)
- Version tags (YYYYMMDD-description format)

**Example**:
```dockerfile
FROM python:3.11-slim
WORKDIR /app
RUN useradd -m -u 1000 appuser
COPY --chown=appuser:appuser . .
USER appuser
CMD ["python", "unified_server.py"]
```

### Azure Container Apps Deployment

**MUST configure**:
- Azure Key Vault integration for secrets
- Managed identity for Key Vault access
- Ingress with HTTPS only
- Min/max replicas for auto-scaling
- Health probes (liveness, readiness)
- Resource limits (CPU, memory)

**MUST verify**:
- Health endpoint returns 200 OK
- All Key Vault secrets accessible
- Temporal connection successful
- Supabase connection successful
- Opik tracing enabled (if configured)

### Temporal Workflow Deployment

**MUST implement**:
- Non-blocking startup (background task initialization)
- Schedule recreation on deployment
- Correct timezone configuration (Australia/Sydney)
- Workflow versioning for safe updates
- Activity timeout protection

**Pattern**:
```python
@app.on_event("startup")
async def startup_event():
    async def initialize_background_services():
        await server.initialize_temporal_client()
        # Start workers in background
    asyncio.create_task(initialize_background_services())
```

### Deployment Verification Checklist

**MUST verify before production**:
- [ ] Health endpoint accessible
- [ ] SMS webhook responds within 10s
- [ ] Quality validation pass rate ≥95%
- [ ] No PII in logs
- [ ] Opik traces appearing in correct project
- [ ] Temporal schedule running at correct time
- [ ] Cost per conversation within budget
- [ ] Error rate <1%

## Quality Gates

### Pre-Deployment Gates

**MUST pass before any deployment:**

1. **Test Coverage**: ≥80% for all agents
2. **Contract Tests**: 100% passing for all agent contracts
3. **Performance Tests**: All targets met in staging
4. **Quality Validation**: ≥95% pass rate on test dataset
5. **Security Scan**: No high/critical vulnerabilities

### Development Gates

**MUST pass before PR approval:**

1. **Unit Tests**: All new code has tests
2. **Contract Compliance**: Changes respect existing contracts or include migration
3. **Performance Impact**: No regressions without justification
4. **Logging**: All agent actions logged with context
5. **Documentation**: Contracts updated for interface changes

### Monitoring Gates

**MUST monitor in production:**

1. **Quality Metrics**: Validation pass rate, refinement rate, failure rate
2. **Performance Metrics**: Latency per agent, end-to-end latency
3. **Cost Metrics**: Token usage, API costs per conversation
4. **Error Metrics**: Error rate by agent, failure reasons
5. **User Metrics**: Response time, message delivery rate

## Governance

### Amendment Process

This constitution supersedes all other development practices. Amendments require:

1. **Proposal**: Document proposed change with rationale
2. **Impact Analysis**: Identify affected components, contracts, tests
3. **Migration Plan**: Define steps to implement change across codebase
4. **Approval**: Technical lead review and approval
5. **Version Update**: Increment version per semantic versioning rules

### Version Semantics

- **MAJOR**: Backward-incompatible principle changes (e.g., removing agent modularity requirement)
- **MINOR**: New principles or material expansions (e.g., adding new quality gate)
- **PATCH**: Clarifications, wording improvements, non-semantic refinements

### Compliance Verification

All PRs and code reviews MUST verify:

- Agent modularity maintained (independent testability)
- Quality validation enforced (no bypassing validation)
- Contracts respected (no breaking changes without migration)
- Performance targets met (no regressions)
- Logging comprehensive (debugging context present)

### Complexity Justification

Any violation of principles MUST be justified in `specs/[feature]/plan.md` Complexity Tracking section:

- **What principle is violated**: Specific principle name
- **Why violation is necessary**: Technical or business justification
- **Simpler alternatives rejected**: Why compliant approach insufficient
- **Mitigation plan**: How to minimize impact of violation

**Version**: 1.1.0 | **Ratified**: 2025-12-30 | **Last Amended**: 2025-12-30
