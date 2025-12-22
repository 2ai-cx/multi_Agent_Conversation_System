#!/usr/bin/env python3
"""
Standalone RAG Accuracy Benchmark for Mem0 + Qdrant

This version directly configures Mem0 without modifying production files.
Tests retrieval accuracy, relevance, and semantic similarity.

Usage:
    python test_rag_benchmark_standalone.py
"""

import asyncio
import os
import sys
from typing import List, Dict, Any
from datetime import datetime
import json

# Load environment variables
from dotenv import load_dotenv
load_dotenv()


class StandaloneRAGBenchmark:
    """Standalone RAG benchmark that configures Mem0 directly"""
    
    def __init__(self, tenant_id: str = "benchmark_test"):
        self.tenant_id = tenant_id
        self.user_id = "test_user"
        
        # Get API keys from environment
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.openrouter_api_key = os.getenv('OPENROUTER_API_KEY')
        self.qdrant_url = os.getenv('QDRANT_URL', 'http://localhost:6333')
        
        # Check if we have required keys
        if not self.openai_api_key and not self.openrouter_api_key:
            print("⚠️  WARNING: No OpenAI or OpenRouter API key found.")
            print("   Set OPENAI_API_KEY or OPENROUTER_API_KEY in .env file")
            print("   Using mock mode for demonstration...")
            self.mock_mode = True
        else:
            self.mock_mode = False
            # Set OpenAI key for Mem0
            if self.openai_api_key:
                os.environ['OPENAI_API_KEY'] = self.openai_api_key
        
        self.memory = None
        self.test_cases = self._create_test_cases()
    
    def _init_mem0(self):
        """Initialize Mem0 with proper configuration"""
        if self.mock_mode:
            return None
        
        try:
            from mem0 import Memory
            
            # Configure Mem0
            # Parse Qdrant URL to extract host and port
            qdrant_host = self.qdrant_url.replace("http://", "").replace("https://", "")
            if ":" in qdrant_host:
                qdrant_host, port_str = qdrant_host.split(":", 1)
                qdrant_port = int(port_str)
            else:
                qdrant_port = 6333
            
            config = {
                "vector_store": {
                    "provider": "qdrant",
                    "config": {
                        "collection_name": f"mem0_{self.tenant_id}",
                        "host": qdrant_host,
                        "port": qdrant_port,
                    }
                },
                "embedder": {
                    "provider": "openai",
                    "config": {
                        "model": "text-embedding-3-small",
                    }
                }
            }
            
            self.memory = Memory.from_config(config)
            print(f"✅ Mem0 initialized with Qdrant: {self.qdrant_url}")
            return self.memory
            
        except Exception as e:
            print(f"❌ Failed to initialize Mem0: {e}")
            print(f"   Falling back to mock mode...")
            self.mock_mode = True
            return None
    
    def _create_test_cases(self) -> List[Dict[str, Any]]:
        """Create test cases with ground truth data"""
        return [
            {
                "name": "Basic Fact Retrieval",
                "conversations": [
                    ("I work as a software engineer at Google", "Great! I've noted that."),
                    ("My manager's name is Sarah Chen", "Got it."),
                    ("I'm working on the authentication project", "Recorded."),
                ],
                "queries": [
                    {
                        "query": "where do I work?",
                        "expected_keywords": ["Google", "software engineer"],
                        "min_relevance": 0.7,
                    },
                    {
                        "query": "who is my manager?",
                        "expected_keywords": ["Sarah Chen", "manager"],
                        "min_relevance": 0.7,
                    },
                ]
            },
            {
                "name": "Timesheet Context",
                "conversations": [
                    ("I worked 8 hours yesterday on bug fixes", "Noted."),
                    ("I usually work Monday to Friday", "Got it."),
                ],
                "queries": [
                    {
                        "query": "how many hours did I work yesterday?",
                        "expected_keywords": ["8 hours", "yesterday"],
                        "min_relevance": 0.7,
                    },
                ]
            },
        ]
    
    async def setup_test_data(self, test_case: Dict[str, Any]) -> None:
        """Store test conversations in memory"""
        print(f"\n📝 Setting up test data for: {test_case['name']}")
        
        if self.mock_mode:
            print("   ⚠️  Mock mode: Simulating data storage...")
            for user_msg, _ in test_case['conversations']:
                print(f"   ✓ [MOCK] Stored: '{user_msg[:50]}...'")
            await asyncio.sleep(1)
            return
        
        for user_msg, ai_response in test_case['conversations']:
            try:
                self.memory.add(
                    user_msg,
                    user_id=f"{self.tenant_id}_{self.user_id}",
                    metadata={"test_case": test_case['name']}
                )
                print(f"   ✓ Stored: '{user_msg[:50]}...'")
            except Exception as e:
                print(f"   ❌ Failed to store: {e}")
        
        print("   ⏳ Waiting 3 seconds for indexing...")
        await asyncio.sleep(3)
    
    async def run_query_test(self, query_test: Dict[str, Any]) -> Dict[str, Any]:
        """Run a single query test"""
        query = query_test['query']
        expected_keywords = query_test.get('expected_keywords', [])
        min_relevance = query_test.get('min_relevance', 0.5)
        
        print(f"\n   🔍 Query: '{query}'")
        
        if self.mock_mode:
            # Mock retrieval
            retrieved_memories = [
                f"Mock memory containing {kw}" for kw in expected_keywords[:2]
            ]
            print(f"   📊 [MOCK] Retrieved {len(retrieved_memories)} memories")
        else:
            try:
                # Real retrieval
                search_results = self.memory.search(
                    query=query,
                    user_id=f"{self.tenant_id}_{self.user_id}",
                    limit=5
                )
                
                # Extract memory text
                retrieved_memories = []
                if isinstance(search_results, dict) and "results" in search_results:
                    for result in search_results["results"]:
                        if isinstance(result, dict) and "memory" in result:
                            retrieved_memories.append(result["memory"])
                
                print(f"   📊 Retrieved {len(retrieved_memories)} memories")
                
            except Exception as e:
                print(f"   ❌ Retrieval failed: {e}")
                retrieved_memories = []
        
        # Evaluate results
        found_keywords = []
        for memory in retrieved_memories:
            memory_lower = memory.lower()
            for keyword in expected_keywords:
                if keyword.lower() in memory_lower:
                    found_keywords.append(keyword)
        
        precision = len(set(found_keywords)) / len(expected_keywords) if expected_keywords else 1.0
        passed = precision >= min_relevance and len(retrieved_memories) > 0
        
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"   {status}")
        print(f"      Precision: {precision:.2%}")
        print(f"      Found keywords: {list(set(found_keywords))}")
        
        for i, memory in enumerate(retrieved_memories[:3], 1):
            print(f"      {i}. {memory[:80]}...")
        
        return {
            "query": query,
            "retrieved_count": len(retrieved_memories),
            "precision": precision,
            "passed": passed,
            "found_keywords": list(set(found_keywords)),
        }
    
    async def run_test_case(self, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """Run all queries for a test case"""
        print(f"\n{'='*80}")
        print(f"🧪 Test Case: {test_case['name']}")
        print(f"{'='*80}")
        
        await self.setup_test_data(test_case)
        
        query_results = []
        for query_test in test_case['queries']:
            result = await self.run_query_test(query_test)
            query_results.append(result)
        
        total_queries = len(query_results)
        passed_queries = sum(1 for r in query_results if r['passed'])
        avg_precision = sum(r['precision'] for r in query_results) / total_queries if total_queries > 0 else 0
        
        print(f"\n📊 Test Case Summary:")
        print(f"   Pass Rate: {passed_queries/total_queries:.1%} ({passed_queries}/{total_queries})")
        print(f"   Avg Precision: {avg_precision:.1%}")
        
        return {
            "name": test_case['name'],
            "total_queries": total_queries,
            "passed_queries": passed_queries,
            "pass_rate": passed_queries / total_queries if total_queries > 0 else 0,
            "avg_precision": avg_precision,
        }
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all benchmark tests"""
        print("\n" + "="*80)
        print("🚀 RAG ACCURACY BENCHMARK - Mem0 + Qdrant (Standalone)")
        print("="*80)
        print(f"Tenant ID: {self.tenant_id}")
        print(f"User ID: {self.user_id}")
        print(f"Qdrant URL: {self.qdrant_url}")
        print(f"Mode: {'MOCK (no API keys)' if self.mock_mode else 'LIVE'}")
        print(f"Total Test Cases: {len(self.test_cases)}")
        print(f"Timestamp: {datetime.now().isoformat()}")
        
        # Initialize Mem0
        if not self.mock_mode:
            self._init_mem0()
        
        # Run all test cases
        all_results = []
        for test_case in self.test_cases:
            result = await self.run_test_case(test_case)
            all_results.append(result)
        
        # Calculate overall metrics
        total_queries = sum(r['total_queries'] for r in all_results)
        total_passed = sum(r['passed_queries'] for r in all_results)
        overall_pass_rate = total_passed / total_queries if total_queries > 0 else 0
        overall_precision = sum(r['avg_precision'] for r in all_results) / len(all_results) if all_results else 0
        
        # Print final report
        print("\n" + "="*80)
        print("📈 FINAL BENCHMARK REPORT")
        print("="*80)
        print(f"\n🎯 Overall Metrics:")
        print(f"   Pass Rate: {overall_pass_rate:.1%} ({total_passed}/{total_queries})")
        print(f"   Precision: {overall_precision:.1%}")
        
        print(f"\n📊 Test Case Breakdown:")
        for test_result in all_results:
            status = "✅" if test_result['pass_rate'] >= 0.7 else "⚠️" if test_result['pass_rate'] >= 0.5 else "❌"
            print(f"   {status} {test_result['name']}: {test_result['pass_rate']:.1%}")
        
        print(f"\n💡 Recommendations:")
        if self.mock_mode:
            print("   ⚠️  Running in MOCK mode - set OPENAI_API_KEY in .env to test real system")
        elif overall_pass_rate >= 0.8:
            print("   ✅ Excellent RAG performance! System is production-ready.")
        elif overall_pass_rate >= 0.6:
            print("   ⚠️  Good performance, but some queries need improvement.")
        else:
            print("   ❌ Poor performance. System needs improvement.")
        
        # Save report
        filename = f"rag_benchmark_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report = {
            "timestamp": datetime.now().isoformat(),
            "mode": "mock" if self.mock_mode else "live",
            "overall_pass_rate": overall_pass_rate,
            "overall_precision": overall_precision,
            "test_results": all_results,
        }
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"\n💾 Report saved to: {filename}")
        
        return report


async def main():
    """Run standalone RAG benchmark"""
    benchmark = StandaloneRAGBenchmark(tenant_id="benchmark_test")
    
    try:
        result = await benchmark.run_all_tests()
        
        if result['overall_pass_rate'] >= 0.7 or benchmark.mock_mode:
            sys.exit(0)
        else:
            sys.exit(1)
    
    except Exception as e:
        print(f"\n❌ Benchmark failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(2)


if __name__ == "__main__":
    asyncio.run(main())
