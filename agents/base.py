"""
Base Agent Interface for Multi-Agent System

All agents inherit from BaseAgent and implement the execute method.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any
import logging
import time
from agents.models import AgentInteractionLog

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """
    Base class for all agents in the multi-agent system.
    
    All agents must:
    - Implement the execute() method for their specific functionality
    - Use the centralized LLM client for AI operations
    - Log all interactions using log_interaction()
    """
    
    def __init__(self, llm_client):
        """
        Initialize base agent.
        
        Args:
            llm_client: Centralized LLM client from llm/ module
        """
        self.llm_client = llm_client
        self.logger = logger
    
    @abstractmethod
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute agent action.
        
        Args:
            input_data: Agent-specific input parameters
            
        Returns:
            Agent-specific output data
            
        Raises:
            Exception: If agent execution fails
        """
        pass
    
    def log_interaction(
        self,
        request_id: str,
        action: str,
        input_data: Dict[str, Any],
        output_data: Dict[str, Any],
        duration_ms: int,
        success: bool,
        error: str = None
    ):
        """
        Log agent interaction for debugging and monitoring.
        
        Args:
            request_id: Unique request identifier
            action: Action performed by agent
            input_data: Input parameters (sanitized, no PII)
            output_data: Output data (sanitized, no PII)
            duration_ms: Execution time in milliseconds
            success: Whether agent call succeeded
            error: Error message if failed
        """
        # Sanitize input/output to remove PII
        sanitized_input = self._sanitize_data(input_data)
        sanitized_output = self._sanitize_data(output_data)
        
        # Create interaction log
        log = AgentInteractionLog(
            request_id=request_id,
            agent_name=self.__class__.__name__,
            action=action,
            input_data=sanitized_input,
            output_data=sanitized_output,
            duration_ms=duration_ms,
            success=success,
            error=error
        )
        
        # Log as structured JSON
        self.logger.info(f"Agent interaction: {log.json()}")
    
    def _sanitize_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitize data to remove PII before logging.
        
        Args:
            data: Data to sanitize
            
        Returns:
            Sanitized data with PII removed
        """
        if not isinstance(data, dict):
            return {}
        
        sanitized = {}
        pii_fields = {
            'phone_number', 'email', 'access_token', 'api_key',
            'password', 'secret', 'credential', 'ssn', 'address'
        }
        
        for key, value in data.items():
            # Check if key contains PII field names
            if any(pii in key.lower() for pii in pii_fields):
                sanitized[key] = "[REDACTED]"
            elif isinstance(value, dict):
                sanitized[key] = self._sanitize_data(value)
            elif isinstance(value, list):
                sanitized[key] = [
                    self._sanitize_data(item) if isinstance(item, dict) else item
                    for item in value
                ]
            else:
                sanitized[key] = value
        
        return sanitized
    
    async def _execute_with_logging(
        self,
        request_id: str,
        action: str,
        input_data: Dict[str, Any],
        func,
        *args,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Execute a function with automatic logging.
        
        Args:
            request_id: Unique request identifier
            action: Action being performed
            input_data: Input parameters for logging
            func: Function to execute
            *args: Positional arguments for func
            **kwargs: Keyword arguments for func
            
        Returns:
            Function output
            
        Raises:
            Exception: If function execution fails
        """
        start_time = time.time()
        
        try:
            result = await func(*args, **kwargs)
            duration_ms = int((time.time() - start_time) * 1000)
            
            self.log_interaction(
                request_id=request_id,
                action=action,
                input_data=input_data,
                output_data=result if isinstance(result, dict) else {"result": str(result)},
                duration_ms=duration_ms,
                success=True
            )
            
            return result
            
        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            
            self.log_interaction(
                request_id=request_id,
                action=action,
                input_data=input_data,
                output_data={},
                duration_ms=duration_ms,
                success=False,
                error=str(e)
            )
            
            raise
