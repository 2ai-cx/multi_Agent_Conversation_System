# Agent Contracts: Multi-Agent Conversation System

**Feature**: 001-multi-agent-architecture  
**Date**: November 24, 2025  
**Purpose**: Define input/output contracts for all agents

## Overview

This document defines the contracts (interfaces) for all four agents in the multi-agent system. Each agent has clear input/output specifications to enable independent development and testing.

---

## 1. Planner Agent (Coordinator)

### Purpose
Analyzes user requests, creates execution plans, generates scorecards, coordinates other agents, handles refinement, and composes responses.

### Contract: `analyze_request`

**Input**:
```python
{
    "request_id": str,           # Unique request identifier
    "user_message": str,         # User's message
    "channel": str,              # "sms" | "email" | "whatsapp" | "teams"
    "conversation_history": [    # Last 10 messages
        {
            "role": str,         # "user" | "assistant"
            "content": str,
            "timestamp": str
        }
    ],
    "user_context": {            # User information
        "user_id": str,
        "timezone": str,
        "preferences": dict
    }
}
```

**Output**:
```python
{
    "execution_plan": {
        "request_id": str,
        "steps": [
            {
                "agent": str,    # "timesheet" | "planner" | "branding" | "quality"
                "action": str,
                "parameters": dict
            }
        ],
        "requires_timesheet_data": bool,
        "context": dict
    },
    "scorecard": {
        "request_id": str,
        "criteria": [
            {
                "id": str,
                "description": str,
                "expected": str
            }
        ]
    }
}
```

**Error Handling**:
- Returns error if user_message is empty
- Returns error if channel is invalid
- Logs warning if conversation_history is empty (new conversation)

**Performance Target**: < 2 seconds

---

### Contract: `compose_response`

**Input**:
```python
{
    "request_id": str,
    "user_message": str,
    "timesheet_data": dict | None,  # From Timesheet Agent
    "conversation_history": list,
    "user_context": dict
}
```

**Output**:
```python
{
    "response": str,             # Composed response (channel-agnostic)
    "metadata": {
        "used_timesheet_data": bool,
        "response_type": str,    # "data" | "conversational" | "error"
        "confidence": float      # 0.0 to 1.0
    }
}
```

**Error Handling**:
- Returns graceful error message if timesheet_data is required but missing
- Handles API errors from timesheet extraction
- Falls back to conversational response if data unavailable

**Performance Target**: < 2 seconds

---

### Contract: `refine_response`

**Input**:
```python
{
    "request_id": str,
    "original_response": str,
    "failed_criteria": [
        {
            "id": str,
            "description": str,
            "expected": str,
            "feedback": str
        }
    ],
    "attempt_number": int        # Always 1 (max 1 refinement)
}
```

**Output**:
```python
{
    "refined_response": str,
    "changes_made": [str],       # List of changes applied
    "confidence": float          # 0.0 to 1.0
}
```

**Error Handling**:
- Returns error if attempt_number > 1
- Returns original response with warning if refinement fails
- Logs all refinement attempts

**Performance Target**: < 2 seconds

---

### Contract: `compose_graceful_failure`

**Input**:
```python
{
    "request_id": str,
    "user_message": str,
    "failure_reason": str,
    "channel": str
}
```

**Output**:
```python
{
    "failure_message": str,      # User-friendly error message
    "metadata": {
        "failure_type": str,     # "validation" | "api_error" | "timeout"
        "logged": bool
    }
}
```

**Error Handling**:
- Always succeeds (graceful failure cannot fail)
- Logs failure details for debugging

**Performance Target**: < 500ms

---

## 2. Timesheet Agent (Data Specialist)

### Purpose
Extracts timesheet data using existing 51 Harvest API tools.

### Contract: `extract_timesheet_data`

**Input**:
```python
{
    "request_id": str,
    "user_id": str,
    "query_type": str,           # "hours_logged" | "projects" | "time_entries" | "summary"
    "parameters": {
        "date_range": str | None,  # "today" | "this_week" | "this_month" | "YYYY-MM-DD:YYYY-MM-DD"
        "project_name": str | None,
        "include_details": bool
    },
    "user_credentials": {
        "harvest_access_token": str,
        "harvest_account_id": str,
        "harvest_user_id": int
    },
    "user_timezone": str         # e.g., "Australia/Sydney"
}
```

**Output**:
```python
{
    "data": {
        "hours_logged": float | None,
        "hours_target": float | None,
        "projects": list | None,
        "time_entries": list | None,
        "summary": dict | None
    },
    "metadata": {
        "tools_used": [str],     # List of Harvest tools called
        "api_calls": int,
        "cache_hit": bool
    },
    "success": bool,
    "error": str | None
}
```

**Error Handling**:
- Returns `success: false` with error message if Harvest API fails
- Returns `success: false` if user credentials invalid
- Returns `success: false` if date range invalid
- Logs all API errors with user context

**Performance Target**: < 2 seconds (including Harvest API calls)

---

## 3. Branding Agent (Formatter)

### Purpose
Formats responses according to channel specifications and style guide.

### Contract: `format_for_channel`

**Input**:
```python
{
    "request_id": str,
    "response": str,             # Channel-agnostic response from Planner
    "channel": str,              # "sms" | "email" | "whatsapp" | "teams"
    "style_guide": dict,         # Loaded from config/style_guide.yaml
    "channel_spec": dict,        # Loaded from config/channels.yaml
    "user_context": {
        "user_name": str | None,
        "preferences": dict
    }
}
```

**Output**:
```python
{
    "formatted_response": {
        "content": str,
        "is_split": bool,
        "parts": [               # If is_split is true
            {
                "sequence": int,
                "content": str,
                "continuation_indicator": str
            }
        ],
        "metadata": {
            "emojis_used": [str],
            "markdown_applied": bool,
            "length": int,
            "split_count": int
        }
    }
}
```

**Channel-Specific Rules**:

**SMS**:
- Max 1600 characters
- Plain text only (no markdown)
- Emojis allowed (if style guide permits)
- Split at sentence boundaries if needed

**Email**:
- Unlimited length
- Full markdown support (headers, tables, bold, italic, links, code)
- Rich formatting encouraged
- No splitting needed

**WhatsApp**:
- Moderate length (recommend < 4000 chars)
- Limited markdown (bold, italic only)
- Emojis encouraged
- Split at paragraph boundaries if needed

**Teams**:
- Adaptive card format
- Structured layout
- Action buttons if applicable
- Rich media support

**Error Handling**:
- Returns error if channel is invalid
- Returns plain text fallback if formatting fails
- Logs formatting errors

**Performance Target**: < 500ms

---

## 4. Quality Agent (Validator)

### Purpose
Validates responses against scorecard criteria before sending.

### Contract: `validate_response`

**Input**:
```python
{
    "request_id": str,
    "response": str,             # Formatted response from Branding Agent
    "scorecard": {
        "request_id": str,
        "criteria": [
            {
                "id": str,
                "description": str,
                "expected": str
            }
        ]
    },
    "channel": str,
    "original_question": str
}
```

**Output**:
```python
{
    "validation_result": {
        "passed": bool,
        "scorecard": {
            "request_id": str,
            "criteria": [
                {
                    "id": str,
                    "description": str,
                    "expected": str,
                    "passed": bool,
                    "feedback": str | None
                }
            ],
            "overall_passed": bool,
            "evaluated_at": str
        },
        "failed_criteria_ids": [str],
        "feedback": str | None   # Aggregated feedback for refinement
    }
}
```

**Validation Logic**:
- Evaluates each criterion as boolean (pass/fail)
- Provides specific feedback for failed criteria
- Aggregates feedback for refinement
- Logs all validation results

**Error Handling**:
- Returns error if scorecard is invalid
- Defaults to approval with warning if validation fails (prevents blocking)
- Logs all validation errors

**Performance Target**: < 1 second

---

### Contract: `validate_graceful_failure`

**Input**:
```python
{
    "request_id": str,
    "failure_message": str,
    "failure_reason": str
}
```

**Output**:
```python
{
    "approved": bool,            # Always true for graceful failures
    "logged": bool
}
```

**Error Handling**:
- Always approves graceful failures
- Logs failure details for debugging

**Performance Target**: < 100ms

---

## Workflow Orchestration Contract

### Multi-Agent Conversation Workflow

**Input** (from webhook):
```python
{
    "user_id": str,
    "message": str,
    "channel": str,
    "conversation_id": str,
    "metadata": dict
}
```

**Workflow Steps**:
```python
1. planner.analyze_request() → execution_plan, scorecard
2. IF execution_plan.requires_timesheet_data:
       timesheet.extract_timesheet_data() → timesheet_data
3. planner.compose_response() → response
4. branding.format_for_channel() → formatted_response
5. quality.validate_response() → validation_result
6. IF NOT validation_result.passed AND refinement_count < 1:
       planner.refine_response() → refined_response
       branding.format_for_channel() → reformatted_response
       quality.validate_response() → revalidation_result
7. IF STILL NOT passed:
       planner.compose_graceful_failure() → failure_message
       quality.validate_graceful_failure() → approval
8. Send final response to user
```

**Output**:
```python
{
    "request_id": str,
    "final_response": str,
    "validation_passed": bool,
    "refinement_attempted": bool,
    "graceful_failure": bool,
    "metadata": {
        "total_duration_ms": int,
        "agent_calls": int,
        "llm_calls": int
    }
}
```

---

## Agent Communication Pattern

All agents are Temporal activities called by the workflow orchestrator:

```python
# Workflow orchestrates agent calls
@workflow.defn
class MultiAgentConversationWorkflow:
    @workflow.run
    async def run(self, request: dict) -> dict:
        # Step 1: Planner analyzes
        plan_result = await workflow.execute_activity(
            planner_analyze_request,
            args=[request],
            start_to_close_timeout=timedelta(seconds=5)
        )
        
        # Step 2: Timesheet extracts (if needed)
        if plan_result["execution_plan"]["requires_timesheet_data"]:
            timesheet_data = await workflow.execute_activity(
                timesheet_extract_data,
                args=[...],
                start_to_close_timeout=timedelta(seconds=5)
            )
        
        # Step 3: Planner composes
        response = await workflow.execute_activity(
            planner_compose_response,
            args=[...],
            start_to_close_timeout=timedelta(seconds=5)
        )
        
        # Step 4: Branding formats
        formatted = await workflow.execute_activity(
            branding_format_for_channel,
            args=[...],
            start_to_close_timeout=timedelta(seconds=2)
        )
        
        # Step 5: Quality validates
        validation = await workflow.execute_activity(
            quality_validate_response,
            args=[...],
            start_to_close_timeout=timedelta(seconds=2)
        )
        
        # Step 6: Refinement if needed
        if not validation["validation_result"]["passed"]:
            # ... refinement logic
        
        return final_result
```

---

## Testing Contracts

### Unit Test Contract (per agent)

Each agent must have unit tests that:
- Test happy path with valid inputs
- Test error handling with invalid inputs
- Test edge cases (empty strings, null values, etc.)
- Mock external dependencies (LLM, Harvest API, etc.)
- Verify performance targets

### Integration Test Contract (workflow)

Multi-agent workflow must have integration tests that:
- Test complete workflow end-to-end
- Test refinement loop
- Test graceful failure path
- Test channel-specific formatting
- Verify all agents called in correct order
- Verify performance targets (< 10s total)

---

## Summary

All agent contracts are:
- ✅ **Clearly defined** with input/output schemas
- ✅ **Type-safe** using Pydantic models
- ✅ **Independently testable** with mocked dependencies
- ✅ **Performance-bounded** with specific targets
- ✅ **Error-resilient** with graceful degradation
- ✅ **Observable** with comprehensive logging

These contracts enable parallel development of agents and ensure system reliability.
