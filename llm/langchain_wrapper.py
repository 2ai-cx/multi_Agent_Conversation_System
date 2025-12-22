"""
LangChain wrapper for custom LLM client.
Allows using our custom client (with rate limiting, caching, multi-tenant) through LangChain interface.
"""

from typing import Any, List, Optional, Dict
from langchain_core.language_models.llms import LLM
from langchain_core.callbacks.manager import CallbackManagerForLLMRun
from llm.client import LLMClient
from llm.config import LLMConfig
import logging

logger = logging.getLogger(__name__)


class CustomLangChainLLM(LLM):
    """
    Wrap our custom LLM client as a LangChain LLM.
    
    This preserves all custom features:
    - Rate limiting
    - Response caching
    - Multi-tenant API key management
    - JSON minification
    
    While enabling LangChain features:
    - Callbacks and monitoring
    - Chain composition
    - Agent integration
    """
    
    custom_client: Any = None
    tenant_id: Optional[str] = None
    
    model_config = {"arbitrary_types_allowed": True}
    
    def __init__(self, config: Optional[LLMConfig] = None, tenant_id: Optional[str] = None, **kwargs):
        """Initialize with optional config and tenant_id"""
        if config is None:
            config = LLMConfig()
        custom_client = LLMClient(config)
        super().__init__(custom_client=custom_client, tenant_id=tenant_id, **kwargs)
    
    @property
    def _llm_type(self) -> str:
        """Return identifier for this LLM type"""
        return "custom_openrouter"
    
    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        """
        Synchronous call to LLM.
        Uses our custom client which handles rate limiting, caching, etc.
        """
        try:
            # Extract tenant_id from kwargs if provided
            tenant_id = kwargs.pop("tenant_id", self.tenant_id)
            
            # Use our custom client
            response = self.custom_client.generate(
                prompt=prompt,
                tenant_id=tenant_id,
                **kwargs
            )
            
            # Log via callback manager if available
            if run_manager:
                run_manager.on_llm_end(response)
            
            return response
            
        except Exception as e:
            logger.error(f"LangChain LLM call failed: {e}")
            if run_manager:
                run_manager.on_llm_error(e)
            raise
    
    async def _acall(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        """
        Async call to LLM.
        Uses our custom client's async method.
        """
        try:
            # Extract tenant_id from kwargs if provided
            tenant_id = kwargs.pop("tenant_id", self.tenant_id)
            
            # Use our custom client's async method
            response = await self.custom_client.generate_async(
                prompt=prompt,
                tenant_id=tenant_id,
                **kwargs
            )
            
            # Log via callback manager if available
            if run_manager:
                run_manager.on_llm_end(response)
            
            return response
            
        except Exception as e:
            logger.error(f"LangChain async LLM call failed: {e}")
            if run_manager:
                run_manager.on_llm_error(e)
            raise
    
    @property
    def _identifying_params(self) -> Dict[str, Any]:
        """Return identifying parameters for this LLM"""
        return {
            "llm_type": self._llm_type,
            "tenant_id": self.tenant_id,
            "model": self.custom_client.config.model,
        }
