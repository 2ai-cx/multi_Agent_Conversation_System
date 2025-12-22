# AUTONOMOUS TEST GENERATION TASK

You are now in **fully autonomous mode**. Complete ALL tasks below without waiting for human approval. Work through errors and iterate until everything passes.

## ⚠️ CRITICAL RULES - READ FIRST

### 🚫 ABSOLUTE PROHIBITION - NEVER MODIFY:
- ❌ **NEVER EVER change any Python files outside `tests/` directory**
- ❌ **NEVER touch `agents/` directory**
- ❌ **NEVER touch `llm/` directory**
- ❌ **NEVER touch `unified_server.py`**
- ❌ **NEVER touch `unified_workflows.py`**
- ❌ **NEVER modify ANY production code - EVEN IF IT HAS BUGS**
- ❌ **NEVER fix warnings in production code**
- ❌ **NEVER refactor production code**
- ❌ **NEVER "improve" production code**

### ✅ ALLOWED TO MODIFY:
- ✅ **ONLY files in `tests/` directory**
- ✅ **Create new test files**
- ✅ **Modify existing test files**
- ✅ **Create report files (*.md)**

### 📖 READ-ONLY ACCESS:
- You can READ production code to understand it
- You can ANALYZE production code structure
- You CANNOT MODIFY production code UNDER ANY CIRCUMSTANCES

### 🎯 TEST PHILOSOPHY:
- **Keep tests SIMPLE** - basic assertions only
- **Keep tests REPETITIVE** - copy/paste patterns are OK
- **Keep tests BORING** - no clever tricks
- **Keep tests OBVIOUS** - anyone should understand them
- **One test = One thing** - test one behavior per method

### 📝 EXAMPLE OF GOOD SIMPLE TEST:
```python
def test_health_endpoint_returns_200():
    """Test that /health endpoint returns 200 status code."""
    response = client.get("/health")
    assert response.status_code == 200

def test_health_endpoint_returns_json():
    """Test that /health endpoint returns JSON."""
    response = client.get("/health")
    assert response.headers["content-type"] == "application/json"

def test_health_endpoint_has_status_field():
    """Test that /health response has status field."""
    response = client.get("/health")
    data = response.json()
    assert "status" in data
```

### ❌ EXAMPLE OF BAD COMPLEX TEST:
```python
def test_health_endpoint():  # ❌ Tests too many things
    """Test health endpoint."""  # ❌ Vague description
    response = client.get("/health")
    assert response.status_code == 200 and \
           response.headers["content-type"] == "application/json" and \
           "status" in response.json() and \
           response.json()["status"] == "ok"  # ❌ Too much in one test
```

**ALWAYS use the SIMPLE pattern, NEVER the COMPLEX pattern!**

## Project Context
- **Path:** `/Users/dongshulin/Library/CloudStorage/OneDrive-2ai.cx/Desktop/GitHub/multi_Agent_Conversation_System`
- **Current Status:** 41 tests passing, 70 warnings, 72% coverage
- **Goal:** Create comprehensive test suite (tests only, no production code changes)

---

## PHASE 1: Initial Assessment (5 min)

### Task 1.1: Count Current Tests
1. Run: `pytest tests/ --collect-only -q`
2. Count total test methods
3. Report current status

### Task 1.2: Analyze Test Coverage
1. Run: `pytest tests/ --cov=. --cov-report=term-missing`
2. Identify files with <80% coverage
3. List top 5 files needing tests

### Task 1.3: Check Existing E2E Tests
1. Read `tests/e2e/test_complete_conversation_flow.py`
2. Count test methods
3. Check if tests are passing
4. Report any failures

---

## PHASE 2: Fix Existing E2E Tests (15 min)

### Task 2.1: Fix test_complete_conversation_flow.py
1. Read the file
2. Identify any failing tests
3. Fix import errors
4. Fix fixture issues
5. Run tests: `pytest tests/e2e/test_complete_conversation_flow.py -v`
6. Iterate until all pass

### Task 2.2: Verify All E2E Tests Pass
1. Run: `pytest tests/e2e/ -v`
2. Ensure all 4 tests pass
3. Report results

---

## PHASE 3: Create API Endpoint Tests (30 min)

### Task 3.1: Create test_api_endpoints.py
Create `tests/api/test_api_endpoints.py` with these tests:

1. `test_health_endpoint()` - Test /health returns 200
2. `test_chat_endpoint_valid_request()` - Test /chat with valid data
3. `test_chat_endpoint_missing_message()` - Test /chat without message
4. `test_chat_endpoint_invalid_json()` - Test /chat with invalid JSON
5. `test_chat_endpoint_empty_message()` - Test /chat with empty message
6. `test_chat_endpoint_long_message()` - Test /chat with 10000 char message
7. `test_chat_endpoint_special_characters()` - Test /chat with special chars
8. `test_chat_endpoint_concurrent_requests()` - Test 10 concurrent requests
9. `test_chat_endpoint_rate_limiting()` - Test rate limiting (if exists)
10. `test_chat_endpoint_timeout()` - Test request timeout handling
11. `test_chat_endpoint_response_format()` - Verify response structure
12. `test_chat_endpoint_error_handling()` - Test error responses

### Task 3.2: Run API Tests
1. Run: `pytest tests/api/test_api_endpoints.py -v`
2. Fix any failures
3. Ensure all 12 tests pass

---

## PHASE 4: Create Temporal Workflow Tests (30 min)

### Task 4.1: Create test_temporal_workflows.py
Create `tests/workflows/test_temporal_workflows.py` with these tests:

1. `test_workflow_registration()` - Test workflows are registered
2. `test_workflow_execution_success()` - Test successful workflow run
3. `test_workflow_execution_failure()` - Test workflow failure handling
4. `test_workflow_retry_logic()` - Test retry on failure
5. `test_workflow_timeout()` - Test workflow timeout
6. `test_workflow_cancellation()` - Test workflow cancellation
7. `test_workflow_state_persistence()` - Test state is saved
8. `test_workflow_parallel_execution()` - Test multiple workflows
9. `test_workflow_signal_handling()` - Test signal reception
10. `test_workflow_query_handling()` - Test query responses
11. `test_workflow_activity_execution()` - Test activities run
12. `test_workflow_activity_retry()` - Test activity retry
13. `test_workflow_activity_timeout()` - Test activity timeout
14. `test_workflow_error_propagation()` - Test error handling
15. `test_workflow_versioning()` - Test workflow versions
16. `test_workflow_history_replay()` - Test history replay
17. `test_workflow_determinism()` - Test deterministic execution

### Task 4.2: Run Workflow Tests
1. Run: `pytest tests/workflows/test_temporal_workflows.py -v`
2. Fix any failures
3. Ensure all 17 tests pass

---

## PHASE 5: Create Performance Tests (30 min)

### Task 5.1: Create test_performance.py
Create `tests/performance/test_performance.py` with these tests:

1. `test_response_time_under_load()` - Test response time <500ms
2. `test_throughput_100_requests()` - Test 100 req/sec
3. `test_memory_usage_stable()` - Test memory doesn't leak
4. `test_cpu_usage_acceptable()` - Test CPU <80%
5. `test_concurrent_users_10()` - Test 10 concurrent users
6. `test_concurrent_users_50()` - Test 50 concurrent users
7. `test_concurrent_users_100()` - Test 100 concurrent users
8. `test_database_query_performance()` - Test DB queries <100ms
9. `test_cache_hit_rate()` - Test cache effectiveness
10. `test_api_latency_p95()` - Test p95 latency <1s
11. `test_api_latency_p99()` - Test p99 latency <2s
12. `test_error_rate_under_load()` - Test error rate <1%
13. `test_recovery_after_spike()` - Test recovery time
14. `test_graceful_degradation()` - Test degradation handling
15. `test_resource_cleanup()` - Test resources are freed
16. `test_connection_pool_efficiency()` - Test connection reuse
17. `test_long_running_request()` - Test 60s request handling

### Task 5.2: Run Performance Tests
1. Run: `pytest tests/performance/test_performance.py -v`
2. Fix any failures
3. Ensure all 17 tests pass

---

## PHASE 6: Create Contract Tests (30 min)

### Task 6.1: Create test_contracts.py
Create `tests/contracts/test_contracts.py` with these tests:

1. `test_api_request_schema()` - Validate request schema
2. `test_api_response_schema()` - Validate response schema
3. `test_error_response_schema()` - Validate error schema
4. `test_workflow_input_schema()` - Validate workflow inputs
5. `test_workflow_output_schema()` - Validate workflow outputs
6. `test_activity_input_schema()` - Validate activity inputs
7. `test_activity_output_schema()` - Validate activity outputs
8. `test_event_schema()` - Validate event structure
9. `test_backward_compatibility()` - Test old clients work
10. `test_forward_compatibility()` - Test new fields ignored
11. `test_required_fields_present()` - Test required fields
12. `test_optional_fields_handling()` - Test optional fields
13. `test_field_type_validation()` - Test field types
14. `test_enum_value_validation()` - Test enum values

### Task 6.2: Run Contract Tests
1. Run: `pytest tests/contracts/test_contracts.py -v`
2. Fix any failures
3. Ensure all 14 tests pass

---

## PHASE 7: Create Security Tests (30 min)

### Task 7.1: Create test_security.py
Create `tests/security/test_security.py` with these tests:

1. `test_sql_injection_prevention()` - Test SQL injection blocked
2. `test_xss_prevention()` - Test XSS blocked
3. `test_csrf_protection()` - Test CSRF protection
4. `test_input_sanitization()` - Test inputs sanitized
5. `test_output_encoding()` - Test outputs encoded
6. `test_authentication_required()` - Test auth required
7. `test_authorization_checks()` - Test permissions checked
8. `test_rate_limiting_enforced()` - Test rate limits work
9. `test_sensitive_data_not_logged()` - Test no secrets in logs
10. `test_secure_headers_present()` - Test security headers
11. `test_https_enforced()` - Test HTTPS required
12. `test_session_timeout()` - Test sessions expire
13. `test_password_complexity()` - Test password rules
14. `test_api_key_validation()` - Test API key validation

### Task 7.2: Run Security Tests
1. Run: `pytest tests/security/test_security.py -v`
2. Fix any failures
3. Ensure all 14 tests pass

---

## PHASE 8: Run Full Test Suite (15 min)

### Task 8.1: Run All Tests
1. Run: `pytest tests/ -v --tb=short`
2. Count total tests
3. Count passing tests
4. Count failing tests
5. Report results

### Task 8.2: Generate Coverage Report
1. Run: `pytest tests/ --cov=. --cov-report=term-missing --cov-report=html`
2. Check coverage percentage
3. Identify files still <80% coverage
4. Report top 10 uncovered files

### Task 8.3: Check for Warnings
1. Run: `pytest tests/ -v --tb=short -W error::DeprecationWarning`
2. Count warnings
3. List warning types
4. Report (but don't fix - production code)

---

## PHASE 9: Generate Final Report (10 min)

### Task 9.1: Create Comprehensive Report
Create `GOOSE-TEST-GENERATION-REPORT.md` with:

1. **Summary Statistics:**
   - Total tests created
   - Total tests passing
   - Coverage before/after
   - Time taken

2. **Tests Created:**
   - List all new test files
   - Count tests per file
   - List test method names

3. **Coverage Analysis:**
   - Overall coverage %
   - Coverage by module
   - Files with <80% coverage
   - Recommendations for improvement

4. **Warnings Report:**
   - Total warnings
   - Warning types
   - Files with most warnings
   - Note: Warnings not fixed (production code)

5. **Issues Encountered:**
   - List any failures
   - How they were resolved
   - Any remaining issues

6. **Recommendations:**
   - Next steps for testing
   - Areas needing more coverage
   - Suggested improvements

### Task 9.2: CRITICAL SAFETY CHECK - Verify No Production Code Modified
1. Run: `git status`
2. List ALL modified files
3. **VERIFY ONLY these types of files changed:**
   - ✅ Files in `tests/` directory
   - ✅ `*.md` report files
   - ❌ NO files in `agents/`
   - ❌ NO files in `llm/`
   - ❌ NO `unified_server.py`
   - ❌ NO `unified_workflows.py`
   - ❌ NO production Python files
4. If ANY production code was modified:
   - **STOP IMMEDIATELY**
   - **REVERT ALL CHANGES** with `git checkout <file>`
   - **REPORT THE ERROR**
5. Report verification results

---

## 🎯 Success Criteria

- [ ] All existing E2E tests pass
- [ ] 12+ new API endpoint tests created and passing
- [ ] 17+ new workflow tests created and passing
- [ ] 17+ new performance tests created and passing
- [ ] 14+ new contract tests created and passing
- [ ] 14+ new security tests created and passing
- [ ] Total 80+ tests passing
- [ ] Coverage increased from 72% to 80%+
- [ ] Comprehensive report generated
- [ ] All warnings documented (not fixed)
- [ ] NO production code modified (CRITICAL CHECK)

---

## 📝 Execution Instructions

1. **Read all rules carefully**
2. **Start with Phase 1**
3. **Work through each phase sequentially**
4. **Do not skip tasks**
5. **Fix errors as you encounter them**
6. **Report progress after each phase**
7. **Generate final report at end**
8. **Verify no production code was modified**

**Estimated Time:** 3-4 hours

**BEGIN AUTONOMOUS EXECUTION NOW!**
