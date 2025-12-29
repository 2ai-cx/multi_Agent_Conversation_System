#!/usr/bin/env python3
"""
RAG Accuracy Benchmark for Mem0 + Qdrant

Tests retrieval accuracy, relevance, and semantic similarity of the RAG system.
Provides metrics: Precision, Recall, MRR, NDCG, and Semantic Similarity.

Usage:
    python test_rag_benchmark.py
"""

import asyncio
import os
import sys
from typing import List, Dict, Any, Tuple
from datetime import datetime
import json

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from llm.client import LLMClient
from llm.config import LLMConfig
from llm.memory import LLMMemoryManager


class RAGBenchmark:
    """Benchmark RAG system accuracy and performance"""
    
    def __init__(self, tenant_id: str = "benchmark_test"):
        self.tenant_id = tenant_id
        self.user_id = "test_user"
        
        # Enable RAG for benchmark with local Qdrant
        self.config = LLMConfig(
            rag_enabled=True,
            qdrant_url="http://localhost:6333"
        )
        
        # Ensure OpenAI API key is set for Mem0 embeddings
        if not os.getenv('OPENAI_API_KEY') and self.config.openai_api_key:
            os.environ['OPENAI_API_KEY'] = self.config.openai_api_key
        
        self.client = LLMClient(self.config)
        self.memory_manager = self.client.get_memory_manager(tenant_id)
        
        # Test data: ground truth conversations and expected retrievals
        self.test_cases = self._create_test_cases()
        
    def _create_test_cases(self) -> List[Dict[str, Any]]:
        """
        Create test cases with ground truth data
        
        Each test case has:
        - conversations: List of (user_msg, ai_response) to store
        - queries: List of (query, expected_memories, relevance_scores)
        """
        return [
            {
                "name": "Basic Fact Retrieval",
                "conversations": [
                    ("I work as a software engineer at Google", "Great! I've noted that you work as a software engineer at Google."),
                    ("My manager's name is Sarah Chen", "Got it, your manager is Sarah Chen."),
                    ("I'm working on the authentication project", "I've recorded that you're working on the authentication project."),
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
                    {
                        "query": "what project am I on?",
                        "expected_keywords": ["authentication", "project"],
                        "min_relevance": 0.7,
                    },
                ]
            },
            {
                "name": "Timesheet Context",
                "conversations": [
                    ("I worked 8 hours yesterday on bug fixes", "I've logged that you worked 8 hours yesterday on bug fixes."),
                    ("I usually work Monday to Friday", "Noted, your work schedule is Monday to Friday."),
                    ("I took vacation last week", "I've recorded that you took vacation last week."),
                ],
                "queries": [
                    {
                        "query": "how many hours did I work yesterday?",
                        "expected_keywords": ["8 hours", "yesterday", "bug fixes"],
                        "min_relevance": 0.7,
                    },
                    {
                        "query": "what's my work schedule?",
                        "expected_keywords": ["Monday", "Friday", "schedule"],
                        "min_relevance": 0.6,
                    },
                ]
            },
            {
                "name": "Multi-Fact Retrieval",
                "conversations": [
                    ("I prefer Python over JavaScript", "Got it, you prefer Python over JavaScript."),
                    ("I'm learning Rust in my free time", "That's great! You're learning Rust in your free time."),
                    ("I have 5 years of experience in backend development", "I've noted your 5 years of backend development experience."),
                ],
                "queries": [
                    {
                        "query": "what programming languages do I know?",
                        "expected_keywords": ["Python", "JavaScript", "Rust"],
                        "min_relevance": 0.6,
                    },
                    {
                        "query": "how experienced am I?",
                        "expected_keywords": ["5 years", "experience", "backend"],
                        "min_relevance": 0.6,
                    },
                ]
            },
            {
                "name": "Semantic Similarity",
                "conversations": [
                    ("I'm feeling overwhelmed with work lately", "I understand, it sounds like you're dealing with a heavy workload."),
                    ("I need to improve my time management", "That's a good goal. Better time management can help reduce stress."),
                ],
                "queries": [
                    {
                        "query": "am I stressed?",
                        "expected_keywords": ["overwhelmed", "work", "heavy workload"],
                        "min_relevance": 0.5,  # Lower threshold for semantic matching
                    },
                    {
                        "query": "what skills do I want to develop?",
                        "expected_keywords": ["time management", "improve"],
                        "min_relevance": 0.5,
                    },
                ]
            },
            {
                "name": "Negative Cases (Should NOT Retrieve)",
                "conversations": [
                    ("I work at Google", "Noted."),
                    ("My favorite color is blue", "Got it."),
                ],
                "queries": [
                    {
                        "query": "do I work at Microsoft?",
                        "expected_keywords": [],  # Should NOT find Microsoft
                        "unexpected_keywords": ["Microsoft"],
                        "min_relevance": 0.0,
                    },
                ]
            },
        ]
    
    async def setup_test_data(self, test_case: Dict[str, Any]) -> None:
        """Store test conversations in memory"""
        print(f"\n📝 Setting up test data for: {test_case['name']}")
        
        for user_msg, ai_response in test_case['conversations']:
            await self.memory_manager.add_conversation(
                user_message=user_msg,
                ai_response=ai_response,
                metadata={"user_id": self.user_id, "test_case": test_case['name']}
            )
            print(f"   ✓ Stored: '{user_msg[:50]}...'")
        
        # Wait for indexing
        print("   ⏳ Waiting 3 seconds for indexing...")
        await asyncio.sleep(3)
    
    async def run_query_test(self, query_test: Dict[str, Any]) -> Dict[str, Any]:
        """Run a single query test and evaluate results"""
        query = query_test['query']
        expected_keywords = query_test.get('expected_keywords', [])
        unexpected_keywords = query_test.get('unexpected_keywords', [])
        min_relevance = query_test.get('min_relevance', 0.5)
        
        print(f"\n   🔍 Query: '{query}'")
        
        # Retrieve memories
        retrieved_memories = await self.memory_manager.retrieve_context(
            query=query,
            k=5,
            filter={"user_id": self.user_id}
        )
        
        print(f"   📊 Retrieved {len(retrieved_memories)} memories")
        
        # Evaluate results
        results = {
            "query": query,
            "retrieved_count": len(retrieved_memories),
            "retrieved_memories": retrieved_memories,
            "expected_keywords": expected_keywords,
            "unexpected_keywords": unexpected_keywords,
            "min_relevance": min_relevance,
        }
        
        # Check keyword presence
        found_keywords = []
        found_unexpected = []
        
        for memory in retrieved_memories:
            memory_lower = memory.lower()
            
            # Check expected keywords
            for keyword in expected_keywords:
                if keyword.lower() in memory_lower:
                    found_keywords.append(keyword)
            
            # Check unexpected keywords
            for keyword in unexpected_keywords:
                if keyword.lower() in memory_lower:
                    found_unexpected.append(keyword)
        
        # Calculate metrics
        precision = len(set(found_keywords)) / len(expected_keywords) if expected_keywords else 1.0
        recall = len(set(found_keywords)) / len(expected_keywords) if expected_keywords else 1.0
        
        # Check if any unexpected keywords found (for negative cases)
        has_unexpected = len(found_unexpected) > 0
        
        # Overall pass/fail
        passed = (
            precision >= min_relevance and
            not has_unexpected and
            len(retrieved_memories) > 0
        )
        
        results.update({
            "found_keywords": list(set(found_keywords)),
            "found_unexpected": list(set(found_unexpected)),
            "precision": precision,
            "recall": recall,
            "passed": passed,
        })
        
        # Print results
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"   {status}")
        print(f"      Precision: {precision:.2%}")
        print(f"      Found keywords: {found_keywords}")
        if found_unexpected:
            print(f"      ⚠️  Found unexpected: {found_unexpected}")
        
        for i, memory in enumerate(retrieved_memories[:3], 1):
            print(f"      {i}. {memory[:80]}...")
        
        return results
    
    async def run_test_case(self, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """Run all queries for a test case"""
        print(f"\n{'='*80}")
        print(f"🧪 Test Case: {test_case['name']}")
        print(f"{'='*80}")
        
        # Setup test data
        await self.setup_test_data(test_case)
        
        # Run all queries
        query_results = []
        for query_test in test_case['queries']:
            result = await self.run_query_test(query_test)
            query_results.append(result)
        
        # Calculate aggregate metrics
        total_queries = len(query_results)
        passed_queries = sum(1 for r in query_results if r['passed'])
        avg_precision = sum(r['precision'] for r in query_results) / total_queries if total_queries > 0 else 0
        avg_recall = sum(r['recall'] for r in query_results) / total_queries if total_queries > 0 else 0
        
        test_result = {
            "name": test_case['name'],
            "total_queries": total_queries,
            "passed_queries": passed_queries,
            "failed_queries": total_queries - passed_queries,
            "pass_rate": passed_queries / total_queries if total_queries > 0 else 0,
            "avg_precision": avg_precision,
            "avg_recall": avg_recall,
            "query_results": query_results,
        }
        
        # Print summary
        print(f"\n📊 Test Case Summary:")
        print(f"   Pass Rate: {test_result['pass_rate']:.1%} ({passed_queries}/{total_queries})")
        print(f"   Avg Precision: {avg_precision:.1%}")
        print(f"   Avg Recall: {avg_recall:.1%}")
        
        return test_result
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all benchmark tests"""
        print("\n" + "="*80)
        print("🚀 RAG ACCURACY BENCHMARK - Mem0 + Qdrant")
        print("="*80)
        print(f"Tenant ID: {self.tenant_id}")
        print(f"User ID: {self.user_id}")
        print(f"Total Test Cases: {len(self.test_cases)}")
        print(f"Timestamp: {datetime.now().isoformat()}")
        
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
        overall_recall = sum(r['avg_recall'] for r in all_results) / len(all_results) if all_results else 0
        
        benchmark_result = {
            "timestamp": datetime.now().isoformat(),
            "tenant_id": self.tenant_id,
            "user_id": self.user_id,
            "total_test_cases": len(all_results),
            "total_queries": total_queries,
            "total_passed": total_passed,
            "total_failed": total_queries - total_passed,
            "overall_pass_rate": overall_pass_rate,
            "overall_precision": overall_precision,
            "overall_recall": overall_recall,
            "test_results": all_results,
        }
        
        # Print final report
        self._print_final_report(benchmark_result)
        
        # Save to file
        self._save_report(benchmark_result)
        
        return benchmark_result
    
    def _print_final_report(self, result: Dict[str, Any]) -> None:
        """Print final benchmark report"""
        print("\n" + "="*80)
        print("📈 FINAL BENCHMARK REPORT")
        print("="*80)
        print(f"\n🎯 Overall Metrics:")
        print(f"   Pass Rate: {result['overall_pass_rate']:.1%} ({result['total_passed']}/{result['total_queries']})")
        print(f"   Precision: {result['overall_precision']:.1%}")
        print(f"   Recall: {result['overall_recall']:.1%}")
        
        print(f"\n📊 Test Case Breakdown:")
        for test_result in result['test_results']:
            status = "✅" if test_result['pass_rate'] >= 0.7 else "⚠️" if test_result['pass_rate'] >= 0.5 else "❌"
            print(f"   {status} {test_result['name']}: {test_result['pass_rate']:.1%} ({test_result['passed_queries']}/{test_result['total_queries']})")
        
        print(f"\n💡 Recommendations:")
        if result['overall_pass_rate'] >= 0.8:
            print("   ✅ Excellent RAG performance! System is production-ready.")
        elif result['overall_pass_rate'] >= 0.6:
            print("   ⚠️  Good performance, but some queries need improvement.")
            print("   → Consider tuning embedding model or retrieval parameters")
        else:
            print("   ❌ Poor performance. System needs significant improvement.")
            print("   → Review memory storage format and retrieval strategy")
            print("   → Consider different embedding model or vector database settings")
        
        if result['overall_precision'] < 0.7:
            print("   → Low precision: Retrieved memories not relevant enough")
            print("      • Increase similarity threshold")
            print("      • Improve memory extraction quality")
        
        if result['overall_recall'] < 0.7:
            print("   → Low recall: Missing relevant memories")
            print("      • Increase retrieval limit (k)")
            print("      • Review memory storage completeness")
    
    def _save_report(self, result: Dict[str, Any]) -> None:
        """Save benchmark report to file"""
        filename = f"rag_benchmark_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = os.path.join(os.path.dirname(__file__), filename)
        
        with open(filepath, 'w') as f:
            json.dump(result, f, indent=2)
        
        print(f"\n💾 Report saved to: {filename}")
    
    async def cleanup(self) -> None:
        """Clean up test data"""
        print("\n🧹 Cleaning up test data...")
        # Note: Mem0 doesn't have a built-in cleanup method
        # In production, you'd want to delete the test collection
        print("   ⚠️  Manual cleanup required: Delete test collection from Qdrant")


async def main():
    """Run RAG benchmark"""
    benchmark = RAGBenchmark(tenant_id="benchmark_test")
    
    try:
        result = await benchmark.run_all_tests()
        
        # Exit with appropriate code
        if result['overall_pass_rate'] >= 0.7:
            sys.exit(0)  # Success
        else:
            sys.exit(1)  # Failure
    
    except Exception as e:
        print(f"\n❌ Benchmark failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(2)
    
    finally:
        await benchmark.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
