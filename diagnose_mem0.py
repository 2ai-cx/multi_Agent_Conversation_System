"""
Mem0 Diagnostic Tool

Deep analysis of Mem0 memory extraction, storage, and retrieval.
Helps identify issues with memory management.
"""

import asyncio
import logging
import json
from typing import Dict, Any
from llm.memory import LLMMemoryManager
from llm.config import LLMConfig

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_memory_extraction():
    """Test what Mem0 actually extracts from conversations"""
    
    print("=" * 80)
    print("MEM0 DIAGNOSTIC TOOL - Memory Extraction Analysis")
    print("=" * 80)
    print()
    
    # Initialize
    config = LLMConfig()
    tenant_id = "diagnostic-tenant"
    user_id = "diagnostic-user"
    memory = LLMMemoryManager(tenant_id=tenant_id, config=config)
    
    # Test cases
    test_cases = [
        {
            "name": "Simple Fact",
            "user": "I work as a software engineer.",
            "ai": "That's great! Software engineering is a rewarding field."
        },
        {
            "name": "Numeric Data",
            "user": "I worked 847 hours and earned $125,000.",
            "ai": "That's impressive! You've put in a lot of hours."
        },
        {
            "name": "Multiple Facts",
            "user": "I work at Google as a senior developer specializing in machine learning.",
            "ai": "Excellent! Google is a great place to work on ML."
        },
        {
            "name": "Preference",
            "user": "I prefer Python over JavaScript for backend development.",
            "ai": "Python is indeed very popular for backend development."
        }
    ]
    
    print("📝 PHASE 1: Storing Conversations")
    print("-" * 80)
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n{i}. {test['name']}")
        print(f"   User: {test['user']}")
        print(f"   AI: {test['ai']}")
        
        try:
            await memory.add_conversation(
                user_message=test['user'],
                ai_response=test['ai'],
                metadata={"user_id": user_id, "test_case": test['name']}
            )
            print(f"   ✅ Stored successfully")
        except Exception as e:
            print(f"   ❌ Failed: {e}")
        
        # Wait for indexing
        await asyncio.sleep(2)
    
    print("\n" + "=" * 80)
    print("⏳ Waiting 10 seconds for Mem0 to process and index...")
    print("=" * 80)
    await asyncio.sleep(10)
    
    print("\n📖 PHASE 2: Retrieving All Memories")
    print("-" * 80)
    
    try:
        all_memories = await memory.get_all_memories(user_id=user_id, k=20)
        print(f"\nTotal memories stored: {len(all_memories)}")
        
        if all_memories:
            print("\nMemories extracted by Mem0:")
            for i, mem in enumerate(all_memories, 1):
                print(f"\n{i}. Memory ID: {mem.get('id', 'N/A')}")
                print(f"   Content: {mem.get('memory', mem.get('data', 'N/A'))}")
                print(f"   Created: {mem.get('created_at', 'N/A')}")
                if 'metadata' in mem:
                    print(f"   Metadata: {json.dumps(mem['metadata'], indent=6)}")
        else:
            print("⚠️  No memories found!")
    except Exception as e:
        print(f"❌ Failed to retrieve all memories: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 80)
    print("🔍 PHASE 3: Testing Semantic Search")
    print("-" * 80)
    
    search_queries = [
        ("What is my job?", "Simple Fact"),
        ("How many hours did I work?", "Numeric Data"),
        ("Where do I work?", "Multiple Facts"),
        ("What programming language do I prefer?", "Preference"),
        ("Tell me about my professional background", "Multiple Facts")
    ]
    
    for query, expected in search_queries:
        print(f"\nQuery: '{query}'")
        print(f"Expected to find: {expected}")
        
        try:
            context = await memory.retrieve_context(
                query=query,
                filter={"user_id": user_id}
            )
            
            if context:
                print(f"✅ Retrieved {len(context)} memories:")
                for i, ctx in enumerate(context, 1):
                    print(f"   {i}. {ctx[:100]}...")
            else:
                print("❌ No memories retrieved")
        except Exception as e:
            print(f"❌ Search failed: {e}")
    
    print("\n" + "=" * 80)
    print("🔬 PHASE 4: Direct Mem0 API Analysis")
    print("-" * 80)
    
    try:
        # Test direct Mem0 search
        print("\nDirect Mem0 search for 'software engineer':")
        full_user_id = f"{tenant_id}_{user_id}"
        
        search_result = memory.memory.search(
            query="software engineer",
            user_id=full_user_id,
            limit=5
        )
        
        print(f"Raw search result type: {type(search_result)}")
        print(f"Raw search result: {json.dumps(search_result, indent=2, default=str)}")
        
    except Exception as e:
        print(f"❌ Direct search failed: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 80)
    print("📊 PHASE 5: Mem0 Configuration Analysis")
    print("-" * 80)
    
    print(f"\nMem0 Configuration:")
    print(f"  Tenant ID: {tenant_id}")
    print(f"  User ID: {user_id}")
    print(f"  Full User ID: {tenant_id}_{user_id}")
    print(f"  Collection: mem0_{tenant_id}")
    print(f"  Qdrant URL: {config.qdrant_url}")
    print(f"  Retrieval K: {config.memory_retrieval_k}")
    
    print("\n" + "=" * 80)
    print("✅ DIAGNOSTIC COMPLETE")
    print("=" * 80)
    
    return {
        "total_memories": len(all_memories) if all_memories else 0,
        "search_results": len([q for q in search_queries if context])
    }


async def test_conversation_format():
    """Test different conversation formats to see what Mem0 extracts best"""
    
    print("\n" + "=" * 80)
    print("🧪 TESTING DIFFERENT CONVERSATION FORMATS")
    print("=" * 80)
    
    config = LLMConfig()
    tenant_id = "format-test-tenant"
    user_id = "format-test-user"
    memory = LLMMemoryManager(tenant_id=tenant_id, config=config)
    
    formats = [
        {
            "name": "Current Format (User: ... Assistant: ...)",
            "text": "User: I am 30 years old.\nAssistant: Thank you for sharing that."
        },
        {
            "name": "User Message Only",
            "text": "I am 30 years old."
        },
        {
            "name": "Statement Format",
            "text": "The user is 30 years old."
        },
        {
            "name": "Fact Format",
            "text": "Age: 30 years old"
        }
    ]
    
    for fmt in formats:
        print(f"\n📝 Testing: {fmt['name']}")
        print(f"   Text: {fmt['text']}")
        
        try:
            # Use Mem0's add directly
            memory.memory.add(
                fmt['text'],
                user_id=f"{tenant_id}_{user_id}_{fmt['name'].replace(' ', '_')}",
                metadata={"format": fmt['name']}
            )
            print(f"   ✅ Stored")
        except Exception as e:
            print(f"   ❌ Failed: {e}")
        
        await asyncio.sleep(3)
    
    print("\n⏳ Waiting for indexing...")
    await asyncio.sleep(10)
    
    print("\n🔍 Retrieving all memories to see what was extracted:")
    
    for fmt in formats:
        try:
            user_id_fmt = f"{user_id}_{fmt['name'].replace(' ', '_')}"
            all_mems = await memory.get_all_memories(user_id=user_id_fmt, k=10)
            
            print(f"\n{fmt['name']}:")
            if all_mems:
                for mem in all_mems:
                    print(f"  Extracted: {mem.get('memory', mem.get('data', 'N/A'))}")
            else:
                print(f"  ⚠️  No memories extracted")
        except Exception as e:
            print(f"  ❌ Error: {e}")


if __name__ == "__main__":
    print("\n🚀 Starting Mem0 Deep Diagnostic\n")
    
    # Run main diagnostic
    results = asyncio.run(test_memory_extraction())
    
    print(f"\n📈 Summary:")
    print(f"  Total memories stored: {results['total_memories']}")
    print(f"  Successful searches: {results['search_results']}")
    
    # Run format testing
    print("\n" + "=" * 80)
    asyncio.run(test_conversation_format())
    
    print("\n✅ All diagnostics complete!")
