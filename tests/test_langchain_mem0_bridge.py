"""
Unit tests for Mem0-LangChain bridge.
Tests the integration between Mem0 and LangChain memory interface.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from llm.langchain_mem0_bridge import Mem0LangChainMemory, Mem0VectorStoreRetriever


class TestMem0LangChainMemory:
    """Test suite for Mem0LangChainMemory bridge"""
    
    @pytest.fixture
    def mock_mem0_manager(self):
        """Create mock Mem0 manager"""
        manager = Mock()
        manager.retrieve_context = Mock(return_value=["Context 1", "Context 2", "Context 3"])
        manager.add_conversation = Mock()
        return manager
    
    def test_initialization(self, mock_mem0_manager):
        """Test memory bridge initialization"""
        memory = Mem0LangChainMemory(
            mem0_manager=mock_mem0_manager,
            tenant_id="test-tenant",
            user_id="test-user",
            k=5
        )
        
        assert memory.tenant_id == "test-tenant"
        assert memory.user_id == "test-user"
        assert memory.k == 5
        assert memory.memory_key == "context"
        assert memory.chat_history_key == "chat_history"
    
    def test_memory_variables(self, mock_mem0_manager):
        """Test memory variables property"""
        memory = Mem0LangChainMemory(
            mem0_manager=mock_mem0_manager,
            tenant_id="test-tenant",
            user_id="test-user"
        )
        
        variables = memory.memory_variables
        assert "context" in variables
        assert "chat_history" in variables
    
    def test_load_memory_variables(self, mock_mem0_manager):
        """Test loading memory variables from Mem0"""
        memory = Mem0LangChainMemory(
            mem0_manager=mock_mem0_manager,
            tenant_id="test-tenant",
            user_id="test-user",
            k=10
        )
        
        inputs = {"input": "What is my name?"}
        result = memory.load_memory_variables(inputs)
        
        assert "context" in result
        assert "chat_history" in result
        assert "Context 1" in result["context"]
        assert "Context 2" in result["context"]
        
        mock_mem0_manager.retrieve_context.assert_called_once_with(
            query="What is my name?",
            tenant_id="test-tenant",
            user_id="test-user",
            k=10
        )
    
    def test_load_memory_variables_no_query(self, mock_mem0_manager):
        """Test loading memory with no query in inputs"""
        memory = Mem0LangChainMemory(
            mem0_manager=mock_mem0_manager,
            tenant_id="test-tenant",
            user_id="test-user"
        )
        
        inputs = {}
        result = memory.load_memory_variables(inputs)
        
        assert result["context"] == ""
        assert result["chat_history"] == []
    
    def test_save_context(self, mock_mem0_manager):
        """Test saving conversation context to Mem0"""
        memory = Mem0LangChainMemory(
            mem0_manager=mock_mem0_manager,
            tenant_id="test-tenant",
            user_id="test-user"
        )
        
        inputs = {"input": "What is my name?"}
        outputs = {"output": "Your name is John."}
        
        memory.save_context(inputs, outputs)
        
        mock_mem0_manager.add_conversation.assert_called_once_with(
            user_message="What is my name?",
            ai_response="Your name is John.",
            tenant_id="test-tenant",
            user_id="test-user"
        )
    
    def test_save_context_missing_data(self, mock_mem0_manager):
        """Test saving context with missing data"""
        memory = Mem0LangChainMemory(
            mem0_manager=mock_mem0_manager,
            tenant_id="test-tenant",
            user_id="test-user"
        )
        
        inputs = {}
        outputs = {}
        
        memory.save_context(inputs, outputs)
        
        mock_mem0_manager.add_conversation.assert_not_called()
    
    def test_clear(self, mock_mem0_manager):
        """Test clear method (should not do anything for Mem0)"""
        memory = Mem0LangChainMemory(
            mem0_manager=mock_mem0_manager,
            tenant_id="test-tenant",
            user_id="test-user"
        )
        
        memory.clear()
    
    def test_error_handling_load(self, mock_mem0_manager):
        """Test error handling when loading memory fails"""
        mock_mem0_manager.retrieve_context = Mock(side_effect=Exception("Mem0 error"))
        
        memory = Mem0LangChainMemory(
            mem0_manager=mock_mem0_manager,
            tenant_id="test-tenant",
            user_id="test-user"
        )
        
        inputs = {"input": "test query"}
        result = memory.load_memory_variables(inputs)
        
        assert result["context"] == ""
        assert result["chat_history"] == []


class TestMem0VectorStoreRetriever:
    """Test suite for Mem0VectorStoreRetriever"""
    
    @pytest.fixture
    def mock_mem0_manager(self):
        """Create mock Mem0 manager"""
        manager = Mock()
        manager.retrieve_context = Mock(return_value=["Doc 1", "Doc 2"])
        return manager
    
    def test_initialization(self, mock_mem0_manager):
        """Test retriever initialization"""
        retriever = Mem0VectorStoreRetriever(
            mem0_manager=mock_mem0_manager,
            tenant_id="test-tenant",
            user_id="test-user",
            k=5
        )
        
        assert retriever.tenant_id == "test-tenant"
        assert retriever.user_id == "test-user"
        assert retriever.k == 5
    
    def test_get_relevant_documents(self, mock_mem0_manager):
        """Test retrieving relevant documents"""
        retriever = Mem0VectorStoreRetriever(
            mem0_manager=mock_mem0_manager,
            tenant_id="test-tenant",
            user_id="test-user",
            k=10
        )
        
        docs = retriever.get_relevant_documents("test query")
        
        assert len(docs) == 2
        assert docs[0]["page_content"] == "Doc 1"
        assert docs[0]["metadata"]["source"] == "mem0"
        assert docs[1]["page_content"] == "Doc 2"
        
        mock_mem0_manager.retrieve_context.assert_called_once_with(
            query="test query",
            tenant_id="test-tenant",
            user_id="test-user",
            k=10
        )
    
    @pytest.mark.asyncio
    async def test_aget_relevant_documents(self, mock_mem0_manager):
        """Test async retrieval of relevant documents"""
        retriever = Mem0VectorStoreRetriever(
            mem0_manager=mock_mem0_manager,
            tenant_id="test-tenant",
            user_id="test-user"
        )
        
        docs = await retriever.aget_relevant_documents("test query")
        
        assert len(docs) == 2
        assert docs[0]["page_content"] == "Doc 1"
    
    def test_error_handling(self, mock_mem0_manager):
        """Test error handling when retrieval fails"""
        mock_mem0_manager.retrieve_context = Mock(side_effect=Exception("Retrieval error"))
        
        retriever = Mem0VectorStoreRetriever(
            mem0_manager=mock_mem0_manager,
            tenant_id="test-tenant",
            user_id="test-user"
        )
        
        docs = retriever.get_relevant_documents("test query")
        
        assert docs == []


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
