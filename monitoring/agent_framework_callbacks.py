"""
Microsoft Agent Framework middleware for monitoring and observability.
Tracks agent actions, tool usage, and performance metrics.
"""

from typing import Any, Dict, List, Optional
from agent_framework import Middleware
import logging
import time
from datetime import datetime

logger = logging.getLogger(__name__)


class ProductionMiddleware:
    """
    Production-ready middleware for Agent Framework.
    
    Tracks:
    - Agent invocations
    - Tool calls
    - Execution times
    - Errors and failures
    """
    
    def __init__(self, tenant_id: Optional[str] = None, user_id: Optional[str] = None):
        self.tenant_id = tenant_id
        self.user_id = user_id
        self.start_times: Dict[str, float] = {}
        self.metrics: Dict[str, Any] = {
            "agent_calls": 0,
            "tool_calls": 0,
            "total_tokens": 0,
            "errors": 0,
        }
    
    async def on_agent_start(self, context: Any) -> None:
        """Called when agent starts running"""
        run_id = id(context)
        self.start_times[f"agent_{run_id}"] = time.time()
        
        logger.info(f"🤖 Agent started")
        logger.debug(f"Tenant: {self.tenant_id}, User: {self.user_id}")
        
        self.metrics["agent_calls"] += 1
    
    async def on_agent_end(self, context: AgentContext, result: Any) -> None:
        """Called when agent ends running"""
        run_id = id(context)
        start_time = self.start_times.pop(f"agent_{run_id}", time.time())
        duration_ms = (time.time() - start_time) * 1000
        
        logger.info(f"✅ Agent finished: {duration_ms:.0f}ms")
        
        self._track_metric("agent_duration_ms", duration_ms)
    
    async def on_agent_error(self, context: Any, error: Exception) -> None:
        """Called when agent errors"""
        run_id = id(context)
        self.start_times.pop(f"agent_{run_id}", None)
        
        logger.error(f"❌ Agent error: {error}")
        self.metrics["errors"] += 1
        
        self._track_metric("agent_error", 1)
    
    async def on_tool_start(self, context: Any, tool_call: Any) -> None:
        """Called when tool starts running"""
        run_id = id(tool_call)
        tool_name = tool_call.function.name
        
        self.start_times[f"tool_{run_id}"] = time.time()
        
        logger.info(f"🔧 Tool started: {tool_name}")
        logger.debug(f"Arguments: {tool_call.function.arguments}")
        
        self.metrics["tool_calls"] += 1
    
    async def on_tool_end(self, context: AgentContext, tool_call: ToolCall, result: Any) -> None:
        """Called when tool ends running"""
        run_id = id(tool_call)
        start_time = self.start_times.pop(f"tool_{run_id}", time.time())
        duration_ms = (time.time() - start_time) * 1000
        
        logger.info(f"✅ Tool finished: {duration_ms:.0f}ms")
        logger.debug(f"Result: {str(result)[:100]}...")
        
        self._track_metric("tool_duration_ms", duration_ms)
    
    async def on_tool_error(self, context: Any, tool_call: Any, error: Exception) -> None:
        """Called when tool errors"""
        run_id = id(tool_call)
        self.start_times.pop(f"tool_{run_id}", None)
        
        logger.error(f"❌ Tool error: {error}")
        self.metrics["errors"] += 1
        
        self._track_metric("tool_error", 1)
    
    async def on_message(self, context: Any, message: Any) -> None:
        """Called when a message is processed"""
        logger.debug(f"💬 Message: {message.role} - {message.content[:50]}...")
    
    def _track_metric(self, metric_name: str, value: float) -> None:
        """
        Track metric to monitoring system.
        In production, this would send to Azure Application Insights.
        """
        logger.debug(f"📊 Metric: {metric_name} = {value}")
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get collected metrics"""
        return {
            **self.metrics,
            "tenant_id": self.tenant_id,
            "user_id": self.user_id,
            "timestamp": datetime.now().isoformat()
        }


class AzureInsightsMiddleware:
    """
    Middleware that sends metrics to Azure Application Insights.
    """
    
    def __init__(
        self,
        instrumentation_key: Optional[str] = None,
        tenant_id: Optional[str] = None,
        user_id: Optional[str] = None
    ):
        pass
        self.tenant_id = tenant_id
        self.user_id = user_id
        self.telemetry_client = None
        
        if instrumentation_key:
            try:
                from applicationinsights import TelemetryClient
                self.telemetry_client = TelemetryClient(instrumentation_key)
                logger.info("Azure Application Insights enabled")
            except ImportError:
                logger.warning("applicationinsights package not installed, metrics will only be logged")
    
    async def on_agent_end(self, context: AgentContext, result: Any) -> None:
        """Track agent completion to Azure"""
        if not self.telemetry_client:
            return
        
        self.telemetry_client.track_event(
            "agent_framework_agent_call",
            properties={
                "tenant_id": self.tenant_id,
                "user_id": self.user_id,
                "framework": "agent_framework"
            }
        )
    
    async def on_tool_end(self, context: AgentContext, tool_call: ToolCall, result: Any) -> None:
        """Track tool call to Azure"""
        if not self.telemetry_client:
            return
        
        self.telemetry_client.track_event(
            "agent_framework_tool_call",
            properties={
                "tenant_id": self.tenant_id,
                "user_id": self.user_id,
                "framework": "agent_framework",
                "tool_name": tool_call.function.name
            }
        )


class PerformanceMonitor:
    """
    Standalone performance monitor for Agent Framework.
    Tracks execution metrics and provides reporting.
    """
    
    def __init__(self):
        self.metrics: Dict[str, List[float]] = {
            "agent_duration": [],
            "tool_duration": [],
            "total_calls": []
        }
    
    def record_agent_duration(self, duration_ms: float) -> None:
        """Record agent execution duration"""
        self.metrics["agent_duration"].append(duration_ms)
    
    def record_tool_duration(self, duration_ms: float) -> None:
        """Record tool execution duration"""
        self.metrics["tool_duration"].append(duration_ms)
    
    def get_summary(self) -> Dict[str, Any]:
        """Get performance summary"""
        import statistics
        
        summary = {}
        
        for metric_name, values in self.metrics.items():
            if values:
                summary[metric_name] = {
                    "count": len(values),
                    "mean": statistics.mean(values),
                    "median": statistics.median(values),
                    "min": min(values),
                    "max": max(values)
                }
            else:
                summary[metric_name] = {
                    "count": 0,
                    "mean": 0,
                    "median": 0,
                    "min": 0,
                    "max": 0
                }
        
        return summary
    
    def reset(self) -> None:
        """Reset all metrics"""
        for key in self.metrics:
            self.metrics[key] = []
