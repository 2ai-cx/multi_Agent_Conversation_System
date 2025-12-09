"""Unit tests for Timesheet Agent"""

import pytest
from unittest.mock import Mock, AsyncMock
from agents.timesheet import TimesheetAgent
from tests.fixtures.mock_harvest_data import (
    MOCK_HOURS_LOGGED,
    MOCK_PROJECTS,
    MOCK_USER_CREDENTIALS,
    MOCK_API_RESPONSES
)


class TestTimesheetExtractData:
    """Test Timesheet.extract_timesheet_data method"""
    
    @pytest.fixture
    def mock_llm_client(self):
        """Mock LLM client"""
        client = Mock()
        client.generate = AsyncMock()
        return client
    
    @pytest.fixture
    def mock_harvest_tools(self):
        """Mock Harvest API tools"""
        tools = Mock()
        tools.check_my_timesheet = AsyncMock(return_value=MOCK_HOURS_LOGGED)
        tools.list_my_projects = AsyncMock(return_value=MOCK_PROJECTS)
        tools.get_time_entries = AsyncMock(return_value=[])
        return tools
    
    @pytest.fixture
    def timesheet_agent(self, mock_llm_client, mock_harvest_tools):
        """Create Timesheet agent with mocks"""
        return TimesheetAgent(mock_llm_client, mock_harvest_tools)
    
    @pytest.mark.asyncio
    async def test_extract_hours_logged(self, timesheet_agent, mock_harvest_tools):
        """Test extracting hours logged data"""
        # Arrange
        request_id = "test-req-001"
        user_id = "user-123"
        query_type = "hours_logged"
        parameters = {"date_range": "this_week"}
        
        # Act
        result = await timesheet_agent.extract_timesheet_data(
            request_id,
            user_id,
            query_type,
            parameters,
            MOCK_USER_CREDENTIALS,
            "Australia/Sydney"
        )
        
        # Assert
        assert result["success"] is True
        assert result["error"] is None
        assert "data" in result
        assert result["data"]["hours_logged"] == 32.0
        assert result["data"]["hours_target"] == 40.0
        assert "metadata" in result
        assert "check_my_timesheet" in result["metadata"]["tools_used"]
    
    @pytest.mark.asyncio
    async def test_extract_projects(self, timesheet_agent, mock_harvest_tools):
        """Test extracting projects data"""
        # Arrange
        query_type = "projects"
        parameters = {}
        
        # Act
        result = await timesheet_agent.extract_timesheet_data(
            "test-req-002",
            "user-123",
            query_type,
            parameters,
            MOCK_USER_CREDENTIALS,
            "Australia/Sydney"
        )
        
        # Assert
        assert result["success"] is True
        assert "projects" in result["data"]
        assert len(result["data"]["projects"]) > 0
        assert "list_my_projects" in result["metadata"]["tools_used"]
    
    @pytest.mark.asyncio
    async def test_extract_handles_api_error(self, timesheet_agent, mock_harvest_tools):
        """Test handling of Harvest API errors"""
        # Arrange
        mock_harvest_tools.check_my_timesheet.side_effect = Exception("API timeout")
        
        # Act
        result = await timesheet_agent.extract_timesheet_data(
            "test-req-003",
            "user-123",
            "hours_logged",
            {},
            MOCK_USER_CREDENTIALS,
            "Australia/Sydney"
        )
        
        # Assert
        assert result["success"] is False
        assert result["error"] is not None
        assert "timeout" in result["error"].lower() or "API" in result["error"]
    
    @pytest.mark.asyncio
    async def test_extract_uses_user_credentials(self, timesheet_agent, mock_harvest_tools):
        """Test that user-specific credentials are used"""
        # Arrange
        user_credentials = {
            "harvest_access_token": "user_token_123",
            "harvest_account_id": "account_456",
            "harvest_user_id": 789
        }
        
        # Act
        await timesheet_agent.extract_timesheet_data(
            "test-req-004",
            "user-123",
            "hours_logged",
            {},
            user_credentials,
            "Australia/Sydney"
        )
        
        # Assert
        # Verify the tool was called with user credentials
        mock_harvest_tools.check_my_timesheet.assert_called_once()
        call_kwargs = mock_harvest_tools.check_my_timesheet.call_args.kwargs
        assert call_kwargs.get("user_credentials") == user_credentials
    
    @pytest.mark.asyncio
    async def test_extract_respects_timezone(self, timesheet_agent, mock_harvest_tools):
        """Test that user timezone is respected for date calculations"""
        # Arrange
        timezone = "America/New_York"
        
        # Act
        await timesheet_agent.extract_timesheet_data(
            "test-req-005",
            "user-123",
            "hours_logged",
            {"date_range": "today"},
            MOCK_USER_CREDENTIALS,
            timezone
        )
        
        # Assert
        call_kwargs = mock_harvest_tools.check_my_timesheet.call_args.kwargs
        assert call_kwargs.get("timezone") == timezone
    
    @pytest.mark.asyncio
    async def test_extract_multiple_query_types(self, timesheet_agent, mock_harvest_tools):
        """Test handling multiple query types"""
        # Arrange
        query_types = ["hours_logged", "projects", "time_entries"]
        
        for query_type in query_types:
            # Act
            result = await timesheet_agent.extract_timesheet_data(
                f"test-req-{query_type}",
                "user-123",
                query_type,
                {},
                MOCK_USER_CREDENTIALS,
                "Australia/Sydney"
            )
            
            # Assert
            assert result["success"] is True, f"Failed for query_type: {query_type}"
            assert "data" in result
            assert "metadata" in result
