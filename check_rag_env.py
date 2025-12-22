#!/usr/bin/env python3
"""Check RAG environment variables in production"""
import os

print("="*60)
print("RAG ENVIRONMENT CHECK")
print("="*60)

env_vars = {
    "RAG_ENABLED": os.getenv("RAG_ENABLED"),
    "VECTOR_DB_PROVIDER": os.getenv("VECTOR_DB_PROVIDER"),
    "QDRANT_URL": os.getenv("QDRANT_URL"),
    "QDRANT_API_KEY": os.getenv("QDRANT_API_KEY"),
    "QDRANT_COLLECTION_NAME": os.getenv("QDRANT_COLLECTION_NAME"),
    "EMBEDDINGS_PROVIDER": os.getenv("EMBEDDINGS_PROVIDER"),
    "EMBEDDINGS_MODEL": os.getenv("EMBEDDINGS_MODEL"),
    "EMBEDDINGS_DIMENSION": os.getenv("EMBEDDINGS_DIMENSION"),
    "OPENAI_API_KEY": "SET" if os.getenv("OPENAI_API_KEY") else "NOT SET"
}

for key, value in env_vars.items():
    status = "✅" if value else "❌"
    print(f"{status} {key}: {value}")

print("="*60)

# Try to import and initialize
print("\nTrying to import llm.config...")
try:
    from llm.config import LLMConfig
    config = LLMConfig()
    print(f"✅ LLMConfig loaded")
    print(f"   rag_enabled: {config.rag_enabled}")
    print(f"   vector_db_provider: {config.vector_db_provider}")
    print(f"   qdrant_url: {config.qdrant_url}")
except Exception as e:
    print(f"❌ Failed: {e}")

print("\n" + "="*60)
