"""Unit tests for Quality Agent"""

import pytest
from unittest.mock import Mock, AsyncMock
from agents.quality import QualityAgent
from agents.models import Scorecard, ScorecardCriterion, ValidationResult, Channel
from tests.fixtures.sample_scorecards import (
    TIMESHEET_QUERY_SCORECARD,
    SMS_FORMAT_SCORECARD,
    PASSING_SCORECARD,
    FAILING_SCORECARD
)


class TestQualityValidateResponse:
    """Test Quality.validate_response method"""
    
    @pytest.fixture
    def mock_llm_client(self):
        client = Mock()
        client.generate = AsyncMock()
        return client
    
    @pytest.fixture
    def quality_agent(self, mock_llm_client):
        return QualityAgent(mock_llm_client)
    
    @pytest.mark.asyncio
    async def test_validate_passing_response(self, quality_agent, mock_llm_client):
        """Test validation of a response that passes all criteria"""
        # Arrange
        response = "You've logged 32 hours this week. Great progress!"
        scorecard = TIMESHEET_QUERY_SCORECARD.model_dump()
        
        # Mock LLM to return "yes" for all criteria
        mock_llm_client.generate.return_value = "yes"
        
        # Act
        result = await quality_agent.validate_response(
            "test-req-001",
            response,
            scorecard,
            Channel.SMS,
            "Check my timesheet"
        )
        
        # Assert
        validation = ValidationResult(**result["validation_result"])
        assert validation.passed is True
        assert len(validation.failed_criteria_ids) == 0
        assert validation.feedback is None or validation.feedback == ""
    
    @pytest.mark.asyncio
    async def test_validate_failing_response(self, quality_agent, mock_llm_client):
        """Test validation of a response that fails criteria"""
        # Arrange
        response = "You've logged **32 hours** this week."  # Has markdown for SMS
        scorecard = SMS_FORMAT_SCORECARD.model_dump()
        
        # Mock LLM to return "no" for markdown criterion
        async def mock_generate(prompt):
            if "markdown" in prompt.lower():
                return "no - contains markdown symbols"
            return "yes"
        
        mock_llm_client.generate.side_effect = mock_generate
        
        # Act
        result = await quality_agent.validate_response(
            "test-req-002",
            response,
            scorecard,
            Channel.SMS,
            "Check my timesheet"
        )
        
        # Assert
        validation = ValidationResult(**result["validation_result"])
        assert validation.passed is False
        assert len(validation.failed_criteria_ids) > 0
        assert validation.feedback is not None
        assert "markdown" in validation.feedback.lower()
    
    @pytest.mark.asyncio
    async def test_validate_evaluates_all_criteria(self, quality_agent, mock_llm_client):
        """Test that all scorecard criteria are evaluated"""
        # Arrange
        scorecard = Scorecard(
            request_id="test-req-003",
            criteria=[
                ScorecardCriterion(
                    id="criterion_1",
                    description="First criterion",
                    expected="Should pass"
                ),
                ScorecardCriterion(
                    id="criterion_2",
                    description="Second criterion",
                    expected="Should pass"
                ),
                ScorecardCriterion(
                    id="criterion_3",
                    description="Third criterion",
                    expected="Should pass"
                )
            ]
        )
        
        mock_llm_client.generate.return_value = "yes"
        
        # Act
        result = await quality_agent.validate_response(
            "test-req-003",
            "Some response",
            scorecard.model_dump(),
            Channel.SMS,
            "Some question"
        )
        
        # Assert
        # LLM should have been called once per criterion
        assert mock_llm_client.generate.call_count == 3
    
    @pytest.mark.asyncio
    async def test_validate_provides_specific_feedback(self, quality_agent, mock_llm_client):
        """Test that validation provides specific feedback for failed criteria"""
        # Arrange
        scorecard = Scorecard(
            request_id="test-req-004",
            criteria=[
                ScorecardCriterion(
                    id="length_check",
                    description="Response is under 1600 characters",
                    expected="Character count <= 1600"
                )
            ]
        )
        
        response = "A" * 2000  # Exceeds limit
        mock_llm_client.generate.return_value = "no - response is 2000 characters, exceeds 1600 limit"
        
        # Act
        result = await quality_agent.validate_response(
            "test-req-004",
            response,
            scorecard.model_dump(),
            Channel.SMS,
            "Some question"
        )
        
        # Assert
        validation = ValidationResult(**result["validation_result"])
        assert validation.feedback is not None
        assert "1600" in validation.feedback or "2000" in validation.feedback
    
    @pytest.mark.asyncio
    async def test_validate_aggregates_multiple_failures(self, quality_agent, mock_llm_client):
        """Test that multiple failed criteria are aggregated in feedback"""
        # Arrange
        scorecard = Scorecard(
            request_id="test-req-005",
            criteria=[
                ScorecardCriterion(id="c1", description="Criterion 1", expected="Pass"),
                ScorecardCriterion(id="c2", description="Criterion 2", expected="Pass"),
                ScorecardCriterion(id="c3", description="Criterion 3", expected="Pass")
            ]
        )
        
        # Mock all criteria to fail
        mock_llm_client.generate.return_value = "no - failed"
        
        # Act
        result = await quality_agent.validate_response(
            "test-req-005",
            "Some response",
            scorecard.model_dump(),
            Channel.SMS,
            "Some question"
        )
        
        # Assert
        validation = ValidationResult(**result["validation_result"])
        assert len(validation.failed_criteria_ids) == 3
        assert validation.feedback is not None


class TestQualityValidateGracefulFailure:
    """Test Quality.validate_graceful_failure method"""
    
    @pytest.fixture
    def mock_llm_client(self):
        client = Mock()
        client.generate = AsyncMock()
        return client
    
    @pytest.fixture
    def quality_agent(self, mock_llm_client):
        return QualityAgent(mock_llm_client)
    
    @pytest.mark.asyncio
    async def test_validate_graceful_failure_always_approves(self, quality_agent):
        """Test that graceful failure messages are always approved"""
        # Arrange
        failure_message = "I can't help with that right now."
        
        # Act
        result = await quality_agent.validate_graceful_failure(
            "test-req-006",
            failure_message,
            "validation_failed"
        )
        
        # Assert
        assert result["approved"] is True
        assert result["logged"] is True
    
    @pytest.mark.asyncio
    async def test_validate_graceful_failure_logs_details(self, quality_agent):
        """Test that graceful failure validation logs failure details"""
        # Arrange
        failure_message = "I'm having trouble accessing your timesheet data."
        failure_reason = "API timeout after 3 retries"
        
        # Act
        result = await quality_agent.validate_graceful_failure(
            "test-req-007",
            failure_message,
            failure_reason
        )
        
        # Assert
        assert result["logged"] is True
        # Logging should happen (verified through agent logs)


class TestQualityPerformance:
    """Test Quality Agent performance requirements"""
    
    @pytest.fixture
    def mock_llm_client(self):
        client = Mock()
        client.generate = AsyncMock(return_value="yes")
        return client
    
    @pytest.fixture
    def quality_agent(self, mock_llm_client):
        return QualityAgent(mock_llm_client)
    
    @pytest.mark.asyncio
    async def test_validation_completes_within_time_limit(self, quality_agent):
        """Test that validation completes within 1 second (performance requirement)"""
        import time
        
        # Arrange
        scorecard = Scorecard(
            request_id="test-req-008",
            criteria=[
                ScorecardCriterion(id="c1", description="Test criterion for performance", expected="Pass")
            ]
        )
        
        # Act
        start_time = time.time()
        await quality_agent.validate_response(
            "test-req-008",
            "Test response",
            scorecard.model_dump(),
            Channel.SMS,
            "Test question"
        )
        duration = time.time() - start_time
        
        # Assert
        # Should complete within 1 second (FR-046)
        assert duration < 1.0, f"Validation took {duration}s, should be < 1s"
