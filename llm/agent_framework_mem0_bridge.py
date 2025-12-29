"""
Bridge between Mem0 and Microsoft Agent Framework.
Allows using Mem0's self-improving memory with Agent Framework's context providers.
"""

from typing import Any, Dict, List, Optional
from agent_framework import ContextProvider
from llm.memory import LLMMemoryManager
import logging

logger = logging.getLogger(__name__)


class Mem0AgentFrameworkContext(ContextProvider):
    """
    Bridge Mem0 to Agent Framework context provider interface.
    
    This allows using Mem0's features:
    - Self-improving memory
    - Qdrant vector storage
    - Semantic search
    
    Through Agent Framework's context system for agents.
    """
    
    def __init__(
        self,
        mem0_manager: LLMMemoryManager,
        tenant_id: str,
        user_id: str,
        k: int = 10
    ):
        """
        Initialize with Mem0 manager and user context.
        
        Args:
            mem0_manager: LLM memory manager instance
            tenant_id: Tenant identifier
            user_id: User identifier
            k: Number of memories to retrieve
        """
        super().__init__()
        self.mem0_manager = mem0_manager
        self.tenant_id = tenant_id
        self.user_id = user_id
        self.k = k
    
    async def get_context(
        self,
        context: Any,
        query: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get context from Mem0 for the agent.
        
        Args:
            agent_context: Current agent context
            query: Optional query for retrieval
            
        Returns:
            Dictionary with retrieved context
        """
        try:
            # Use query from context if not provided
            if query is None and hasattr(context, 'messages') and context.messages:
                # Get last user message as query
                for msg in reversed(context.messages):
                    if hasattr(msg, 'role') and msg.role == "user":
                        query = msg.content if hasattr(msg, 'content') else ""
                        break
            
            if not query:
                logger.debug("No query available for context retrieval")
                return {"memories": [], "context": ""}
            
            # Retrieve context from Mem0
            memories = self.mem0_manager.retrieve_context(
                query=query,
                tenant_id=self.tenant_id,
                user_id=self.user_id,
                k=self.k
            )
            
            # Format context for agent
            context_text = "\n".join(memories) if memories else ""
            
            logger.info(f"📚 Retrieved {len(memories)} memories from Mem0")
            
            return {
                "memories": memories,
                "context": context_text,
                "tenant_id": self.tenant_id,
                "user_id": self.user_id
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to retrieve Mem0 context: {e}")
            return {"memories": [], "context": ""}
    
    async def save_context(
        self,
        context: Any,
        user_message: str,
        agent_response: str
    ) -> None:
        """
        Save conversation to Mem0.
        
        Args:
            agent_context: Current agent context
            user_message: User's message
            agent_response: Agent's response
        """
        try:
            self.mem0_manager.add_conversation(
                user_message=user_message,
                ai_response=agent_response,
                tenant_id=self.tenant_id,
                user_id=self.user_id
            )
            
            logger.info(f"💾 Saved conversation to Mem0")
            
        except Exception as e:
            logger.error(f"❌ Failed to save to Mem0: {e}")


class Mem0AgentFrameworkMemory:
    """
    Simple wrapper for Mem0 that can be used with Agent Framework agents.
    Provides easy access to memory operations.
    """
    
    def __init__(
        self,
        mem0_manager: LLMMemoryManager,
        tenant_id: str,
        user_id: str,
        k: int = 10
    ):
        """Initialize Mem0 memory wrapper"""
        self.mem0_manager = mem0_manager
        self.tenant_id = tenant_id
        self.user_id = user_id
        self.k = k
    
    def retrieve(self, query: str) -> List[str]:
        """
        Retrieve memories for a query.
        
        Args:
            query: Search query
            
        Returns:
            List of retrieved memory strings
        """
        try:
            return self.mem0_manager.retrieve_context(
                query=query,
                tenant_id=self.tenant_id,
                user_id=self.user_id,
                k=self.k
            )
        except Exception as e:
            logger.error(f"❌ Memory retrieval failed: {e}")
            return []
    
    def add(self, user_message: str, ai_response: str) -> None:
        """
        Add conversation to memory.
        
        Args:
            user_message: User's message
            ai_response: AI's response
        """
        try:
            self.mem0_manager.add_conversation(
                user_message=user_message,
                ai_response=ai_response,
                tenant_id=self.tenant_id,
                user_id=self.user_id
            )
        except Exception as e:
            logger.error(f"❌ Memory save failed: {e}")
    
    def search(self, query: str, k: Optional[int] = None) -> List[str]:
        """
        Search memories.
        
        Args:
            query: Search query
            k: Number of results (optional, uses default)
            
        Returns:
            List of relevant memories
        """
        return self.retrieve(query) if k is None else self.mem0_manager.retrieve_context(
            query=query,
            tenant_id=self.tenant_id,
            user_id=self.user_id,
            k=k
        )
