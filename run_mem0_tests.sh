#!/bin/bash

# Mem0 + Qdrant Integration Test Runner
# Runs comprehensive test suite and generates report

set -e

echo "🧪 Mem0 + Qdrant Integration Test Suite"
echo "========================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check prerequisites
echo "📋 Checking prerequisites..."

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    echo -e "${RED}❌ pytest not found. Installing...${NC}"
    pip install pytest requests
else
    echo -e "${GREEN}✅ pytest found${NC}"
fi

# Check if Azure deployment is running
echo "🔍 Checking Azure deployment status..."
STATUS=$(az containerapp show \
    --name unified-temporal-worker \
    --resource-group rg-secure-timesheet-agent \
    --query "properties.runningStatus" -o tsv 2>/dev/null || echo "ERROR")

if [ "$STATUS" = "Running" ]; then
    echo -e "${GREEN}✅ Azure deployment is running${NC}"
else
    echo -e "${RED}❌ Azure deployment not running: $STATUS${NC}"
    echo "Please ensure the container app is deployed and running."
    exit 1
fi

echo ""
echo "🚀 Starting test execution..."
echo ""

# Create test results directory
mkdir -p test_results

# Run tests with different verbosity levels
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
REPORT_FILE="test_results/mem0_test_report_${TIMESTAMP}.txt"

# Run all tests
echo "Running all tests..."
pytest tests/test_mem0_qdrant_integration.py -v --tb=short 2>&1 | tee "$REPORT_FILE"

# Capture exit code
TEST_EXIT_CODE=${PIPESTATUS[0]}

echo ""
echo "========================================"
echo "📊 Test Summary"
echo "========================================"

# Parse results
PASSED=$(grep -c "PASSED" "$REPORT_FILE" || echo "0")
FAILED=$(grep -c "FAILED" "$REPORT_FILE" || echo "0")
TOTAL=$((PASSED + FAILED))

echo "Total Tests: $TOTAL"
echo -e "${GREEN}Passed: $PASSED${NC}"
if [ "$FAILED" -gt 0 ]; then
    echo -e "${RED}Failed: $FAILED${NC}"
else
    echo -e "${GREEN}Failed: $FAILED${NC}"
fi

# Calculate success rate
if [ "$TOTAL" -gt 0 ]; then
    SUCCESS_RATE=$(awk "BEGIN {printf \"%.1f\", ($PASSED/$TOTAL)*100}")
    echo "Success Rate: ${SUCCESS_RATE}%"
fi

# Extract performance metrics if available
echo ""
echo "📈 Performance Metrics"
echo "========================================"
grep "Average.*latency" "$REPORT_FILE" || echo "No performance metrics found"

echo ""
echo "📄 Full report saved to: $REPORT_FILE"

# Final status
echo ""
if [ "$TEST_EXIT_CODE" -eq 0 ]; then
    echo -e "${GREEN}✅ All tests passed!${NC}"
    echo ""
    echo "🎉 Mem0 + Qdrant integration is verified and operational!"
    echo ""
    echo "Next steps:"
    echo "  1. Review performance metrics above"
    echo "  2. Run load tests for production readiness"
    echo "  3. Update documentation with test results"
    echo "  4. Deploy to production with confidence"
else
    echo -e "${RED}❌ Some tests failed${NC}"
    echo ""
    echo "Please review the failures above and:"
    echo "  1. Check Azure logs: az containerapp logs show --name unified-temporal-worker"
    echo "  2. Verify Qdrant service health"
    echo "  3. Review QDRANT_RETRIEVAL_EVALUATION.md for known issues"
    echo "  4. Re-run specific failed tests for debugging"
fi

echo ""
exit $TEST_EXIT_CODE
