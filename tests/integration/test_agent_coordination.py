"""Integration tests for multi-agent coordination"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from agents.planner import PlannerAgent
from agents.timesheet import TimesheetAgent
from agents.branding import BrandingAgent
from agents.quality import QualityAgent
from agents.models import Channel, ExecutionPlan, Scorecard, ValidationResult
from tests.fixtures.sample_requests import SAMPLE_SMS_REQUEST, SAMPLE_USER_CONTEXT
from tests.fixtures.mock_harvest_data import MOCK_HOURS_LOGGED, MOCK_USER_CREDENTIALS


class TestMultiAgentWorkflow:
    """Test complete multi-agent workflow end-to-end"""
    
    @pytest.fixture
    def mock_llm_client(self):
        """Mock LLM client for all agents"""
        client = Mock()
        client.generate = AsyncMock()
        return client
    
    @pytest.fixture
    def mock_harvest_tools(self):
        """Mock Harvest API tools"""
        tools = Mock()
        tools.check_my_timesheet = AsyncMock(return_value=MOCK_HOURS_LOGGED)
        return tools
    
    @pytest.fixture
    def all_agents(self, mock_llm_client, mock_harvest_tools):
        """Create all agents"""
        return {
            "planner": PlannerAgent(mock_llm_client),
            "timesheet": TimesheetAgent(mock_llm_client, mock_harvest_tools),
            "branding": BrandingAgent(mock_llm_client),
            "quality": QualityAgent(mock_llm_client)
        }
    
    @pytest.mark.asyncio
    async def test_complete_workflow_success(self, all_agents, mock_llm_client):
        """Test complete workflow: analyze → extract → compose → format → validate → send"""
        # Arrange
        request_id = "integration-test-001"
        user_message = "Check my timesheet"
        channel = Channel.SMS
        
        # Mock LLM responses for each step
        async def mock_llm_generate(prompt):
            print(f"[DEBUG] Mock received prompt (first 200 chars): {prompt[:200]}")
            
            # Match planner analyze_request - look for the specific prompt signature
            if "Return ONLY valid JSON, no other text." in prompt and "needs_data" in prompt:
                print("[DEBUG] Matched planner analyze_request")
                return '{"needs_data": true, "message_to_timesheet": "Extract user timesheet data for this week", "criteria": [{"id": "answers_question", "description": "Response answers user question appropriately", "expected": "Contains timesheet hours"}]}'
            elif "compose" in prompt.lower() and ("timesheet data" in prompt.lower() or "user question" in prompt.lower()):
                print("[DEBUG] Matched planner compose_response")
                return "You've logged 32/40 hours this week. Great progress!"
            elif "format" in prompt.lower() and "channel" in prompt.lower() and "sms" in prompt.lower():
                print("[DEBUG] Matched branding format_for_channel") 
                return '{"formatted_content": "You have logged 32/40 hours this week. Great progress!", "is_split": false, "parts": [], "reasoning": "SMS format applied", "metadata": {"original_length": 50, "final_length": 50}}'
            elif "evaluate" in prompt.lower() and "criterion" in prompt.lower():
                print("[DEBUG] Matched quality validation")
                return "yes"
            else:
                print(f"[DEBUG] No match found for prompt: {prompt[:100]}...")
                return "default response"
        
        mock_llm_client.generate.side_effect = mock_llm_generate
        
        # Act - Step 1: Planner analyzes request
        plan_result = await all_agents["planner"].analyze_request(
            request_id, user_message, channel, [], SAMPLE_USER_CONTEXT
        )
        
        # Assert Step 1
        assert "execution_plan" in plan_result
        assert "scorecard" in plan_result
        plan = plan_result["execution_plan"]
        assert plan["needs_data"] is True
        
        # Act - Step 2: Timesheet extracts data
        timesheet_result = await all_agents["timesheet"].extract_timesheet_data(
            request_id,
            SAMPLE_USER_CONTEXT["user_id"],
            "hours_logged",
            {"date_range": "this_week"},
            MOCK_USER_CREDENTIALS,
            SAMPLE_USER_CONTEXT["timezone"]
        )
        
        # Assert Step 2
        assert timesheet_result["success"] is True
        assert timesheet_result["data"]["hours_logged"] == 32.0
        
        # Act - Step 3: Planner composes response
        compose_result = await all_agents["planner"].compose_response(
            request_id,
            user_message,
            timesheet_result["data"],
            [],
            SAMPLE_USER_CONTEXT
        )
        
        # Assert Step 3
        assert "response" in compose_result
        assert "32" in compose_result["response"]
        
        # Act - Step 4: Branding formats for SMS
        branding_result = await all_agents["branding"].format_for_channel(
            request_id,
            compose_result["response"],
            channel,
            SAMPLE_USER_CONTEXT
        )
        
        # Assert Step 4
        formatted = branding_result["formatted_response"]
        assert formatted["channel"] == Channel.SMS
        assert len(formatted["content"]) <= 1600
        assert "**" not in formatted["content"]  # No markdown
        
        # Act - Step 5: Quality validates
        validation_result = await all_agents["quality"].validate_response(
            request_id,
            formatted["content"],
            plan_result["scorecard"],
            channel,
            user_message
        )
        
        # Assert Step 5
        validation = ValidationResult(**validation_result["validation_result"])
        assert validation.passed is True
        assert len(validation.failed_criteria_ids) == 0
    
    @pytest.mark.asyncio
    async def test_workflow_with_refinement(self, all_agents, mock_llm_client):
        """Test workflow with quality validation failure and refinement"""
        # Arrange
        request_id = "integration-test-002"
        
        # Mock LLM to fail validation first time, pass second time
        validation_call_count = 0
        
        async def mock_llm_generate(prompt):
            nonlocal validation_call_count
            print(f"\n[DEBUG] ================================")
            print(f"[DEBUG] Mock call #{mock_llm_client.generate.call_count + 1}")
            print(f"[DEBUG] Prompt first 300 chars:\n{prompt[:300]}")
            print(f"[DEBUG] ================================\n")
            
            # PRIORITY 1: Match quality validation first (to avoid conflicts with other conditions)
            if "Evaluate if this response meets the criterion" in prompt and "Answer with \"yes\" if it passes" in prompt:
                validation_call_count += 1
                print(f"[DEBUG] ✅ Matched quality validation (call #{validation_call_count})")
                # Extract the actual response from the prompt
                response_start = prompt.find('Response: "') + len('Response: "')
                response_end = prompt.find('"\nChannel:', response_start)
                actual_response = prompt[response_start:response_end]
                print(f"[DEBUG] Extracted response: '{actual_response}'")
                
                if "**" in actual_response:
                    print("[DEBUG] Response contains markdown - FAIL")
                    return "no - contains markdown symbols"
                else:
                    print("[DEBUG] Response has no markdown - PASS")
                    return "yes"
            # Match planner analyze_request 
            elif "Return ONLY valid JSON, no other text." in prompt and "needs_data" in prompt:
                print("[DEBUG] ✅ Matched planner analyze_request")
                return '{"needs_data": true, "message_to_timesheet": "Extract user timesheet data", "criteria": [{"id": "no_markdown", "description": "No markdown formatting for SMS", "expected": "Plain text only"}]}'
            elif "compose" in prompt.lower() and "timesheet data" in prompt.lower() and "refine" not in prompt.lower():
                print("[DEBUG] ✅ Matched planner compose_response")
                return "You've logged **32 hours** this week."
            elif "refine" in prompt.lower() and "feedback" in prompt.lower():
                print("[DEBUG] ✅ Matched planner refine_response")
                return "You've logged 32 hours this week."
            elif "You are a Branding Specialist" in prompt and "channel" in prompt.lower():
                print("[DEBUG] ✅ Matched branding format_for_channel")
                # Determine response content based on input
                if "**32 hours**" in prompt:
                    print("[DEBUG] Branding input has markdown")
                    return '{"formatted_content": "You have logged **32 hours** this week.", "is_split": false, "parts": [], "reasoning": "SMS format with markdown", "metadata": {"original_length": 40, "final_length": 40}}'
                else:
                    print("[DEBUG] Branding input has no markdown")
                    return '{"formatted_content": "You have logged 32 hours this week.", "is_split": false, "parts": [], "reasoning": "SMS format no markdown", "metadata": {"original_length": 35, "final_length": 35}}'
            else:
                print(f"[DEBUG] ❌ No match found!")
                print(f"[DEBUG] Prompt keywords: {[word for word in ['analyze', 'compose', 'refine', 'format', 'evaluate'] if word in prompt.lower()]}")
                return "default"
        
        mock_llm_client.generate.side_effect = mock_llm_generate
        
        # Act - Complete workflow
        plan_result = await all_agents["planner"].analyze_request(
            request_id, "Check my timesheet", Channel.SMS, [], SAMPLE_USER_CONTEXT
        )
        
        compose_result = await all_agents["planner"].compose_response(
            request_id, "Check my timesheet", MOCK_HOURS_LOGGED, [], SAMPLE_USER_CONTEXT
        )
        
        branding_result = await all_agents["branding"].format_for_channel(
            request_id, compose_result["response"], Channel.SMS, SAMPLE_USER_CONTEXT
        )
        
        # First validation - should fail
        validation1 = await all_agents["quality"].validate_response(
            request_id,
            branding_result["formatted_response"]["content"],
            plan_result["scorecard"],
            Channel.SMS,
            "Check my timesheet"
        )
        
        # Assert first validation fails
        assert validation1["validation_result"]["passed"] is False
        
        # Act - Refinement
        refine_result = await all_agents["planner"].refine_response(
            request_id,
            compose_result["response"],
            validation1["failed_criteria"],
            1
        )
        
        # Reformat
        rebranding_result = await all_agents["branding"].format_for_channel(
            request_id, refine_result["refined_response"], Channel.SMS, SAMPLE_USER_CONTEXT
        )
        
        # Revalidate
        validation2 = await all_agents["quality"].validate_response(
            request_id,
            rebranding_result["formatted_response"]["content"],
            plan_result["scorecard"],
            Channel.SMS,
            "Check my timesheet"
        )
        
        # Assert second validation passes
        assert validation2["validation_result"]["passed"] is True
        assert "**" not in rebranding_result["formatted_response"]["content"]
    
    @pytest.mark.asyncio
    async def test_workflow_with_graceful_failure(self, all_agents, mock_llm_client):
        """Test workflow that results in graceful failure"""
        # Arrange
        request_id = "integration-test-003"
        
        # Mock LLM to always fail validation
        async def mock_llm_generate(prompt):
            print(f"[DEBUG] Graceful failure mock: {prompt[:200]}")
            
            # Quality validation first
            if "Evaluate if this response meets the criterion" in prompt and "Answer with \"yes\" if it passes" in prompt:
                print("[DEBUG] ✅ Matched quality validation - always fail")
                return "no - criterion cannot be met"
            elif "Return ONLY valid JSON, no other text." in prompt and "needs_data" in prompt:
                print("[DEBUG] ✅ Matched planner analyze_request")
                return '{"needs_data": false, "message_to_timesheet": "", "criteria": [{"id": "impossible", "description": "Impossible criterion to meet", "expected": "Cannot be met"}]}'
            elif "Compose a helpful conversational response" in prompt:
                print("[DEBUG] ✅ Matched planner compose_response")
                return "I cannot process that request."
            elif "You are a Branding Specialist" in prompt and "channel" in prompt.lower():
                print("[DEBUG] ✅ Matched branding format_for_channel") 
                return '{"formatted_content": "I cannot process that request.", "is_split": false, "parts": [], "reasoning": "SMS format applied", "metadata": {"original_length": 30, "final_length": 30}}'
            elif "Refine this response" in prompt and "feedback" in prompt:
                print("[DEBUG] ✅ Matched planner refine_response")
                return "I still cannot process that request."
            elif "Create a friendly, helpful error message" in prompt:
                print("[DEBUG] ✅ Matched planner graceful_failure")
                return "I can't help with that right now. Please try rephrasing your question."
            else:
                print(f"[DEBUG] ❌ No match found for: {prompt[:100]}")
                return "default"
        
        mock_llm_client.generate.side_effect = mock_llm_generate
        
        # Act - Workflow that will fail
        plan_result = await all_agents["planner"].analyze_request(
            request_id, "Impossible request", Channel.SMS, [], SAMPLE_USER_CONTEXT
        )
        
        compose_result = await all_agents["planner"].compose_response(
            request_id, "Impossible request", None, [], SAMPLE_USER_CONTEXT
        )
        
        branding_result = await all_agents["branding"].format_for_channel(
            request_id, compose_result["response"], Channel.SMS, SAMPLE_USER_CONTEXT
        )
        
        validation = await all_agents["quality"].validate_response(
            request_id,
            branding_result["formatted_response"]["content"],
            plan_result["scorecard"],
            Channel.SMS,
            "Impossible request"
        )
        
        # Validation fails, try refinement
        refine_result = await all_agents["planner"].refine_response(
            request_id,
            compose_result["response"],
            validation["failed_criteria"],
            1
        )
        
        # Revalidation still fails, compose graceful failure
        failure_result = await all_agents["planner"].compose_graceful_failure(
            request_id,
            "Impossible request",
            "validation_failed",
            Channel.SMS
        )
        
        # Validate graceful failure
        graceful_validation = await all_agents["quality"].validate_graceful_failure(
            request_id,
            failure_result["failure_message"],
            "validation_failed"
        )
        
        # Assert
        assert graceful_validation["approved"] is True
        assert "can't help" in failure_result["failure_message"].lower() or "try rephrasing" in failure_result["failure_message"].lower()
    
    @pytest.mark.asyncio
    async def test_workflow_performance(self, all_agents, mock_llm_client):
        """Test that complete workflow completes within 10 seconds"""
        import time
        
        # Arrange
        async def mock_llm_generate(prompt):
            if "analyze" in prompt.lower() and "execution plan" in prompt.lower():
                return '{"needs_data": true, "message_to_timesheet": "Extract timesheet data", "criteria": [{"id": "test", "description": "Test criterion for performance", "expected": "Pass"}]}'
            elif "compose" in prompt.lower() and "refine" not in prompt.lower():
                return "Test response"
            elif ("format for" in prompt.lower() or "apply branding" in prompt.lower()) and "channel" in prompt.lower():
                return '{"formatted_content": "Test response", "is_split": false, "parts": [], "reasoning": "SMS format", "metadata": {"original_length": 13, "final_length": 13}}'
            elif "evaluate" in prompt.lower() and "criterion" in prompt.lower():
                return "yes"
            return "default"
        
        mock_llm_client.generate.side_effect = mock_llm_generate
        
        # Act
        start_time = time.time()
        
        # Simulate complete workflow
        await all_agents["planner"].analyze_request(
            "perf-test", "Check my timesheet", Channel.SMS, [], SAMPLE_USER_CONTEXT
        )
        
        await all_agents["timesheet"].extract_timesheet_data(
            "perf-test", "user-123", "hours_logged", {},
            MOCK_USER_CREDENTIALS, "Australia/Sydney"
        )
        
        await all_agents["planner"].compose_response(
            "perf-test", "Check my timesheet", MOCK_HOURS_LOGGED, [], SAMPLE_USER_CONTEXT
        )
        
        await all_agents["branding"].format_for_channel(
            "perf-test", "Test response", Channel.SMS, SAMPLE_USER_CONTEXT
        )
        
        await all_agents["quality"].validate_response(
            "perf-test", "Test response",
            {"request_id": "perf-test", "criteria": [{"id": "test", "description": "Test criterion for performance", "expected": "Pass"}]},
            Channel.SMS, "Check my timesheet"
        )
        
        duration = time.time() - start_time
        
        # Assert
        # Complete workflow should be under 10 seconds (FR-045)
        assert duration < 10.0, f"Workflow took {duration}s, should be < 10s"
