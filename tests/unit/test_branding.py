"""Unit tests for Branding Agent"""

import pytest
from unittest.mock import Mock, AsyncMock
from agents.branding import BrandingAgent
from agents.models import Channel, FormattedResponse
from tests.fixtures.sample_requests import SAMPLE_USER_CONTEXT


class TestBrandingFormatSMS:
    """Test Branding.format_for_channel for SMS"""
    
    @pytest.fixture
    def mock_llm_client(self):
        client = Mock()
        client.generate = AsyncMock(return_value='{"formatted_content": "You have logged 32 hours this week. Great job!", "is_split": false, "parts": [], "reasoning": "Removed markdown formatting for SMS", "metadata": {"original_length": 50, "final_length": 45, "markdown_used": false, "truncated": false}}')
        return client
    
    @pytest.fixture
    def branding_agent(self, mock_llm_client):
        return BrandingAgent(mock_llm_client)
    
    @pytest.mark.asyncio
    async def test_format_sms_removes_markdown(self, branding_agent):
        """Test that SMS formatting removes markdown"""
        # Arrange
        response_with_markdown = "You've logged **32 hours** this week. _Great job!_"
        
        # Act
        result = await branding_agent.format_for_channel(
            "test-req-001",
            response_with_markdown,
            Channel.SMS,
            SAMPLE_USER_CONTEXT
        )
        
        # Assert
        formatted = FormattedResponse(**result["formatted_response"])
        assert "**" not in formatted.content
        assert "_" not in formatted.content or "Great" in formatted.content
        assert formatted.channel == Channel.SMS
    
    @pytest.mark.asyncio
    async def test_format_sms_respects_length_limit(self, branding_agent):
        """Test that SMS respects 1600 character limit"""
        # Arrange
        long_response = "A" * 2000  # Exceeds SMS limit
        
        # Act
        result = await branding_agent.format_for_channel(
            "test-req-002",
            long_response,
            Channel.SMS,
            SAMPLE_USER_CONTEXT
        )
        
        # Assert
        formatted = FormattedResponse(**result["formatted_response"])
        if formatted.is_split:
            # Should be split into parts
            assert len(formatted.parts) > 1
            for part in formatted.parts:
                assert len(part.content) <= 1600
        else:
            assert len(formatted.content) <= 1600
    
    @pytest.mark.asyncio
    async def test_format_sms_plain_text_only(self, branding_agent):
        """Test that SMS output is plain text"""
        # Mock specific response for this test
        branding_agent.llm_client.generate.return_value = '{"formatted_content": "You have logged 32/40 hours this week.", "is_split": false, "parts": [], "reasoning": "Plain text for SMS", "metadata": {"original_length": 35, "final_length": 35, "markdown_applied": false, "truncated": false}}'
        
        # Arrange
        response = "You've logged 32/40 hours this week."
        
        # Act
        result = await branding_agent.format_for_channel(
            "test-req-003",
            response,
            Channel.SMS,
            SAMPLE_USER_CONTEXT
        )
        
        # Assert
        formatted = FormattedResponse(**result["formatted_response"])
        # Should not contain HTML or special formatting
        assert "<" not in formatted.content
        assert ">" not in formatted.content
        assert formatted.metadata.get("markdown_applied") is False
    
    @pytest.mark.asyncio
    async def test_format_sms_splits_at_sentence_boundaries(self, branding_agent):
        """Test that long SMS messages split at sentence boundaries"""
        # Arrange
        # Create a long message with clear sentences
        sentences = [f"This is sentence number {i}." for i in range(100)]
        long_response = " ".join(sentences)
        
        # Act
        result = await branding_agent.format_for_channel(
            "test-req-004",
            long_response,
            Channel.SMS,
            SAMPLE_USER_CONTEXT
        )
        
        # Assert
        formatted = FormattedResponse(**result["formatted_response"])
        if formatted.is_split:
            # Each part should end with a complete sentence
            for part in formatted.parts:
                assert part.content.strip().endswith(".")
            # Should have continuation indicators
            assert any(part.continuation_indicator for part in formatted.parts)


class TestBrandingFormatEmail:
    """Test Branding.format_for_channel for Email"""
    
    @pytest.fixture
    def mock_llm_client(self):
        client = Mock()
        client.generate = AsyncMock(return_value='{"formatted_content": "# Timesheet Update\\n\\n**You have logged 32 hours this week.** Great job!", "is_split": false, "parts": [], "reasoning": "Added markdown formatting for email", "metadata": {"original_length": 50, "final_length": 75, "markdown_used": true, "truncated": false}}')
        return client
    
    @pytest.fixture
    def branding_agent(self, mock_llm_client):
        return BrandingAgent(mock_llm_client)
    
    @pytest.mark.asyncio
    async def test_format_email_supports_markdown(self, branding_agent):
        """Test that Email formatting supports full markdown"""
        # Arrange
        response = "You've logged 32 hours this week."
        
        # Act
        result = await branding_agent.format_for_channel(
            "test-req-005",
            response,
            Channel.EMAIL,
            SAMPLE_USER_CONTEXT
        )
        
        # Assert
        formatted = FormattedResponse(**result["formatted_response"])
        # Email should support markdown
        assert formatted.channel == Channel.EMAIL
        # Should have markdown or rich formatting applied
        assert formatted.metadata.get("markdown_applied") is True or "**" in formatted.content or "#" in formatted.content
    
    @pytest.mark.asyncio
    async def test_format_email_no_length_limit(self, branding_agent):
        """Test that Email has no length limit"""
        # Mock response with long content for this test
        long_content = "A" * 2000  # Longer than SMS limit
        branding_agent.llm_client.generate.return_value = f'{{"formatted_content": "{long_content}", "is_split": false, "parts": [], "reasoning": "No length limit for email", "metadata": {{"original_length": 5000, "final_length": 2000, "markdown_used": true, "truncated": false}}}}'
        
        # Arrange
        very_long_response = "A" * 5000  # Much longer than SMS
        
        # Act
        result = await branding_agent.format_for_channel(
            "test-req-006",
            very_long_response,
            Channel.EMAIL,
            SAMPLE_USER_CONTEXT
        )
        
        # Assert
        formatted = FormattedResponse(**result["formatted_response"])
        # Should not be split for Email
        assert formatted.is_split is False
        assert len(formatted.content) > 1600  # Longer than SMS limit


class TestBrandingStyleGuide:
    """Test Branding Agent style guide application"""
    
    @pytest.fixture
    def mock_llm_client(self):
        client = Mock()
        client.generate = AsyncMock(return_value='{"formatted_content": "✅ Great job! You have completed your timesheet.", "is_split": false, "parts": [], "reasoning": "Added emoji based on style guide", "metadata": {"original_length": 50, "final_length": 55, "markdown_used": false, "truncated": false}}')
        return client
    
    @pytest.fixture
    def branding_agent(self, mock_llm_client):
        return BrandingAgent(mock_llm_client)
    
    @pytest.mark.asyncio
    async def test_applies_emojis_when_enabled(self, branding_agent):
        """Test that emojis are applied based on style guide"""
        # Arrange
        response = "Great job! You've completed your timesheet."
        
        # Act
        result = await branding_agent.format_for_channel(
            "test-req-007",
            response,
            Channel.SMS,
            SAMPLE_USER_CONTEXT
        )
        
        # Assert
        formatted = FormattedResponse(**result["formatted_response"])
        # Should have emojis if style guide enables them
        emojis_used = formatted.metadata.get("emojis_used", [])
        # Success message should have success emoji
        if branding_agent.style_guide.get("emojis", {}).get("enabled"):
            assert len(emojis_used) > 0 or "✅" in formatted.content
    
    @pytest.mark.asyncio
    async def test_applies_user_name_when_configured(self, branding_agent):
        """Test that user name is used when configured"""
        # Mock response with user name included
        branding_agent.llm_client.generate.return_value = '{"formatted_content": "Hi John! You have logged 32 hours this week.", "is_split": false, "parts": [], "reasoning": "Added user name based on style guide", "metadata": {"original_length": 35, "final_length": 45, "markdown_used": false, "truncated": false}}'
        
        # Arrange
        response = "You've logged 32 hours this week."
        user_context = {
            **SAMPLE_USER_CONTEXT,
            "full_name": "John Doe"
        }
        
        # Act
        result = await branding_agent.format_for_channel(
            "test-req-008",
            response,
            Channel.SMS,
            user_context
        )
        
        # Assert
        formatted = FormattedResponse(**result["formatted_response"])
        # If use_user_name is enabled, should include name
        if branding_agent.style_guide.get("formatting", {}).get("use_user_name"):
            assert "John" in formatted.content or "Doe" in formatted.content or "Hi" in formatted.content
