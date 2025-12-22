# Data Model: Multi-Agent Conversation System

**Feature**: 001-multi-agent-architecture  
**Date**: November 24, 2025  
**Purpose**: Define data structures for multi-agent system entities

## Overview

This document defines the data models for the multi-agent conversation system. All models use Pydantic for validation and type safety, with JSON serialization for logging and persistence.

---

## Core Agent Models

### 1. ExecutionPlan

**Purpose**: Created by Planner Agent to specify workflow execution steps

**Fields**:
- `request_id`: Unique identifier for the request
- `user_message`: Original user message
- `channel`: Communication channel (sms, email, whatsapp, teams)
- `steps`: List of execution steps (which agents to call, in what order)
- `requires_timesheet_data`: Boolean flag for Timesheet Agent invocation
- `context`: Conversation context (previous messages, user info)
- `created_at`: Timestamp

**Validation Rules**:
- `request_id` must be unique UUID
- `channel` must be one of: sms, email, whatsapp, teams
- `steps` must not be empty
- `created_at` must be ISO 8601 format

**State Transitions**:
- Created → In Progress → Completed/Failed

**Pydantic Model**:
```python
from pydantic import BaseModel, Field, validator
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum

class Channel(str, Enum):
    SMS = "sms"
    EMAIL = "email"
    WHATSAPP = "whatsapp"
    TEAMS = "teams"

class ExecutionStep(BaseModel):
    agent: str = Field(..., description="Agent to invoke")
    action: str = Field(..., description="Action to perform")
    parameters: Dict[str, Any] = Field(default_factory=dict)

class ExecutionPlan(BaseModel):
    request_id: str = Field(..., description="Unique request identifier")
    user_message: str = Field(..., description="Original user message")
    channel: Channel = Field(..., description="Communication channel")
    steps: List[ExecutionStep] = Field(..., description="Execution steps")
    requires_timesheet_data: bool = Field(default=False)
    context: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    @validator('steps')
    def steps_not_empty(cls, v):
        if not v:
            raise ValueError('Execution plan must have at least one step')
        return v
```

---

### 2. Scorecard

**Purpose**: Created by Planner Agent for Quality Agent validation

**Fields**:
- `request_id`: Links to ExecutionPlan
- `criteria`: List of validation criteria (boolean pass/fail)
- `overall_passed`: Computed from all criteria
- `created_at`: Timestamp
- `evaluated_at`: When validation completed

**Validation Rules**:
- Each criterion must have unique ID
- Criterion description must be specific and measurable
- `overall_passed` is true only if ALL criteria pass

**Relationships**:
- One-to-one with ExecutionPlan
- One-to-many with ScorecardCriterion

**Pydantic Model**:
```python
class ScorecardCriterion(BaseModel):
    id: str = Field(..., description="Unique criterion identifier")
    description: str = Field(..., description="What is being validated")
    expected: str = Field(..., description="Expected outcome")
    passed: Optional[bool] = Field(None, description="Validation result")
    feedback: Optional[str] = Field(None, description="Feedback if failed")
    
    @validator('description')
    def description_specific(cls, v):
        if len(v) < 10:
            raise ValueError('Criterion description must be specific (min 10 chars)')
        return v

class Scorecard(BaseModel):
    request_id: str
    criteria: List[ScorecardCriterion] = Field(..., min_items=1)
    overall_passed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    evaluated_at: Optional[datetime] = None
    
    def evaluate(self) -> bool:
        """Evaluate all criteria and update overall_passed"""
        if not all(c.passed is not None for c in self.criteria):
            return False  # Not all criteria evaluated
        self.overall_passed = all(c.passed for c in self.criteria)
        self.evaluated_at = datetime.utcnow()
        return self.overall_passed
    
    def get_failed_criteria(self) -> List[ScorecardCriterion]:
        """Get list of failed criteria for refinement feedback"""
        return [c for c in self.criteria if c.passed is False]
```

---

### 3. ValidationResult

**Purpose**: Output from Quality Agent validation

**Fields**:
- `request_id`: Links to Scorecard
- `passed`: Overall validation result
- `scorecard`: Reference to evaluated scorecard
- `failed_criteria_ids`: List of failed criterion IDs
- `feedback`: Aggregated feedback for refinement
- `validated_at`: Timestamp

**Validation Rules**:
- `passed` must match scorecard.overall_passed
- `failed_criteria_ids` must be empty if passed is true
- `feedback` required if passed is false

**Pydantic Model**:
```python
class ValidationResult(BaseModel):
    request_id: str
    passed: bool
    scorecard_id: str = Field(..., description="Reference to scorecard")
    failed_criteria_ids: List[str] = Field(default_factory=list)
    feedback: Optional[str] = Field(None, description="Aggregated feedback")
    validated_at: datetime = Field(default_factory=datetime.utcnow)
    
    @validator('feedback')
    def feedback_required_if_failed(cls, v, values):
        if not values.get('passed') and not v:
            raise ValueError('Feedback required when validation fails')
        return v
```

---

### 4. RefinementRequest

**Purpose**: Sent from Quality Agent to Planner when validation fails

**Fields**:
- `request_id`: Links to original request
- `original_response`: Response that failed validation
- `failed_criteria`: List of failed criteria with feedback
- `attempt_number`: Refinement attempt count (max 1)
- `created_at`: Timestamp

**Validation Rules**:
- `attempt_number` must be 1 (only one refinement allowed)
- `failed_criteria` must not be empty
- `original_response` must not be empty

**Pydantic Model**:
```python
class RefinementRequest(BaseModel):
    request_id: str
    original_response: str = Field(..., min_length=1)
    failed_criteria: List[ScorecardCriterion] = Field(..., min_items=1)
    attempt_number: int = Field(default=1, ge=1, le=1)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    @validator('attempt_number')
    def max_one_refinement(cls, v):
        if v > 1:
            raise ValueError('Maximum 1 refinement attempt allowed')
        return v
```

---

### 5. FormattedResponse

**Purpose**: Output from Branding Agent with channel-specific formatting

**Fields**:
- `request_id`: Links to original request
- `channel`: Target channel
- `content`: Formatted response content
- `is_split`: Whether message was split into multiple parts
- `parts`: List of message parts if split
- `metadata`: Channel-specific metadata (emojis used, formatting applied, etc.)
- `formatted_at`: Timestamp

**Validation Rules**:
- SMS: `content` max 1600 chars, no markdown
- Email: unlimited length, markdown allowed
- WhatsApp: moderate length, limited markdown
- Teams: structured card format
- If `is_split` is true, `parts` must not be empty

**Pydantic Model**:
```python
class MessagePart(BaseModel):
    sequence: int = Field(..., ge=1)
    content: str
    continuation_indicator: Optional[str] = None  # e.g., "(1/3)"

class FormattedResponse(BaseModel):
    request_id: str
    channel: Channel
    content: str
    is_split: bool = Field(default=False)
    parts: List[MessagePart] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    formatted_at: datetime = Field(default_factory=datetime.utcnow)
    
    @validator('content')
    def validate_channel_limits(cls, v, values):
        channel = values.get('channel')
        if channel == Channel.SMS and len(v) > 1600:
            raise ValueError('SMS content exceeds 1600 character limit')
        return v
    
    @validator('parts')
    def parts_required_if_split(cls, v, values):
        if values.get('is_split') and not v:
            raise ValueError('Parts required when is_split is true')
        return v
```

---

### 6. AgentInteractionLog

**Purpose**: Records all agent invocations for debugging and monitoring

**Fields**:
- `request_id`: Links to original request
- `agent_name`: Which agent was called
- `action`: What action was performed
- `input_data`: Agent input (sanitized, no PII)
- `output_data`: Agent output (sanitized)
- `duration_ms`: Execution time in milliseconds
- `success`: Whether agent call succeeded
- `error`: Error message if failed
- `timestamp`: When agent was called

**Validation Rules**:
- `duration_ms` must be non-negative
- `error` required if `success` is false
- PII must be sanitized from input/output

**Pydantic Model**:
```python
class AgentInteractionLog(BaseModel):
    request_id: str
    agent_name: str = Field(..., description="Agent that was called")
    action: str = Field(..., description="Action performed")
    input_data: Dict[str, Any] = Field(default_factory=dict)
    output_data: Dict[str, Any] = Field(default_factory=dict)
    duration_ms: int = Field(..., ge=0)
    success: bool
    error: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    @validator('error')
    def error_required_if_failed(cls, v, values):
        if not values.get('success') and not v:
            raise ValueError('Error message required when success is false')
        return v
```

---

### 7. ValidationFailureLog

**Purpose**: Detailed record of quality validation failures

**Fields**:
- `request_id`: Links to original request
- `original_question`: User's question
- `scorecard`: The scorecard that was evaluated
- `validation_results`: Results for each criterion
- `refinement_attempted`: Whether refinement was tried
- `refinement_succeeded`: Whether refinement passed revalidation
- `final_outcome`: What was sent to user (improved response or graceful failure)
- `failure_reason`: Root cause analysis
- `logged_at`: Timestamp

**Validation Rules**:
- `refinement_succeeded` can only be true if `refinement_attempted` is true
- `failure_reason` required for debugging

**Pydantic Model**:
```python
class ValidationFailureLog(BaseModel):
    request_id: str
    original_question: str
    scorecard: Scorecard
    validation_results: List[ScorecardCriterion]
    refinement_attempted: bool = Field(default=False)
    refinement_succeeded: Optional[bool] = None
    final_outcome: str = Field(..., description="What was sent to user")
    failure_reason: str = Field(..., description="Root cause analysis")
    logged_at: datetime = Field(default_factory=datetime.utcnow)
    
    @validator('refinement_succeeded')
    def refinement_succeeded_requires_attempted(cls, v, values):
        if v is True and not values.get('refinement_attempted'):
            raise ValueError('refinement_succeeded can only be true if refinement_attempted')
        return v
```

---

## Configuration Models

### 8. ChannelSpecification

**Purpose**: Defines formatting rules for each channel

**Fields**:
- `channel`: Channel identifier
- `max_length`: Maximum message length (None for unlimited)
- `supports_markdown`: Whether markdown is supported
- `markdown_features`: List of supported markdown features
- `supports_emojis`: Whether emojis are supported
- `split_strategy`: How to split long messages

**Pydantic Model**:
```python
class MarkdownFeature(str, Enum):
    BOLD = "bold"
    ITALIC = "italic"
    HEADERS = "headers"
    TABLES = "tables"
    LINKS = "links"
    CODE = "code"

class SplitStrategy(str, Enum):
    SENTENCE = "sentence"
    PARAGRAPH = "paragraph"
    WORD = "word"

class ChannelSpecification(BaseModel):
    channel: Channel
    max_length: Optional[int] = None
    supports_markdown: bool = Field(default=False)
    markdown_features: List[MarkdownFeature] = Field(default_factory=list)
    supports_emojis: bool = Field(default=True)
    split_strategy: SplitStrategy = Field(default=SplitStrategy.SENTENCE)
```

---

### 9. StyleGuide

**Purpose**: Configurable branding and tone rules

**Fields**:
- `version`: Style guide version
- `brand_name`: Brand/product name
- `personality`: Brand personality traits
- `tone`: Tone settings (default, error, success)
- `emojis`: Emoji usage rules
- `humor`: Humor settings
- `formatting`: Formatting preferences

**Pydantic Model**:
```python
class ToneSettings(BaseModel):
    default: str = "conversational"
    error: str = "empathetic"
    success: str = "encouraging"

class EmojiSettings(BaseModel):
    enabled: bool = True
    success: str = "✅"
    warning: str = "⚠️"
    error: str = "❌"
    info: str = "ℹ️"

class HumorSettings(BaseModel):
    enabled: bool = True
    style: str = "light, work-related"
    frequency: str = "occasional"

class FormattingPreferences(BaseModel):
    greeting: bool = True
    sign_off: bool = False
    use_user_name: bool = True

class StyleGuide(BaseModel):
    version: str
    brand_name: str
    personality: str
    tone: ToneSettings
    emojis: EmojiSettings
    humor: HumorSettings
    formatting: FormattingPreferences
```

---

## Workflow State Models

### 10. MultiAgentWorkflowState

**Purpose**: Tracks state of multi-agent workflow execution

**Fields**:
- `request_id`: Unique request identifier
- `execution_plan`: Current execution plan
- `scorecard`: Quality scorecard
- `timesheet_data`: Data from Timesheet Agent (if applicable)
- `composed_response`: Response from Planner
- `formatted_response`: Response from Branding Agent
- `validation_result`: Result from Quality Agent
- `refinement_count`: Number of refinement attempts (0 or 1)
- `final_response`: What was sent to user
- `status`: Workflow status
- `created_at`: When workflow started
- `completed_at`: When workflow finished

**State Transitions**:
```
CREATED → PLANNING → EXTRACTING → COMPOSING → FORMATTING → 
VALIDATING → [REFINING] → SENDING → COMPLETED

Or: CREATED → ... → VALIDATING → FAILED → COMPLETED
```

**Pydantic Model**:
```python
class WorkflowStatus(str, Enum):
    CREATED = "created"
    PLANNING = "planning"
    EXTRACTING = "extracting"
    COMPOSING = "composing"
    FORMATTING = "formatting"
    VALIDATING = "validating"
    REFINING = "refining"
    SENDING = "sending"
    COMPLETED = "completed"
    FAILED = "failed"

class MultiAgentWorkflowState(BaseModel):
    request_id: str
    execution_plan: Optional[ExecutionPlan] = None
    scorecard: Optional[Scorecard] = None
    timesheet_data: Optional[Dict[str, Any]] = None
    composed_response: Optional[str] = None
    formatted_response: Optional[FormattedResponse] = None
    validation_result: Optional[ValidationResult] = None
    refinement_count: int = Field(default=0, ge=0, le=1)
    final_response: Optional[str] = None
    status: WorkflowStatus = Field(default=WorkflowStatus.CREATED)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    
    @validator('refinement_count')
    def max_one_refinement(cls, v):
        if v > 1:
            raise ValueError('Maximum 1 refinement allowed')
        return v
```

---

## Entity Relationships

```
User Message
    ↓
ExecutionPlan (1) ←→ (1) Scorecard
    ↓                       ↓
TimesheetData (0..1)   ValidationResult
    ↓                       ↓
ComposedResponse ←→ RefinementRequest (0..1)
    ↓
FormattedResponse
    ↓
FinalResponse

All entities → AgentInteractionLog (many)
Failed validations → ValidationFailureLog (1)
```

---

## Storage Strategy

### In-Memory (Workflow State)
- `ExecutionPlan`
- `Scorecard`
- `ValidationResult`
- `RefinementRequest`
- `FormattedResponse`
- `MultiAgentWorkflowState`

### Persistent (Supabase - existing tables)
- User messages → `conversation_context` table
- Final responses → `conversation_context` table
- Conversation metadata → `conversations` table

### Logging (Structured logs)
- `AgentInteractionLog` → Application logs (JSON)
- `ValidationFailureLog` → Application logs (JSON)

### Configuration (YAML files)
- `ChannelSpecification` → `agents/config/channels.yaml`
- `StyleGuide` → `agents/config/style_guide.yaml`

---

## Data Flow Example

```python
# 1. User sends message
user_message = "Check my timesheet"
channel = Channel.SMS

# 2. Planner creates execution plan
plan = ExecutionPlan(
    request_id="req-123",
    user_message=user_message,
    channel=channel,
    steps=[
        ExecutionStep(agent="timesheet", action="extract_hours"),
        ExecutionStep(agent="planner", action="compose_response"),
        ExecutionStep(agent="branding", action="format_for_channel"),
        ExecutionStep(agent="quality", action="validate")
    ],
    requires_timesheet_data=True
)

# 3. Planner creates scorecard
scorecard = Scorecard(
    request_id="req-123",
    criteria=[
        ScorecardCriterion(
            id="answers_question",
            description="Response answers user's question about timesheet hours",
            expected="Response includes hours logged information"
        ),
        ScorecardCriterion(
            id="correct_format",
            description="Response is plain text without markdown (SMS channel)",
            expected="No markdown symbols in response"
        )
    ]
)

# 4. Timesheet Agent extracts data
timesheet_data = {"hours_logged": 32, "hours_target": 40}

# 5. Planner composes response
composed_response = "You've logged 32/40 hours this week. Great progress!"

# 6. Branding Agent formats for SMS
formatted = FormattedResponse(
    request_id="req-123",
    channel=Channel.SMS,
    content="You've logged 32/40 hours this week. Great progress!",
    is_split=False,
    metadata={"emojis_used": [], "markdown_removed": False}
)

# 7. Quality Agent validates
validation = ValidationResult(
    request_id="req-123",
    passed=True,
    scorecard_id="scorecard-123",
    failed_criteria_ids=[],
    feedback=None
)

# 8. Send to user
final_response = formatted.content
```

---

## Summary

All data models are defined using Pydantic for:
- ✅ Type safety and validation
- ✅ JSON serialization for logging
- ✅ Clear documentation through field descriptions
- ✅ Runtime validation of business rules
- ✅ IDE support and autocomplete

Models support the complete multi-agent workflow from request to response, with comprehensive logging and debugging capabilities.
