"""
Unit tests for LangChain wrapper.
Tests the CustomLangChainLLM wrapper for our custom LLM client.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from llm.langchain_wrapper import CustomLangChainLLM
from llm.config import LLMConfig


class TestCustomLangChainLLM:
    """Test suite for CustomLangChainLLM wrapper"""
    
    @pytest.fixture
    def mock_config(self):
        """Create mock LLM config"""
        config = Mock(spec=LLMConfig)
        config.model = "test-model"
        config.api_key = "test-key"
        config.log_level = "INFO"
        config.max_retries = 3
        config.timeout = 30
        config.temperature = 0.7
        return config
    
    @pytest.fixture
    def mock_llm_client(self):
        """Create mock LLM client"""
        client = Mock()
        client.generate = Mock(return_value="Test response")
        client.generate_async = AsyncMock(return_value="Test async response")
        client.config = Mock(model="test-model")
        return client
    
    def test_initialization(self, mock_config):
        """Test LangChain LLM wrapper initialization"""
        llm = CustomLangChainLLM(config=mock_config, tenant_id="test-tenant")
        
        assert llm.tenant_id == "test-tenant"
        assert llm._llm_type == "custom_openrouter"
    
    def test_initialization_without_config(self):
        """Test initialization with default config"""
        with patch('llm.langchain_wrapper.LLMConfig') as mock_config_class:
            mock_config = Mock()
            mock_config.log_level = "INFO"
            mock_config.model = "test-model"
            mock_config_class.return_value = mock_config
            
            llm = CustomLangChainLLM()
            assert llm.custom_client is not None
    
    @patch('llm.langchain_wrapper.LLMClient')
    def test_sync_call(self, mock_client_class, mock_config, mock_llm_client):
        """Test synchronous LLM call"""
        mock_client_class.return_value = mock_llm_client
        
        llm = CustomLangChainLLM(config=mock_config, tenant_id="test-tenant")
        llm.custom_client = mock_llm_client
        
        response = llm._call("Test prompt")
        
        assert response == "Test response"
        mock_llm_client.generate.assert_called_once()
    
    @pytest.mark.asyncio
    @patch('llm.langchain_wrapper.LLMClient')
    async def test_async_call(self, mock_client_class, mock_config, mock_llm_client):
        """Test asynchronous LLM call"""
        mock_client_class.return_value = mock_llm_client
        
        llm = CustomLangChainLLM(config=mock_config, tenant_id="test-tenant")
        llm.custom_client = mock_llm_client
        
        response = await llm._acall("Test prompt")
        
        assert response == "Test async response"
        mock_llm_client.generate_async.assert_called_once()
    
    @patch('llm.langchain_wrapper.LLMClient')
    def test_tenant_id_override(self, mock_client_class, mock_config, mock_llm_client):
        """Test tenant_id can be overridden in call"""
        mock_client_class.return_value = mock_llm_client
        
        llm = CustomLangChainLLM(config=mock_config, tenant_id="default-tenant")
        llm.custom_client = mock_llm_client
        
        llm._call("Test prompt", tenant_id="override-tenant")
        
        call_args = mock_llm_client.generate.call_args
        assert call_args[1].get("tenant_id") == "override-tenant"
    
    def test_identifying_params(self, mock_config):
        """Test identifying parameters"""
        with patch('llm.langchain_wrapper.LLMClient') as mock_client_class:
            mock_client = Mock()
            mock_client.config = Mock(model="test-model")
            mock_client_class.return_value = mock_client
            
            llm = CustomLangChainLLM(config=mock_config, tenant_id="test-tenant")
            llm.custom_client = mock_client
            
            params = llm._identifying_params
            
            assert params["llm_type"] == "custom_openrouter"
            assert params["tenant_id"] == "test-tenant"
            assert params["model"] == "test-model"
    
    @patch('llm.langchain_wrapper.LLMClient')
    def test_error_handling(self, mock_client_class, mock_config):
        """Test error handling in LLM call"""
        mock_client = Mock()
        mock_client.generate = Mock(side_effect=Exception("Test error"))
        mock_client_class.return_value = mock_client
        
        llm = CustomLangChainLLM(config=mock_config)
        llm.custom_client = mock_client
        
        with pytest.raises(Exception, match="Test error"):
            llm._call("Test prompt")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
