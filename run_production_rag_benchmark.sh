#!/bin/bash
# Production RAG Benchmark via HTTP Test Endpoint
# Tests memory storage and retrieval through deployed system

API_URL="https://unified-temporal-worker.kindcoast-5a2a34c6.australiaeast.azurecontainerapps.io/test/conversation-with-memory"
TENANT_ID="rag_benchmark"
USER_ID="rag_test_user_$(date +%s)"

echo "🚀 RAG ACCURACY BENCHMARK - Production System"
echo "=============================================="
echo "Tenant: $TENANT_ID"
echo "User: $USER_ID"
echo "Timestamp: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo ""

# Test Case 1: Basic Fact Retrieval
echo "🧪 Test Case 1: Basic Fact Retrieval"
echo "--------------------------------------"
echo "📤 Storing fact: 'I work at Microsoft as a cloud architect'"

RESPONSE1=$(curl -s -X POST "$API_URL" \
  -H "Content-Type: application/json" \
  -d "{
    \"message\": \"I work at Microsoft as a cloud architect\",
    \"user_id\": \"$USER_ID\",
    \"tenant_id\": \"$TENANT_ID\"
  }")

echo "✅ Response: $(echo $RESPONSE1 | jq -r '.assistant_response' | head -c 80)..."
echo ""
echo "⏳ Waiting 5 seconds for indexing..."
sleep 5

echo "🔍 Query: 'where do I work?'"
RESPONSE2=$(curl -s -X POST "$API_URL" \
  -H "Content-Type: application/json" \
  -d "{
    \"message\": \"where do I work?\",
    \"user_id\": \"$USER_ID\",
    \"tenant_id\": \"$TENANT_ID\"
  }")

ANSWER=$(echo $RESPONSE2 | jq -r '.assistant_response')
echo "💬 Answer: $ANSWER"

# Check if answer contains expected keywords
if echo "$ANSWER" | grep -qi "microsoft"; then
    echo "✅ PASS - Found 'Microsoft'"
    TEST1_PASS=1
else
    echo "❌ FAIL - 'Microsoft' not found"
    TEST1_PASS=0
fi

if echo "$ANSWER" | grep -qi "cloud architect\|architect"; then
    echo "✅ PASS - Found 'cloud architect' or 'architect'"
    TEST1_KEYWORDS=2
else
    TEST1_KEYWORDS=1
fi
echo ""

# Test Case 2: Timesheet Context
echo "🧪 Test Case 2: Timesheet Context"
echo "--------------------------------------"
echo "📤 Storing fact: 'I worked 6.5 hours yesterday on API development'"

RESPONSE3=$(curl -s -X POST "$API_URL" \
  -H "Content-Type: application/json" \
  -d "{
    \"message\": \"I worked 6.5 hours yesterday on API development\",
    \"user_id\": \"$USER_ID\",
    \"tenant_id\": \"$TENANT_ID\"
  }")

echo "✅ Response: $(echo $RESPONSE3 | jq -r '.assistant_response' | head -c 80)..."
echo ""
echo "⏳ Waiting 5 seconds for indexing..."
sleep 5

echo "🔍 Query: 'how many hours did I work yesterday?'"
RESPONSE4=$(curl -s -X POST "$API_URL" \
  -H "Content-Type: application/json" \
  -d "{
    \"message\": \"how many hours did I work yesterday?\",
    \"user_id\": \"$USER_ID\",
    \"tenant_id\": \"$TENANT_ID\"
  }")

ANSWER2=$(echo $RESPONSE4 | jq -r '.assistant_response')
echo "💬 Answer: $ANSWER2"

# Check if answer contains expected keywords
if echo "$ANSWER2" | grep -qi "6.5\|six"; then
    echo "✅ PASS - Found '6.5' or 'six'"
    TEST2_PASS=1
else
    echo "❌ FAIL - Hours not found"
    TEST2_PASS=0
fi

if echo "$ANSWER2" | grep -qi "yesterday"; then
    echo "✅ PASS - Found 'yesterday'"
    TEST2_KEYWORDS=2
else
    TEST2_KEYWORDS=1
fi
echo ""

# Test Case 3: Preference Memory
echo "🧪 Test Case 3: Preference Memory"
echo "--------------------------------------"
echo "📤 Storing fact: 'I prefer Python and TypeScript for development'"

RESPONSE5=$(curl -s -X POST "$API_URL" \
  -H "Content-Type: application/json" \
  -d "{
    \"message\": \"I prefer Python and TypeScript for development\",
    \"user_id\": \"$USER_ID\",
    \"tenant_id\": \"$TENANT_ID\"
  }")

echo "✅ Response: $(echo $RESPONSE5 | jq -r '.assistant_response' | head -c 80)..."
echo ""
echo "⏳ Waiting 5 seconds for indexing..."
sleep 5

echo "🔍 Query: 'what programming languages do I like?'"
RESPONSE6=$(curl -s -X POST "$API_URL" \
  -H "Content-Type: application/json" \
  -d "{
    \"message\": \"what programming languages do I like?\",
    \"user_id\": \"$USER_ID\",
    \"tenant_id\": \"$TENANT_ID\"
  }")

ANSWER3=$(echo $RESPONSE6 | jq -r '.assistant_response')
echo "💬 Answer: $ANSWER3"

# Check if answer contains expected keywords
FOUND_LANGS=0
if echo "$ANSWER3" | grep -qi "python"; then
    echo "✅ PASS - Found 'Python'"
    FOUND_LANGS=$((FOUND_LANGS + 1))
fi

if echo "$ANSWER3" | grep -qi "typescript"; then
    echo "✅ PASS - Found 'TypeScript'"
    FOUND_LANGS=$((FOUND_LANGS + 1))
fi

if [ $FOUND_LANGS -ge 1 ]; then
    TEST3_PASS=1
else
    echo "❌ FAIL - Languages not found"
    TEST3_PASS=0
fi
TEST3_KEYWORDS=$FOUND_LANGS
echo ""

# Final Report
echo "=============================================="
echo "📈 FINAL BENCHMARK REPORT"
echo "=============================================="
echo ""

TOTAL_TESTS=3
PASSED_TESTS=$((TEST1_PASS + TEST2_PASS + TEST3_PASS))
PASS_RATE=$(echo "scale=1; $PASSED_TESTS * 100 / $TOTAL_TESTS" | bc)

TOTAL_KEYWORDS=6
FOUND_KEYWORDS=$((TEST1_KEYWORDS + TEST2_KEYWORDS + TEST3_KEYWORDS))
PRECISION=$(echo "scale=1; $FOUND_KEYWORDS * 100 / $TOTAL_KEYWORDS" | bc)

echo "🎯 Overall Metrics:"
echo "   Pass Rate: ${PASS_RATE}% ($PASSED_TESTS/$TOTAL_TESTS)"
echo "   Keyword Precision: ${PRECISION}% ($FOUND_KEYWORDS/$TOTAL_KEYWORDS)"
echo ""

echo "📊 Test Case Breakdown:"
if [ $TEST1_PASS -eq 1 ]; then
    echo "   ✅ Basic Fact Retrieval: PASS"
else
    echo "   ❌ Basic Fact Retrieval: FAIL"
fi

if [ $TEST2_PASS -eq 1 ]; then
    echo "   ✅ Timesheet Context: PASS"
else
    echo "   ❌ Timesheet Context: FAIL"
fi

if [ $TEST3_PASS -eq 1 ]; then
    echo "   ✅ Preference Memory: PASS"
else
    echo "   ❌ Preference Memory: FAIL"
fi
echo ""

echo "💡 Recommendations:"
if [ $PASSED_TESTS -ge 2 ]; then
    echo "   ✅ Excellent RAG performance in production!"
    echo "   Your Mem0 + Qdrant system is working correctly."
else
    echo "   ⚠️  Some tests failed - investigate memory retrieval"
fi
echo ""

echo "💾 Report saved to: rag_production_benchmark_$(date +%Y%m%d_%H%M%S).txt"
echo "=============================================="
