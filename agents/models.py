"""
Pydantic Data Models for Multi-Agent Conversation System

All models use Pydantic for validation and type safety, with JSON serialization
for logging and persistence.
"""

from pydantic import BaseModel, Field, validator
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum


# ============================================================================
# Core Enums
# ============================================================================

class Channel(str, Enum):
    """Communication channels supported by the system"""
    SMS = "sms"
    EMAIL = "email"
    WHATSAPP = "whatsapp"
    TEAMS = "teams"


class WorkflowStatus(str, Enum):
    """Multi-agent workflow execution status"""
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


class MarkdownFeature(str, Enum):
    """Markdown features supported by channels"""
    BOLD = "bold"
    ITALIC = "italic"
    HEADERS = "headers"
    TABLES = "tables"
    LINKS = "links"
    CODE = "code"


class SplitStrategy(str, Enum):
    """Message splitting strategies for long content"""
    SENTENCE = "sentence"
    PARAGRAPH = "paragraph"
    WORD = "word"


# ============================================================================
# Execution Planning Models
# ============================================================================

class ExecutionStep(BaseModel):
    """Single step in execution plan"""
    agent: str = Field(..., description="Agent to invoke")
    action: str = Field(..., description="Action to perform")
    parameters: Dict[str, Any] = Field(default_factory=dict)


class ExecutionPlan(BaseModel):
    """Created by Planner Agent to specify workflow execution steps"""
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


# ============================================================================
# Quality Validation Models
# ============================================================================

class ScorecardCriterion(BaseModel):
    """Single validation criterion with pass/fail result"""
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
    """Quality validation scorecard for a response"""
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


class ValidationResult(BaseModel):
    """Output from Quality Agent validation"""
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


class RefinementRequest(BaseModel):
    """Sent from Quality Agent to Planner when validation fails"""
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


# ============================================================================
# Response Formatting Models
# ============================================================================

class MessagePart(BaseModel):
    """Single part of a split message"""
    sequence: int = Field(..., ge=1)
    content: str
    continuation_indicator: Optional[str] = None  # e.g., "(1/3)"


class FormattedResponse(BaseModel):
    """Output from Branding Agent with channel-specific formatting"""
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


# ============================================================================
# Logging Models
# ============================================================================

class AgentInteractionLog(BaseModel):
    """Records all agent invocations for debugging and monitoring"""
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


class ValidationFailureLog(BaseModel):
    """Detailed record of quality validation failures"""
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


# ============================================================================
# Configuration Models
# ============================================================================

class ChannelSpecification(BaseModel):
    """Defines formatting rules for each channel"""
    channel: Channel
    max_length: Optional[int] = None
    supports_markdown: bool = Field(default=False)
    markdown_features: List[MarkdownFeature] = Field(default_factory=list)
    supports_emojis: bool = Field(default=True)
    split_strategy: SplitStrategy = Field(default=SplitStrategy.SENTENCE)


class ToneSettings(BaseModel):
    """Tone configuration for different contexts"""
    default: str = "conversational"
    error: str = "empathetic"
    success: str = "encouraging"


class EmojiSettings(BaseModel):
    """Emoji usage configuration"""
    enabled: bool = True
    success: str = "✅"
    warning: str = "⚠️"
    error: str = "❌"
    info: str = "ℹ️"


class HumorSettings(BaseModel):
    """Humor configuration"""
    enabled: bool = True
    style: str = "light, work-related"
    frequency: str = "occasional"


class FormattingPreferences(BaseModel):
    """Formatting preferences"""
    greeting: bool = True
    sign_off: bool = False
    use_user_name: bool = True


class StyleGuide(BaseModel):
    """Configurable branding and tone rules"""
    version: str
    brand_name: str
    personality: str
    tone: ToneSettings
    emojis: EmojiSettings
    humor: HumorSettings
    formatting: FormattingPreferences


# ============================================================================
# Workflow State Models
# ============================================================================

class MultiAgentWorkflowState(BaseModel):
    """Tracks state of multi-agent workflow execution"""
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
