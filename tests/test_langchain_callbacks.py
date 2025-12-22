"""
Unit tests for LangChain callbacks.
Tests the monitoring and observability callbacks.
"""

import pytest
from unittest.mock import Mock, patch
from monitoring.langchain_callbacks import ProductionCallbackHandler, AzureInsightsCallback
from langchain.schema import AgentAction, AgentFinish, LLMResult


class TestProductionCallbackHandler:
    """Test suite for ProductionCallbackHandler"""
    
    @pytest.fixture
    def callback(self):
        """Create callback handler"""
        return ProductionCallbackHandler(tenant_id="test-tenant", user_id="test-user")
    
    def test_initialization(self, callback):
        """Test callback initialization"""
        assert callback.tenant_id == "test-tenant"
        assert callback.user_id == "test-user"
        assert callback.metrics["llm_calls"] == 0
        assert callback.metrics["tool_calls"] == 0
        assert callback.metrics["total_tokens"] == 0
        assert callback.metrics["errors"] == 0
    
    def test_on_llm_start(self, callback):
        """Test LLM start callback"""
        callback.on_llm_start({}, ["prompt1", "prompt2"], run_id="test-run")
        
        assert callback.metrics["llm_calls"] == 1
        assert "llm_test-run" in callback.start_times
    
    def test_on_llm_end(self, callback):
        """Test LLM end callback"""
        callback.start_times["llm_test-run"] = 0
        
        llm_output = {
            "token_usage": {
                "total_tokens": 100
            }
        }
        result = LLMResult(generations=[], llm_output=llm_output)
        
        callback.on_llm_end(result, run_id="test-run")
        
        assert callback.metrics["total_tokens"] == 100
        assert "llm_test-run" not in callback.start_times
    
    def test_on_llm_error(self, callback):
        """Test LLM error callback"""
        callback.start_times["llm_test-run"] = 0
        
        callback.on_llm_error(Exception("Test error"), run_id="test-run")
        
        assert callback.metrics["errors"] == 1
        assert "llm_test-run" not in callback.start_times
    
    def test_on_tool_start(self, callback):
        """Test tool start callback"""
        callback.on_tool_start({"name": "test_tool"}, "input", run_id="test-run")
        
        assert callback.metrics["tool_calls"] == 1
        assert "tool_test-run" in callback.start_times
    
    def test_on_tool_end(self, callback):
        """Test tool end callback"""
        callback.start_times["tool_test-run"] = 0
        
        callback.on_tool_end("output", run_id="test-run")
        
        assert "tool_test-run" not in callback.start_times
    
    def test_on_tool_error(self, callback):
        """Test tool error callback"""
        callback.start_times["tool_test-run"] = 0
        
        callback.on_tool_error(Exception("Tool error"), run_id="test-run")
        
        assert callback.metrics["errors"] == 1
        assert "tool_test-run" not in callback.start_times
    
    def test_on_agent_action(self, callback):
        """Test agent action callback"""
        action = AgentAction(tool="test_tool", tool_input="input", log="log")
        callback.on_agent_action(action)
    
    def test_on_agent_finish(self, callback):
        """Test agent finish callback"""
        finish = AgentFinish(return_values={"output": "result"}, log="log")
        callback.on_agent_finish(finish)
    
    def test_on_chain_start(self, callback):
        """Test chain start callback"""
        callback.on_chain_start({"name": "test_chain"}, {}, run_id="test-run")
        
        assert "chain_test-run" in callback.start_times
    
    def test_on_chain_end(self, callback):
        """Test chain end callback"""
        callback.start_times["chain_test-run"] = 0
        
        callback.on_chain_end({}, run_id="test-run")
        
        assert "chain_test-run" not in callback.start_times
    
    def test_on_chain_error(self, callback):
        """Test chain error callback"""
        callback.start_times["chain_test-run"] = 0
        
        callback.on_chain_error(Exception("Chain error"), run_id="test-run")
        
        assert callback.metrics["errors"] == 1
        assert "chain_test-run" not in callback.start_times
    
    def test_get_metrics(self, callback):
        """Test getting metrics"""
        callback.metrics["llm_calls"] = 5
        callback.metrics["tool_calls"] = 3
        callback.metrics["total_tokens"] = 500
        
        metrics = callback.get_metrics()
        
        assert metrics["llm_calls"] == 5
        assert metrics["tool_calls"] == 3
        assert metrics["total_tokens"] == 500
        assert metrics["tenant_id"] == "test-tenant"
        assert metrics["user_id"] == "test-user"
        assert "timestamp" in metrics


class TestAzureInsightsCallback:
    """Test suite for AzureInsightsCallback"""
    
    def test_initialization_without_key(self):
        """Test initialization without instrumentation key"""
        callback = AzureInsightsCallback(tenant_id="test-tenant", user_id="test-user")
        
        assert callback.tenant_id == "test-tenant"
        assert callback.user_id == "test-user"
        assert callback.telemetry_client is None
    
    @patch('monitoring.langchain_callbacks.TelemetryClient')
    def test_initialization_with_key(self, mock_telemetry):
        """Test initialization with instrumentation key"""
        callback = AzureInsightsCallback(
            instrumentation_key="test-key",
            tenant_id="test-tenant",
            user_id="test-user"
        )
        
        assert callback.telemetry_client is not None
        mock_telemetry.assert_called_once_with("test-key")
    
    @patch('monitoring.langchain_callbacks.TelemetryClient')
    def test_on_llm_end(self, mock_telemetry):
        """Test LLM end tracking to Azure"""
        mock_client = Mock()
        mock_telemetry.return_value = mock_client
        
        callback = AzureInsightsCallback(
            instrumentation_key="test-key",
            tenant_id="test-tenant",
            user_id="test-user"
        )
        
        llm_output = {
            "token_usage": {
                "total_tokens": 100
            }
        }
        result = LLMResult(generations=[], llm_output=llm_output)
        
        callback.on_llm_end(result)
        
        mock_client.track_event.assert_called_once()
        call_args = mock_client.track_event.call_args
        assert call_args[0][0] == "langchain_llm_call"
        assert call_args[1]["measurements"]["tokens"] == 100
    
    @patch('monitoring.langchain_callbacks.TelemetryClient')
    def test_on_tool_end(self, mock_telemetry):
        """Test tool end tracking to Azure"""
        mock_client = Mock()
        mock_telemetry.return_value = mock_client
        
        callback = AzureInsightsCallback(
            instrumentation_key="test-key",
            tenant_id="test-tenant",
            user_id="test-user"
        )
        
        callback.on_tool_end("output")
        
        mock_client.track_event.assert_called_once()
        call_args = mock_client.track_event.call_args
        assert call_args[0][0] == "langchain_tool_call"
    
    @patch('monitoring.langchain_callbacks.TelemetryClient')
    def test_on_agent_finish(self, mock_telemetry):
        """Test agent finish tracking to Azure"""
        mock_client = Mock()
        mock_telemetry.return_value = mock_client
        
        callback = AzureInsightsCallback(
            instrumentation_key="test-key",
            tenant_id="test-tenant",
            user_id="test-user"
        )
        
        finish = AgentFinish(return_values={"output": "result"}, log="log")
        callback.on_agent_finish(finish)
        
        mock_client.track_event.assert_called_once()
        call_args = mock_client.track_event.call_args
        assert call_args[0][0] == "langchain_agent_complete"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
