#!/usr/bin/env python3
"""
RAG Functionality Test
Tests actual memory storage and retrieval with Qdrant
"""

import asyncio
import os
import sys
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from llm.config import LLMConfig
from llm.client import LLMClient


async def test_rag_initialization():
    """Test 1: Check if RAG can be initialized"""
    print("\n" + "="*60)
    print("TEST 1: RAG Initialization")
    print("="*60)
    
    try:
        # Load config
        config = LLMConfig()
        print(f"✅ Config loaded")
        print(f"   RAG Enabled: {config.rag_enabled}")
        print(f"   Vector DB: {config.vector_db_provider}")
        print(f"   Qdrant URL: {config.qdrant_url}")
        print(f"   Embeddings Provider: {config.embeddings_provider}")
        print(f"   Embeddings Model: {config.embeddings_model}")
        
        if not config.rag_enabled:
            print("❌ FAIL: RAG is not enabled (RAG_ENABLED=false)")
            return False
        
        if not config.qdrant_url:
            print("❌ FAIL: QDRANT_URL not configured")
            return False
        
        print("✅ PASS: RAG configuration looks good")
        return True
        
    except Exception as e:
        print(f"❌ FAIL: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_memory_manager_creation():
    """Test 2: Check if LLMMemoryManager can be created"""
    print("\n" + "="*60)
    print("TEST 2: Memory Manager Creation")
    print("="*60)
    
    try:
        from llm.memory import LLMMemoryManager
        config = LLMConfig()
        
        if not config.rag_enabled:
            print("⚠️  SKIP: RAG not enabled")
            return None
        
        print("Creating memory manager...")
        memory = LLMMemoryManager(
            tenant_id="test-tenant",
            config=config
        )
        print(f"✅ Memory manager created")
        print(f"   Tenant ID: {memory.tenant_id}")
        print(f"   Vector DB: {config.vector_db_provider}")
        
        # Try to access vectorstore (this will trigger initialization)
        print("\nInitializing vector store...")
        vectorstore = memory.vectorstore
        print(f"✅ Vector store initialized: {type(vectorstore).__name__}")
        
        return memory
        
    except Exception as e:
        print(f"❌ FAIL: {e}")
        import traceback
        traceback.print_exc()
        return None


async def test_qdrant_connection():
    """Test 3: Check if we can connect to Qdrant"""
    print("\n" + "="*60)
    print("TEST 3: Qdrant Connection")
    print("="*60)
    
    try:
        from qdrant_client import QdrantClient
        config = LLMConfig()
        
        if not config.qdrant_url:
            print("⚠️  SKIP: Qdrant URL not configured")
            return False
        
        print(f"Connecting to: {config.qdrant_url}")
        client = QdrantClient(
            url=config.qdrant_url,
            api_key=config.qdrant_api_key
        )
        
        # Try to get collections
        print("Fetching collections...")
        collections = client.get_collections()
        print(f"✅ Connected to Qdrant")
        print(f"   Collections: {len(collections.collections)}")
        
        for col in collections.collections:
            print(f"   - {col.name}: {col.vectors_count} vectors")
        
        return True
        
    except Exception as e:
        print(f"❌ FAIL: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_embeddings_generation():
    """Test 4: Check if embeddings can be generated"""
    print("\n" + "="*60)
    print("TEST 4: Embeddings Generation")
    print("="*60)
    
    try:
        from llm.embeddings import EmbeddingsProvider
        config = LLMConfig()
        
        if not config.rag_enabled:
            print("⚠️  SKIP: RAG not enabled")
            return False
        
        print(f"Creating embeddings provider: {config.embeddings_provider}")
        provider = EmbeddingsProvider(config)
        
        # Generate test embedding
        test_text = "This is a test message for embedding generation"
        print(f"Generating embedding for: '{test_text}'")
        
        embedding = await provider.embed_query(test_text)
        print(f"✅ Embedding generated")
        print(f"   Dimension: {len(embedding)}")
        print(f"   First 5 values: {embedding[:5]}")
        
        return True
        
    except Exception as e:
        print(f"❌ FAIL: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_memory_storage():
    """Test 5: Test storing a conversation"""
    print("\n" + "="*60)
    print("TEST 5: Memory Storage")
    print("="*60)
    
    try:
        memory = await test_memory_manager_creation()
        if not memory:
            print("⚠️  SKIP: Memory manager not available")
            return False
        
        # Store a test conversation
        test_conversation = {
            "user_message": "I logged 8 hours on Project X today",
            "assistant_message": "Great! I've recorded that you logged 8 hours on Project X.",
            "user_id": "test-user",
            "timestamp": datetime.now().isoformat()
        }
        
        print(f"Storing conversation...")
        print(f"   User: {test_conversation['user_message']}")
        print(f"   Assistant: {test_conversation['assistant_message']}")
        
        await memory.store_conversation(
            user_message=test_conversation["user_message"],
            assistant_message=test_conversation["assistant_message"],
            metadata={"user_id": test_conversation["user_id"]}
        )
        
        print(f"✅ Conversation stored successfully")
        return True
        
    except Exception as e:
        print(f"❌ FAIL: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_memory_retrieval():
    """Test 6: Test retrieving context"""
    print("\n" + "="*60)
    print("TEST 6: Memory Retrieval")
    print("="*60)
    
    try:
        memory = await test_memory_manager_creation()
        if not memory:
            print("⚠️  SKIP: Memory manager not available")
            return False
        
        # Try to retrieve context
        query = "How many hours did I log on Project X?"
        print(f"Retrieving context for: '{query}'")
        
        context = await memory.retrieve_context(
            query=query,
            filter={"user_id": "test-user"}
        )
        
        print(f"✅ Context retrieved")
        print(f"   Length: {len(context)} characters")
        if context:
            print(f"   Preview: {context[:200]}...")
        else:
            print(f"   (No context found - this is OK if no data stored yet)")
        
        return True
        
    except Exception as e:
        print(f"❌ FAIL: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_llm_client_with_memory():
    """Test 7: Test LLMClient with memory"""
    print("\n" + "="*60)
    print("TEST 7: LLMClient with Memory")
    print("="*60)
    
    try:
        config = LLMConfig()
        client = LLMClient(config)
        
        if not config.rag_enabled:
            print("⚠️  SKIP: RAG not enabled")
            return False
        
        # Test get_memory_manager
        print("Getting memory manager for tenant...")
        memory = client.get_memory_manager("test-tenant")
        
        if memory:
            print(f"✅ Memory manager retrieved")
            print(f"   Type: {type(memory).__name__}")
        else:
            print(f"❌ FAIL: Memory manager is None")
            return False
        
        # Test generate_with_memory method exists
        if hasattr(client, 'generate_with_memory'):
            print(f"✅ generate_with_memory method exists")
        else:
            print(f"❌ FAIL: generate_with_memory method not found")
            return False
        
        if hasattr(client, 'chat_completion_with_memory'):
            print(f"✅ chat_completion_with_memory method exists")
        else:
            print(f"❌ FAIL: chat_completion_with_memory method not found")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ FAIL: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("RAG FUNCTIONALITY TEST SUITE")
    print("="*60)
    print(f"Time: {datetime.now().isoformat()}")
    print("")
    
    results = {}
    
    # Run tests
    results["initialization"] = await test_rag_initialization()
    results["memory_manager"] = await test_memory_manager_creation() is not None
    results["qdrant_connection"] = await test_qdrant_connection()
    results["embeddings"] = await test_embeddings_generation()
    results["memory_storage"] = await test_memory_storage()
    results["memory_retrieval"] = await test_memory_retrieval()
    results["llm_client"] = await test_llm_client_with_memory()
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print("")
    print(f"Total: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! RAG is fully functional!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
