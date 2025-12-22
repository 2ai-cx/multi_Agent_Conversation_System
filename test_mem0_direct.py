"""
Direct Mem0 testing via API endpoint
Tests memory extraction and retrieval through the deployed service
"""

import requests
import time
import json
import uuid

BASE_URL = "https://unified-temporal-worker.kindcoast-5a2a34c6.australiaeast.azurecontainerapps.io"
ENDPOINT = f"{BASE_URL}/test/conversation-with-memory"

def test_case(name, user_msg, query, expected_keyword):
    """Run a single test case"""
    print(f"\n{'='*80}")
    print(f"TEST: {name}")
    print(f"{'='*80}")
    
    user_id = f"diag-{uuid.uuid4()}"
    tenant_id = f"tenant-{uuid.uuid4()}"
    
    # Store
    print(f"\n📝 STORING:")
    print(f"   Message: {user_msg}")
    
    r1 = requests.post(ENDPOINT, json={
        "user_id": user_id,
        "tenant_id": tenant_id,
        "message": user_msg
    })
    
    print(f"   Status: {r1.status_code}")
    if r1.status_code == 200:
        print(f"   Response: {r1.json()['assistant_response'][:100]}...")
    else:
        print(f"   Error: {r1.text}")
        return False
    
    # Wait for indexing
    print(f"\n⏳ Waiting 5 seconds for Mem0 indexing...")
    time.sleep(5)
    
    # Retrieve
    print(f"\n🔍 RETRIEVING:")
    print(f"   Query: {query}")
    print(f"   Expected keyword: {expected_keyword}")
    
    r2 = requests.post(ENDPOINT, json={
        "user_id": user_id,
        "tenant_id": tenant_id,
        "message": query
    })
    
    print(f"   Status: {r2.status_code}")
    if r2.status_code == 200:
        response = r2.json()['assistant_response']
        print(f"   Response: {response}")
        
        # Check if expected keyword is in response
        if expected_keyword.lower() in response.lower():
            print(f"   ✅ SUCCESS - Found '{expected_keyword}'")
            return True
        else:
            print(f"   ❌ FAILED - '{expected_keyword}' not found in response")
            return False
    else:
        print(f"   Error: {r2.text}")
        return False


def main():
    print("\n" + "="*80)
    print("MEM0 DIRECT API DIAGNOSTIC")
    print("="*80)
    
    test_cases = [
        {
            "name": "Simple Job Title",
            "store": "I work as a software engineer.",
            "query": "What is my job?",
            "keyword": "software engineer"
        },
        {
            "name": "Numeric Data",
            "store": "I worked exactly 847 hours last month.",
            "query": "How many hours did I work?",
            "keyword": "847"
        },
        {
            "name": "Company Name",
            "store": "I work at Google.",
            "query": "Where do I work?",
            "keyword": "Google"
        },
        {
            "name": "Programming Preference",
            "store": "I prefer Python for backend development.",
            "query": "What language do I prefer?",
            "keyword": "Python"
        },
        {
            "name": "Multiple Facts",
            "store": "I am a senior developer at Microsoft specializing in AI.",
            "query": "Tell me about my job.",
            "keyword": "Microsoft"
        }
    ]
    
    results = []
    for tc in test_cases:
        success = test_case(tc["name"], tc["store"], tc["query"], tc["keyword"])
        results.append((tc["name"], success))
        time.sleep(2)  # Pause between tests
    
    # Summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    print(f"\nResults: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    print("\nDetailed Results:")
    for name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {status} - {name}")
    
    # Analysis
    print("\n" + "="*80)
    print("ANALYSIS")
    print("="*80)
    
    if passed == total:
        print("\n✅ All tests passed! Mem0 is working correctly.")
    elif passed > total / 2:
        print(f"\n⚠️  {total - passed} tests failed. Mem0 is partially working.")
        print("   Possible issues:")
        print("   - Indexing delay (try increasing wait time)")
        print("   - Semantic matching threshold too high")
        print("   - Memory extraction not capturing all facts")
    else:
        print(f"\n❌ {total - passed} tests failed. Mem0 has significant issues.")
        print("   Possible causes:")
        print("   - Mem0 not extracting memories properly")
        print("   - Qdrant connection issues")
        print("   - Configuration problems")
        print("   - Memory format not optimal")


if __name__ == "__main__":
    main()
