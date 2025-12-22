---
description: "Implementation tasks for multi-agent conversation system"
---

# Tasks: Multi-Agent Conversation System

**Input**: Design documents from `/specs/001-multi-agent-architecture/`  
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/agent-contracts.md, quickstart.md

**Tests**: Tests are included based on specification requirements (FR-054 through FR-058 require comprehensive testing)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: Repository root with `agents/`, `tests/`, existing `unified_server.py`, `unified_workflows.py`
- Configuration files in `agents/config/`
- Tests in `tests/unit/`, `tests/integration/`, `tests/fixtures/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure for multi-agent system

- [x] T001 Create agents module directory structure: `agents/`, `agents/config/`
- [x] T002 Create test directory structure: `tests/unit/`, `tests/integration/`, `tests/fixtures/`
- [x] T003 [P] Create `agents/__init__.py` with module exports
- [x] T004 [P] Create `agents/config/style_guide.yaml` with brand configuration (tone, emojis, humor, formatting)
- [x] T005 [P] Create `agents/config/channels.yaml` with channel specifications (SMS, Email, WhatsApp, Teams)
- [x] T006 [P] Install additional dependencies if needed (pyyaml for config loading)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T007 Create Pydantic data models in `agents/models.py`: ExecutionPlan, ExecutionStep, Channel enum
- [x] T008 [P] Create Pydantic data models in `agents/models.py`: Scorecard, ScorecardCriterion, ValidationResult
- [x] T009 [P] Create Pydantic data models in `agents/models.py`: RefinementRequest, FormattedResponse, MessagePart
- [x] T010 [P] Create Pydantic data models in `agents/models.py`: AgentInteractionLog, ValidationFailureLog
- [x] T011 [P] Create Pydantic data models in `agents/models.py`: ChannelSpecification, StyleGuide, MultiAgentWorkflowState
- [x] T012 Create base agent interface in `agents/base.py` with BaseAgent abstract class, execute method, log_interaction method
- [x] T013 [P] Create test fixtures in `tests/fixtures/sample_requests.py` with sample user messages, channels, conversation history
- [x] T014 [P] Create test fixtures in `tests/fixtures/sample_scorecards.py` with sample scorecard criteria for different scenarios
- [x] T015 [P] Create test fixtures in `tests/fixtures/mock_harvest_data.py` with mock timesheet data for testing

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Quality-Validated Timesheet Response (Priority: P1) 🎯 MVP

**Goal**: User sends "Check my timesheet" via SMS, system coordinates agents to extract data, validate quality, format for SMS, and send accurate plain-text response within 10 seconds

**Independent Test**: Send timesheet query via SMS and verify: (1) response is accurate, (2) passes quality validation, (3) formatted correctly for SMS (plain text, no markdown, <1600 chars), (4) delivered within 10 seconds

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T016 [P] [US1] Unit test for Planner.analyze_request in `tests/unit/test_planner.py` - verify execution plan creation and scorecard generation
- [x] T017 [P] [US1] Unit test for Timesheet.extract_timesheet_data in `tests/unit/test_timesheet.py` - verify data extraction with mock Harvest tools
- [x] T018 [P] [US1] Unit test for Planner.compose_response in `tests/unit/test_planner.py` - verify response composition from timesheet data
- [x] T019 [P] [US1] Unit test for Branding.format_for_channel (SMS) in `tests/unit/test_branding.py` - verify plain text formatting, no markdown, length limits
- [x] T020 [P] [US1] Unit test for Quality.validate_response in `tests/unit/test_quality.py` - verify scorecard evaluation and validation logic
- [x] T021 [US1] Integration test for complete multi-agent workflow in `tests/integration/test_agent_coordination.py` - verify all agents called in correct order, response validated and sent

### Implementation for User Story 1

- [x] T022 [P] [US1] Implement PlannerAgent class in `agents/planner.py` with analyze_request method (uses LLM to analyze user message, create execution plan, generate scorecard)
- [x] T023 [P] [US1] Implement TimesheetAgent class in `agents/timesheet.py` with extract_timesheet_data method (reuses existing 51 Harvest tools from unified_workflows.py)
- [x] T024 [US1] Implement PlannerAgent.compose_response method in `agents/planner.py` (uses LLM to compose response from timesheet data and context)
- [x] T025 [US1] Implement BrandingAgent class in `agents/branding.py` with format_for_channel method and _format_sms helper (loads config, strips markdown, applies style, handles splitting)
- [x] T026 [US1] Implement QualityAgent class in `agents/quality.py` with validate_response method (evaluates each scorecard criterion using LLM, aggregates results)
- [x] T027 [US1] Create Temporal activities in `unified_workflows.py`: planner_analyze_activity, timesheet_extract_activity, planner_compose_activity, branding_format_activity, quality_validate_activity
- [x] T028 [US1] Create MultiAgentConversationWorkflow in `unified_workflows.py` with workflow orchestration (Steps 1-5: analyze → extract → compose → format → validate)
- [x] T029 [US1] Add agent interaction logging to all agents (log request_id, agent_name, action, input/output, duration, success/error)
- [x] T030 [US1] Register MultiAgentConversationWorkflow and activities with Temporal worker in `unified_server.py`
- [x] T031 [US1] Add feature flag USE_MULTI_AGENT to webhook handlers in `unified_server.py` to enable/disable multi-agent system
- [x] T032 [US1] Update webhook handlers to route to MultiAgentConversationWorkflow when USE_MULTI_AGENT=true

**Checkpoint**: At this point, User Story 1 should be fully functional - user can send timesheet query via SMS and receive quality-validated, properly formatted response

---

## Phase 4: User Story 2 - Channel-Specific Formatting (Priority: P1)

**Goal**: User receives same timesheet information via different channels (SMS, Email, WhatsApp) with channel-appropriate formatting

**Independent Test**: Send identical query via SMS, Email, WhatsApp and verify SMS gets plain text (no markdown, <1600 chars), Email gets full markdown, WhatsApp gets limited markdown

### Tests for User Story 2

- [ ] T033 [P] [US2] Unit test for Branding._format_email in `tests/unit/test_branding.py` - verify full markdown support (headers, tables, bold, italic, links)
- [ ] T034 [P] [US2] Unit test for Branding._format_whatsapp in `tests/unit/test_branding.py` - verify limited markdown (bold, italic only, no tables)
- [ ] T035 [P] [US2] Unit test for Branding._split_message in `tests/unit/test_branding.py` - verify intelligent splitting at sentence/paragraph boundaries with continuation indicators
- [ ] T036 [US2] Integration test for channel formatting in `tests/integration/test_channel_formatting.py` - verify same data formatted differently per channel

### Implementation for User Story 2

- [ ] T037 [P] [US2] Implement BrandingAgent._format_email method in `agents/branding.py` (apply full markdown, use style guide, no length limits)
- [ ] T038 [P] [US2] Implement BrandingAgent._format_whatsapp method in `agents/branding.py` (apply limited markdown, moderate length, style guide)
- [ ] T039 [P] [US2] Implement BrandingAgent._format_teams method in `agents/branding.py` (adaptive card format, structured layout)
- [ ] T040 [US2] Implement BrandingAgent._split_message helper in `agents/branding.py` (split at natural boundaries, add continuation indicators)
- [ ] T041 [US2] Implement BrandingAgent._strip_markdown helper in `agents/branding.py` (remove all markdown symbols for SMS)
- [ ] T042 [US2] Implement BrandingAgent._apply_style helper in `agents/branding.py` (apply tone, emojis, humor from style guide)
- [ ] T043 [US2] Add channel-specific validation to Quality Agent scorecard criteria (verify format matches channel spec)

**Checkpoint**: At this point, User Stories 1 AND 2 should both work - responses properly formatted for each channel

---

## Phase 5: User Story 3 - Quality Validation with Refinement (Priority: P1)

**Goal**: System detects low-quality response, automatically refines it once, or sends graceful failure message if refinement doesn't help

**Independent Test**: Trigger scenarios producing poor initial responses, verify Quality Agent detects issues, triggers refinement, sends improved response or graceful failure

### Tests for User Story 3

- [ ] T044 [P] [US3] Unit test for Planner.refine_response in `tests/unit/test_planner.py` - verify refinement based on failed criteria feedback
- [ ] T045 [P] [US3] Unit test for Planner.compose_graceful_failure in `tests/unit/test_planner.py` - verify user-friendly error messages
- [ ] T046 [P] [US3] Unit test for Quality.validate_graceful_failure in `tests/unit/test_quality.py` - verify graceful failure approval and logging
- [ ] T047 [US3] Integration test for quality validation with refinement in `tests/integration/test_quality_validation.py` - verify refinement loop (fail → refine → revalidate → send or graceful failure)

### Implementation for User Story 3

- [ ] T048 [P] [US3] Implement PlannerAgent.refine_response method in `agents/planner.py` (uses LLM with failed criteria feedback to improve response)
- [ ] T049 [P] [US3] Implement PlannerAgent.compose_graceful_failure method in `agents/planner.py` (creates user-friendly error message based on failure reason)
- [ ] T050 [P] [US3] Implement QualityAgent.validate_graceful_failure method in `agents/quality.py` (always approves, logs failure details)
- [ ] T051 [US3] Create Temporal activities in `unified_workflows.py`: planner_refine_activity, planner_graceful_failure_activity, quality_validate_graceful_failure_activity
- [ ] T052 [US3] Add refinement loop to MultiAgentConversationWorkflow in `unified_workflows.py` (Step 6: if validation fails and refinement_count < 1, refine → reformat → revalidate)
- [ ] T053 [US3] Add graceful failure path to MultiAgentConversationWorkflow in `unified_workflows.py` (Step 7: if still fails, compose graceful failure → validate → send)
- [ ] T054 [US3] Add ValidationFailureLog creation in QualityAgent when validation fails (log original question, scorecard, failed criteria, refinement attempts, final outcome)
- [ ] T055 [US3] Add refinement tracking to MultiAgentWorkflowState in `agents/models.py` (track refinement_count, ensure max 1 attempt)

**Checkpoint**: All P1 user stories complete - quality validation with refinement working, graceful failures logged

---

## Phase 6: User Story 4 - Agent Coordination for Complex Requests (Priority: P2)

**Goal**: User asks complex question requiring multiple data sources ("Show my hours and project status"), Planner coordinates Timesheet Agent, composes unified response, ensures quality validation

**Independent Test**: Send complex queries requiring multiple tool calls, verify Planner coordinates correctly, data gathered from all sources, response coherent, quality validation passes

### Tests for User Story 4

- [ ] T056 [P] [US4] Unit test for Planner.analyze_request with complex queries in `tests/unit/test_planner.py` - verify multi-step execution plans
- [ ] T057 [P] [US4] Unit test for Timesheet.extract_timesheet_data with multiple query types in `tests/unit/test_timesheet.py` - verify projects, hours, time entries extraction
- [ ] T058 [US4] Integration test for complex request coordination in `tests/integration/test_agent_coordination.py` - verify multiple Timesheet calls, unified response composition

### Implementation for User Story 4

- [ ] T059 [US4] Enhance PlannerAgent.analyze_request in `agents/planner.py` to handle complex multi-part queries (identify multiple data needs, create multi-step plans)
- [ ] T060 [US4] Enhance TimesheetAgent.extract_timesheet_data in `agents/timesheet.py` to support multiple query types (hours_logged, projects, time_entries, summary)
- [ ] T061 [US4] Enhance PlannerAgent.compose_response in `agents/planner.py` to compose unified responses from multiple data sources
- [ ] T062 [US4] Add error handling to TimesheetAgent for API failures (return success: false with error message, log API errors)
- [ ] T063 [US4] Update MultiAgentConversationWorkflow to support multiple Timesheet calls if execution plan requires it
- [ ] T064 [US4] Add conversation context handling to PlannerAgent for follow-up questions ("And what about yesterday?")

**Checkpoint**: User Story 4 complete - complex requests with multiple data sources handled correctly

---

## Phase 7: User Story 5 - Graceful Failure Logging (Priority: P2)

**Goal**: When system cannot produce quality response after refinement, send user-friendly message and log detailed debugging information for troubleshooting within 5 minutes

**Independent Test**: Trigger failure scenarios, verify user receives friendly message, detailed logs created with failure reasons, developers can troubleshoot within 5 minutes using logs

### Tests for User Story 5

- [ ] T065 [P] [US5] Unit test for ValidationFailureLog creation in `tests/unit/test_quality.py` - verify all required fields logged (question, scorecard, failures, refinement, outcome)
- [ ] T066 [P] [US5] Unit test for AgentInteractionLog creation in `tests/unit/test_planner.py` - verify agent calls logged with timing and success/error
- [ ] T067 [US5] Integration test for failure logging in `tests/integration/test_quality_validation.py` - verify complete failure scenario logged with all details

### Implementation for User Story 5

- [ ] T068 [US5] Enhance QualityAgent.validate_response to create ValidationFailureLog when validation fails (include original question, scorecard, validation results, refinement attempts, final outcome, failure reason)
- [ ] T069 [US5] Enhance BaseAgent.log_interaction to use structured logging with JSON format (enable easy parsing and searching)
- [ ] T070 [US5] Add failure pattern aggregation to logging system (detect multiple failures within time window, create alerts)
- [ ] T071 [US5] Add detailed error context to all agent error handling (include user context, request details, stack traces)
- [ ] T072 [US5] Create logging documentation in `specs/001-multi-agent-architecture/logging-guide.md` (explain log formats, how to search, common failure patterns)

**Checkpoint**: User Story 5 complete - comprehensive logging enables quick troubleshooting

---

## Phase 8: User Story 6 - Brand-Consistent Responses (Priority: P3)

**Goal**: All responses maintain consistent tone, style, brand voice across channels with appropriate emojis and humor

**Independent Test**: Review responses across channels, verify consistent tone, appropriate emoji usage, brand-aligned humor

### Tests for User Story 6

- [ ] T073 [P] [US6] Unit test for BrandingAgent._apply_style in `tests/unit/test_branding.py` - verify tone application (conversational, empathetic, encouraging)
- [ ] T074 [P] [US6] Unit test for emoji usage in `tests/unit/test_branding.py` - verify correct emojis used (✅ success, ⚠️ warning, ❌ error, ℹ️ info)
- [ ] T075 [US6] Integration test for brand consistency in `tests/integration/test_channel_formatting.py` - verify same tone across all channels

### Implementation for User Story 6

- [ ] T076 [US6] Enhance BrandingAgent._apply_style to use tone settings from style guide (default, error, success tones)
- [ ] T077 [US6] Implement emoji insertion logic in BrandingAgent based on style guide and channel capabilities
- [ ] T078 [US6] Implement humor insertion logic in BrandingAgent (light, work-related, occasional frequency)
- [ ] T079 [US6] Add user name personalization to BrandingAgent when formatting.use_user_name is true
- [ ] T080 [US6] Add greeting/sign-off logic to BrandingAgent based on formatting preferences
- [ ] T081 [US6] Create style guide validation schema to ensure config changes don't break system
- [ ] T082 [US6] Add hot-reload capability for style guide (watch file for changes, reload without restart)

**Checkpoint**: All user stories complete - full multi-agent system with quality control, channel formatting, brand consistency

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories and final production readiness

- [ ] T083 [P] Add comprehensive docstrings to all agent classes and methods in `agents/*.py`
- [ ] T084 [P] Add type hints to all function signatures in `agents/*.py`
- [ ] T085 [P] Create README.md for agents module in `agents/README.md` with architecture overview and usage examples
- [ ] T086 [P] Update SYSTEM_ANALYSIS.md with multi-agent architecture documentation
- [ ] T087 [P] Create performance monitoring dashboard queries (track P95 latency, validation pass rate, refinement success rate, graceful failure rate)
- [ ] T088 Code cleanup and refactoring: extract common patterns, remove duplication, improve readability
- [ ] T089 Performance optimization: add caching for common queries, optimize LLM prompts, reduce unnecessary LLM calls
- [ ] T090 [P] Security review: sanitize PII from logs, validate all inputs, secure config file access
- [ ] T091 [P] Add deployment documentation in `specs/001-multi-agent-architecture/deployment.md` (Docker build, Azure deployment, feature flag usage)
- [ ] T092 Run complete test suite and verify all tests pass: `pytest tests/ -v`
- [ ] T093 Run quickstart.md validation: follow guide end-to-end, verify all steps work
- [ ] T094 Create rollback plan in case multi-agent system has issues (how to disable feature flag, revert to single-agent)
- [ ] T095 [P] Create monitoring alerts for critical metrics (response time >10s, validation failure rate >10%, graceful failure rate >1%)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phases 3-8)**: All depend on Foundational phase completion
  - US1 (P1): Can start after Foundational - No dependencies on other stories
  - US2 (P1): Can start after Foundational - Extends US1 branding, but independently testable
  - US3 (P1): Can start after Foundational - Extends US1 workflow, but independently testable
  - US4 (P2): Can start after Foundational - Enhances US1 coordination, but independently testable
  - US5 (P2): Can start after Foundational - Enhances US3 logging, but independently testable
  - US6 (P3): Can start after Foundational - Enhances US2 branding, but independently testable
- **Polish (Phase 9)**: Depends on all desired user stories being complete

### User Story Dependencies

**Priority 1 (MVP - Must Have)**:
- **User Story 1**: Quality-Validated Timesheet Response - FOUNDATION for all other stories
- **User Story 2**: Channel-Specific Formatting - CRITICAL for user experience
- **User Story 3**: Quality Validation with Refinement - CORE quality control mechanism

**Priority 2 (Important - Should Have)**:
- **User Story 4**: Agent Coordination for Complex Requests - Enhances US1
- **User Story 5**: Graceful Failure Logging - Enhances US3

**Priority 3 (Nice to Have - Could Have)**:
- **User Story 6**: Brand-Consistent Responses - Enhances US2

### Within Each User Story

- Tests MUST be written and FAIL before implementation
- Models before services
- Services before workflow integration
- Core implementation before enhancements
- Story complete before moving to next priority

### Parallel Opportunities

**Setup Phase**:
- T003, T004, T005, T006 can all run in parallel

**Foundational Phase**:
- T008, T009, T010, T011 (data models) can run in parallel after T007
- T013, T014, T015 (test fixtures) can run in parallel

**User Story 1**:
- T016, T017, T018, T019, T020 (all unit tests) can run in parallel
- T022, T023 (Planner and Timesheet agents) can run in parallel
- T025, T026 (Branding and Quality agents) can run in parallel after T024

**User Story 2**:
- T033, T034, T035 (all unit tests) can run in parallel
- T037, T038, T039 (all format methods) can run in parallel

**User Story 3**:
- T044, T045, T046 (all unit tests) can run in parallel
- T048, T049, T050 (all Planner/Quality methods) can run in parallel

**User Story 4**:
- T056, T057 (unit tests) can run in parallel

**User Story 5**:
- T065, T066 (unit tests) can run in parallel

**User Story 6**:
- T073, T074 (unit tests) can run in parallel

**Polish Phase**:
- T083, T084, T085, T086, T087, T090, T091, T095 can all run in parallel

**Different user stories can be worked on in parallel by different team members after Foundational phase completes**

---

## Parallel Example: User Story 1

```bash
# Launch all unit tests for User Story 1 together:
Task T016: "Unit test for Planner.analyze_request in tests/unit/test_planner.py"
Task T017: "Unit test for Timesheet.extract_timesheet_data in tests/unit/test_timesheet.py"
Task T018: "Unit test for Planner.compose_response in tests/unit/test_planner.py"
Task T019: "Unit test for Branding.format_for_channel (SMS) in tests/unit/test_branding.py"
Task T020: "Unit test for Quality.validate_response in tests/unit/test_quality.py"

# Launch Planner and Timesheet agents together:
Task T022: "Implement PlannerAgent class in agents/planner.py"
Task T023: "Implement TimesheetAgent class in agents/timesheet.py"

# Launch Branding and Quality agents together (after T024):
Task T025: "Implement BrandingAgent class in agents/branding.py"
Task T026: "Implement QualityAgent class in agents/quality.py"
```

---

## Implementation Strategy

### MVP First (User Stories 1, 2, 3 - All P1)

1. Complete Phase 1: Setup (T001-T006)
2. Complete Phase 2: Foundational (T007-T015) - CRITICAL, blocks all stories
3. Complete Phase 3: User Story 1 (T016-T032) - Core quality-validated workflow
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Complete Phase 4: User Story 2 (T033-T043) - Channel formatting
6. **STOP and VALIDATE**: Test User Story 2 independently
7. Complete Phase 5: User Story 3 (T044-T055) - Refinement and graceful failures
8. **STOP and VALIDATE**: Test User Story 3 independently
9. Deploy/demo MVP with feature flag

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (Basic multi-agent!)
3. Add User Story 2 → Test independently → Deploy/Demo (Channel formatting!)
4. Add User Story 3 → Test independently → Deploy/Demo (Quality control complete - MVP!)
5. Add User Story 4 → Test independently → Deploy/Demo (Complex queries!)
6. Add User Story 5 → Test independently → Deploy/Demo (Better debugging!)
7. Add User Story 6 → Test independently → Deploy/Demo (Brand consistency!)
8. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together (T001-T015)
2. Once Foundational is done:
   - Developer A: User Story 1 (T016-T032)
   - Developer B: User Story 2 (T033-T043) - can start in parallel
   - Developer C: User Story 3 (T044-T055) - can start in parallel
3. Stories complete and integrate independently
4. Continue with P2 stories (US4, US5) and P3 stories (US6)

---

## Task Summary

**Total Tasks**: 95 tasks

**Tasks by Phase**:
- Phase 1 (Setup): 6 tasks
- Phase 2 (Foundational): 9 tasks
- Phase 3 (US1 - P1): 17 tasks
- Phase 4 (US2 - P1): 11 tasks
- Phase 5 (US3 - P1): 12 tasks
- Phase 6 (US4 - P2): 9 tasks
- Phase 7 (US5 - P2): 8 tasks
- Phase 8 (US6 - P3): 10 tasks
- Phase 9 (Polish): 13 tasks

**Parallel Opportunities**: 42 tasks marked [P] can run in parallel within their phase

**Independent Test Criteria**:
- US1: Send SMS timesheet query, verify accurate response in plain text <1600 chars within 10s
- US2: Send same query via SMS/Email/WhatsApp, verify channel-appropriate formatting
- US3: Trigger poor response, verify refinement or graceful failure
- US4: Send complex query, verify coordinated data extraction and unified response
- US5: Trigger failure, verify detailed logs enable 5-minute troubleshooting
- US6: Review responses, verify consistent brand voice and tone

**Suggested MVP Scope**: User Stories 1, 2, 3 (all P1) = 40 implementation tasks + 15 foundational tasks = 55 tasks total

---

## Notes

- [P] tasks = different files, no dependencies, can run in parallel
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing (TDD approach)
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Feature flag (USE_MULTI_AGENT) enables gradual rollout and easy rollback
- All agents reuse existing LLM client, Temporal infrastructure, Supabase database
- Zero breaking changes - existing single-agent workflow remains functional
