"""Unit tests for Planner Agent"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from agents.planner import PlannerAgent
from agents.models import ExecutionPlan, Scorecard, Channel
from tests.fixtures.sample_requests import SAMPLE_SMS_REQUEST, SAMPLE_USER_CONTEXT


class TestPlannerAnalyzeRequest:
    """Test Planner.analyze_request method"""
    
    @pytest.fixture
    def mock_llm_client(self):
        """Mock LLM client"""
        client = Mock()
        client.generate = AsyncMock()
        return client
    
    @pytest.fixture
    def planner_agent(self, mock_llm_client):
        """Create Planner agent with mock LLM client"""
        return PlannerAgent(mock_llm_client)
    
    @pytest.mark.asyncio
    async def test_analyze_request_creates_execution_plan(self, planner_agent, mock_llm_client):
        """Test that analyze_request creates a valid execution plan"""
        # Arrange
        request_id = "test-req-001"
        user_message = "Check my timesheet"
        channel = Channel.SMS
        conversation_history = []
        user_context = SAMPLE_USER_CONTEXT
        
        # Mock LLM response
        mock_llm_client.generate.return_value = '{"needs_data": true, "message_to_timesheet": "Extract user timesheet data for this week", "criteria": [{"id": "data_completeness", "description": "Response includes timesheet data", "expected": "Shows hours and projects"}]}'
        
        # Act
        result = await planner_agent.analyze_request(
            request_id, user_message, channel, conversation_history, user_context
        )
        
        # Assert
        assert "execution_plan" in result
        assert "scorecard" in result
        
        plan = result["execution_plan"]
        assert plan["request_id"] == request_id
        assert plan["user_message"] == user_message
        assert plan["channel"] == channel
        assert plan["needs_data"] is True
    
    @pytest.mark.asyncio
    async def test_analyze_request_creates_scorecard(self, planner_agent, mock_llm_client):
        """Test that analyze_request creates a valid scorecard"""
        # Arrange
        request_id = "test-req-002"
        
        # Mock LLM response
        mock_llm_client.generate.return_value = '{"needs_data": true, "message_to_timesheet": "Extract user timesheet data", "criteria": [{"id": "answers_question", "description": "Response answers user question", "expected": "Contains timesheet hours"}]}'
        
        # Act
        result = await planner_agent.analyze_request(
            request_id, "Check my timesheet", Channel.SMS, [], SAMPLE_USER_CONTEXT
        )
        
        # Assert
        scorecard = Scorecard(**result["scorecard"])
        assert scorecard.request_id == request_id
        assert len(scorecard.criteria) > 0
        assert all(c.id and c.description and c.expected for c in scorecard.criteria)
    
    @pytest.mark.asyncio
    async def test_analyze_request_handles_sms_channel(self, planner_agent, mock_llm_client):
        """Test that SMS channel creates appropriate scorecard criteria"""
        # Arrange
        mock_llm_client.generate.return_value = '{"needs_data": true, "message_to_timesheet": "Extract user timesheet data", "criteria": [{"id": "no_markdown", "description": "Response has no markdown for SMS", "expected": "Plain text only"}]}'
        
        # Act
        result = await planner_agent.analyze_request(
            "test-req-003", "Check my timesheet", Channel.SMS, [], SAMPLE_USER_CONTEXT
        )
        
        # Assert
        scorecard = Scorecard(**result["scorecard"])
        # Should have criteria about SMS formatting
        criteria_ids = [c.id for c in scorecard.criteria]
        assert any("format" in cid or "markdown" in cid for cid in criteria_ids)


class TestPlannerComposeResponse:
    """Test Planner.compose_response method"""
    
    @pytest.fixture
    def mock_llm_client(self):
        client = Mock()
        client.generate = AsyncMock()
        return client
    
    @pytest.fixture
    def planner_agent(self, mock_llm_client):
        return PlannerAgent(mock_llm_client)
    
    @pytest.mark.asyncio
    async def test_compose_response_with_timesheet_data(self, planner_agent, mock_llm_client):
        """Test composing response with timesheet data"""
        # Arrange
        timesheet_data = {
            "hours_logged": 32.0,
            "hours_target": 40.0
        }
        
        mock_llm_client.generate.return_value = "You've logged 32/40 hours this week."
        
        # Act
        result = await planner_agent.compose_response(
            "test-req-004",
            "Check my timesheet",
            timesheet_data,
            [],
            SAMPLE_USER_CONTEXT
        )
        
        # Assert
        assert "response" in result
        assert "metadata" in result
        assert result["metadata"]["used_timesheet_data"] is True
        assert "32" in result["response"] or "40" in result["response"]
    
    @pytest.mark.asyncio
    async def test_compose_response_without_timesheet_data(self, planner_agent, mock_llm_client):
        """Test composing conversational response without data"""
        # Arrange
        mock_llm_client.generate.return_value = "Hi! How can I help you today?"
        
        # Act
        result = await planner_agent.compose_response(
            "test-req-005",
            "Hello",
            None,
            [],
            SAMPLE_USER_CONTEXT
        )
        
        # Assert
        assert "response" in result
        assert result["metadata"]["used_timesheet_data"] is False
        assert result["metadata"]["response_type"] == "conversational"


class TestPlannerRefineResponse:
    """Test Planner.refine_response method"""
    
    @pytest.fixture
    def mock_llm_client(self):
        client = Mock()
        client.generate = AsyncMock()
        return client
    
    @pytest.fixture
    def planner_agent(self, mock_llm_client):
        return PlannerAgent(mock_llm_client)
    
    @pytest.mark.asyncio
    async def test_refine_response_improves_quality(self, planner_agent, mock_llm_client):
        """Test that refinement improves response based on feedback"""
        # Arrange
        original_response = "You logged **32 hours** this week."  # Has markdown
        failed_criteria = [
            {
                "id": "no_markdown",
                "description": "No markdown for SMS",
                "expected": "Plain text",
                "feedback": "Remove markdown symbols"
            }
        ]
        
        mock_llm_client.generate.return_value = "You logged 32 hours this week."  # Fixed
        
        # Act
        result = await planner_agent.refine_response(
            "test-req-006",
            original_response,
            failed_criteria,
            1
        )
        
        # Assert
        assert "refined_response" in result
        assert "**" not in result["refined_response"]  # Markdown removed
        assert "changes_made" in result
        assert len(result["changes_made"]) > 0
    
    @pytest.mark.asyncio
    async def test_refine_response_max_one_attempt(self, planner_agent):
        """Test that refinement enforces max 1 attempt"""
        # Arrange
        with pytest.raises(ValueError, match="Maximum 1 refinement"):
            # Act
            await planner_agent.refine_response(
                "test-req-007",
                "Some response",
                [],
                2  # Attempt 2 should fail
            )


class TestPlannerGracefulFailure:
    """Test Planner.compose_graceful_failure method"""
    
    @pytest.fixture
    def mock_llm_client(self):
        client = Mock()
        client.generate = AsyncMock()
        return client
    
    @pytest.fixture
    def planner_agent(self, mock_llm_client):
        return PlannerAgent(mock_llm_client)
    
    @pytest.mark.asyncio
    async def test_compose_graceful_failure_user_friendly(self, planner_agent, mock_llm_client):
        """Test that graceful failure message is user-friendly"""
        # Arrange
        mock_llm_client.generate.return_value = "I can't help with that right now. Please try rephrasing your question."
        
        # Act
        result = await planner_agent.compose_graceful_failure(
            "test-req-008",
            "Some complex query",
            "validation_failed",
            Channel.SMS
        )
        
        # Assert
        assert "failure_message" in result
        assert "metadata" in result
        assert result["metadata"]["logged"] is True
        # Should be friendly, not technical
        assert "error" not in result["failure_message"].lower() or "can't" in result["failure_message"].lower()
