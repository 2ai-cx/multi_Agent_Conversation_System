"""
Unit tests for Agent Framework middleware.
Tests the monitoring and observability middleware.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from monitoring.agent_framework_callbacks import ProductionMiddleware, AzureInsightsMiddleware, PerformanceMonitor


class TestProductionMiddleware:
    """Test suite for ProductionMiddleware"""
    
    @pytest.fixture
    def middleware(self):
        """Create middleware instance"""
        return ProductionMiddleware(tenant_id="test-tenant", user_id="test-user")
    
    def test_initialization(self, middleware):
        """Test middleware initialization"""
        assert middleware.tenant_id == "test-tenant"
        assert middleware.user_id == "test-user"
        assert middleware.metrics["agent_calls"] == 0
        assert middleware.metrics["tool_calls"] == 0
        assert middleware.metrics["total_tokens"] == 0
        assert middleware.metrics["errors"] == 0
    
    @pytest.mark.asyncio
    async def test_on_agent_start(self, middleware):
        """Test agent start callback"""
        context = Mock()
        
        await middleware.on_agent_start(context)
        
        assert middleware.metrics["agent_calls"] == 1
        assert f"agent_{id(context)}" in middleware.start_times
    
    @pytest.mark.asyncio
    async def test_on_agent_end(self, middleware):
        """Test agent end callback"""
        context = Mock()
        middleware.start_times[f"agent_{id(context)}"] = 0
        
        await middleware.on_agent_end(context, result="test result")
        
        assert f"agent_{id(context)}" not in middleware.start_times
    
    @pytest.mark.asyncio
    async def test_on_agent_error(self, middleware):
        """Test agent error callback"""
        context = Mock()
        middleware.start_times[f"agent_{id(context)}"] = 0
        
        await middleware.on_agent_error(context, Exception("Test error"))
        
        assert middleware.metrics["errors"] == 1
        assert f"agent_{id(context)}" not in middleware.start_times
    
    @pytest.mark.asyncio
    async def test_on_tool_start(self, middleware):
        """Test tool start callback"""
        context = Mock()
        tool_call = Mock()
        tool_call.function = Mock(name="test_tool", arguments={})
        
        await middleware.on_tool_start(context, tool_call)
        
        assert middleware.metrics["tool_calls"] == 1
        assert f"tool_{id(tool_call)}" in middleware.start_times
    
    @pytest.mark.asyncio
    async def test_on_tool_end(self, middleware):
        """Test tool end callback"""
        context = Mock()
        tool_call = Mock()
        middleware.start_times[f"tool_{id(tool_call)}"] = 0
        
        await middleware.on_tool_end(context, tool_call, result="test result")
        
        assert f"tool_{id(tool_call)}" not in middleware.start_times
    
    @pytest.mark.asyncio
    async def test_on_tool_error(self, middleware):
        """Test tool error callback"""
        context = Mock()
        tool_call = Mock()
        middleware.start_times[f"tool_{id(tool_call)}"] = 0
        
        await middleware.on_tool_error(context, tool_call, Exception("Tool error"))
        
        assert middleware.metrics["errors"] == 1
        assert f"tool_{id(tool_call)}" not in middleware.start_times
    
    @pytest.mark.asyncio
    async def test_on_message(self, middleware):
        """Test message callback"""
        context = Mock()
        message = Mock(role="user", content="Test message")
        
        await middleware.on_message(context, message)
    
    def test_get_metrics(self, middleware):
        """Test getting metrics"""
        middleware.metrics["agent_calls"] = 5
        middleware.metrics["tool_calls"] = 3
        
        metrics = middleware.get_metrics()
        
        assert metrics["agent_calls"] == 5
        assert metrics["tool_calls"] == 3
        assert metrics["tenant_id"] == "test-tenant"
        assert metrics["user_id"] == "test-user"
        assert "timestamp" in metrics


class TestAzureInsightsMiddleware:
    """Test suite for AzureInsightsMiddleware"""
    
    def test_initialization_without_key(self):
        """Test initialization without instrumentation key"""
        middleware = AzureInsightsMiddleware(tenant_id="test-tenant", user_id="test-user")
        
        assert middleware.tenant_id == "test-tenant"
        assert middleware.user_id == "test-user"
        assert middleware.telemetry_client is None
    
    @pytest.mark.asyncio
    async def test_on_agent_end(self):
        """Test agent end tracking (without telemetry client)"""
        middleware = AzureInsightsMiddleware(
            instrumentation_key=None,
            tenant_id="test-tenant",
            user_id="test-user"
        )
        
        context = Mock()
        
        # Should not raise error when telemetry_client is None
        await middleware.on_agent_end(context, result="test")
    
    @pytest.mark.asyncio
    async def test_on_tool_end(self):
        """Test tool end tracking (without telemetry client)"""
        middleware = AzureInsightsMiddleware(
            instrumentation_key=None,
            tenant_id="test-tenant",
            user_id="test-user"
        )
        
        context = Mock()
        tool_call = Mock()
        tool_call.function = Mock(name="test_tool")
        
        # Should not raise error when telemetry_client is None
        await middleware.on_tool_end(context, tool_call, result="test")


class TestPerformanceMonitor:
    """Test suite for PerformanceMonitor"""
    
    @pytest.fixture
    def monitor(self):
        """Create performance monitor"""
        return PerformanceMonitor()
    
    def test_initialization(self, monitor):
        """Test monitor initialization"""
        assert "agent_duration" in monitor.metrics
        assert "tool_duration" in monitor.metrics
        assert len(monitor.metrics["agent_duration"]) == 0
    
    def test_record_agent_duration(self, monitor):
        """Test recording agent duration"""
        monitor.record_agent_duration(100.5)
        monitor.record_agent_duration(200.3)
        
        assert len(monitor.metrics["agent_duration"]) == 2
        assert monitor.metrics["agent_duration"][0] == 100.5
    
    def test_record_tool_duration(self, monitor):
        """Test recording tool duration"""
        monitor.record_tool_duration(50.2)
        
        assert len(monitor.metrics["tool_duration"]) == 1
        assert monitor.metrics["tool_duration"][0] == 50.2
    
    def test_get_summary(self, monitor):
        """Test getting performance summary"""
        monitor.record_agent_duration(100)
        monitor.record_agent_duration(200)
        monitor.record_agent_duration(300)
        
        summary = monitor.get_summary()
        
        assert summary["agent_duration"]["count"] == 3
        assert summary["agent_duration"]["mean"] == 200
        assert summary["agent_duration"]["median"] == 200
        assert summary["agent_duration"]["min"] == 100
        assert summary["agent_duration"]["max"] == 300
    
    def test_get_summary_empty(self, monitor):
        """Test summary with no data"""
        summary = monitor.get_summary()
        
        assert summary["agent_duration"]["count"] == 0
        assert summary["agent_duration"]["mean"] == 0
    
    def test_reset(self, monitor):
        """Test resetting metrics"""
        monitor.record_agent_duration(100)
        monitor.record_tool_duration(50)
        
        monitor.reset()
        
        assert len(monitor.metrics["agent_duration"]) == 0
        assert len(monitor.metrics["tool_duration"]) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
