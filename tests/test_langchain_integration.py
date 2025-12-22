"""
Integration tests for LangChain components.
Tests the full integration of LangChain wrapper, Mem0 bridge, and tools.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from llm.langchain_wrapper import CustomLangChainLLM
from llm.langchain_mem0_bridge import Mem0LangChainMemory
from agents.langchain_tools import HarvestLangChainTools


class TestLangChainIntegration:
    """Integration tests for LangChain components"""
    
    @pytest.fixture
    def mock_harvest_tools(self):
        """Create mock Harvest tools object"""
        tools = Mock()
        
        # Mock all 51 Harvest API methods
        tools.list_time_entries = AsyncMock(return_value={"entries": []})
        tools.get_time_entry = AsyncMock(return_value={"id": 1})
        tools.create_time_entry = AsyncMock(return_value={"id": 2})
        tools.update_time_entry = AsyncMock(return_value={"id": 1})
        tools.delete_time_entry = AsyncMock(return_value={"success": True})
        tools.restart_time_entry = AsyncMock(return_value={"id": 1})
        tools.stop_time_entry = AsyncMock(return_value={"id": 1})
        
        tools.list_projects = AsyncMock(return_value={"projects": []})
        tools.get_project = AsyncMock(return_value={"id": 1})
        tools.create_project = AsyncMock(return_value={"id": 2})
        tools.update_project = AsyncMock(return_value={"id": 1})
        tools.delete_project = AsyncMock(return_value={"success": True})
        
        tools.list_tasks = AsyncMock(return_value={"tasks": []})
        tools.get_task = AsyncMock(return_value={"id": 1})
        tools.create_task = AsyncMock(return_value={"id": 2})
        tools.update_task = AsyncMock(return_value={"id": 1})
        tools.delete_task = AsyncMock(return_value={"success": True})
        
        tools.list_clients = AsyncMock(return_value={"clients": []})
        tools.get_client = AsyncMock(return_value={"id": 1})
        tools.create_client = AsyncMock(return_value={"id": 2})
        tools.update_client = AsyncMock(return_value={"id": 1})
        tools.delete_client = AsyncMock(return_value={"success": True})
        
        tools.list_users = AsyncMock(return_value={"users": []})
        tools.get_user = AsyncMock(return_value={"id": 1})
        tools.get_current_user = AsyncMock(return_value={"id": 1})
        tools.create_user = AsyncMock(return_value={"id": 2})
        tools.update_user = AsyncMock(return_value={"id": 1})
        
        tools.list_project_assignments = AsyncMock(return_value={"assignments": []})
        tools.get_project_assignment = AsyncMock(return_value={"id": 1})
        tools.create_project_assignment = AsyncMock(return_value={"id": 2})
        tools.update_project_assignment = AsyncMock(return_value={"id": 1})
        tools.delete_project_assignment = AsyncMock(return_value={"success": True})
        
        tools.list_task_assignments = AsyncMock(return_value={"assignments": []})
        tools.get_task_assignment = AsyncMock(return_value={"id": 1})
        tools.create_task_assignment = AsyncMock(return_value={"id": 2})
        tools.update_task_assignment = AsyncMock(return_value={"id": 1})
        tools.delete_task_assignment = AsyncMock(return_value={"success": True})
        
        tools.time_report = AsyncMock(return_value={"report": {}})
        tools.expense_report = AsyncMock(return_value={"report": {}})
        tools.project_budget_report = AsyncMock(return_value={"report": {}})
        tools.uninvoiced_report = AsyncMock(return_value={"report": {}})
        tools.team_time_report = AsyncMock(return_value={"report": {}})
        
        tools.list_invoices = AsyncMock(return_value={"invoices": []})
        tools.get_invoice = AsyncMock(return_value={"id": 1})
        tools.create_invoice = AsyncMock(return_value={"id": 2})
        tools.update_invoice = AsyncMock(return_value={"id": 1})
        tools.delete_invoice = AsyncMock(return_value={"success": True})
        
        tools.list_estimates = AsyncMock(return_value={"estimates": []})
        tools.get_estimate = AsyncMock(return_value={"id": 1})
        tools.create_estimate = AsyncMock(return_value={"id": 2})
        tools.update_estimate = AsyncMock(return_value={"id": 1})
        
        tools.get_company_info = AsyncMock(return_value={"company": {}})
        
        return tools
    
    def test_harvest_tools_wrapper_creation(self, mock_harvest_tools):
        """Test creating LangChain tools from Harvest MCP"""
        wrapper = HarvestLangChainTools(mock_harvest_tools)
        
        tools = wrapper.get_tools()
        assert len(tools) == 51
        
        tool_names = wrapper.get_tool_names()
        assert "list_time_entries" in tool_names
        assert "create_time_entry" in tool_names
        assert "list_projects" in tool_names
        assert "get_company_info" in tool_names
    
    def test_get_tool_by_name(self, mock_harvest_tools):
        """Test retrieving specific tool by name"""
        wrapper = HarvestLangChainTools(mock_harvest_tools)
        
        tool = wrapper.get_tool_by_name("list_time_entries")
        assert tool is not None
        assert tool.name == "list_time_entries"
        
        non_existent = wrapper.get_tool_by_name("non_existent_tool")
        assert non_existent is None
    
    @patch('llm.langchain_wrapper.LLMClient')
    def test_llm_wrapper_with_mem0_bridge(self, mock_client_class):
        """Test LLM wrapper working with Mem0 bridge"""
        mock_client = Mock()
        mock_client.generate = Mock(return_value="Test response")
        mock_client.config = Mock(model="test-model")
        mock_client_class.return_value = mock_client
        
        mock_mem0 = Mock()
        mock_mem0.retrieve_context = Mock(return_value=["Context 1", "Context 2"])
        mock_mem0.add_conversation = Mock()
        
        llm = CustomLangChainLLM(tenant_id="test-tenant")
        memory = Mem0LangChainMemory(
            mem0_manager=mock_mem0,
            tenant_id="test-tenant",
            user_id="test-user"
        )
        
        # Load memory
        inputs = {"input": "What is my name?"}
        mem_vars = memory.load_memory_variables(inputs)
        
        assert "context" in mem_vars
        assert "Context 1" in mem_vars["context"]
        
        # Generate response
        response = llm._call("Test prompt")
        assert response == "Test response"
        
        # Save context
        outputs = {"output": response}
        memory.save_context(inputs, outputs)
        
        mock_mem0.add_conversation.assert_called_once()
    
    def test_tool_descriptions(self, mock_harvest_tools):
        """Test that all tools have proper descriptions"""
        wrapper = HarvestLangChainTools(mock_harvest_tools)
        
        for tool in wrapper.get_tools():
            assert tool.name is not None
            assert tool.description is not None
            assert len(tool.description) > 10
            assert tool.func is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
