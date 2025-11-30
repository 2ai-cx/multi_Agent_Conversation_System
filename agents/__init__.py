"""
Multi-Agent Conversation System

This module implements a 4-agent architecture for quality-controlled,
channel-specific conversation responses:

- PlannerAgent: Coordinates workflow, creates execution plans and scorecards
- TimesheetAgent: Extracts data using existing Harvest API tools
- BrandingAgent: Formats responses for specific channels (SMS, Email, WhatsApp, Teams)
- QualityAgent: Validates responses against scorecards, triggers refinement

All agents use the centralized LLM client and integrate with Temporal workflows.
"""

from agents.base import BaseAgent
from agents.models import (
    ExecutionPlan,
    ExecutionStep,
    Channel,
    Scorecard,
    ScorecardCriterion,
    ValidationResult,
    RefinementRequest,
    FormattedResponse,
    MessagePart,
    AgentInteractionLog,
    ValidationFailureLog,
    ChannelSpecification,
    StyleGuide,
    MultiAgentWorkflowState,
    WorkflowStatus,
)

__all__ = [
    "BaseAgent",
    "ExecutionPlan",
    "ExecutionStep",
    "Channel",
    "Scorecard",
    "ScorecardCriterion",
    "ValidationResult",
    "RefinementRequest",
    "FormattedResponse",
    "MessagePart",
    "AgentInteractionLog",
    "ValidationFailureLog",
    "ChannelSpecification",
    "StyleGuide",
    "MultiAgentWorkflowState",
    "WorkflowStatus",
]
