# Research: Multi-Agent Conversation System

**Feature**: 001-multi-agent-architecture  
**Date**: November 24, 2025  
**Purpose**: Resolve technical clarifications and establish design patterns for multi-agent implementation

## Research Questions

### 1. Agent Communication Pattern

**Question**: Should agents communicate via direct function calls or message passing?

**Decision**: **Direct function calls within Temporal workflow activities**

**Rationale**:
- Temporal workflows already provide message passing, orchestration, and retry semantics
- Agents are activities/functions called by the workflow orchestrator
- Direct calls are simpler, faster, and leverage existing Temporal infrastructure
- No need for additional message queue (Temporal IS the message queue)
- Temporal handles retries, timeouts, and error propagation automatically
- Fits existing codebase pattern (activities call other functions directly)

**Alternatives Considered**:
- **Message queue (Redis/RabbitMQ)**: Rejected - adds complexity, latency, and new dependency when Temporal already provides orchestration
- **Event bus pattern**: Rejected - overkill for sequential agent workflow, adds debugging complexity
- **Actor model (Ray/Akka)**: Rejected - requires new framework, doesn't integrate with existing Temporal workflows

**Implementation Approach**:
```python
# Workflow orchestrates agent calls
@workflow.defn
class MultiAgentConversationWorkflow:
    async def run(self, user_message, channel):
        # Agents are activities called in sequence
        plan = await workflow.execute_activity(planner_analyze, ...)
        data = await workflow.execute_activity(timesheet_extract, ...)
        response = await workflow.execute_activity(planner_compose, ...)
        formatted = await workflow.execute_activity(branding_format, ...)
        validation = await workflow.execute_activity(quality_validate, ...)
        # Refinement if needed
        if not validation.passed:
            response = await workflow.execute_activity(planner_refine, ...)
            # ... repeat
```

---

### 2. Scorecard Schema Format

**Question**: How should scorecards be structured - JSON, Pydantic models, or custom format?

**Decision**: **Pydantic models with JSON serialization**

**Rationale**:
- Type safety and validation at runtime (Pydantic enforces schema)
- IDE autocomplete and type checking during development
- Easy JSON serialization for logging and debugging
- Integrates with existing Python/FastAPI codebase (FastAPI uses Pydantic)
- Supports nested structures for complex criteria
- Clear documentation through model definitions

**Alternatives Considered**:
- **Plain JSON/dict**: Rejected - no type safety, prone to typos, no validation, poor IDE support
- **Custom classes**: Rejected - reinventing Pydantic, more code to maintain
- **Dataclasses**: Rejected - less validation than Pydantic, no JSON schema generation

**Implementation Approach**:
```python
from pydantic import BaseModel, Field
from typing import List, Optional

class ScorecardCriterion(BaseModel):
    """Single validation criterion with pass/fail result"""
    id: str = Field(..., description="Unique criterion identifier")
    description: str = Field(..., description="What is being validated")
    passed: Optional[bool] = Field(None, description="Validation result")
    feedback: Optional[str] = Field(None, description="Feedback if failed")

class Scorecard(BaseModel):
    """Quality validation scorecard for a response"""
    request_id: str
    criteria: List[ScorecardCriterion]
    overall_passed: bool = Field(default=False)
    created_at: str
    
    def evaluate(self) -> bool:
        """Check if all criteria passed"""
        return all(c.passed for c in self.criteria if c.passed is not None)
```

---

### 3. Style Guide Storage Format

**Question**: Should style guide be stored as JSON, YAML, or in database?

**Decision**: **YAML files in `agents/config/` directory**

**Rationale**:
- Human-readable and editable (easier for non-developers to update)
- Version controlled with code (Git tracks changes, easy rollback)
- No database dependency (simpler deployment, faster loading)
- Supports comments for documentation
- Easy to validate with schema
- Can be hot-reloaded without code deployment (watch file for changes)

**Alternatives Considered**:
- **JSON**: Rejected - less human-readable, no comments, harder to edit manually
- **Database (Supabase)**: Rejected - requires schema changes (violates FR-044), slower loading, harder to version control
- **Environment variables**: Rejected - not suitable for complex nested configuration, hard to manage

**Implementation Approach**:
```yaml
# agents/config/style_guide.yaml
version: "1.0"
brand:
  name: "Timesheet Assistant"
  personality: "friendly, professional, helpful"
  
tone:
  default: "conversational"
  error: "empathetic"
  success: "encouraging"
  
emojis:
  enabled: true
  success: "✅"
  warning: "⚠️"
  error: "❌"
  info: "ℹ️"
  
humor:
  enabled: true
  style: "light, work-related"
  frequency: "occasional"
  
formatting:
  greeting: true
  sign_off: false
  use_user_name: true
```

```python
# Load in agent
import yaml
from pathlib import Path

class BrandingAgent:
    def __init__(self):
        config_path = Path(__file__).parent / "config" / "style_guide.yaml"
        with open(config_path) as f:
            self.style_guide = yaml.safe_load(f)
```

---

### 4. Integration Testing Framework

**Question**: What framework should be used for testing multi-agent Temporal workflows?

**Decision**: **pytest with Temporal testing utilities**

**Rationale**:
- pytest already used in `llm/tests/` (consistency)
- Temporal provides `temporalio.testing.WorkflowEnvironment` for workflow testing
- Can mock activities to test workflow orchestration
- Can test activities in isolation
- Supports async tests (needed for Temporal workflows)
- Rich assertion and fixture ecosystem

**Alternatives Considered**:
- **unittest**: Rejected - less flexible than pytest, no async support out of box
- **Custom test harness**: Rejected - reinventing pytest, more maintenance
- **End-to-end only**: Rejected - slow, brittle, hard to debug

**Implementation Approach**:
```python
# tests/integration/test_agent_coordination.py
import pytest
from temporalio.testing import WorkflowEnvironment
from temporalio.worker import Worker

@pytest.mark.asyncio
async def test_multi_agent_workflow_success():
    """Test complete multi-agent workflow with quality validation passing"""
    async with await WorkflowEnvironment.start_time_skipping() as env:
        # Register workflow and activities
        worker = Worker(
            env.client,
            task_queue="test",
            workflows=[MultiAgentConversationWorkflow],
            activities=[planner_analyze, timesheet_extract, ...]
        )
        
        async with worker:
            # Execute workflow
            result = await env.client.execute_workflow(
                MultiAgentConversationWorkflow.run,
                args=["Check my timesheet", "sms"],
                id="test-workflow",
                task_queue="test"
            )
            
            # Assertions
            assert result.validation_passed
            assert result.channel == "sms"
            assert len(result.formatted_response) < 1600  # SMS limit
```

---

### 5. Expected Request Volume and Concurrency

**Question**: What are the expected request volumes and concurrency patterns?

**Decision**: **Design for current scale + 2x headroom**

**Rationale**:
- Current system handles multi-tenant workload successfully
- Multi-agent adds ~4x LLM calls per request (one per agent)
- Existing LLM client has rate limiting and caching
- Temporal handles concurrency automatically
- Start with current scale, monitor, and scale horizontally if needed

**Assumptions** (based on typical conversational AI usage):
- Peak: ~10-50 concurrent conversations
- Average: ~5-10 requests per minute
- Burst: ~100 requests in 1 minute
- Each request: 4 agent calls = 4 LLM calls
- LLM client rate limit: configurable per environment

**Scaling Strategy**:
- Horizontal: Add more Temporal workers (existing pattern)
- LLM: Use existing rate limiter and caching in `llm/` module
- Database: Supabase handles current load, no schema changes needed
- Monitor: Track request latency, agent call times, validation pass rates

**Performance Budget** (per request):
- Planner analyze: ~2s (LLM call)
- Timesheet extract: ~1-2s (Harvest API + LLM)
- Planner compose: ~2s (LLM call)
- Branding format: ~0.5s (string processing)
- Quality validate: ~1s (LLM call)
- **Total**: ~6.5-7.5s (within 10s target)
- **With refinement**: ~10-12s (may exceed target, acceptable for <30% of requests)

---

## Best Practices Research

### Multi-Agent Systems

**Pattern**: Hierarchical agent architecture with coordinator
- **Coordinator (Planner)**: Orchestrates other agents, maintains context
- **Specialists**: Focus on single responsibility (data, formatting, validation)
- **Communication**: Through coordinator, not peer-to-peer
- **State**: Coordinator maintains state, specialists are stateless

**References**:
- LangChain multi-agent patterns
- Microsoft AutoGen framework
- CrewAI agent orchestration

### Quality Validation Patterns

**Pattern**: Scorecard-based validation with specific criteria
- Each criterion is boolean (pass/fail)
- Criteria are measurable and specific
- Failed criteria provide actionable feedback
- Validation is independent from composition

**Anti-patterns to avoid**:
- Vague criteria ("response is good")
- Subjective criteria ("response is creative")
- Criteria that can't be automatically evaluated

### Channel-Specific Formatting

**Pattern**: Strategy pattern with channel-specific formatters
- Each channel has formatter implementation
- Common interface for all formatters
- Formatters are stateless and composable
- Message splitting at natural boundaries

**Best practices**:
- SMS: Plain text, short sentences, clear structure
- Email: Rich formatting, longer content, visual hierarchy
- WhatsApp: Moderate formatting, emoji-friendly, conversational
- Teams: Structured cards, action buttons, rich media

---

## Technology Decisions Summary

| Decision Area | Choice | Key Reason |
|--------------|--------|------------|
| Agent Communication | Direct function calls in Temporal activities | Leverages existing orchestration, simpler, faster |
| Scorecard Schema | Pydantic models | Type safety, validation, IDE support |
| Style Guide Storage | YAML files | Human-readable, version controlled, no DB changes |
| Testing Framework | pytest + Temporal testing | Consistency with existing tests, async support |
| Concurrency Model | Current scale + 2x headroom | Proven infrastructure, horizontal scaling available |

---

## Implementation Risks and Mitigations

### Risk 1: LLM Call Latency
- **Risk**: 4 LLM calls per request may exceed 10s target
- **Mitigation**: Use existing LLM caching, parallel calls where possible, monitor P95 latency
- **Fallback**: Reduce validation complexity, use smaller/faster models for formatting

### Risk 2: Refinement Loop Performance
- **Risk**: Refinement adds 3-4s, may timeout
- **Mitigation**: Limit to 1 refinement, track refinement rate, optimize based on data
- **Fallback**: Disable refinement for specific channels (SMS), graceful failure

### Risk 3: Configuration Management
- **Risk**: YAML config changes may break system
- **Mitigation**: Schema validation on load, version config files, test config changes
- **Fallback**: Default config embedded in code, config overrides defaults

### Risk 4: Backward Compatibility
- **Risk**: Multi-agent changes may break existing workflows
- **Mitigation**: Feature flag to enable/disable multi-agent, parallel deployment, gradual rollout
- **Fallback**: Keep single-agent workflow as fallback, route based on user/channel

---

## Next Steps

1. ✅ Research complete - all NEEDS CLARIFICATION resolved
2. → Proceed to Phase 1: Design (data models, contracts, quickstart)
3. → Update agent context with technology decisions
4. → Re-evaluate Constitution Check with design details
