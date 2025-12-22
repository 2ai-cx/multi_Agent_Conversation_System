"""
Embeddings Provider Wrapper

Supports multiple embedding providers:
- OpenAI (text-embedding-3-small, text-embedding-3-large)
- Cohere (embed-english-v3.0, embed-multilingual-v3.0)
- HuggingFace (sentence-transformers)

Usage:
    from llm.embeddings import EmbeddingsProvider
    from llm.config import LLMConfig
    
    config = LLMConfig(
        embeddings_provider="openai",
        embeddings_model="text-embedding-3-small"
    )
    provider = EmbeddingsProvider(config)
    
    # Embed single query
    vector = await provider.embed_query("Hello world")
    
    # Embed multiple documents
    vectors = await provider.embed_documents(["Doc 1", "Doc 2"])
"""

import logging
from typing import List, Optional
from llm.config import LLMConfig

logger = logging.getLogger(__name__)


class EmbeddingsProvider:
    """
    Unified embeddings provider
    
    Lazy loads the appropriate embeddings model based on configuration.
    Supports OpenAI, Cohere, and HuggingFace providers.
    """
    
    def __init__(self, config: LLMConfig):
        """
        Initialize embeddings provider
        
        Args:
            config: LLM configuration
        """
        self.config = config
        self._embeddings = None
        
        logger.info(
            f"Embeddings provider initialized: "
            f"provider={config.embeddings_provider}, "
            f"model={config.embeddings_model}"
        )
    
    @property
    def embeddings(self):
        """Lazy load embeddings provider"""
        if self._embeddings is None:
            if self.config.embeddings_provider == "openai":
                try:
                    from langchain_openai import OpenAIEmbeddings
                    
                    self._embeddings = OpenAIEmbeddings(
                        model=self.config.embeddings_model,
                        openai_api_key=self.config.openai_api_key
                    )
                    logger.info(f"Using OpenAI embeddings: {self.config.embeddings_model}")
                
                except ImportError:
                    logger.error(
                        "langchain-openai not installed. "
                        "Install with: pip install langchain-openai"
                    )
                    raise
            
            elif self.config.embeddings_provider == "cohere":
                try:
                    from langchain_cohere import CohereEmbeddings
                    
                    cohere_api_key = self.config.model_extra.get("cohere_api_key")
                    if not cohere_api_key:
                        raise ValueError("COHERE_API_KEY not set in environment")
                    
                    self._embeddings = CohereEmbeddings(
                        model=self.config.embeddings_model,
                        cohere_api_key=cohere_api_key
                    )
                    logger.info(f"Using Cohere embeddings: {self.config.embeddings_model}")
                
                except ImportError:
                    logger.error(
                        "langchain-cohere not installed. "
                        "Install with: pip install langchain-cohere"
                    )
                    raise
            
            elif self.config.embeddings_provider == "huggingface":
                try:
                    from langchain_huggingface import HuggingFaceEmbeddings
                    
                    self._embeddings = HuggingFaceEmbeddings(
                        model_name=self.config.embeddings_model
                    )
                    logger.info(f"Using HuggingFace embeddings: {self.config.embeddings_model}")
                
                except ImportError:
                    logger.error(
                        "langchain-huggingface not installed. "
                        "Install with: pip install langchain-huggingface"
                    )
                    raise
            
            else:
                raise ValueError(
                    f"Unknown embeddings provider: {self.config.embeddings_provider}. "
                    f"Must be one of: openai, cohere, huggingface"
                )
        
        return self._embeddings
    
    async def embed_query(self, text: str) -> List[float]:
        """
        Embed a single query
        
        Args:
            text: Query text
        
        Returns:
            Embedding vector
        """
        try:
            return await self.embeddings.aembed_query(text)
        except Exception as e:
            logger.error(f"Failed to embed query: {e}")
            raise
    
    async def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Embed multiple documents
        
        Args:
            texts: List of document texts
        
        Returns:
            List of embedding vectors
        """
        try:
            return await self.embeddings.aembed_documents(texts)
        except Exception as e:
            logger.error(f"Failed to embed documents: {e}")
            raise
    
    def get_dimension(self) -> int:
        """Get embedding dimension"""
        return self.config.embeddings_dimension
    
    def get_stats(self) -> dict:
        """Get embeddings statistics"""
        return {
            "provider": self.config.embeddings_provider,
            "model": self.config.embeddings_model,
            "dimension": self.config.embeddings_dimension
        }
