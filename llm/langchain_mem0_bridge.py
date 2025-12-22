"""
Bridge between Mem0 and LangChain memory interface.
Allows using Mem0's self-improving memory through LangChain's memory abstraction.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, ConfigDict
from llm.memory import LLMMemoryManager
import logging

logger = logging.getLogger(__name__)


class Mem0LangChainMemory(BaseModel):
    """
    Bridge Mem0 to LangChain memory interface.
    
    This allows using Mem0's features:
    - Self-improving memory
    - Qdrant vector storage
    - Semantic search
    
    Through LangChain's memory interface for agents and chains.
    """
    
    mem0_manager: Any
    tenant_id: str
    user_id: str
    memory_key: str = "context"
    chat_history_key: str = "chat_history"
    k: int = 10
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    def __init__(
        self,
        mem0_manager: LLMMemoryManager,
        tenant_id: str,
        user_id: str,
        memory_key: str = "context",
        chat_history_key: str = "chat_history",
        k: int = 10
    ):
        """Initialize with Mem0 manager and user context"""
        super().__init__(
            mem0_manager=mem0_manager,
            tenant_id=tenant_id,
            user_id=user_id,
            memory_key=memory_key,
            chat_history_key=chat_history_key,
            k=k
        )
    
    @property
    def memory_variables(self) -> List[str]:
        """Return memory variables that this memory class provides"""
        return [self.memory_key, self.chat_history_key]
    
    def load_memory_variables(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Load memory variables from Mem0.
        
        Args:
            inputs: Input variables (should contain the query/input)
        
        Returns:
            Dictionary with context and chat_history
        """
        try:
            # Get the query from inputs
            query = inputs.get("input", inputs.get("question", ""))
            
            if not query:
                logger.warning("No query found in inputs for memory retrieval")
                return {
                    self.memory_key: "",
                    self.chat_history_key: []
                }
            
            # Retrieve context from Mem0
            logger.info(f"Retrieving Mem0 context for query: {query[:100]}...")
            context = self.mem0_manager.retrieve_context(
                query=query,
                tenant_id=self.tenant_id,
                user_id=self.user_id,
                k=self.k
            )
            
            # Format context as string
            context_str = "\n".join([
                f"- {item}" for item in context
            ]) if context else ""
            
            logger.info(f"Retrieved {len(context)} memory items from Mem0")
            
            return {
                self.memory_key: context_str,
                self.chat_history_key: []  # Mem0 handles history internally
            }
            
        except Exception as e:
            logger.error(f"Failed to load Mem0 memory: {e}")
            return {
                self.memory_key: "",
                self.chat_history_key: []
            }
    
    def save_context(self, inputs: Dict[str, Any], outputs: Dict[str, str]) -> None:
        """
        Save conversation context to Mem0.
        
        Args:
            inputs: Input variables (user message)
            outputs: Output variables (AI response)
        """
        try:
            # Extract user message and AI response
            user_message = inputs.get("input", inputs.get("question", ""))
            ai_response = outputs.get("output", outputs.get("answer", ""))
            
            if not user_message or not ai_response:
                logger.warning("Missing user message or AI response, skipping save")
                return
            
            # Store in Mem0
            logger.info(f"Storing conversation in Mem0: {user_message[:50]}...")
            self.mem0_manager.add_conversation(
                user_message=user_message,
                ai_response=ai_response,
                tenant_id=self.tenant_id,
                user_id=self.user_id
            )
            
            logger.info("Conversation stored successfully in Mem0")
            
        except Exception as e:
            logger.error(f"Failed to save context to Mem0: {e}")
    
    def clear(self) -> None:
        """
        Clear memory (not implemented for Mem0).
        Mem0 manages its own memory lifecycle.
        """
        logger.warning("Clear not implemented for Mem0 - memory managed by Mem0 lifecycle")
        pass


class Mem0VectorStoreRetriever:
    """
    Alternative: Use Mem0 as a retriever for LangChain chains.
    This is useful for RAG chains that expect a retriever interface.
    """
    
    def __init__(
        self,
        mem0_manager: LLMMemoryManager,
        tenant_id: str,
        user_id: str,
        k: int = 10
    ):
        self.mem0_manager = mem0_manager
        self.tenant_id = tenant_id
        self.user_id = user_id
        self.k = k
    
    def get_relevant_documents(self, query: str) -> List[Dict[str, Any]]:
        """
        Retrieve relevant documents from Mem0.
        Compatible with LangChain retriever interface.
        """
        try:
            context = self.mem0_manager.retrieve_context(
                query=query,
                tenant_id=self.tenant_id,
                user_id=self.user_id,
                k=self.k
            )
            
            # Convert to LangChain document format
            documents = [
                {"page_content": item, "metadata": {"source": "mem0"}}
                for item in context
            ]
            
            return documents
            
        except Exception as e:
            logger.error(f"Failed to retrieve documents from Mem0: {e}")
            return []
    
    async def aget_relevant_documents(self, query: str) -> List[Dict[str, Any]]:
        """Async version of get_relevant_documents"""
        return self.get_relevant_documents(query)
