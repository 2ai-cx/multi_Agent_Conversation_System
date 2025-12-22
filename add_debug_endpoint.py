#!/usr/bin/env python3
"""
Add debug endpoint to unified_server.py to check RAG environment
"""

# Read the file
with open('unified_server.py', 'r') as f:
    content = f.read()

# Find where to add the endpoint (after app creation)
debug_endpoint = '''
@app.get("/debug/rag-status")
async def debug_rag_status():
    """Debug endpoint to check RAG configuration and environment"""
    import os
    from llm.config import LLMConfig
    
    try:
        # Check environment variables
        env_status = {
            "RAG_ENABLED": os.getenv("RAG_ENABLED"),
            "VECTOR_DB_PROVIDER": os.getenv("VECTOR_DB_PROVIDER"),
            "QDRANT_URL": os.getenv("QDRANT_URL"),
            "QDRANT_API_KEY": "SET" if os.getenv("QDRANT_API_KEY") else "NOT SET",
            "QDRANT_COLLECTION_NAME": os.getenv("QDRANT_COLLECTION_NAME"),
            "EMBEDDINGS_PROVIDER": os.getenv("EMBEDDINGS_PROVIDER"),
            "EMBEDDINGS_MODEL": os.getenv("EMBEDDINGS_MODEL"),
            "EMBEDDINGS_DIMENSION": os.getenv("EMBEDDINGS_DIMENSION"),
            "OPENAI_API_KEY": "SET" if os.getenv("OPENAI_API_KEY") else "NOT SET"
        }
        
        # Try to load config
        try:
            config = LLMConfig()
            config_status = {
                "rag_enabled": config.rag_enabled,
                "vector_db_provider": config.vector_db_provider,
                "qdrant_url": config.qdrant_url,
                "embeddings_provider": config.embeddings_provider,
                "embeddings_model": config.embeddings_model,
                "openai_api_key_set": bool(config.openai_api_key)
            }
        except Exception as e:
            config_status = {"error": str(e)}
        
        # Try to create memory manager
        try:
            from llm.client import LLMClient
            client = LLMClient(config)
            memory = client.get_memory_manager("test-tenant")
            memory_status = {
                "memory_manager_created": memory is not None,
                "memory_manager_type": type(memory).__name__ if memory else None
            }
        except Exception as e:
            memory_status = {"error": str(e)}
        
        return {
            "timestamp": datetime.now().isoformat(),
            "environment_variables": env_status,
            "llm_config": config_status,
            "memory_manager": memory_status,
            "status": "ok"
        }
    except Exception as e:
        return {
            "timestamp": datetime.now().isoformat(),
            "error": str(e),
            "status": "error"
        }

'''

# Find the health endpoint and add after it
if '@app.get("/health")' in content:
    # Find the end of the health endpoint
    health_pos = content.find('@app.get("/health")')
    # Find the next @app decorator or end of function
    next_endpoint = content.find('\n@app.', health_pos + 100)
    
    if next_endpoint > 0:
        # Insert before next endpoint
        new_content = content[:next_endpoint] + '\n' + debug_endpoint + content[next_endpoint:]
    else:
        # Add at the end before if __name__
        main_pos = content.find('if __name__ == "__main__"')
        if main_pos > 0:
            new_content = content[:main_pos] + debug_endpoint + '\n\n' + content[main_pos:]
        else:
            new_content = content + '\n' + debug_endpoint
    
    # Write back
    with open('unified_server.py', 'w') as f:
        f.write(new_content)
    
    print("✅ Debug endpoint added to unified_server.py")
    print("   Endpoint: GET /debug/rag-status")
    print("\nNext steps:")
    print("1. Commit and push changes")
    print("2. Rebuild and redeploy")
    print("3. Access: https://unified-temporal-worker.../debug/rag-status")
else:
    print("❌ Could not find health endpoint")
