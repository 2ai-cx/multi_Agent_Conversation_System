# Implementation Plan: Multi-Agent Conversation System

**Branch**: `001-multi-agent-architecture` | **Date**: November 24, 2025 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-multi-agent-architecture/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Replace the current single-agent conversation system with a 4-agent architecture (Planner, Timesheet, Branding, Quality) to provide quality control and channel-specific response formatting. The system will validate all responses before sending, support refinement loops (max 1 attempt), and ensure channel-appropriate formatting (SMS plain text, Email markdown, WhatsApp limited markdown, Teams adaptive cards). Implementation will reuse existing infrastructure (Temporal workflows, Supabase database, centralized LLM client, 51 Harvest tools) with zero breaking changes to maintain backward compatibility.

## Technical Context

**Language/Version**: Python 3.13 (existing codebase standard)
**Primary Dependencies**: 
- Temporal (workflow orchestration) - existing
- FastAPI (server framework) - existing
- LangChain (agent framework) - existing
- Supabase (database client) - existing
- Twilio (SMS/WhatsApp) - existing
- Centralized LLM client (`llm/` module) - existing
- NEEDS CLARIFICATION: Agent communication pattern (direct calls vs message passing)
- NEEDS CLARIFICATION: Scorecard schema format (JSON, Pydantic models, or custom)
- NEEDS CLARIFICATION: Style guide storage format (JSON, YAML, or database)

**Storage**: Supabase (PostgreSQL) - existing schema for users, conversations, conversation_context
**Testing**: pytest (existing in `llm/tests/`), NEEDS CLARIFICATION: Integration testing framework for multi-agent workflows
**Target Platform**: Azure Container Apps (existing deployment)
**Project Type**: Single project (server application with Temporal workflows)
**Performance Goals**: 
- End-to-end response: <10 seconds (95th percentile)
- Quality validation: <1 second (99th percentile)
- Branding formatting: <500ms (99th percentile)
- Same throughput as current system (concurrent multi-user support)

**Constraints**: 
- Zero breaking changes (backward compatibility required)
- No database schema changes (reuse existing tables)
- Reuse all 51 existing Harvest tools without modification
- Maximum 1 refinement attempt per request (prevent infinite loops)
- Channel-specific limits: SMS 1600 chars, Email unlimited, WhatsApp moderate

**Scale/Scope**: 
- Multi-tenant system (existing user base)
- 4 agent types (Planner, Timesheet, Branding, Quality)
- 4 communication channels (SMS, Email, WhatsApp, Teams)
- 51 existing Harvest API tools
- Estimated ~2000-3000 LOC for agent implementation
- NEEDS CLARIFICATION: Expected request volume and concurrency patterns

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Note**: Constitution file is a template placeholder. Applying general software engineering principles for this check.

### Architecture Principles

✅ **Modularity**: Each agent (Planner, Timesheet, Branding, Quality) is independently testable with clear input/output contracts (FR-002, FR-003)

✅ **Separation of Concerns**: 
- Planner: coordination and planning
- Timesheet: data extraction only
- Branding: formatting only
- Quality: validation only

✅ **Backward Compatibility**: All existing features preserved (FR-036, FR-053), no breaking changes to APIs or database schema (FR-044, SC-004)

✅ **Infrastructure Reuse**: Leverages existing Temporal, Supabase, LLM client, Harvest tools (FR-049 through FR-053)

✅ **Testability**: Each agent independently testable, clear contracts enable unit and integration testing

### Quality Gates

✅ **Performance**: Specific measurable targets defined (10s response, 1s validation, 500ms formatting)

✅ **Observability**: Comprehensive logging requirements (FR-054 through FR-058) enable debugging within 5 minutes (SC-014, SC-015)

✅ **Error Handling**: Graceful failure mechanism with quality validation (FR-029, FR-034, SC-008)

✅ **Configuration**: Style guide configurable without code changes (FR-059, SC-023)

### Complexity Justification

⚠️ **Multi-Agent Architecture**: Adding 4 agents increases system complexity
- **Why Needed**: Quality control requires separation of concerns - validation must be independent from composition, formatting must be channel-aware, data extraction must be isolated from presentation
- **Simpler Alternative Rejected**: Single agent with validation function rejected because it doesn't enforce quality gates, allows bypassing validation, and couples formatting with composition

✅ **GATE PASSED**: Complexity justified by quality control requirements and mitigated by clear agent contracts and comprehensive testing

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

**Existing Structure** (to be extended):
```text
.
├── unified_server.py          # FastAPI server + Temporal worker (1,458 lines)
├── unified_workflows.py       # Temporal workflows + activities (3,209 lines)
├── llm/                       # Centralized LLM client module
│   ├── client.py             # Main LLM client
│   ├── config.py             # Configuration (42 parameters)
│   ├── providers/            # OpenAI, OpenRouter providers
│   └── tests/                # Unit tests (pytest)
└── SYSTEM_ANALYSIS.md        # System documentation
```

**New Structure** (multi-agent implementation):
```text
.
├── unified_server.py          # [EXISTING] FastAPI server (minimal changes)
├── unified_workflows.py       # [MODIFY] Add multi-agent workflow orchestration
├── agents/                    # [NEW] Multi-agent system
│   ├── __init__.py
│   ├── base.py               # Base agent interface/contract
│   ├── planner.py            # Planner Agent (coordinator)
│   ├── timesheet.py          # Timesheet Agent (data specialist)
│   ├── branding.py           # Branding Agent (formatter)
│   ├── quality.py            # Quality Agent (validator)
│   ├── models.py             # Shared data models (ExecutionPlan, Scorecard, etc.)
│   └── config/               # Agent configuration
│       ├── style_guide.yaml  # Branding style guide (configurable)
│       └── channels.yaml     # Channel specifications
├── llm/                       # [EXISTING] Centralized LLM client (reused by agents)
├── tests/                     # [NEW] Test suite
│   ├── unit/                 # Unit tests for each agent
│   │   ├── test_planner.py
│   │   ├── test_timesheet.py
│   │   ├── test_branding.py
│   │   └── test_quality.py
│   ├── integration/          # Integration tests for agent workflows
│   │   ├── test_agent_coordination.py
│   │   ├── test_quality_validation.py
│   │   └── test_channel_formatting.py
│   └── fixtures/             # Test fixtures and mocks
│       ├── sample_requests.py
│       ├── sample_scorecards.py
│       └── mock_harvest_data.py
└── specs/001-multi-agent-architecture/  # [EXISTING] Feature documentation
```

**Structure Decision**: 

Selected **Single Project** structure with new `agents/` module because:

1. **Existing Pattern**: Current codebase uses single-file modules (`unified_server.py`, `unified_workflows.py`) with supporting `llm/` module
2. **Agent Isolation**: New `agents/` module provides clear separation while integrating with existing Temporal workflows
3. **Reuse Infrastructure**: Agents use existing `llm/` client, Temporal workflows, and Supabase connections
4. **Testing Strategy**: New `tests/` directory at root level (existing tests in `llm/tests/` remain)
5. **Configuration**: Agent configs in `agents/config/` as YAML files for non-code updates (FR-059)
6. **Backward Compatibility**: Existing `unified_workflows.py` extended (not replaced) to add multi-agent orchestration alongside existing single-agent workflow

## Complexity Tracking

| Complexity | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| 4-agent architecture | Quality control requires independent validation, channel-specific formatting, and data extraction isolation | Single agent with validation function: doesn't enforce quality gates, allows bypassing validation, couples formatting with composition, no specialization |
| Scorecard-based validation | Need measurable, boolean criteria for automated quality checks | Simple pass/fail flag: not debuggable, no specific feedback for refinement, can't track which criteria failed |
| Refinement loop (max 1) | Quality issues often fixable with specific feedback, but need bounded attempts | No refinement: poor UX for fixable issues; Unlimited refinement: infinite loops, poor performance |
| Channel-specific formatters | Each channel has different capabilities (SMS plain text, Email markdown, Teams adaptive cards) | Single format for all channels: breaks SMS with markdown, underutilizes Email/Teams capabilities, poor UX |
| Configuration-driven style guide | Brand voice changes without code deployment, A/B testing, multi-brand support | Hardcoded style: requires code changes, deployment, testing for simple tone adjustments |
