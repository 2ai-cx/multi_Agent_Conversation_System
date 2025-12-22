"""
Unit tests for Agent Framework Mem0 bridge.
Tests the integration between Mem0 and Agent Framework context providers.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from llm.agent_framework_mem0_bridge import Mem0AgentFrameworkContext, Mem0AgentFrameworkMemory


class TestMem0AgentFrameworkContext:
    """Test suite for Mem0AgentFrameworkContext"""
    
    @pytest.fixture
    def mock_mem0_manager(self):
        """Create mock Mem0 manager"""
        manager = Mock()
        manager.retrieve_context = Mock(return_value=["Context 1", "Context 2", "Context 3"])
        manager.add_conversation = Mock()
        return manager
    
    def test_initialization(self, mock_mem0_manager):
        """Test context provider initialization"""
        context = Mem0AgentFrameworkContext(
            mem0_manager=mock_mem0_manager,
            tenant_id="test-tenant",
            user_id="test-user",
            k=5
        )
        
        assert context.tenant_id == "test-tenant"
        assert context.user_id == "test-user"
        assert context.k == 5
    
    @pytest.mark.asyncio
    async def test_get_context(self, mock_mem0_manager):
        """Test getting context from Mem0"""
        context_provider = Mem0AgentFrameworkContext(
            mem0_manager=mock_mem0_manager,
            tenant_id="test-tenant",
            user_id="test-user",
            k=10
        )
        
        # Mock agent context
        agent_context = Mock()
        agent_context.messages = []
        
        result = await context_provider.get_context(
            agent_context=agent_context,
            query="What is my name?"
        )
        
        assert "memories" in result
        assert "context" in result
        assert len(result["memories"]) == 3
        assert "Context 1" in result["context"]
        
        mock_mem0_manager.retrieve_context.assert_called_once_with(
            query="What is my name?",
            tenant_id="test-tenant",
            user_id="test-user",
            k=10
        )
    
    @pytest.mark.asyncio
    async def test_get_context_no_query(self, mock_mem0_manager):
        """Test getting context with no query"""
        context_provider = Mem0AgentFrameworkContext(
            mem0_manager=mock_mem0_manager,
            tenant_id="test-tenant",
            user_id="test-user"
        )
        
        agent_context = Mock()
        agent_context.messages = []
        
        result = await context_provider.get_context(agent_context=agent_context)
        
        assert result["memories"] == []
        assert result["context"] == ""
    
    @pytest.mark.asyncio
    async def test_save_context(self, mock_mem0_manager):
        """Test saving conversation to Mem0"""
        context_provider = Mem0AgentFrameworkContext(
            mem0_manager=mock_mem0_manager,
            tenant_id="test-tenant",
            user_id="test-user"
        )
        
        agent_context = Mock()
        
        await context_provider.save_context(
            agent_context=agent_context,
            user_message="What is my name?",
            agent_response="Your name is John."
        )
        
        mock_mem0_manager.add_conversation.assert_called_once_with(
            user_message="What is my name?",
            ai_response="Your name is John.",
            tenant_id="test-tenant",
            user_id="test-user"
        )
    
    @pytest.mark.asyncio
    async def test_error_handling_get(self, mock_mem0_manager):
        """Test error handling when getting context fails"""
        mock_mem0_manager.retrieve_context = Mock(side_effect=Exception("Mem0 error"))
        
        context_provider = Mem0AgentFrameworkContext(
            mem0_manager=mock_mem0_manager,
            tenant_id="test-tenant",
            user_id="test-user"
        )
        
        agent_context = Mock()
        agent_context.messages = []
        
        result = await context_provider.get_context(
            agent_context=agent_context,
            query="test query"
        )
        
        assert result["memories"] == []
        assert result["context"] == ""


class TestMem0AgentFrameworkMemory:
    """Test suite for Mem0AgentFrameworkMemory wrapper"""
    
    @pytest.fixture
    def mock_mem0_manager(self):
        """Create mock Mem0 manager"""
        manager = Mock()
        manager.retrieve_context = Mock(return_value=["Memory 1", "Memory 2"])
        manager.add_conversation = Mock()
        return manager
    
    def test_initialization(self, mock_mem0_manager):
        """Test memory wrapper initialization"""
        memory = Mem0AgentFrameworkMemory(
            mem0_manager=mock_mem0_manager,
            tenant_id="test-tenant",
            user_id="test-user",
            k=5
        )
        
        assert memory.tenant_id == "test-tenant"
        assert memory.user_id == "test-user"
        assert memory.k == 5
    
    def test_retrieve(self, mock_mem0_manager):
        """Test retrieving memories"""
        memory = Mem0AgentFrameworkMemory(
            mem0_manager=mock_mem0_manager,
            tenant_id="test-tenant",
            user_id="test-user",
            k=10
        )
        
        memories = memory.retrieve("test query")
        
        assert len(memories) == 2
        assert memories[0] == "Memory 1"
        
        mock_mem0_manager.retrieve_context.assert_called_once_with(
            query="test query",
            tenant_id="test-tenant",
            user_id="test-user",
            k=10
        )
    
    def test_add(self, mock_mem0_manager):
        """Test adding conversation"""
        memory = Mem0AgentFrameworkMemory(
            mem0_manager=mock_mem0_manager,
            tenant_id="test-tenant",
            user_id="test-user"
        )
        
        memory.add(
            user_message="Hello",
            ai_response="Hi there!"
        )
        
        mock_mem0_manager.add_conversation.assert_called_once_with(
            user_message="Hello",
            ai_response="Hi there!",
            tenant_id="test-tenant",
            user_id="test-user"
        )
    
    def test_search(self, mock_mem0_manager):
        """Test searching memories"""
        memory = Mem0AgentFrameworkMemory(
            mem0_manager=mock_mem0_manager,
            tenant_id="test-tenant",
            user_id="test-user",
            k=10
        )
        
        results = memory.search("test query")
        
        assert len(results) == 2
    
    def test_search_custom_k(self, mock_mem0_manager):
        """Test searching with custom k"""
        memory = Mem0AgentFrameworkMemory(
            mem0_manager=mock_mem0_manager,
            tenant_id="test-tenant",
            user_id="test-user",
            k=10
        )
        
        results = memory.search("test query", k=5)
        
        mock_mem0_manager.retrieve_context.assert_called_with(
            query="test query",
            tenant_id="test-tenant",
            user_id="test-user",
            k=5
        )
    
    def test_error_handling_retrieve(self, mock_mem0_manager):
        """Test error handling when retrieval fails"""
        mock_mem0_manager.retrieve_context = Mock(side_effect=Exception("Retrieval error"))
        
        memory = Mem0AgentFrameworkMemory(
            mem0_manager=mock_mem0_manager,
            tenant_id="test-tenant",
            user_id="test-user"
        )
        
        results = memory.retrieve("test query")
        
        assert results == []


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
