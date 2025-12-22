# Quickstart Guide: Multi-Agent Conversation System

**Feature**: 001-multi-agent-architecture  
**Date**: November 24, 2025  
**Audience**: Developers implementing the multi-agent system

## Overview

This guide provides a step-by-step walkthrough for implementing the multi-agent conversation system. Follow these steps to build, test, and deploy the feature.

---

## Prerequisites

- Python 3.13 installed
- Existing codebase cloned (`unified_server.py`, `unified_workflows.py`, `llm/` module)
- Access to Azure Key Vault (for secrets)
- Temporal server running (existing infrastructure)
- Supabase database access (existing)
- pytest installed for testing

---

## Phase 1: Setup Project Structure

### Step 1: Create Agent Module

```bash
# From repository root
mkdir -p agents/config
touch agents/__init__.py
touch agents/base.py
touch agents/planner.py
touch agents/timesheet.py
touch agents/branding.py
touch agents/quality.py
touch agents/models.py
```

### Step 2: Create Test Structure

```bash
mkdir -p tests/unit tests/integration tests/fixtures
touch tests/__init__.py
touch tests/unit/test_planner.py
touch tests/unit/test_timesheet.py
touch tests/unit/test_branding.py
touch tests/unit/test_quality.py
touch tests/integration/test_agent_coordination.py
touch tests/integration/test_quality_validation.py
touch tests/integration/test_channel_formatting.py
touch tests/fixtures/sample_requests.py
touch tests/fixtures/sample_scorecards.py
touch tests/fixtures/mock_harvest_data.py
```

### Step 3: Create Configuration Files

```bash
# Create channel specifications
cat > agents/config/channels.yaml << 'EOF'
sms:
  max_length: 1600
  supports_markdown: false
  markdown_features: []
  supports_emojis: true
  split_strategy: sentence

email:
  max_length: null
  supports_markdown: true
  markdown_features: [bold, italic, headers, tables, links, code]
  supports_emojis: true
  split_strategy: paragraph

whatsapp:
  max_length: 4000
  supports_markdown: true
  markdown_features: [bold, italic]
  supports_emojis: true
  split_strategy: paragraph

teams:
  max_length: null
  supports_markdown: true
  markdown_features: [bold, italic, headers, links]
  supports_emojis: true
  split_strategy: paragraph
EOF

# Create style guide
cat > agents/config/style_guide.yaml << 'EOF'
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
EOF
```

---

## Phase 2: Implement Data Models

### Step 1: Create Pydantic Models

Edit `agents/models.py`:

```python
from pydantic import BaseModel, Field, validator
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum

# Copy all models from data-model.md:
# - ExecutionPlan
# - Scorecard, ScorecardCriterion
# - ValidationResult
# - RefinementRequest
# - FormattedResponse
# - AgentInteractionLog
# - ValidationFailureLog
# - ChannelSpecification
# - StyleGuide
# - MultiAgentWorkflowState

# See specs/001-multi-agent-architecture/data-model.md for complete definitions
```

### Step 2: Test Data Models

Create `tests/unit/test_models.py`:

```python
import pytest
from agents.models import Scorecard, ScorecardCriterion, ExecutionPlan

def test_scorecard_evaluation():
    """Test scorecard evaluates all criteria correctly"""
    scorecard = Scorecard(
        request_id="test-123",
        criteria=[
            ScorecardCriterion(
                id="c1",
                description="Response answers question",
                expected="Contains timesheet data",
                passed=True
            ),
            ScorecardCriterion(
                id="c2",
                description="Response is formatted correctly",
                expected="Plain text for SMS",
                passed=False,
                feedback="Contains markdown"
            )
        ]
    )
    
    assert not scorecard.evaluate()  # Should fail because c2 failed
    assert len(scorecard.get_failed_criteria()) == 1

# Run: pytest tests/unit/test_models.py
```

---

## Phase 3: Implement Base Agent Interface

### Step 1: Create Base Agent Class

Edit `agents/base.py`:

```python
from abc import ABC, abstractmethod
from typing import Dict, Any
import logging
from llm.client import LLMClient

logger = logging.getLogger(__name__)

class BaseAgent(ABC):
    """Base class for all agents"""
    
    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client
        self.logger = logger
    
    @abstractmethod
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute agent action"""
        pass
    
    def log_interaction(self, request_id: str, action: str, 
                       input_data: Dict, output_data: Dict,
                       duration_ms: int, success: bool, error: str = None):
        """Log agent interaction for debugging"""
        from agents.models import AgentInteractionLog
        
        log = AgentInteractionLog(
            request_id=request_id,
            agent_name=self.__class__.__name__,
            action=action,
            input_data=input_data,
            output_data=output_data,
            duration_ms=duration_ms,
            success=success,
            error=error
        )
        
        self.logger.info(f"Agent interaction: {log.json()}")
```

---

## Phase 4: Implement Individual Agents

### Step 1: Implement Planner Agent

Edit `agents/planner.py`:

```python
from agents.base import BaseAgent
from agents.models import ExecutionPlan, Scorecard, ScorecardCriterion
from typing import Dict, Any
import time

class PlannerAgent(BaseAgent):
    """Coordinator agent - analyzes requests, creates plans, composes responses"""
    
    async def analyze_request(self, request_id: str, user_message: str,
                              channel: str, conversation_history: list,
                              user_context: dict) -> Dict[str, Any]:
        """Analyze user request and create execution plan + scorecard"""
        start_time = time.time()
        
        try:
            # Use LLM to analyze request and determine plan
            prompt = f"""Analyze this user request and create an execution plan.
            
User message: {user_message}
Channel: {channel}
Conversation history: {conversation_history}

Determine:
1. Does this require timesheet data? (yes/no)
2. What steps are needed?
3. What validation criteria should be used?

Return JSON with execution_plan and scorecard."""

            # Call LLM (using existing centralized client)
            response = await self.llm_client.generate(prompt)
            
            # Parse response and create models
            # (Implementation details...)
            
            duration_ms = int((time.time() - start_time) * 1000)
            self.log_interaction(request_id, "analyze_request", 
                               {"user_message": user_message}, 
                               {"plan": "created"}, duration_ms, True)
            
            return {
                "execution_plan": execution_plan.dict(),
                "scorecard": scorecard.dict()
            }
            
        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            self.log_interaction(request_id, "analyze_request",
                               {"user_message": user_message},
                               {}, duration_ms, False, str(e))
            raise
    
    async def compose_response(self, request_id: str, user_message: str,
                              timesheet_data: dict, conversation_history: list,
                              user_context: dict) -> Dict[str, Any]:
        """Compose response based on data and context"""
        # Implementation using LLM...
        pass
    
    async def refine_response(self, request_id: str, original_response: str,
                             failed_criteria: list, attempt_number: int) -> Dict[str, Any]:
        """Refine response based on quality feedback"""
        # Implementation using LLM...
        pass
    
    async def compose_graceful_failure(self, request_id: str, user_message: str,
                                      failure_reason: str, channel: str) -> Dict[str, Any]:
        """Compose user-friendly failure message"""
        # Implementation...
        pass

# See specs/001-multi-agent-architecture/contracts/agent-contracts.md for full contracts
```

### Step 2: Implement Timesheet Agent

Edit `agents/timesheet.py`:

```python
from agents.base import BaseAgent
from typing import Dict, Any

class TimesheetAgent(BaseAgent):
    """Data specialist - extracts timesheet data using existing Harvest tools"""
    
    def __init__(self, llm_client, harvest_tools):
        super().__init__(llm_client)
        self.harvest_tools = harvest_tools  # Existing 51 tools
    
    async def extract_timesheet_data(self, request_id: str, user_id: str,
                                    query_type: str, parameters: dict,
                                    user_credentials: dict, user_timezone: str) -> Dict[str, Any]:
        """Extract timesheet data using Harvest API tools"""
        
        # Use existing tools from unified_workflows.py
        # (Reuse without modification per FR-013)
        
        try:
            if query_type == "hours_logged":
                # Call existing check_my_timesheet tool
                result = await self.harvest_tools.check_my_timesheet(
                    date_range=parameters.get("date_range"),
                    user_credentials=user_credentials,
                    timezone=user_timezone
                )
                
                return {
                    "data": result,
                    "metadata": {"tools_used": ["check_my_timesheet"]},
                    "success": True,
                    "error": None
                }
            
            # Handle other query types...
            
        except Exception as e:
            return {
                "data": {},
                "metadata": {},
                "success": False,
                "error": str(e)
            }
```

### Step 3: Implement Branding Agent

Edit `agents/branding.py`:

```python
from agents.base import BaseAgent
from agents.models import FormattedResponse, Channel
from typing import Dict, Any
import yaml
from pathlib import Path

class BrandingAgent(BaseAgent):
    """Formatter - applies channel-specific formatting and style guide"""
    
    def __init__(self, llm_client):
        super().__init__(llm_client)
        
        # Load configuration files
        config_dir = Path(__file__).parent / "config"
        
        with open(config_dir / "style_guide.yaml") as f:
            self.style_guide = yaml.safe_load(f)
        
        with open(config_dir / "channels.yaml") as f:
            self.channel_specs = yaml.safe_load(f)
    
    async def format_for_channel(self, request_id: str, response: str,
                                channel: str, user_context: dict) -> Dict[str, Any]:
        """Format response for specific channel"""
        
        channel_spec = self.channel_specs[channel]
        
        # Apply channel-specific formatting
        if channel == "sms":
            formatted = self._format_sms(response, channel_spec)
        elif channel == "email":
            formatted = self._format_email(response, channel_spec)
        elif channel == "whatsapp":
            formatted = self._format_whatsapp(response, channel_spec)
        elif channel == "teams":
            formatted = self._format_teams(response, channel_spec)
        
        return {"formatted_response": formatted.dict()}
    
    def _format_sms(self, response: str, spec: dict) -> FormattedResponse:
        """Format for SMS: plain text, max 1600 chars"""
        # Remove markdown
        plain_text = self._strip_markdown(response)
        
        # Apply style guide
        styled = self._apply_style(plain_text, "sms")
        
        # Split if needed
        if len(styled) > spec["max_length"]:
            parts = self._split_message(styled, spec["max_length"], spec["split_strategy"])
            return FormattedResponse(
                request_id=request_id,
                channel=Channel.SMS,
                content=parts[0].content,
                is_split=True,
                parts=parts
            )
        
        return FormattedResponse(
            request_id=request_id,
            channel=Channel.SMS,
            content=styled,
            is_split=False
        )
    
    # Implement _format_email, _format_whatsapp, _format_teams...
```

### Step 4: Implement Quality Agent

Edit `agents/quality.py`:

```python
from agents.base import BaseAgent
from agents.models import ValidationResult, Scorecard
from typing import Dict, Any

class QualityAgent(BaseAgent):
    """Validator - validates responses against scorecard criteria"""
    
    async def validate_response(self, request_id: str, response: str,
                               scorecard: dict, channel: str,
                               original_question: str) -> Dict[str, Any]:
        """Validate response against scorecard criteria"""
        
        scorecard_obj = Scorecard(**scorecard)
        
        # Evaluate each criterion using LLM
        for criterion in scorecard_obj.criteria:
            prompt = f"""Evaluate if this response meets the criterion.

Response: {response}
Criterion: {criterion.description}
Expected: {criterion.expected}

Does the response meet this criterion? (yes/no)
If no, provide specific feedback."""

            result = await self.llm_client.generate(prompt)
            
            # Parse result and update criterion
            criterion.passed = self._parse_validation_result(result)
            if not criterion.passed:
                criterion.feedback = self._extract_feedback(result)
        
        # Evaluate overall
        overall_passed = scorecard_obj.evaluate()
        
        # Create validation result
        validation_result = ValidationResult(
            request_id=request_id,
            passed=overall_passed,
            scorecard_id=scorecard_obj.request_id,
            failed_criteria_ids=[c.id for c in scorecard_obj.get_failed_criteria()],
            feedback=self._aggregate_feedback(scorecard_obj.get_failed_criteria())
        )
        
        return {"validation_result": validation_result.dict()}
    
    async def validate_graceful_failure(self, request_id: str,
                                       failure_message: str,
                                       failure_reason: str) -> Dict[str, Any]:
        """Validate and approve graceful failure message"""
        # Always approve, but log for debugging
        self.logger.info(f"Graceful failure approved: {request_id} - {failure_reason}")
        return {"approved": True, "logged": True}
```

---

## Phase 5: Integrate with Temporal Workflows

### Step 1: Create Multi-Agent Workflow

Edit `unified_workflows.py` (add new workflow):

```python
from temporalio import workflow
from datetime import timedelta
from agents.planner import PlannerAgent
from agents.timesheet import TimesheetAgent
from agents.branding import BrandingAgent
from agents.quality import QualityAgent

@workflow.defn
class MultiAgentConversationWorkflow:
    """Multi-agent conversation workflow with quality validation"""
    
    @workflow.run
    async def run(self, user_message: str, channel: str, user_id: str,
                  conversation_id: str) -> dict:
        """Execute multi-agent workflow"""
        
        request_id = workflow.uuid4()
        
        # Step 1: Planner analyzes request
        plan_result = await workflow.execute_activity(
            planner_analyze_activity,
            args=[request_id, user_message, channel, ...],
            start_to_close_timeout=timedelta(seconds=5)
        )
        
        execution_plan = plan_result["execution_plan"]
        scorecard = plan_result["scorecard"]
        
        # Step 2: Timesheet extracts data (if needed)
        timesheet_data = None
        if execution_plan["requires_timesheet_data"]:
            timesheet_data = await workflow.execute_activity(
                timesheet_extract_activity,
                args=[request_id, user_id, ...],
                start_to_close_timeout=timedelta(seconds=5)
            )
        
        # Step 3: Planner composes response
        response_result = await workflow.execute_activity(
            planner_compose_activity,
            args=[request_id, user_message, timesheet_data, ...],
            start_to_close_timeout=timedelta(seconds=5)
        )
        
        response = response_result["response"]
        
        # Step 4: Branding formats for channel
        formatted_result = await workflow.execute_activity(
            branding_format_activity,
            args=[request_id, response, channel, ...],
            start_to_close_timeout=timedelta(seconds=2)
        )
        
        formatted_response = formatted_result["formatted_response"]
        
        # Step 5: Quality validates
        validation_result = await workflow.execute_activity(
            quality_validate_activity,
            args=[request_id, formatted_response["content"], scorecard, channel, user_message],
            start_to_close_timeout=timedelta(seconds=2)
        )
        
        # Step 6: Refinement if needed (max 1 attempt)
        refinement_count = 0
        if not validation_result["validation_result"]["passed"] and refinement_count < 1:
            # Refine response
            refined_result = await workflow.execute_activity(
                planner_refine_activity,
                args=[request_id, response, validation_result["validation_result"]["failed_criteria"], 1],
                start_to_close_timeout=timedelta(seconds=5)
            )
            
            # Reformat
            reformatted_result = await workflow.execute_activity(
                branding_format_activity,
                args=[request_id, refined_result["refined_response"], channel, ...],
                start_to_close_timeout=timedelta(seconds=2)
            )
            
            # Revalidate
            revalidation_result = await workflow.execute_activity(
                quality_validate_activity,
                args=[request_id, reformatted_result["formatted_response"]["content"], scorecard, channel, user_message],
                start_to_close_timeout=timedelta(seconds=2)
            )
            
            refinement_count += 1
            validation_result = revalidation_result
            formatted_response = reformatted_result["formatted_response"]
        
        # Step 7: Graceful failure if still not passed
        final_response = formatted_response["content"]
        graceful_failure = False
        
        if not validation_result["validation_result"]["passed"]:
            failure_result = await workflow.execute_activity(
                planner_graceful_failure_activity,
                args=[request_id, user_message, "validation_failed", channel],
                start_to_close_timeout=timedelta(seconds=1)
            )
            
            final_response = failure_result["failure_message"]
            graceful_failure = True
        
        # Step 8: Return result
        return {
            "request_id": request_id,
            "final_response": final_response,
            "validation_passed": validation_result["validation_result"]["passed"],
            "refinement_attempted": refinement_count > 0,
            "graceful_failure": graceful_failure
        }

# Define activities (one per agent method)
@activity.defn
async def planner_analyze_activity(request_id, user_message, channel, ...):
    llm_client = get_llm_client()  # Use existing centralized client
    planner = PlannerAgent(llm_client)
    return await planner.analyze_request(request_id, user_message, channel, ...)

# Define other activities...
```

---

## Phase 6: Testing

### Step 1: Unit Tests

```bash
# Test each agent independently
pytest tests/unit/test_planner.py -v
pytest tests/unit/test_timesheet.py -v
pytest tests/unit/test_branding.py -v
pytest tests/unit/test_quality.py -v
```

### Step 2: Integration Tests

```bash
# Test multi-agent workflow
pytest tests/integration/test_agent_coordination.py -v
pytest tests/integration/test_quality_validation.py -v
pytest tests/integration/test_channel_formatting.py -v
```

### Step 3: End-to-End Test

```python
# tests/integration/test_e2e.py
@pytest.mark.asyncio
async def test_complete_multi_agent_workflow():
    """Test complete workflow from user message to final response"""
    async with await WorkflowEnvironment.start_time_skipping() as env:
        # Setup worker with all activities
        worker = Worker(
            env.client,
            task_queue="test",
            workflows=[MultiAgentConversationWorkflow],
            activities=[
                planner_analyze_activity,
                timesheet_extract_activity,
                planner_compose_activity,
                branding_format_activity,
                quality_validate_activity,
                planner_refine_activity,
                planner_graceful_failure_activity
            ]
        )
        
        async with worker:
            result = await env.client.execute_workflow(
                MultiAgentConversationWorkflow.run,
                args=["Check my timesheet", "sms", "user-123", "conv-456"],
                id="test-workflow",
                task_queue="test"
            )
            
            assert result["validation_passed"]
            assert not result["graceful_failure"]
            assert len(result["final_response"]) < 1600  # SMS limit
```

---

## Phase 7: Deployment

### Step 1: Update Server

Edit `unified_server.py` (minimal changes):

```python
# Register new workflow with worker
worker = Worker(
    temporal_client,
    task_queue=TASK_QUEUE,
    workflows=[
        TimesheetReminderWorkflow,
        DailyReminderScheduleWorkflow,
        ConversationWorkflow,  # Existing
        MultiAgentConversationWorkflow,  # NEW
        CrossPlatformRoutingWorkflow
    ],
    activities=[
        # Existing activities...
        # New agent activities
        planner_analyze_activity,
        timesheet_extract_activity,
        planner_compose_activity,
        branding_format_activity,
        quality_validate_activity,
        planner_refine_activity,
        planner_graceful_failure_activity
    ]
)
```

### Step 2: Feature Flag

Add feature flag to enable/disable multi-agent system:

```python
# Environment variable
USE_MULTI_AGENT = os.getenv("USE_MULTI_AGENT", "false").lower() == "true"

# In webhook handler
if USE_MULTI_AGENT:
    workflow_id = await temporal_client.start_workflow(
        MultiAgentConversationWorkflow.run,
        args=[message, channel, user_id, conversation_id],
        id=f"multi-agent-{conversation_id}",
        task_queue=TASK_QUEUE
    )
else:
    # Use existing ConversationWorkflow
    workflow_id = await temporal_client.start_workflow(
        ConversationWorkflow.run,
        ...
    )
```

### Step 3: Deploy

```bash
# Build Docker image
docker build -t unified-temporal-worker:v2.0.0-multi-agent .

# Push to Azure Container Registry
docker push secureagentreg2ai.azurecr.io/unified-temporal-worker:v2.0.0-multi-agent

# Update Azure Container App
az containerapp update \
  --name unified-temporal-worker \
  --resource-group <resource-group> \
  --image secureagentreg2ai.azurecr.io/unified-temporal-worker:v2.0.0-multi-agent \
  --set-env-vars USE_MULTI_AGENT=true
```

---

## Phase 8: Monitoring

### Step 1: Monitor Metrics

```python
# Track key metrics
- Request latency (P50, P95, P99)
- Validation pass rate
- Refinement success rate
- Graceful failure rate
- Agent call durations
- LLM call counts
```

### Step 2: Review Logs

```bash
# Check agent interaction logs
grep "Agent interaction" /var/log/app.log | jq

# Check validation failures
grep "ValidationFailureLog" /var/log/app.log | jq

# Check graceful failures
grep "Graceful failure" /var/log/app.log | jq
```

---

## Troubleshooting

### Issue: Validation always fails
- Check scorecard criteria are measurable and specific
- Review Quality Agent LLM prompts
- Verify response format matches channel spec

### Issue: Response timeout (>10s)
- Check individual agent durations in logs
- Optimize LLM prompts for faster responses
- Consider caching for common queries

### Issue: Refinement not improving quality
- Review failed criteria feedback specificity
- Check Planner refinement prompts
- Analyze refinement success rate

---

## Next Steps

1. ✅ Implementation complete
2. → Run `/speckit.tasks` to generate detailed task breakdown
3. → Begin implementation following task order
4. → Run tests continuously during development
5. → Deploy with feature flag for gradual rollout
6. → Monitor metrics and iterate

---

## Resources

- **Specification**: [spec.md](./spec.md)
- **Data Models**: [data-model.md](./data-model.md)
- **Agent Contracts**: [contracts/agent-contracts.md](./contracts/agent-contracts.md)
- **Research**: [research.md](./research.md)
- **Existing System**: [SYSTEM_ANALYSIS.md](../../SYSTEM_ANALYSIS.md)
