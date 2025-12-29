"""
Opik Tracker

Automatic observability for all LLM calls using Opik SDK
"""

import logging
from typing import List, Dict, Optional, Any
from datetime import datetime

from llm.config import LLMConfig
from llm.client import LLMResponse

logger = logging.getLogger(__name__)


class OpikTracker:
    """
    Opik integration for LLM observability
    
    Tracks:
    - Tokens (prompt, completion, total)
    - Latency
    - Cost
    - Model
    - Tenant/User attribution
    - Input/Output messages
    - Metadata (cached, errors, etc.)
    """
    
    def __init__(self, config: LLMConfig):
        """
        Initialize Opik tracker
        
        Args:
            config: LLM configuration
        """
        self.config = config
        self._opik_client = None
        self._initialized = False
        
        logger.info(
            f"Opik tracker initialized: "
            f"enabled={config.opik_enabled}, "
            f"project={config.opik_project_name}"
        )
    
    @property
    def opik_client(self):
        """Lazy load and configure Opik client"""
        if not self._initialized:
            self._initialized = True
            
            if not self.config.opik_enabled:
                logger.info("Opik tracking disabled")
                return None
            
            try:
                import opik
                from opik import Opik
                
                # Initialize Opik client with optional parameters
                init_params = {
                    "project_name": self.config.opik_project_name
                }
                
                # Add optional parameters if provided
                if self.config.opik_api_key:
                    init_params["api_key"] = self.config.opik_api_key
                
                if self.config.opik_workspace:
                    init_params["workspace"] = self.config.opik_workspace
                
                self._opik_client = Opik(**init_params)
                
                logger.info(
                    f"Opik client initialized - "
                    f"project: {self.config.opik_project_name}, "
                    f"workspace: {self.config.opik_workspace or 'default'}"
                )
            
            except ImportError:
                logger.warning(
                    "Opik package not installed. Tracking disabled. "
                    "Install with: pip install opik"
                )
                self._opik_client = None
            
            except Exception as e:
                logger.error(f"Failed to initialize Opik client: {e}")
                self._opik_client = None
        
        return self._opik_client
    
    async def log_completion(
        self,
        messages: List[Dict[str, str]],
        response: LLMResponse,
        tenant_id: Optional[str] = None,
        user_id: Optional[str] = None,
        cached: bool = False,
        error: Optional[str] = None
    ):
        """
        Log LLM completion to Opik
        
        Args:
            messages: Input messages
            response: LLM response
            tenant_id: Tenant ID
            user_id: User ID
            cached: Whether response was cached
            error: Error message if failed
        """
        if not self.opik_client:
            # Opik disabled or not available - log locally
            self._log_locally(messages, response, tenant_id, user_id, cached, error)
            return
        
        try:
            # Prepare trace data
            trace_data = self._prepare_trace_data(
                messages, response, tenant_id, user_id, cached, error
            )
            
            # Log to Opik
            self.opik_client.log_traces([trace_data])
            
            logger.debug(
                f"Logged to Opik: model={response.model}, "
                f"tokens={response.total_tokens}, "
                f"tenant={tenant_id}"
            )
        
        except Exception as e:
            logger.error(f"Failed to log to Opik: {e}")
            # Fallback to local logging
            self._log_locally(messages, response, tenant_id, user_id, cached, error)
    
    def _prepare_trace_data(
        self,
        messages: List[Dict[str, str]],
        response: LLMResponse,
        tenant_id: Optional[str],
        user_id: Optional[str],
        cached: bool,
        error: Optional[str]
    ) -> Dict[str, Any]:
        """
        Prepare trace data for Opik
        
        Args:
            messages: Input messages
            response: LLM response
            tenant_id: Tenant ID
            user_id: User ID
            cached: Whether cached
            error: Error message
        
        Returns:
            Trace data dictionary
        """
        # Extract input and output
        input_text = self._format_messages(messages)
        output_text = response.content if response else ""
        
        # Prepare metadata
        metadata = {
            "model": response.model if response else "unknown",
            "cached": cached,
            "tenant_id": tenant_id,
            "user_id": user_id,
            "timestamp": datetime.now().isoformat()
        }
        
        if response:
            metadata.update({
                "prompt_tokens": response.prompt_tokens,
                "completion_tokens": response.completion_tokens,
                "total_tokens": response.total_tokens,
                "latency_ms": response.latency_ms,
                "cost_usd": response.cost_usd
            })
        
        if error:
            metadata["error"] = error
            metadata["status"] = "error"
        else:
            metadata["status"] = "success"
        
        # Add response metadata
        if response and response.metadata:
            metadata.update(response.metadata)
        
        # Create trace data
        trace_data = {
            "name": "llm_completion",
            "input": {"messages": messages},
            "output": {"content": output_text},
            "metadata": metadata,
            "tags": self._generate_tags(tenant_id, user_id, cached, error)
        }
        
        return trace_data
    
    def _format_messages(self, messages: List[Dict[str, str]]) -> str:
        """
        Format messages for display
        
        Args:
            messages: List of messages
        
        Returns:
            Formatted string
        """
        formatted = []
        for msg in messages:
            role = msg.get("role", "unknown")
            content = msg.get("content", "")
            formatted.append(f"{role}: {content}")
        return "\n".join(formatted)
    
    def _generate_tags(
        self,
        tenant_id: Optional[str],
        user_id: Optional[str],
        cached: bool,
        error: Optional[str]
    ) -> List[str]:
        """
        Generate tags for trace
        
        Args:
            tenant_id: Tenant ID
            user_id: User ID
            cached: Whether cached
            error: Error message
        
        Returns:
            List of tags
        """
        tags = ["llm", "chat_completion"]
        
        if tenant_id:
            tags.append(f"tenant:{tenant_id}")
        
        if user_id:
            tags.append(f"user:{user_id}")
        
        if cached:
            tags.append("cached")
        
        if error:
            tags.append("error")
        else:
            tags.append("success")
        
        return tags
    
    def _log_locally(
        self,
        messages: List[Dict[str, str]],
        response: Optional[LLMResponse],
        tenant_id: Optional[str],
        user_id: Optional[str],
        cached: bool,
        error: Optional[str]
    ):
        """
        Log to local logger when Opik unavailable
        
        Args:
            messages: Input messages
            response: LLM response
            tenant_id: Tenant ID
            user_id: User ID
            cached: Whether cached
            error: Error message
        """
        if error:
            logger.error(
                f"LLM call failed: error={error}, "
                f"tenant={tenant_id}, user={user_id}"
            )
        elif response:
            logger.info(
                f"LLM call: model={response.model}, "
                f"tokens={response.total_tokens}, "
                f"cost=${response.cost_usd:.4f}, "
                f"latency={response.latency_ms:.0f}ms, "
                f"cached={cached}, "
                f"tenant={tenant_id}, "
                f"user={user_id}"
            )
        else:
            logger.warning("LLM call with no response or error")
    
    async def log_error(
        self,
        messages: List[Dict[str, str]],
        error: Exception,
        tenant_id: Optional[str] = None,
        user_id: Optional[str] = None
    ):
        """
        Log LLM error to Opik
        
        Args:
            messages: Input messages
            error: Exception that occurred
            tenant_id: Tenant ID
            user_id: User ID
        """
        # Create empty response for error case
        error_response = LLMResponse(
            content="",
            model="unknown",
            prompt_tokens=0,
            completion_tokens=0,
            total_tokens=0,
            latency_ms=0.0,
            cost_usd=0.0,
            cached=False,
            metadata={"error": str(error)}
        )
        
        await self.log_completion(
            messages=messages,
            response=error_response,
            tenant_id=tenant_id,
            user_id=user_id,
            cached=False,
            error=str(error)
        )
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get Opik tracking statistics
        
        Returns:
            Dictionary with stats
        """
        return {
            "enabled": self.config.opik_enabled,
            "project": self.config.opik_project_name,
            "client_initialized": self._opik_client is not None
        }
