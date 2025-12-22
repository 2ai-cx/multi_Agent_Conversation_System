# Feature Specification: Multi-Agent Conversation System

**Feature Branch**: `001-multi-agent-architecture`  
**Created**: November 24, 2025  
**Status**: Draft  
**Input**: User description: "Replace the current single-agent conversation system with a multi-agent architecture for better quality control and channel-specific responses."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Quality-Validated Timesheet Response (Priority: P1)

A user sends "Check my timesheet" via SMS. The system coordinates multiple agents to extract data, validate quality, format for SMS, and send a response that correctly answers the question in plain text format suitable for SMS.

**Why this priority**: This is the core value proposition - preventing bad responses from reaching users while maintaining all existing functionality. It demonstrates the complete multi-agent workflow and quality validation.

**Independent Test**: Can be fully tested by sending a timesheet query via SMS and verifying: (1) response is accurate, (2) response passes quality validation, (3) response is formatted correctly for SMS (plain text, no markdown, under 1600 chars), (4) response is delivered within 10 seconds.

**Acceptance Scenarios**:

1. **Given** user has logged 32 hours this week, **When** user texts "Check my timesheet", **Then** Planner creates execution plan, Timesheet Agent extracts data showing 32 hours, Planner composes response, Branding Agent formats for SMS (plain text), Quality Agent validates against scorecard, and user receives "You've logged 32/40 hours this week" within 10 seconds
2. **Given** user has no timesheet entries, **When** user texts "How many hours today?", **Then** system responds with "You haven't logged any hours today" in plain text format, validated by Quality Agent
3. **Given** user asks ambiguous question "What's my status?", **When** Planner creates scorecard with criteria, **Then** Quality Agent validates response answers the question appropriately

---

### User Story 2 - Channel-Specific Formatting (Priority: P1)

A user receives the same timesheet information via different channels (SMS, Email, WhatsApp) and each response is formatted appropriately for that channel's capabilities and constraints.

**Why this priority**: Channel-specific formatting is a key differentiator from the current system and prevents user frustration from poorly formatted messages (e.g., markdown in SMS).

**Independent Test**: Can be tested by sending identical query via SMS, Email, and WhatsApp, then verifying SMS gets plain text (no markdown, max 1600 chars), Email gets full markdown with formatting, and WhatsApp gets limited markdown.

**Acceptance Scenarios**:

1. **Given** user requests project list via SMS, **When** Branding Agent formats response, **Then** response is plain text with no markdown, uses line breaks for readability, and stays under 1600 characters
2. **Given** user requests project list via Email, **When** Branding Agent formats response, **Then** response uses full markdown with headers, tables, bold text, and links
3. **Given** user requests project list via WhatsApp, **When** Branding Agent formats response, **Then** response uses limited markdown (bold, italic) but no tables or complex formatting
4. **Given** response exceeds channel limits, **When** Branding Agent processes it, **Then** message is split intelligently at natural boundaries (sentences, paragraphs) with continuation indicators

---

### User Story 3 - Quality Validation with Refinement (Priority: P1)

The system detects a low-quality response (doesn't answer question, wrong format, contains errors) and automatically refines it once before sending, or sends a graceful failure message if refinement doesn't help.

**Why this priority**: This is the core quality control mechanism that prevents bad responses from reaching users - the primary problem being solved.

**Independent Test**: Can be tested by triggering scenarios that produce poor initial responses, then verifying Quality Agent detects issues, triggers refinement, and either sends improved response or graceful failure message.

**Acceptance Scenarios**:

1. **Given** Planner composes response that doesn't answer the question, **When** Quality Agent validates against scorecard, **Then** validation fails, Planner refines response with feedback, Quality Agent revalidates, and improved response is sent
2. **Given** Branding Agent formats response with markdown for SMS channel, **When** Quality Agent validates format, **Then** validation fails, Planner requests reformatting, Branding Agent removes markdown, and plain text response is sent
3. **Given** refinement attempt still produces poor response, **When** Quality Agent revalidates, **Then** validation fails again, system sends graceful failure message "I can't help with that right now", and logs detailed failure reason for debugging
4. **Given** Quality Agent validates response, **When** all scorecard criteria pass, **Then** response is approved and sent immediately without refinement

---

### User Story 4 - Agent Coordination for Complex Requests (Priority: P2)

A user asks a complex question requiring multiple data sources ("Show my hours and project status"). The Planner coordinates Timesheet Agent to gather data, composes a unified response, and ensures quality validation before sending.

**Why this priority**: Demonstrates agent coordination capabilities and validates the architecture can handle complex multi-step workflows while maintaining quality.

**Independent Test**: Can be tested by sending complex queries requiring multiple tool calls, then verifying Planner coordinates agents correctly, data is gathered from all sources, response is coherent, and quality validation passes.

**Acceptance Scenarios**:

1. **Given** user asks "Show my hours and active projects", **When** Planner analyzes request, **Then** Planner creates plan to call Timesheet Agent for hours and projects, coordinates execution, composes unified response, and Quality Agent validates completeness
2. **Given** Timesheet Agent call fails (API error), **When** Planner receives error, **Then** Planner handles error gracefully, composes partial response or failure message, and Quality Agent validates appropriateness
3. **Given** user asks follow-up question "And what about yesterday?", **When** Planner analyzes with conversation context, **Then** Planner understands context, coordinates Timesheet Agent with correct date range, and maintains conversation continuity

---

### User Story 5 - Graceful Failure Logging (Priority: P2)

When the system cannot produce a quality response after refinement, it sends a user-friendly failure message and logs detailed debugging information for quick troubleshooting.

**Why this priority**: Ensures user experience remains positive even in failure cases, and enables rapid debugging to improve system quality over time.

**Independent Test**: Can be tested by triggering failure scenarios, then verifying user receives friendly message, detailed logs are created with failure reasons, and developers can troubleshoot within 5 minutes using logs.

**Acceptance Scenarios**:

1. **Given** system cannot answer user question after refinement, **When** Quality Agent approves graceful failure, **Then** user receives "I can't help with that right now. Please try rephrasing your question" and detailed log entry is created with: original question, scorecard criteria, validation failures, refinement attempts, and final failure reason
2. **Given** Timesheet Agent encounters API error, **When** Planner composes error response, **Then** user receives friendly message "I'm having trouble accessing your timesheet data" and log includes API error details, retry attempts, and user context
3. **Given** multiple failures occur within 1 hour, **When** logging system detects pattern, **Then** system creates alert for investigation and logs include aggregated failure patterns

---

### User Story 6 - Brand-Consistent Responses (Priority: P3)

All responses maintain consistent tone, style, and brand voice across channels, with appropriate use of emojis and humor matching the brand personality.

**Why this priority**: Enhances user experience and brand perception, but not critical for core functionality.

**Independent Test**: Can be tested by reviewing responses across channels and verifying consistent tone, appropriate emoji usage, and brand-aligned humor.

**Acceptance Scenarios**:

1. **Given** Branding Agent has style guide configured, **When** formatting any response, **Then** response uses consistent tone (friendly, professional), appropriate emojis (✅ for success, ⚠️ for warnings), and brand-aligned humor
2. **Given** user receives error message, **When** Branding Agent formats it, **Then** message is empathetic and helpful, not technical or blaming
3. **Given** style guide is updated, **When** Branding Agent processes next response, **Then** new style rules are applied immediately without code changes

---

### Edge Cases

- **What happens when Quality Agent validation takes longer than 1 second?** System logs performance warning but continues processing. If total response time exceeds 10 seconds, system sends partial response or graceful failure.

- **What happens when Timesheet Agent API call times out?** Planner receives timeout error, composes graceful failure message, Quality Agent validates failure message is appropriate, and detailed error is logged.

- **What happens when user sends message while previous response is being processed?** System queues new message, completes current workflow, then processes queued message with updated conversation context.

- **What happens when Branding Agent cannot fit response within channel limits even after splitting?** System sends summary response within limits and offers to send full details via Email.

- **What happens when refinement loop could continue indefinitely?** System enforces maximum 1 refinement attempt, then sends graceful failure to prevent infinite loops.

- **What happens when scorecard criteria are ambiguous or contradictory?** Planner creates clear, measurable boolean criteria. If Quality Agent cannot evaluate, it logs warning and defaults to approval with flag for review.

- **What happens when multiple agents try to access shared resources simultaneously?** System uses existing Temporal workflow isolation to prevent conflicts. Each workflow instance has its own agent instances.

- **What happens when user switches channels mid-conversation?** System maintains conversation continuity using existing conversation_id, agents have no channel-specific state, and Branding Agent adapts format to new channel.

## Requirements *(mandatory)*

### Functional Requirements

#### Agent Architecture

- **FR-001**: System MUST implement four distinct agent types: Planner Agent (coordinator), Timesheet Agent (data specialist), Branding Agent (formatter), and Quality Agent (validator)
- **FR-002**: Each agent MUST operate independently with clear input/output contracts
- **FR-003**: Agents MUST communicate through well-defined interfaces without direct coupling
- **FR-004**: System MUST support agent instances running concurrently within same workflow

#### Planner Agent (Coordinator)

- **FR-005**: Planner Agent MUST analyze incoming user requests and determine required actions
- **FR-006**: Planner Agent MUST create execution plans specifying which agents to invoke and in what order
- **FR-007**: Planner Agent MUST generate scorecards with measurable, boolean pass/fail criteria for Quality Agent validation
- **FR-008**: Planner Agent MUST coordinate Timesheet Agent for data extraction when request requires timesheet information
- **FR-009**: Planner Agent MUST compose responses based on data received from Timesheet Agent
- **FR-010**: Planner Agent MUST handle refinement requests from Quality Agent (maximum 1 refinement attempt per request)
- **FR-011**: Planner Agent MUST compose graceful failure messages when unable to fulfill request after refinement
- **FR-012**: Planner Agent MUST maintain conversation context across multi-turn interactions

#### Timesheet Agent (Data Specialist)

- **FR-013**: Timesheet Agent MUST use existing 51 Harvest API tools without modification
- **FR-014**: Timesheet Agent MUST extract timesheet data (hours logged, projects, time entries) based on Planner requests
- **FR-015**: Timesheet Agent MUST return structured data to Planner Agent
- **FR-016**: Timesheet Agent MUST handle API errors gracefully and return error information to Planner
- **FR-017**: Timesheet Agent MUST use user-specific credentials from existing Supabase user table
- **FR-018**: Timesheet Agent MUST respect user timezone settings for date calculations

#### Branding Agent (Formatter)

- **FR-019**: Branding Agent MUST format responses according to target channel specifications:
  - SMS: plain text only, no markdown, maximum 1600 characters
  - Email: full markdown support (headers, tables, bold, italic, links)
  - WhatsApp: limited markdown (bold, italic only, no tables)
  - Teams: adaptive cards format
- **FR-020**: Branding Agent MUST apply configurable style guide for tone, voice, and personality
- **FR-021**: Branding Agent MUST use emojis appropriately based on style guide and channel capabilities
- **FR-022**: Branding Agent MUST split long messages intelligently at natural boundaries (sentences, paragraphs) when exceeding channel limits
- **FR-023**: Branding Agent MUST add continuation indicators when splitting messages (e.g., "(1/3)", "(continued)")
- **FR-024**: Branding Agent MUST preserve message meaning and coherence when splitting or reformatting

#### Quality Agent (Validator)

- **FR-025**: Quality Agent MUST validate every response against Planner-provided scorecard before sending
- **FR-026**: Quality Agent MUST evaluate each scorecard criterion as boolean pass/fail
- **FR-027**: Quality Agent MUST trigger refinement when any scorecard criterion fails (maximum 1 refinement per request)
- **FR-028**: Quality Agent MUST provide specific feedback to Planner on which criteria failed and why
- **FR-029**: Quality Agent MUST approve graceful failure messages for sending
- **FR-030**: Quality Agent MUST log all validation failures with detailed reasons for debugging
- **FR-031**: Quality Agent MUST complete validation within 1 second per response

#### Workflow Orchestration

- **FR-032**: System MUST execute agent workflow in sequence: User message → Planner analyzes → Timesheet extracts (if needed) → Planner composes → Branding formats → Quality validates → Send or refine
- **FR-033**: System MUST allow maximum 1 refinement attempt: Quality fails → Planner refines → Branding reformats → Quality revalidates → Send or graceful failure
- **FR-034**: System MUST send graceful failure message when refinement attempt still fails validation
- **FR-035**: System MUST complete entire workflow (including refinement if needed) within 10 seconds
- **FR-036**: System MUST maintain backward compatibility with existing conversation workflows

#### Quality Control

- **FR-037**: System MUST prevent any response from being sent without Quality Agent approval
- **FR-038**: System MUST log all quality validation results (pass/fail) for monitoring
- **FR-039**: System MUST track refinement success rate (percentage of refinements that pass revalidation)
- **FR-040**: System MUST ensure graceful failures occur in less than 1% of requests

#### Channel Integration

- **FR-041**: System MUST support all existing channels: SMS (Twilio), WhatsApp (Twilio), Email (Gmail), Teams
- **FR-042**: System MUST preserve existing webhook endpoints and message routing
- **FR-043**: System MUST maintain conversation continuity when user switches channels
- **FR-044**: System MUST use existing Supabase conversation storage without schema changes

#### Performance

- **FR-045**: System MUST respond to user requests within 10 seconds (end-to-end)
- **FR-046**: Quality Agent validation MUST complete within 1 second
- **FR-047**: Branding Agent formatting MUST complete within 500 milliseconds
- **FR-048**: System MUST handle concurrent requests from multiple users without degradation

#### Infrastructure Reuse

- **FR-049**: System MUST use existing Temporal workflows infrastructure
- **FR-050**: System MUST use existing Supabase database for conversation storage
- **FR-051**: System MUST use existing centralized LLM client (llm/ module) for all agent LLM calls
- **FR-052**: System MUST use existing user credential management from Supabase
- **FR-053**: System MUST preserve all existing features (timesheet reminders, tool usage, multi-tenant support)

#### Logging and Debugging

- **FR-054**: System MUST log all agent interactions (which agents called, inputs/outputs, timing)
- **FR-055**: System MUST log all quality validation failures with: original question, scorecard criteria, validation results, refinement attempts, final outcome
- **FR-056**: System MUST log all graceful failures with detailed error information
- **FR-057**: System MUST enable troubleshooting of failures within 5 minutes using logs
- **FR-058**: System MUST aggregate failure patterns for monitoring and alerting

#### Configuration

- **FR-059**: Branding Agent style guide MUST be configurable without code changes
- **FR-060**: System MUST allow configuration of: refinement attempts (default 1), quality validation timeout (default 1s), response timeout (default 10s), channel message limits

### Key Entities

- **Agent**: Represents a specialized component with specific responsibilities (Planner, Timesheet, Branding, Quality). Each agent has clear input/output contracts and operates independently.

- **Execution Plan**: Created by Planner Agent, specifies which agents to invoke, in what order, with what parameters. Guides workflow orchestration.

- **Scorecard**: Created by Planner Agent, contains measurable boolean criteria for Quality Agent to validate. Each criterion has clear pass/fail definition.

- **Validation Result**: Output from Quality Agent, indicates pass/fail for each scorecard criterion, includes specific feedback for failed criteria.

- **Refinement Request**: Sent from Quality Agent to Planner when validation fails, includes specific feedback on what needs improvement.

- **Channel Format Specification**: Defines formatting rules for each channel (SMS, Email, WhatsApp, Teams), including character limits, markdown support, emoji usage.

- **Style Guide**: Configurable rules for tone, voice, personality, emoji usage, humor. Applied by Branding Agent to all responses.

- **Graceful Failure Message**: User-friendly error message sent when system cannot fulfill request after refinement. Approved by Quality Agent before sending.

- **Agent Interaction Log**: Records all agent invocations, inputs, outputs, timing, and outcomes for debugging and monitoring.

- **Validation Failure Log**: Detailed record of quality validation failures, including scorecard criteria, validation results, refinement attempts, and final outcome.

## Success Criteria *(mandatory)*

### Measurable Outcomes

#### Functional Success

- **SC-001**: Multi-agent system handles all current use cases (timesheet queries, project management, conversation) without regression in functionality
- **SC-002**: All responses are validated by Quality Agent before sending (100% validation coverage)
- **SC-003**: Responses are formatted correctly for target channel (100% compliance with channel specifications)
- **SC-004**: System maintains backward compatibility with existing conversation workflows (no breaking changes to APIs or database schema)
- **SC-005**: All 51 existing Harvest tools remain functional and accessible through Timesheet Agent

#### Quality Improvement

- **SC-006**: Quality validation prevents bad responses from reaching users (measured by zero user complaints about incorrect/malformed responses in first month)
- **SC-007**: Refinement improves response quality in more than 70% of cases (measured by validation pass rate after refinement)
- **SC-008**: Graceful failures occur in less than 1% of requests (measured by failure rate in production)
- **SC-009**: Channel-specific formatting eliminates formatting errors (measured by zero markdown in SMS, proper tables in Email)

#### Performance

- **SC-010**: End-to-end response time remains under 10 seconds for 95% of requests
- **SC-011**: Quality validation completes within 1 second for 99% of validations
- **SC-012**: Branding Agent formatting completes within 500 milliseconds for 99% of responses
- **SC-013**: System handles concurrent requests from multiple users without performance degradation (same throughput as current system)

#### Debugging and Monitoring

- **SC-014**: Graceful failures are well-logged with sufficient detail to troubleshoot within 5 minutes (measured by time to identify root cause in failure logs)
- **SC-015**: Debug logs enable quick troubleshooting of any issue within 5 minutes (measured by mean time to diagnosis)
- **SC-016**: All agent interactions are logged with timing and outcomes (100% observability)
- **SC-017**: Failure patterns are aggregated and surfaced for proactive monitoring

#### User Experience

- **SC-018**: Users receive responses in format appropriate for their channel (measured by user feedback and format compliance checks)
- **SC-019**: Users receive helpful error messages when system cannot fulfill request (measured by user satisfaction with error messages)
- **SC-020**: Conversation continuity is maintained when users switch channels (measured by context preservation across channel switches)
- **SC-021**: Brand voice and tone are consistent across all channels and responses (measured by style guide compliance)

#### Operational Excellence

- **SC-022**: System reuses existing infrastructure (Temporal, Supabase, LLM client) without requiring new dependencies
- **SC-023**: Style guide can be updated without code changes (measured by configuration-only style updates)
- **SC-024**: System preserves all existing features (timesheet reminders, multi-tenant support, cross-platform conversations)
- **SC-025**: Deployment does not require database migrations or breaking changes to existing integrations

### Assumptions

- Existing Temporal workflows infrastructure is stable and can support additional workflow complexity
- Existing LLM client (llm/ module) has sufficient capacity for multiple agent LLM calls per request
- Current Supabase schema for conversations and users is adequate for multi-agent system (no schema changes needed)
- Existing 51 Harvest API tools are reliable and can be called by Timesheet Agent without modification
- User credentials in Supabase are valid and accessible for Timesheet Agent
- Channel specifications (SMS 1600 char limit, Email markdown support, etc.) remain stable
- Style guide can be represented as configuration (JSON/YAML) without requiring code changes
- One refinement attempt is sufficient for most quality issues (based on assumption that clear feedback enables effective refinement)
- 10-second response time is acceptable for users across all channels
- Graceful failure rate under 1% is achievable with proper error handling and quality validation
