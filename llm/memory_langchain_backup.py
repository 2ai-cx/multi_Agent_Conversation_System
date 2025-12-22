"""
LLM Memory Manager

Manages long-term memory with RAG using vector stores:
- Pinecone (managed, recommended)
- Weaviate (self-hosted)
- Qdrant (hybrid)

Features:
- Multi-tenant isolation (namespaces)
- Semantic search
- MMR (Maximum Marginal Relevance) retrieval
- Conversation storage
- Context retrieval

Usage:
    from llm.memory import LLMMemoryManager
    from llm.config import LLMConfig
    
    config = LLMConfig(
        rag_enabled=True,
        vector_db_provider="pinecone",
        pinecone_api_key="your-key"
    )
    
    memory = LLMMemoryManager(tenant_id="tenant-123", config=config)
    
    # Store conversation
    await memory.add_conversation(
        user_message="How many hours did I log?",
        ai_response="You logged 35 hours last week.",
        metadata={"user_id": "user-456"}
    )
    
    # Retrieve context
    context = await memory.retrieve_context("hours last week")
"""

import time
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from llm.config import LLMConfig
from llm.embeddings import EmbeddingsProvider

logger = logging.getLogger(__name__)


class LLMMemoryManager:
    """
    Manage long-term memory with RAG
    
    Stores conversations in vector database for semantic retrieval.
    Supports multi-tenant isolation via namespaces.
    """
    
    def __init__(self, tenant_id: str, config: LLMConfig):
        """
        Initialize memory manager
        
        Args:
            tenant_id: Tenant ID for isolation
            config: LLM configuration
        """
        self.tenant_id = tenant_id
        self.config = config
        
        # Initialize embeddings
        self.embeddings_provider = EmbeddingsProvider(config)
        
        # Initialize vector store (lazy)
        self._vectorstore = None
        self._retriever = None
        
        # Initialize Qdrant client attributes (will be set during vectorstore init)
        self._qdrant_client = None
        self._collection_name = None
        
        logger.info(f"Memory manager initialized for tenant: {tenant_id}")
    
    @property
    def vectorstore(self):
        """Lazy load vector store"""
        if self._vectorstore is None:
            if self.config.vector_db_provider == "pinecone":
                try:
                    from langchain_pinecone import PineconeVectorStore
                    
                    if not self.config.pinecone_api_key:
                        raise ValueError("PINECONE_API_KEY not set")
                    
                    self._vectorstore = PineconeVectorStore(
                        index_name=self.config.pinecone_index_name,
                        embedding=self.embeddings_provider.embeddings,
                        namespace=self.tenant_id  # Multi-tenant isolation
                    )
                    logger.info(
                        f"Using Pinecone vector store: "
                        f"index={self.config.pinecone_index_name}, "
                        f"namespace={self.tenant_id}"
                    )
                
                except ImportError:
                    logger.error(
                        "langchain-pinecone not installed. "
                        "Install with: pip install langchain-pinecone"
                    )
                    raise
            
            elif self.config.vector_db_provider == "weaviate":
                try:
                    from langchain_weaviate import WeaviateVectorStore
                    
                    if not self.config.weaviate_url:
                        raise ValueError("WEAVIATE_URL not set")
                    
                    self._vectorstore = WeaviateVectorStore(
                        url=self.config.weaviate_url,
                        embedding=self.embeddings_provider.embeddings,
                        index_name=f"TimesheetMemory_{self.tenant_id}"
                    )
                    logger.info(f"Using Weaviate vector store: url={self.config.weaviate_url}")
                
                except ImportError:
                    logger.error(
                        "langchain-weaviate not installed. "
                        "Install with: pip install langchain-weaviate"
                    )
                    raise
            
            elif self.config.vector_db_provider == "qdrant":
                try:
                    # Use official langchain-qdrant integration
                    from langchain_qdrant import Qdrant
                    from qdrant_client import QdrantClient
                    from qdrant_client.models import Distance, VectorParams
                    
                    if not self.config.qdrant_url:
                        raise ValueError("QDRANT_URL not set")
                    
                    # Create Qdrant client with longer timeout for Azure internal network
                    # For Azure Container Apps, use port 80 (ingress port) instead of 6333 (container port)
                    client = QdrantClient(
                        url=self.config.qdrant_url,
                        port=80,  # Use ingress port for Azure Container Apps
                        api_key=self.config.qdrant_api_key,  # Optional, None for local
                        timeout=60  # Increase timeout for Azure internal network
                    )
                    
                    # Use tenant-specific collection for isolation
                    collection_name = f"{self.config.qdrant_collection_name}_{self.tenant_id}"
                    
                    # Check if collection exists, create if not
                    try:
                        client.get_collection(collection_name)
                        logger.info(f"Collection {collection_name} already exists")
                    except Exception:
                        # Collection doesn't exist, create it
                        logger.info(f"Creating collection: {collection_name}")
                        client.create_collection(
                            collection_name=collection_name,
                            vectors_config=VectorParams(
                                size=self.config.embeddings_dimension,
                                distance=Distance.COSINE
                            )
                        )
                        logger.info(f"Collection {collection_name} created successfully")
                    
                    # Store client and collection name for direct access
                    self._qdrant_client = client
                    self._collection_name = collection_name
                    logger.info(f"✓ Stored Qdrant client and collection name for direct search")
                    
                    # Use official langchain-qdrant Qdrant class
                    self._vectorstore = Qdrant(
                        client=client,
                        collection_name=collection_name,
                        embeddings=self.embeddings_provider.embeddings
                    )
                    logger.info(
                        f"Using Qdrant vector store: "
                        f"url={self.config.qdrant_url}, "
                        f"collection={collection_name}"
                    )
                
                except ImportError:
                    logger.error(
                        "langchain-qdrant or qdrant-client not installed. "
                        "Install with: pip install langchain-qdrant qdrant-client"
                    )
                    raise
            
            else:
                raise ValueError(
                    f"Unknown vector DB provider: {self.config.vector_db_provider}. "
                    f"Must be one of: pinecone, weaviate, qdrant"
                )
        
        return self._vectorstore
    
    @property
    def retriever(self):
        """Lazy load retriever"""
        if self._retriever is None:
            search_kwargs = {
                "k": self.config.memory_retrieval_k,
            }
            
            # Add MMR-specific parameters if using MMR
            if self.config.memory_retrieval_method == "mmr":
                search_kwargs["fetch_k"] = self.config.memory_retrieval_k * 4
                search_kwargs["lambda_mult"] = self.config.memory_mmr_diversity
            
            self._retriever = self.vectorstore.as_retriever(
                search_type=self.config.memory_retrieval_method,
                search_kwargs=search_kwargs
            )
            
            logger.info(
                f"Retriever initialized: "
                f"method={self.config.memory_retrieval_method}, "
                f"k={self.config.memory_retrieval_k}"
            )
        
        return self._retriever
    
    async def add_conversation(
        self,
        user_message: str,
        ai_response: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Store conversation in long-term memory
        
        Args:
            user_message: User's message
            ai_response: AI's response
            metadata: Additional metadata (user_id, model, tokens, cost, etc.)
        """
        start_time = time.time()
        
        try:
            # Create document text
            doc_text = f"User: {user_message}\nAI: {ai_response}"
            
            # Prepare metadata
            doc_metadata = {
                "tenant_id": self.tenant_id,
                "timestamp": datetime.now().isoformat(),
                "user_message": user_message,
                "ai_response": ai_response,
                **(metadata or {})
            }
            
            # Add to vector store
            await self.vectorstore.aadd_texts(
                texts=[doc_text],
                metadatas=[doc_metadata]
            )
            
            latency_ms = (time.time() - start_time) * 1000
            logger.debug(f"Stored conversation in memory: {latency_ms:.0f}ms")
        
        except Exception as e:
            logger.error(f"Failed to store conversation: {e}")
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
            query: Query text
            k: Number of results (default: config.memory_retrieval_k)
            filter: Metadata filters
        
        Returns:
            List of relevant context strings
        """
        start_time = time.time()
        
        try:
            # Use configured k if not specified
            if k is None:
                k = self.config.memory_retrieval_k
            
            # Ensure vectorstore is initialized (this sets _qdrant_client for Qdrant)
            _ = self.vectorstore
            
            # Use direct HTTP REST API to bypass SDK limitations
            # This works with Azure Container Apps HTTP/port 80 configuration
            if hasattr(self, '_qdrant_client') and self._qdrant_client:
                logger.info("Using direct HTTP REST API for Qdrant search")
                import requests
                from qdrant_client.models import FieldCondition, Filter, MatchValue
                
                # Generate embedding for the query using our embeddings provider
                query_embedding = await self.embeddings_provider.embeddings.aembed_query(query)
                
                # Build filter if provided
                filter_dict = None
                if filter:
                    conditions = []
                    for key, value in filter.items():
                        conditions.append({"key": key, "match": {"value": value}})
                    if conditions:
                        filter_dict = {"must": conditions}
                
                # Direct HTTP POST to Qdrant search endpoint
                # LangChain Qdrant uses an empty string as the default vector name
                logger.info(f"Executing HTTP search: collection={self._collection_name}, embedding_len={len(query_embedding)}, limit={k}")
                
                search_url = f"{self.config.qdrant_url}/collections/{self._collection_name}/points/search"
                search_payload = {
                    "vector": {
                        "name": "",  # LangChain Qdrant default vector name
                        "vector": query_embedding
                    },
                    "limit": k,
                    "with_payload": True
                }
                if filter_dict:
                    search_payload["filter"] = filter_dict
                
                response = requests.post(search_url, json=search_payload, timeout=30)
                response.raise_for_status()
                response_data = response.json()
                logger.info(f"HTTP response status: {response.status_code}, response keys: {list(response_data.keys())}")
                search_results = response_data.get("result", [])
                
                logger.info(f"Query returned {len(search_results)} results")
                
                # Extract content from results (HTTP API returns dicts, not objects)
                context = []
                for i, result in enumerate(search_results):
                    payload = result.get('payload', {})
                    logger.info(f"Result {i}: payload_keys={list(payload.keys())}")
                    if 'page_content' in payload:
                        context.append(payload['page_content'])
                        logger.info(f"Added page_content: {payload['page_content'][:100]}...")
                    elif 'text' in payload:
                        context.append(payload['text'])
                        logger.info(f"Added text: {payload['text'][:100]}...")
                
                latency_ms = (time.time() - start_time) * 1000
                logger.info(f"Retrieved {len(context)} memories using direct Qdrant search: {latency_ms:.0f}ms")
                
                return context
            else:
                # Fallback to LangChain wrapper (may fail with Azure setup)
                logger.warning("Qdrant client not available, falling back to LangChain wrapper")
                docs = await self.vectorstore.asimilarity_search(
                    query=query,
                    k=k,
                    filter=filter
                )
                
                # Extract content
                context = [doc.page_content for doc in docs]
                
                latency_ms = (time.time() - start_time) * 1000
                logger.debug(f"Retrieved {len(context)} memories: {latency_ms:.0f}ms")
                
                return context
        
        except Exception as e:
            logger.error(f"Failed to retrieve context: {e}")
            # Return empty list on error (don't fail the request)
            return []
    
    async def search_by_metadata(
        self,
        filter: Dict[str, Any],
        k: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search memories by metadata
        
        Args:
            filter: Metadata filter (e.g., {"user_id": "user-456"})
            k: Number of results
        
        Returns:
            List of documents with metadata
        """
        try:
            docs = await self.vectorstore.asimilarity_search(
                query="",  # Empty query, filter by metadata only
                k=k,
                namespace=self.tenant_id,
                filter=filter
            )
            
            return [
                {
                    "content": doc.page_content,
                    "metadata": doc.metadata
                }
                for doc in docs
            ]
        
        except Exception as e:
            logger.error(f"Failed to search by metadata: {e}")
            return []
    
    async def delete_memories(
        self,
        filter: Dict[str, Any]
    ):
        """
        Delete memories by metadata filter
        
        Args:
            filter: Metadata filter (e.g., {"user_id": "user-456"})
        """
        try:
            # Implementation depends on vector store
            # For Pinecone: use delete with filter
            # For Weaviate: use delete with where clause
            # For Qdrant: use delete with filter
            
            logger.info(f"Deleting memories for tenant {self.tenant_id} with filter: {filter}")
            
            # TODO: Implement based on vector store provider
            # This is a placeholder - actual implementation varies by provider
            
        except Exception as e:
            logger.error(f"Failed to delete memories: {e}")
            raise
    
    def get_stats(self) -> Dict[str, Any]:
        """Get memory statistics"""
        return {
            "tenant_id": self.tenant_id,
            "vector_db": self.config.vector_db_provider,
            "embeddings_model": self.config.embeddings_model,
            "retrieval_k": self.config.memory_retrieval_k,
            "retrieval_method": self.config.memory_retrieval_method,
            "mmr_diversity": self.config.memory_mmr_diversity
        }
