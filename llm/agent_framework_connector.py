"""
Microsoft Agent Framework connector for custom LLM client.
Allows using our custom client (with rate limiting, caching, multi-tenant) with Agent Framework.
"""

from typing import Any, Dict, List, Optional, AsyncIterator
from agent_framework import BaseChatClient, ChatMessage, ChatResponse, ChatContext
from llm.client import LLMClient
from llm.config import LLMConfig
import logging

logger = logging.getLogger(__name__)


class CustomAgentFrameworkLLM(BaseChatClient):
    """
    Wrap our custom LLM client as an Agent Framework ModelClient.
    
    This preserves all custom features:
    - Rate limiting
    - Response caching
    - Multi-tenant API key management
    - JSON minification
    
    While enabling Agent Framework features:
    - Agent orchestration
    - Workflow integration
    - MCP tool support
    - State management
    """
    
    def __init__(
        self,
        config: Optional[LLMConfig] = None,
        tenant_id: Optional[str] = None,
        **kwargs
    ):
        """Initialize with optional config and tenant_id"""
        super().__init__(**kwargs)
        if config is None:
            config = LLMConfig()
        self.custom_client = LLMClient(config)
        self.tenant_id = tenant_id
        self.config = config
    
    async def create(
        self,
        messages: List[ChatMessage],
        context: ChatContext,
        **kwargs
    ) -> ChatResponse:
        """
        Create chat response using custom LLM client.
        
        Args:
            messages: List of chat messages
            context: Chat context
            **kwargs: Additional arguments
            
        Returns:
            ChatResponse object
        """
        try:
            # Convert Agent Framework messages to our format
            formatted_messages = []
            for msg in messages:
                formatted_messages.append({
                    "role": msg.role,
                    "content": msg.content
                })
            
            # Use custom client to generate
            response_text = await self.custom_client.generate_async(
                messages=formatted_messages,
                tenant_id=kwargs.get("tenant_id", self.tenant_id),
                temperature=self.config.temperature
            )
            
            # Convert response to Agent Framework format
            from agent_framework import TextContent
            response = ChatResponse(
                messages=[
                    ChatMessage(
                        role="assistant",
                        content=[TextContent(text=response_text)]
                    )
                ]
            )
            
            logger.info(f"✅ Agent Framework chat completion successful")
            return response
            
        except Exception as e:
            logger.error(f"❌ Agent Framework chat error: {e}")
            raise
    
    async def create_stream(
        self,
        messages: List[ChatMessage],
        context: ChatContext,
        **kwargs
    ) -> AsyncIterator[ChatResponse]:
        """
        Create streaming chat response.
        
        Note: Custom client doesn't support streaming yet,
        so this returns a single response.
        """
        response = await self.create(
            messages=messages,
            context=context,
            **kwargs
        )
        yield response
    
    @property
    def model_info(self) -> Dict[str, Any]:
        """Return model information"""
        return {
            "model": self.config.model,
            "tenant_id": self.tenant_id,
            "provider": "custom_openrouter"
        }
