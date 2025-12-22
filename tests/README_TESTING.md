# Mem0 + Qdrant Integration Testing Guide

## Overview

Comprehensive test suite for verifying the Mem0 + Qdrant memory integration is fully operational before production deployment.

## Test Categories

### 1. Basic Memory Operations (6 tests)
- ✅ Single memory storage and retrieval
- ✅ Multiple memories retrieval
- ✅ Memory persistence across sessions

**Purpose**: Verify core functionality works as expected

### 2. Multi-Tenant Isolation (2 tests)
- ✅ Tenant isolation
- ✅ User isolation within tenant

**Purpose**: Ensure no data leakage between tenants or users

### 3. Edge Cases (6 tests)
- ✅ Empty query handling
- ✅ Very long conversations
- ✅ Special characters
- ✅ Unicode and emoji
- ✅ Duplicate memories
- ✅ Contradictory information

**Purpose**: Verify robustness with unusual inputs

### 4. Performance (3 tests)
- ✅ Storage latency measurement
- ✅ Retrieval latency measurement
- ✅ Concurrent users

**Purpose**: Establish performance baselines

### 5. Data Integrity (2 tests)
- ✅ Numeric data accuracy
- ✅ Date and time information

**Purpose**: Ensure data is stored and retrieved accurately

### 6. Reliability (3 tests)
- ✅ Invalid tenant ID handling
- ✅ Missing user ID handling
- ✅ Malformed request handling

**Purpose**: Verify error handling and graceful degradation

### 7. Semantic Search (2 tests)
- ✅ Semantic similarity
- ✅ Context understanding

**Purpose**: Verify RAG semantic capabilities

## Prerequisites

```bash
# Install test dependencies
pip install pytest requests

# Ensure Azure deployment is running
az containerapp show --name unified-temporal-worker \
  --resource-group rg-secure-timesheet-agent \
  --query "properties.runningStatus"
```

## Running Tests

### Run All Tests
```bash
cd /Users/dongshulin/Library/CloudStorage/OneDrive-2ai.cx/Desktop/GitHub/multi_Agent_Conversation_System
pytest tests/test_mem0_qdrant_integration.py -v
```

### Run Specific Test Category
```bash
# Basic operations only
pytest tests/test_mem0_qdrant_integration.py::TestBasicMemoryOperations -v

# Multi-tenant isolation only
pytest tests/test_mem0_qdrant_integration.py::TestMultiTenantIsolation -v

# Performance tests only
pytest tests/test_mem0_qdrant_integration.py::TestPerformance -v
```

### Run Single Test
```bash
pytest tests/test_mem0_qdrant_integration.py::TestBasicMemoryOperations::test_single_memory_storage_and_retrieval -v
```

### Run with Coverage
```bash
pytest tests/test_mem0_qdrant_integration.py --cov=llm.memory --cov-report=html
```

### Run with Detailed Output
```bash
pytest tests/test_mem0_qdrant_integration.py -v -s
```

## Expected Results

### Success Criteria
- ✅ All basic memory operations pass (100%)
- ✅ Multi-tenant isolation verified (100%)
- ✅ Edge cases handled gracefully (>90%)
- ✅ Performance within acceptable limits:
  - Storage latency: < 5 seconds
  - Retrieval latency: < 5 seconds
- ✅ Data integrity maintained (100%)
- ✅ Error handling works correctly (100%)
- ✅ Semantic search functional (100%)

### Performance Benchmarks
```
Average storage latency: ~2-3 seconds
Average retrieval latency: ~2-3 seconds
Concurrent users: 3+ simultaneous users supported
```

## Test Output Example

```
tests/test_mem0_qdrant_integration.py::TestBasicMemoryOperations::test_single_memory_storage_and_retrieval PASSED
tests/test_mem0_qdrant_integration.py::TestBasicMemoryOperations::test_multiple_memories_retrieval PASSED
tests/test_mem0_qdrant_integration.py::TestMultiTenantIsolation::test_tenant_isolation PASSED
tests/test_mem0_qdrant_integration.py::TestPerformance::test_storage_latency PASSED

Average storage latency: 2.34s
Average retrieval latency: 2.78s

======================== 24 passed in 180.45s ========================
```

## Troubleshooting

### Tests Failing

1. **Connection Errors**
   ```
   Check Azure deployment status:
   az containerapp show --name unified-temporal-worker \
     --resource-group rg-secure-timesheet-agent
   ```

2. **Timeout Errors**
   - Increase `time.sleep()` delays in tests
   - Check Qdrant service health
   - Verify network connectivity

3. **Assertion Errors**
   - Check logs: `az containerapp logs show --name unified-temporal-worker`
   - Verify Mem0 is properly installed
   - Check for recent deployments

### Performance Issues

If latency tests fail (>5 seconds):
1. Check Qdrant resource allocation
2. Verify network latency to Azure
3. Review concurrent load on system
4. Check for memory/CPU constraints

## Continuous Integration

### GitHub Actions Example

```yaml
name: Mem0 Integration Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install pytest requests
      - name: Run tests
        run: |
          pytest tests/test_mem0_qdrant_integration.py -v
        env:
          AZURE_ENDPOINT: ${{ secrets.AZURE_ENDPOINT }}
```

## Manual Testing Checklist

Beyond automated tests, manually verify:

- [ ] Memory persists after container restart
- [ ] Memory persists after deployment
- [ ] Large conversation histories (50+ turns)
- [ ] Multi-language support (test with Chinese, Arabic, etc.)
- [ ] Memory updates work correctly
- [ ] Memory deletion works correctly
- [ ] GDPR compliance (right to be forgotten)
- [ ] Cost per 1000 conversations is acceptable
- [ ] Monitoring and alerting configured

## Next Steps

After all tests pass:

1. **Load Testing**: Use tools like Locust or JMeter for sustained load
2. **Security Testing**: Penetration testing, injection attacks
3. **Disaster Recovery**: Test backup and restore procedures
4. **Documentation**: Update API documentation with memory features
5. **Production Deployment**: Deploy with monitoring and rollback plan

## Test Maintenance

- **Update tests** when adding new features
- **Review test coverage** monthly
- **Update performance benchmarks** as system scales
- **Add regression tests** for any bugs found in production

## Contact

For questions or issues with tests:
- Check logs: `az containerapp logs show`
- Review evaluation: `QDRANT_RETRIEVAL_EVALUATION.md`
- Check Mem0 docs: https://docs.mem0.ai/
