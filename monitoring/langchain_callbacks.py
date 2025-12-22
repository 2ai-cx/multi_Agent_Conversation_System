"""
LangChain callbacks for monitoring and observability.
Tracks LLM calls, tool usage, agent actions, and performance metrics.
"""

from typing import Any, Dict, List, Optional
from langchain_core.callbacks.base import BaseCallbackHandler
from langchain_core.agents import AgentAction, AgentFinish
from langchain_core.outputs import LLMResult
import logging
import time
from datetime import datetime

logger = logging.getLogger(__name__)


class ProductionCallbackHandler(BaseCallbackHandler):
    """
    Production-ready callback handler for LangChain.
    
    Tracks:
    - LLM calls and token usage
    - Tool invocations
    - Agent actions and decisions
    - Execution times
    - Errors and failures
    """
    
    def __init__(self, tenant_id: Optional[str] = None, user_id: Optional[str] = None):
        super().__init__()
        self.tenant_id = tenant_id
        self.user_id = user_id
        self.start_times: Dict[str, float] = {}
        self.metrics: Dict[str, Any] = {
            "llm_calls": 0,
            "tool_calls": 0,
            "total_tokens": 0,
            "errors": 0,
        }
    
    def on_llm_start(
        self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any
    ) -> None:
        """Called when LLM starts running"""
        run_id = kwargs.get("run_id", "unknown")
        self.start_times[f"llm_{run_id}"] = time.time()
        
        logger.info(f"🤖 LLM started: {len(prompts)} prompt(s)")
        logger.debug(f"Tenant: {self.tenant_id}, User: {self.user_id}")
        
        self.metrics["llm_calls"] += 1
    
    def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        """Called when LLM ends running"""
        run_id = kwargs.get("run_id", "unknown")
        start_time = self.start_times.pop(f"llm_{run_id}", time.time())
        duration_ms = (time.time() - start_time) * 1000
        
        # Extract token usage if available
        tokens = 0
        if response.llm_output:
            token_usage = response.llm_output.get("token_usage", {})
            tokens = token_usage.get("total_tokens", 0)
            self.metrics["total_tokens"] += tokens
        
        logger.info(f"✅ LLM finished: {duration_ms:.0f}ms, {tokens} tokens")
        
        # Track metrics (could send to Azure Application Insights here)
        self._track_metric("llm_duration_ms", duration_ms)
        self._track_metric("llm_tokens", tokens)
    
    def on_llm_error(self, error: Exception, **kwargs: Any) -> None:
        """Called when LLM errors"""
        run_id = kwargs.get("run_id", "unknown")
        self.start_times.pop(f"llm_{run_id}", None)
        
        logger.error(f"❌ LLM error: {error}")
        self.metrics["errors"] += 1
        
        self._track_metric("llm_error", 1)
    
    def on_tool_start(
        self, serialized: Dict[str, Any], input_str: str, **kwargs: Any
    ) -> None:
        """Called when tool starts running"""
        run_id = kwargs.get("run_id", "unknown")
        tool_name = serialized.get("name", "unknown_tool")
        
        self.start_times[f"tool_{run_id}"] = time.time()
        
        logger.info(f"🔧 Tool started: {tool_name}")
        logger.debug(f"Input: {input_str[:100]}...")
        
        self.metrics["tool_calls"] += 1
    
    def on_tool_end(self, output: str, **kwargs: Any) -> None:
        """Called when tool ends running"""
        run_id = kwargs.get("run_id", "unknown")
        start_time = self.start_times.pop(f"tool_{run_id}", time.time())
        duration_ms = (time.time() - start_time) * 1000
        
        logger.info(f"✅ Tool finished: {duration_ms:.0f}ms")
        logger.debug(f"Output: {output[:100]}...")
        
        self._track_metric("tool_duration_ms", duration_ms)
    
    def on_tool_error(self, error: Exception, **kwargs: Any) -> None:
        """Called when tool errors"""
        run_id = kwargs.get("run_id", "unknown")
        self.start_times.pop(f"tool_{run_id}", None)
        
        logger.error(f"❌ Tool error: {error}")
        self.metrics["errors"] += 1
        
        self._track_metric("tool_error", 1)
    
    def on_agent_action(self, action: AgentAction, **kwargs: Any) -> None:
        """Called when agent takes an action"""
        logger.info(f"🎯 Agent action: {action.tool}")
        logger.debug(f"Tool input: {action.tool_input}")
        logger.debug(f"Log: {action.log}")
    
    def on_agent_finish(self, finish: AgentFinish, **kwargs: Any) -> None:
        """Called when agent finishes"""
        logger.info(f"🏁 Agent finished")
        logger.debug(f"Output: {finish.return_values}")
        logger.debug(f"Log: {finish.log}")
    
    def on_chain_start(
        self, serialized: Dict[str, Any], inputs: Dict[str, Any], **kwargs: Any
    ) -> None:
        """Called when chain starts running"""
        run_id = kwargs.get("run_id", "unknown")
        chain_type = serialized.get("name", "unknown_chain")
        
        self.start_times[f"chain_{run_id}"] = time.time()
        
        logger.info(f"⛓️  Chain started: {chain_type}")
    
    def on_chain_end(self, outputs: Dict[str, Any], **kwargs: Any) -> None:
        """Called when chain ends running"""
        run_id = kwargs.get("run_id", "unknown")
        start_time = self.start_times.pop(f"chain_{run_id}", time.time())
        duration_ms = (time.time() - start_time) * 1000
        
        logger.info(f"✅ Chain finished: {duration_ms:.0f}ms")
        
        self._track_metric("chain_duration_ms", duration_ms)
    
    def on_chain_error(self, error: Exception, **kwargs: Any) -> None:
        """Called when chain errors"""
        run_id = kwargs.get("run_id", "unknown")
        self.start_times.pop(f"chain_{run_id}", None)
        
        logger.error(f"❌ Chain error: {error}")
        self.metrics["errors"] += 1
        
        self._track_metric("chain_error", 1)
    
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


class AzureInsightsCallback(BaseCallbackHandler):
    """
    Callback handler that sends metrics to Azure Application Insights.
    Requires applicationinsights package.
    """
    
    def __init__(
        self,
        instrumentation_key: Optional[str] = None,
        tenant_id: Optional[str] = None,
        user_id: Optional[str] = None
    ):
        super().__init__()
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
    
    def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        """Track LLM call to Azure"""
        if not self.telemetry_client:
            return
        
        tokens = 0
        if response.llm_output:
            token_usage = response.llm_output.get("token_usage", {})
            tokens = token_usage.get("total_tokens", 0)
        
        self.telemetry_client.track_event(
            "langchain_llm_call",
            properties={
                "tenant_id": self.tenant_id,
                "user_id": self.user_id,
                "framework": "langchain"
            },
            measurements={
                "tokens": tokens
            }
        )
    
    def on_tool_end(self, output: str, **kwargs: Any) -> None:
        """Track tool call to Azure"""
        if not self.telemetry_client:
            return
        
        self.telemetry_client.track_event(
            "langchain_tool_call",
            properties={
                "tenant_id": self.tenant_id,
                "user_id": self.user_id,
                "framework": "langchain"
            }
        )
    
    def on_agent_finish(self, finish: AgentFinish, **kwargs: Any) -> None:
        """Track agent completion to Azure"""
        if not self.telemetry_client:
            return
        
        self.telemetry_client.track_event(
            "langchain_agent_complete",
            properties={
                "tenant_id": self.tenant_id,
                "user_id": self.user_id,
                "framework": "langchain"
            }
        )
