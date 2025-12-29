"""
LLM Memory Manager using Mem0

Mem0 is a self-improving memory layer for LLMs with native Qdrant support.
Provides automatic memory management, deduplication, and semantic search.

Features:
- Multi-tenant isolation via user_id
- Automatic memory extraction and storage
- Semantic search and retrieval
- Memory updates and history
- Native Qdrant integration

Usage:
    from llm.memory_mem0 import LLMMemoryManager
    from llm.config import LLMConfig
    
    config = LLMConfig(rag_enabled=True)
    memory = LLMMemoryManager(tenant_id="tenant-123", config=config)
    
    # Store conversation (Mem0 auto-extracts memories)
    await memory.add_conversation(
        user_message="I worked 40 hours last week",
        ai_response="Great! I've noted that.",
        metadata={"user_id": "user-456"}
    )
    
    # Retrieve context
    context = await memory.retrieve_context("hours last week", user_id="user-456")
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from llm.config import LLMConfig

logger = logging.getLogger(__name__)


class LLMMemoryManager:
    """
    Manage long-term memory using Mem0
    
    Mem0 automatically extracts and stores memories from conversations,
    providing intelligent semantic search and retrieval.
    """
    
    def __init__(self, tenant_id: str, config: LLMConfig):
        """
        Initialize Mem0 memory manager
        
        Args:
            tenant_id: Tenant ID for isolation
            config: LLM configuration
        """
        self.tenant_id = tenant_id
        self.config = config
        self._memory = None
        
        logger.info(f"Mem0 memory manager initialized for tenant: {tenant_id}")
    
    @property
    def memory(self):
        """Lazy load Mem0 instance"""
        if self._memory is None:
            try:
                from mem0 import Memory
                
                # Configure Mem0 with Qdrant
                # Parse URL to extract host and port
                qdrant_url = self.config.qdrant_url
                url_without_protocol = qdrant_url.replace("http://", "").replace("https://", "")
                
                # Extract host and port
                if ":" in url_without_protocol:
                    host, port_str = url_without_protocol.split(":", 1)
                    port = int(port_str.split("/")[0])  # Handle URLs with paths
                else:
                    host = url_without_protocol.split("/")[0]
                    port = 443 if "https://" in qdrant_url else 80
                
                mem0_config = {
                    "vector_store": {
                        "provider": "qdrant",
                        "config": {
                            "collection_name": f"mem0_{self.tenant_id}",
                            "host": host,
                            "port": port,
                        }
                    }
                }
                
                # Add API key if configured
                if self.config.qdrant_api_key:
                    mem0_config["vector_store"]["config"]["api_key"] = self.config.qdrant_api_key
                
                self._memory = Memory.from_config(mem0_config)
                logger.info(f"Mem0 initialized with Qdrant: collection=mem0_{self.tenant_id}")
                
            except ImportError as e:
                logger.error(f"mem0ai not installed: {e}")
                raise
            except Exception as e:
                logger.error(f"Failed to initialize Mem0: {e}")
                raise
        
        return self._memory
    
    async def add_conversation(
        self,
        user_message: str,
        ai_response: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Store conversation in memory
        
        Mem0 automatically extracts relevant memories from the conversation.
        
        Args:
            user_message: User's message
            ai_response: AI's response
            metadata: Additional metadata (should include user_id)
        """
        try:
            user_id = metadata.get("user_id", "default") if metadata else "default"
            
            # Store user message directly for better memory extraction
            # Mem0 works best with first-person statements
            # If the message is a statement, keep it as-is
            # If it's a question, store the AI's extracted fact
            memory_text = user_message
            
            # Add metadata to help with context and temporal queries
            enhanced_metadata = metadata or {}
            enhanced_metadata["original_message"] = user_message
            enhanced_metadata["ai_response_preview"] = ai_response[:100]
            enhanced_metadata["timestamp"] = datetime.now().isoformat()
            
            # Add temporal keywords for better time-based retrieval
            temporal_keywords = ["yesterday", "today", "last week", "hours", "worked", "timesheet"]
            found_keywords = [kw for kw in temporal_keywords if kw in user_message.lower()]
            if found_keywords:
                enhanced_metadata["temporal_context"] = ", ".join(found_keywords)
            
            self.memory.add(
                memory_text,
                user_id=f"{self.tenant_id}_{user_id}",  # Tenant isolation
                metadata=enhanced_metadata
            )
            
            logger.info(f"Stored conversation in Mem0 for user: {user_id}")
            logger.debug(f"Memory text: {memory_text[:100]}...")
            
        except Exception as e:
            logger.error(f"Failed to store conversation in Mem0: {e}")
            raise
    
    async def retrieve_context(
        self,
        query: str,
        k: Optional[int] = None,
        filter: Optional[Dict[str, Any]] = None
    ) -> List[str]:
        """
        Retrieve relevant context from memory
        
        Args:
            query: Search query
            k: Number of results (default from config)
            filter: Filter dict (should include user_id)
        
        Returns:
            List of relevant context strings
        """
        try:
            if k is None:
                k = self.config.memory_retrieval_k
            
            user_id = filter.get("user_id", "default") if filter else "default"
            
            # Expand query with synonyms and related terms for better semantic matching
            expanded_queries = [query]
            
            # Add query expansions for common patterns
            query_lower = query.lower()
            if "project" in query_lower:
                expanded_queries.append(query + " work assignment task")
            if "schedule" in query_lower or "when" in query_lower:
                expanded_queries.append(query + " Monday Tuesday Wednesday Thursday Friday weekend")
            if "work" in query_lower and "hours" in query_lower:
                expanded_queries.append(query + " timesheet time entry")
            
            # Search with original query first, then expanded if needed
            all_results = []
            for expanded_query in expanded_queries:
                search_results = self.memory.search(
                    query=expanded_query,
                    user_id=f"{self.tenant_id}_{user_id}",
                    limit=k
                )
                
                # Mem0 returns {"results": [...]} format
                results = search_results.get("results", []) if isinstance(search_results, dict) else search_results
                all_results.extend(results)
                
                # If we got good results (high scores), stop expanding
                if results and any(r.get("score", 0) > 0.5 for r in results):
                    break
            
            # Deduplicate results by memory text
            seen_memories = set()
            unique_results = []
            for result in all_results:
                if isinstance(result, dict) and "memory" in result:
                    memory_text = result["memory"]
                    if memory_text not in seen_memories:
                        seen_memories.add(memory_text)
                        unique_results.append(result)
            
            # Sort by score and take top k
            unique_results.sort(key=lambda x: x.get("score", 0), reverse=True)
            results = unique_results[:k]
            
            # Extract memory text from results and format for better LLM understanding
            context = []
            for i, result in enumerate(results):
                if isinstance(result, dict) and "memory" in result:
                    memory_text = result["memory"]
                    score = result.get("score", 0.0)
                    
                    # Format memory for better LLM comprehension with explicit context
                    # Add "The user" prefix for clarity and include relevance score
                    if not memory_text.strip().lower().startswith(("i ", "the user", "user")):
                        formatted_memory = f"[Relevance: {score:.2f}] The user {memory_text.lower()}"
                    else:
                        formatted_memory = f"[Relevance: {score:.2f}] {memory_text}"
                    
                    context.append(formatted_memory)
                    logger.info(f"Extracted memory {i} (score={score:.2f}): {formatted_memory[:100]}...")
            
            logger.info(f"Retrieved {len(context)} memories from Mem0")
            return context
            
        except Exception as e:
            logger.error(f"Failed to retrieve context from Mem0: {e}")
            return []
    
    async def get_all_memories(
        self,
        user_id: Optional[str] = None,
        k: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get all memories for a user
        
        Args:
            user_id: User ID (optional)
            k: Limit number of results
        
        Returns:
            List of memory dictionaries
        """
        try:
            if k is None:
                k = self.config.memory_retrieval_k * 2
            
            user_id = user_id or "default"
            
            # Get all memories for user
            results = self.memory.get_all(
                user_id=f"{self.tenant_id}_{user_id}"
            )
            
            return results[:k] if results else []
            
        except Exception as e:
            logger.error(f"Failed to get all memories: {e}")
            return []
    
    async def update_memory(
        self,
        memory_id: str,
        data: str
    ) -> bool:
        """
        Update an existing memory
        
        Args:
            memory_id: Memory ID to update
            data: New memory content
        
        Returns:
            True if successful
        """
        try:
            self.memory.update(memory_id=memory_id, data=data)
            logger.info(f"Updated memory: {memory_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to update memory: {e}")
            return False
    
    async def delete_memory(
        self,
        memory_id: str
    ) -> bool:
        """
        Delete a memory
        
        Args:
            memory_id: Memory ID to delete
        
        Returns:
            True if successful
        """
        try:
            self.memory.delete(memory_id=memory_id)
            logger.info(f"Deleted memory: {memory_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete memory: {e}")
            return False
    
    async def get_memory_history(
        self,
        memory_id: str
    ) -> List[Dict[str, Any]]:
        """
        Get history of a memory
        
        Args:
            memory_id: Memory ID
        
        Returns:
            List of history entries
        """
        try:
            history = self.memory.history(memory_id=memory_id)
            return history if history else []
        except Exception as e:
            logger.error(f"Failed to get memory history: {e}")
            return []
