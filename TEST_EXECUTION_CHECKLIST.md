# Mem0 + Qdrant Test Execution Checklist

## Pre-Test Verification

### Environment Check
- [ ] Azure Container App is running
  ```bash
  az containerapp show --name unified-temporal-worker \
    --resource-group rg-secure-timesheet-agent \
    --query "properties.runningStatus"
  ```
  Expected: `Running`

- [ ] Qdrant service is healthy
  ```bash
  curl http://qdrant-service/health
  ```
  Expected: HTTP 200

- [ ] Latest code deployed
  ```bash
  az containerapp revision list --name unified-temporal-worker \
    --resource-group rg-secure-timesheet-agent \
    --query "[0].name"
  ```
  Expected: Latest revision active

### Dependencies Check
- [ ] Python 3.9+ installed
  ```bash
  python3 --version
  ```

- [ ] pytest installed
  ```bash
  pip install pytest requests
  ```

- [ ] Azure CLI authenticated
  ```bash
  az account show
  ```

## Test Execution

### Phase 1: Smoke Test (5 minutes)
- [ ] Run smoke test
  ```bash
  python3 -c "import requests, time, uuid; ..."
  ```
  Expected: ✅ SMOKE TEST PASSED

### Phase 2: Automated Test Suite (30-60 minutes)

#### Basic Operations (10 minutes)
- [ ] Single memory storage and retrieval
- [ ] Multiple memories retrieval
- [ ] Memory persistence across sessions

**Command**:
```bash
pytest tests/test_mem0_qdrant_integration.py::TestBasicMemoryOperations -v
```

**Expected**: 3/3 passed

#### Multi-Tenant Isolation (10 minutes)
- [ ] Tenant isolation verified
- [ ] User isolation within tenant verified

**Command**:
```bash
pytest tests/test_mem0_qdrant_integration.py::TestMultiTenantIsolation -v
```

**Expected**: 2/2 passed

#### Edge Cases (15 minutes)
- [ ] Empty query handled
- [ ] Very long conversation handled
- [ ] Special characters handled
- [ ] Unicode and emoji handled
- [ ] Duplicate memories handled
- [ ] Contradictory information handled

**Command**:
```bash
pytest tests/test_mem0_qdrant_integration.py::TestEdgeCases -v
```

**Expected**: 6/6 passed

#### Performance Tests (15 minutes)
- [ ] Storage latency measured
- [ ] Retrieval latency measured
- [ ] Concurrent users tested

**Command**:
```bash
pytest tests/test_mem0_qdrant_integration.py::TestPerformance -v
```

**Expected**: 3/3 passed
**Benchmarks**:
- Storage latency: < 5s
- Retrieval latency: < 5s

#### Data Integrity (10 minutes)
- [ ] Numeric data accuracy verified
- [ ] Date/time information verified

**Command**:
```bash
pytest tests/test_mem0_qdrant_integration.py::TestDataIntegrity -v
```

**Expected**: 2/2 passed

#### Reliability Tests (10 minutes)
- [ ] Invalid tenant ID handled
- [ ] Missing user ID handled
- [ ] Malformed request handled

**Command**:
```bash
pytest tests/test_mem0_qdrant_integration.py::TestReliability -v
```

**Expected**: 3/3 passed

#### Semantic Search (10 minutes)
- [ ] Semantic similarity working
- [ ] Context understanding working

**Command**:
```bash
pytest tests/test_mem0_qdrant_integration.py::TestSemanticSearch -v
```

**Expected**: 2/2 passed

### Phase 3: Full Test Suite (60 minutes)
- [ ] Run complete test suite
  ```bash
  ./run_mem0_tests.sh
  ```

**Expected Results**:
```
Total Tests: 24
Passed: 24
Failed: 0
Success Rate: 100.0%
```

## Post-Test Verification

### Results Review
- [ ] All tests passed (24/24)
- [ ] No errors in logs
  ```bash
  az containerapp logs show --name unified-temporal-worker \
    --tail 100 | grep ERROR
  ```
  Expected: No critical errors

- [ ] Performance metrics acceptable
  - [ ] Storage latency < 5s
  - [ ] Retrieval latency < 5s

### Test Report
- [ ] Test report generated
  Location: `test_results/mem0_test_report_YYYYMMDD_HHMMSS.txt`

- [ ] Performance metrics documented
  - Average storage latency: _____ seconds
  - Average retrieval latency: _____ seconds
  - Concurrent users supported: _____

- [ ] Any failures documented
  - Number of failures: _____
  - Failure categories: _____
  - Root causes identified: _____

## Known Issues Check

Review and verify status of known issues from evaluation:

- [ ] Opik proxy parameter warning
  Status: ⚠️ Non-blocking, tracking works
  
- [ ] Tenant key management 401 error
  Status: ⚠️ Falls back to default key
  
- [ ] Rate limiter fallback warning
  Status: ⚠️ V1 rate limiter functional

## Additional Manual Tests

### Memory Persistence
- [ ] Store memory
- [ ] Restart container app
  ```bash
  az containerapp revision restart --name unified-temporal-worker \
    --resource-group rg-secure-timesheet-agent \
    --revision [revision-name]
  ```
- [ ] Verify memory still retrievable

### Large Conversation Test
- [ ] Create conversation with 20+ turns
- [ ] Verify all context maintained
- [ ] Check retrieval performance

### Multi-Language Test
- [ ] Test with Chinese characters: "我喜欢编程"
- [ ] Test with Arabic: "أحب البرمجة"
- [ ] Test with emoji: "I love coding 💻"
- [ ] Verify all stored and retrieved correctly

## Load Testing (Optional - Separate Session)

### Light Load (10 concurrent users, 5 minutes)
- [ ] Use Locust or JMeter
- [ ] Monitor response times
- [ ] Check error rates
- [ ] Review resource usage

### Medium Load (50 concurrent users, 15 minutes)
- [ ] Monitor degradation
- [ ] Check for failures
- [ ] Review Qdrant performance

### Heavy Load (100+ concurrent users, 30 minutes)
- [ ] Identify breaking point
- [ ] Document failure modes
- [ ] Plan scaling strategy

## Security Testing (Optional - Separate Session)

### Injection Attacks
- [ ] SQL injection attempts in queries
- [ ] XSS attempts in memory content
- [ ] Command injection attempts

### Access Control
- [ ] Attempt cross-tenant access
- [ ] Attempt cross-user access
- [ ] Verify all blocked correctly

## Sign-Off

### Test Execution
- **Date**: _________________
- **Executed By**: _________________
- **Duration**: _________________
- **Environment**: Production / Staging / Development

### Results Summary
- **Total Tests**: 24
- **Passed**: _____
- **Failed**: _____
- **Success Rate**: _____%

### Performance Summary
- **Storage Latency**: _____ seconds (Target: < 5s)
- **Retrieval Latency**: _____ seconds (Target: < 5s)
- **Concurrent Users**: _____ (Target: 3+)

### Decision
- [ ] ✅ **APPROVED FOR PRODUCTION** - All tests passed, performance acceptable
- [ ] ⚠️ **APPROVED WITH CAVEATS** - Minor issues, acceptable for production
- [ ] ❌ **NOT APPROVED** - Critical issues found, requires fixes

### Caveats/Issues (if any):
```
[List any issues or concerns]
```

### Next Steps:
- [ ] Deploy to production
- [ ] Set up monitoring
- [ ] Configure alerts
- [ ] Update documentation
- [ ] Train team

### Signatures
- **QA Lead**: _________________ Date: _______
- **Tech Lead**: _________________ Date: _______
- **Product Owner**: _________________ Date: _______

---

## Quick Reference Commands

### Run All Tests
```bash
./run_mem0_tests.sh
```

### Run Specific Category
```bash
pytest tests/test_mem0_qdrant_integration.py::TestBasicMemoryOperations -v
```

### Check Logs
```bash
az containerapp logs show --name unified-temporal-worker \
  --resource-group rg-secure-timesheet-agent --tail 100
```

### Check Deployment Status
```bash
az containerapp show --name unified-temporal-worker \
  --resource-group rg-secure-timesheet-agent \
  --query "properties.runningStatus"
```

### Manual Test Endpoint
```bash
curl -X POST "https://unified-temporal-worker.kindcoast-5a2a34c6.australiaeast.azurecontainerapps.io/test/conversation-with-memory" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test", "tenant_id": "test", "message": "Hello"}'
```

---

**Checklist Version**: 1.0  
**Last Updated**: December 17, 2025  
**Next Review**: After production deployment
