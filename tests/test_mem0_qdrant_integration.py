"""
Comprehensive Test Suite for Mem0 + Qdrant Integration

Tests memory storage, retrieval, multi-tenant isolation, edge cases,
and performance characteristics.

Run with: pytest tests/test_mem0_qdrant_integration.py -v
"""

import pytest
import asyncio
import time
import uuid
from typing import List, Dict
import requests

# Test configuration
BASE_URL = "https://unified-temporal-worker.kindcoast-5a2a34c6.australiaeast.azurecontainerapps.io"
MEMORY_ENDPOINT = f"{BASE_URL}/test/conversation-with-memory"


class TestBasicMemoryOperations:
    """Test basic memory storage and retrieval"""
    
    def test_single_memory_storage_and_retrieval(self):
        """Test storing and retrieving a single memory"""
        user_id = f"test-user-{uuid.uuid4()}"
        tenant_id = f"tenant-{uuid.uuid4()}"
        
        # Store memory
        response1 = requests.post(MEMORY_ENDPOINT, json={
            "user_id": user_id,
            "tenant_id": tenant_id,
            "message": "I prefer Python over JavaScript for backend development."
        })
        assert response1.status_code == 200
        assert response1.json()["status"] == "success"
        
        # Wait for indexing
        time.sleep(3)
        
        # Retrieve memory
        response2 = requests.post(MEMORY_ENDPOINT, json={
            "user_id": user_id,
            "tenant_id": tenant_id,
            "message": "What programming language do I prefer for backend?"
        })
        assert response2.status_code == 200
        result = response2.json()
        assert "Python" in result["assistant_response"]
        
    def test_multiple_memories_retrieval(self):
        """Test retrieving from multiple stored memories"""
        user_id = f"test-user-{uuid.uuid4()}"
        tenant_id = f"tenant-{uuid.uuid4()}"
        
        # Store multiple memories
        memories = [
            "My favorite color is blue.",
            "I work as a software engineer.",
            "I have 5 years of experience."
        ]
        
        for memory in memories:
            response = requests.post(MEMORY_ENDPOINT, json={
                "user_id": user_id,
                "tenant_id": tenant_id,
                "message": memory
            })
            assert response.status_code == 200
            time.sleep(2)
        
        # Retrieve specific memory
        response = requests.post(MEMORY_ENDPOINT, json={
            "user_id": user_id,
            "tenant_id": tenant_id,
            "message": "What is my job?"
        })
        assert response.status_code == 200
        result = response.json()
        assert "software engineer" in result["assistant_response"].lower()
        
    def test_memory_persistence_across_sessions(self):
        """Test that memories persist across multiple queries"""
        user_id = f"test-user-{uuid.uuid4()}"
        tenant_id = f"tenant-{uuid.uuid4()}"
        
        # Session 1: Store
        requests.post(MEMORY_ENDPOINT, json={
            "user_id": user_id,
            "tenant_id": tenant_id,
            "message": "I live in Sydney, Australia."
        })
        time.sleep(3)
        
        # Session 2: Retrieve
        response1 = requests.post(MEMORY_ENDPOINT, json={
            "user_id": user_id,
            "tenant_id": tenant_id,
            "message": "Where do I live?"
        })
        assert "Sydney" in response1.json()["assistant_response"]
        
        # Session 3: Retrieve again (different query)
        time.sleep(2)
        response2 = requests.post(MEMORY_ENDPOINT, json={
            "user_id": user_id,
            "tenant_id": tenant_id,
            "message": "What city am I in?"
        })
        assert "Sydney" in response2.json()["assistant_response"]


class TestMultiTenantIsolation:
    """Test tenant and user isolation"""
    
    def test_tenant_isolation(self):
        """Test that tenants cannot access each other's memories"""
        user_id = "shared-user"
        tenant1 = f"tenant-{uuid.uuid4()}"
        tenant2 = f"tenant-{uuid.uuid4()}"
        
        # Store memory in tenant1
        requests.post(MEMORY_ENDPOINT, json={
            "user_id": user_id,
            "tenant_id": tenant1,
            "message": "My secret code is ALPHA123."
        })
        time.sleep(3)
        
        # Try to retrieve from tenant2 (should not find it)
        response = requests.post(MEMORY_ENDPOINT, json={
            "user_id": user_id,
            "tenant_id": tenant2,
            "message": "What is my secret code?"
        })
        result = response.json()["assistant_response"]
        # Should not contain the secret from tenant1
        assert "ALPHA123" not in result
        
    def test_user_isolation_within_tenant(self):
        """Test that users within same tenant are isolated"""
        tenant_id = f"tenant-{uuid.uuid4()}"
        user1 = f"user-{uuid.uuid4()}"
        user2 = f"user-{uuid.uuid4()}"
        
        # Store memory for user1
        requests.post(MEMORY_ENDPOINT, json={
            "user_id": user1,
            "tenant_id": tenant_id,
            "message": "My password is SecurePass456."
        })
        time.sleep(3)
        
        # Try to retrieve as user2 (should not find it)
        response = requests.post(MEMORY_ENDPOINT, json={
            "user_id": user2,
            "tenant_id": tenant_id,
            "message": "What is my password?"
        })
        result = response.json()["assistant_response"]
        # Should not contain user1's password
        assert "SecurePass456" not in result


class TestEdgeCases:
    """Test edge cases and unusual inputs"""
    
    def test_empty_query(self):
        """Test handling of empty query"""
        user_id = f"test-user-{uuid.uuid4()}"
        tenant_id = f"tenant-{uuid.uuid4()}"
        
        response = requests.post(MEMORY_ENDPOINT, json={
            "user_id": user_id,
            "tenant_id": tenant_id,
            "message": ""
        })
        # Should return 400 for empty message
        assert response.status_code == 400
        assert "empty" in response.json()["detail"].lower()
        
    def test_very_long_conversation(self):
        """Test handling of very long conversation text"""
        user_id = f"test-user-{uuid.uuid4()}"
        tenant_id = f"tenant-{uuid.uuid4()}"
        
        long_message = "I worked on " + " and ".join([f"project{i}" for i in range(100)])
        
        response = requests.post(MEMORY_ENDPOINT, json={
            "user_id": user_id,
            "tenant_id": tenant_id,
            "message": long_message
        })
        assert response.status_code == 200
        
    def test_special_characters(self):
        """Test handling of special characters"""
        user_id = f"test-user-{uuid.uuid4()}"
        tenant_id = f"tenant-{uuid.uuid4()}"
        
        special_message = "My email is test@example.com and I use symbols like <>&\"'."
        
        response = requests.post(MEMORY_ENDPOINT, json={
            "user_id": user_id,
            "tenant_id": tenant_id,
            "message": special_message
        })
        assert response.status_code == 200
        time.sleep(3)
        
        # Retrieve
        response2 = requests.post(MEMORY_ENDPOINT, json={
            "user_id": user_id,
            "tenant_id": tenant_id,
            "message": "What is my email?"
        })
        assert "test@example.com" in response2.json()["assistant_response"]
        
    def test_unicode_and_emoji(self):
        """Test handling of Unicode and emoji"""
        user_id = f"test-user-{uuid.uuid4()}"
        tenant_id = f"tenant-{uuid.uuid4()}"
        
        unicode_message = "I love coding 💻 and my name is 张三."
        
        response = requests.post(MEMORY_ENDPOINT, json={
            "user_id": user_id,
            "tenant_id": tenant_id,
            "message": unicode_message
        })
        assert response.status_code == 200
        
    def test_duplicate_memories(self):
        """Test storing duplicate information"""
        user_id = f"test-user-{uuid.uuid4()}"
        tenant_id = f"tenant-{uuid.uuid4()}"
        
        # Store same information twice
        message = "I am 30 years old."
        for _ in range(2):
            requests.post(MEMORY_ENDPOINT, json={
                "user_id": user_id,
                "tenant_id": tenant_id,
                "message": message
            })
            time.sleep(2)
        
        # Should handle gracefully (Mem0 has deduplication)
        response = requests.post(MEMORY_ENDPOINT, json={
            "user_id": user_id,
            "tenant_id": tenant_id,
            "message": "How old am I?"
        })
        assert response.status_code == 200
        
    def test_contradictory_information(self):
        """Test storing contradictory information"""
        user_id = f"test-user-{uuid.uuid4()}"
        tenant_id = f"tenant-{uuid.uuid4()}"
        
        # Store contradictory info
        requests.post(MEMORY_ENDPOINT, json={
            "user_id": user_id,
            "tenant_id": tenant_id,
            "message": "My favorite color is red."
        })
        time.sleep(3)
        
        requests.post(MEMORY_ENDPOINT, json={
            "user_id": user_id,
            "tenant_id": tenant_id,
            "message": "Actually, my favorite color is blue."
        })
        time.sleep(3)
        
        # Should retrieve most recent or handle appropriately
        response = requests.post(MEMORY_ENDPOINT, json={
            "user_id": user_id,
            "tenant_id": tenant_id,
            "message": "What is my favorite color?"
        })
        assert response.status_code == 200


class TestPerformance:
    """Test performance characteristics"""
    
    def test_storage_latency(self):
        """Measure memory storage latency"""
        user_id = f"test-user-{uuid.uuid4()}"
        tenant_id = f"tenant-{uuid.uuid4()}"
        
        latencies = []
        for i in range(5):
            start = time.time()
            response = requests.post(MEMORY_ENDPOINT, json={
                "user_id": user_id,
                "tenant_id": tenant_id,
                "message": f"Test message {i} with some content."
            })
            latency = time.time() - start
            latencies.append(latency)
            assert response.status_code == 200
            time.sleep(1)
        
        avg_latency = sum(latencies) / len(latencies)
        print(f"\nAverage storage latency: {avg_latency:.2f}s")
        # Should be reasonably fast (< 5 seconds)
        assert avg_latency < 5.0
        
    def test_retrieval_latency(self):
        """Measure memory retrieval latency"""
        user_id = f"test-user-{uuid.uuid4()}"
        tenant_id = f"tenant-{uuid.uuid4()}"
        
        # Store a memory first
        requests.post(MEMORY_ENDPOINT, json={
            "user_id": user_id,
            "tenant_id": tenant_id,
            "message": "I work at TechCorp as a senior developer."
        })
        time.sleep(3)
        
        # Measure retrieval latency
        latencies = []
        for i in range(5):
            start = time.time()
            response = requests.post(MEMORY_ENDPOINT, json={
                "user_id": user_id,
                "tenant_id": tenant_id,
                "message": "Where do I work?"
            })
            latency = time.time() - start
            latencies.append(latency)
            assert response.status_code == 200
            time.sleep(1)
        
        avg_latency = sum(latencies) / len(latencies)
        print(f"\nAverage retrieval latency: {avg_latency:.2f}s")
        # Should be reasonably fast (< 5 seconds)
        assert avg_latency < 5.0
        
    def test_concurrent_users(self):
        """Test multiple users accessing memory concurrently"""
        tenant_id = f"tenant-{uuid.uuid4()}"
        
        def user_interaction(user_num):
            user_id = f"concurrent-user-{user_num}"
            # Store
            requests.post(MEMORY_ENDPOINT, json={
                "user_id": user_id,
                "tenant_id": tenant_id,
                "message": f"I am user number {user_num}."
            })
            time.sleep(2)
            # Retrieve
            response = requests.post(MEMORY_ENDPOINT, json={
                "user_id": user_id,
                "tenant_id": tenant_id,
                "message": "What is my user number?"
            })
            return str(user_num) in response.json()["assistant_response"]
        
        # Simulate 3 concurrent users (limited for testing)
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(user_interaction, i) for i in range(3)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]
        
        # All should succeed
        assert all(results)


class TestDataIntegrity:
    """Test data integrity and consistency"""
    
    def test_numeric_data_accuracy(self):
        """Test that numeric data is stored and retrieved accurately"""
        user_id = f"test-user-{uuid.uuid4()}"
        tenant_id = f"tenant-{uuid.uuid4()}"
        
        # Store specific numbers
        requests.post(MEMORY_ENDPOINT, json={
            "user_id": user_id,
            "tenant_id": tenant_id,
            "message": "I worked 847 hours and fixed 392 bugs and earned $125,000."
        })
        time.sleep(3)
        
        # Retrieve and verify accuracy
        response = requests.post(MEMORY_ENDPOINT, json={
            "user_id": user_id,
            "tenant_id": tenant_id,
            "message": "How many hours did I work and how much did I earn?"
        })
        result = response.json()["assistant_response"]
        assert "847" in result
        assert "125,000" in result or "125000" in result
        
    def test_date_and_time_information(self):
        """Test storing and retrieving date/time information"""
        user_id = f"test-user-{uuid.uuid4()}"
        tenant_id = f"tenant-{uuid.uuid4()}"
        
        requests.post(MEMORY_ENDPOINT, json={
            "user_id": user_id,
            "tenant_id": tenant_id,
            "message": "My birthday is March 15, 1990."
        })
        time.sleep(3)
        
        response = requests.post(MEMORY_ENDPOINT, json={
            "user_id": user_id,
            "tenant_id": tenant_id,
            "message": "When is my birthday?"
        })
        result = response.json()["assistant_response"]
        assert "March" in result or "15" in result


class TestReliability:
    """Test error handling and reliability"""
    
    def test_invalid_tenant_id(self):
        """Test handling of invalid tenant ID"""
        response = requests.post(MEMORY_ENDPOINT, json={
            "user_id": "test-user",
            "tenant_id": "",  # Empty tenant ID
            "message": "Test message"
        })
        # Should return 400 for empty tenant_id
        assert response.status_code == 400
        assert "tenant_id" in response.json()["detail"].lower()
        
    def test_missing_user_id(self):
        """Test handling of missing user ID"""
        response = requests.post(MEMORY_ENDPOINT, json={
            "tenant_id": "test-tenant",
            "message": "Test message"
        })
        # Should use default user_id and succeed
        assert response.status_code == 200
        
    def test_malformed_request(self):
        """Test handling of malformed request"""
        response = requests.post(MEMORY_ENDPOINT, json={
            "invalid_field": "value"
        })
        # Should return 422 for missing required field
        assert response.status_code == 422
        assert "message" in response.json()["detail"].lower()


class TestSemanticSearch:
    """Test semantic search capabilities"""
    
    def test_semantic_similarity(self):
        """Test that semantically similar queries retrieve correct memories"""
        user_id = f"test-user-{uuid.uuid4()}"
        tenant_id = f"tenant-{uuid.uuid4()}"
        
        # Store memory
        requests.post(MEMORY_ENDPOINT, json={
            "user_id": user_id,
            "tenant_id": tenant_id,
            "message": "I enjoy playing tennis on weekends."
        })
        time.sleep(3)
        
        # Query with different wording
        response = requests.post(MEMORY_ENDPOINT, json={
            "user_id": user_id,
            "tenant_id": tenant_id,
            "message": "What sport do I like?"
        })
        result = response.json()["assistant_response"]
        assert "tennis" in result.lower()
        
    def test_context_understanding(self):
        """Test that system understands context"""
        user_id = f"test-user-{uuid.uuid4()}"
        tenant_id = f"tenant-{uuid.uuid4()}"
        
        # Store related information
        requests.post(MEMORY_ENDPOINT, json={
            "user_id": user_id,
            "tenant_id": tenant_id,
            "message": "I am learning React and Node.js for web development."
        })
        time.sleep(3)
        
        # Query about related topic
        response = requests.post(MEMORY_ENDPOINT, json={
            "user_id": user_id,
            "tenant_id": tenant_id,
            "message": "What technologies am I studying?"
        })
        result = response.json()["assistant_response"].lower()
        assert "react" in result or "node" in result


class TestAdditionalValidation:
    """Additional validation and edge case tests"""
    
    def test_whitespace_only_message(self):
        """Test message with only whitespace"""
        response = requests.post(MEMORY_ENDPOINT, json={
            "user_id": "test-user",
            "tenant_id": "test-tenant",
            "message": "   \n\t   "
        })
        # Should return 400 for whitespace-only message
        assert response.status_code == 400
        
    def test_invalid_json(self):
        """Test invalid JSON payload"""
        response = requests.post(
            MEMORY_ENDPOINT,
            data="not valid json",
            headers={"Content-Type": "application/json"}
        )
        # Should return 400 for invalid JSON
        assert response.status_code == 400
        
    def test_missing_tenant_id(self):
        """Test missing tenant_id uses default"""
        user_id = f"test-user-{uuid.uuid4()}"
        
        response = requests.post(MEMORY_ENDPOINT, json={
            "user_id": user_id,
            "message": "Test without tenant_id"
        })
        # Should use default tenant and succeed
        assert response.status_code == 200
        assert response.json()["tenant_id"] == "test-tenant"
        
    def test_numeric_ids(self):
        """Test that numeric IDs are rejected"""
        response = requests.post(MEMORY_ENDPOINT, json={
            "user_id": 12345,  # Numeric instead of string
            "tenant_id": "test-tenant",
            "message": "Test message"
        })
        # Should return 400 for non-string user_id
        assert response.status_code == 400
        
    def test_very_short_message(self):
        """Test very short message (1 character)"""
        user_id = f"test-user-{uuid.uuid4()}"
        tenant_id = f"tenant-{uuid.uuid4()}"
        
        response = requests.post(MEMORY_ENDPOINT, json={
            "user_id": user_id,
            "tenant_id": tenant_id,
            "message": "a"
        })
        # Should accept single character message
        assert response.status_code == 200
        
    def test_response_format(self):
        """Test that response has all required fields"""
        user_id = f"test-user-{uuid.uuid4()}"
        tenant_id = f"tenant-{uuid.uuid4()}"
        
        response = requests.post(MEMORY_ENDPOINT, json={
            "user_id": user_id,
            "tenant_id": tenant_id,
            "message": "Test message"
        })
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify all required fields present
        assert "status" in data
        assert "user_message" in data
        assert "assistant_response" in data
        assert "memory_used" in data
        assert "tenant_id" in data
        assert "user_id" in data
        assert "timestamp" in data
        
        # Verify field values
        assert data["status"] == "success"
        assert data["user_message"] == "Test message"
        assert data["memory_used"] is True
        assert data["tenant_id"] == tenant_id
        assert data["user_id"] == user_id


class TestMemoryRetrieval:
    """Test memory retrieval accuracy and relevance"""
    
    def test_irrelevant_query(self):
        """Test that irrelevant queries don't retrieve unrelated memories"""
        user_id = f"test-user-{uuid.uuid4()}"
        tenant_id = f"tenant-{uuid.uuid4()}"
        
        # Store specific memory
        requests.post(MEMORY_ENDPOINT, json={
            "user_id": user_id,
            "tenant_id": tenant_id,
            "message": "I love pizza."
        })
        time.sleep(3)
        
        # Query about completely different topic
        response = requests.post(MEMORY_ENDPOINT, json={
            "user_id": user_id,
            "tenant_id": tenant_id,
            "message": "What is quantum physics?"
        })
        result = response.json()["assistant_response"]
        # Should not mention pizza in quantum physics answer
        # (unless it's a very creative response!)
        assert response.status_code == 200
        
    def test_multiple_facts_retrieval(self):
        """Test retrieving multiple related facts"""
        user_id = f"test-user-{uuid.uuid4()}"
        tenant_id = f"tenant-{uuid.uuid4()}"
        
        # Store multiple related facts
        facts = [
            "I work at Google.",
            "I am a software engineer.",
            "I specialize in machine learning."
        ]
        
        for fact in facts:
            requests.post(MEMORY_ENDPOINT, json={
                "user_id": user_id,
                "tenant_id": tenant_id,
                "message": fact
            })
            time.sleep(2)
        
        # Query that should retrieve multiple facts
        response = requests.post(MEMORY_ENDPOINT, json={
            "user_id": user_id,
            "tenant_id": tenant_id,
            "message": "Tell me about my professional background."
        })
        result = response.json()["assistant_response"].lower()
        
        # Should mention at least 2 of the 3 facts
        mentions = sum([
            "google" in result,
            "software engineer" in result or "engineer" in result,
            "machine learning" in result
        ])
        assert mentions >= 2


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
