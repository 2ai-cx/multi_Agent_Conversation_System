# 🤖 Goose Autonomous Test Generation Workflow

## Objective
Generate comprehensive test suite completely autonomously without human intervention.

---

## 📋 Full Autonomous Workflow

Copy this ENTIRE prompt into Goose and let it run in **autonomous mode**:

---

# AUTONOMOUS TEST GENERATION TASK

You are now in **fully autonomous mode**. Complete ALL tasks below without waiting for human approval. Work through errors and iterate until everything passes.

## ⚠️ CRITICAL RULES - READ FIRST

### 🚫 DO NOT MODIFY:
- ❌ **NO changes to any Python files outside `tests/` directory**
- ❌ **NO changes to `agents/` directory**
- ❌ **NO changes to `llm/` directory**
- ❌ **NO changes to `unified_server.py`**
- ❌ **NO changes to `unified_workflows.py`**
- ❌ **NO changes to any production code**

### ✅ ALLOWED TO MODIFY:
- ✅ **Only files in `tests/` directory**
- ✅ **Create new test files**
- ✅ **Modify existing test files**
- ✅ **Create report files (*.md)**
- ✅ **Read any file for understanding**

### 📖 READ-ONLY ACCESS:
- You can READ production code to understand it
- You can ANALYZE production code structure
- You CANNOT MODIFY production code

## Project Context
- **Path:** `/Users/dongshulin/Library/CloudStorage/OneDrive-2ai.cx/Desktop/GitHub/multi_Agent_Conversation_System`
- **Current Status:** 41 tests passing, 70 warnings, 72% coverage
- **Goal:** Create comprehensive test suite (tests only, no production code changes)

---

## PHASE 1: Fix Existing E2E Tests (30 min)

### Task 1.1: Fix test_complete_conversation_flow.py
1. Read `tests/e2e/test_complete_conversation_flow.py`
2. Identify all errors (SenderAgent, timestamp assertions)
3. Fix ALL errors:
   - Remove SenderAgent references
   - Replace timestamp assertions with `unittest.mock.ANY`
   - Fix error_recovery test logic
4. Run: `pytest tests/e2e/test_complete_conversation_flow.py -v`
5. If errors, fix and re-run until ALL PASS
6. Log result: "E2E tests: X/4 passing"

---

## PHASE 2: Create API Tests (45 min)

### Task 2.1: Read unified_server.py
1. Read entire `unified_server.py` file
2. List all endpoints found
3. Note authentication requirements

### Task 2.2: Create tests/api/test_endpoints.py
Create complete test file with:
- TestClient fixture
- Test all health endpoints
- Test all conversation endpoints
- Test all webhook endpoints
- Test error handling (404, 400, 500)
- Test rate limiting
- Minimum 12 test methods
- Use AsyncMock for all async operations

### Task 2.3: Verify API tests
1. Run: `pytest tests/api/test_endpoints.py -v`
2. If errors, fix and re-run
3. Iterate until ALL PASS
4. Log result: "API tests: X/12 passing"

---

## PHASE 3: Create Workflow Tests (45 min)

### Task 3.1: Read unified_workflows.py
1. Read entire `unified_workflows.py` file
2. Identify all workflows and activities
3. Note Temporal-specific patterns

### Task 3.2: Create tests/workflows/test_temporal_workflows.py
Create complete test file with:
- Mock Temporal client
- Test ConversationWorkflow (5 methods)
- Test DailyReminderWorkflow (3 methods)
- Test all activities (6 methods)
- Test workflow signals/queries (3 methods)
- Minimum 17 test methods

### Task 3.3: Verify workflow tests
1. Run: `pytest tests/workflows/test_temporal_workflows.py -v`
2. Fix errors and re-run until ALL PASS
3. Log result: "Workflow tests: X/17 passing"

---

## PHASE 4: Create Performance Tests (30 min)

### Task 4.1: Create tests/performance/test_load_and_stress.py
Create complete test file with:
- @pytest.mark.performance on all tests
- Response time tests (5 methods)
- Concurrent load tests (4 methods)
- Memory usage tests (3 methods)
- Throughput tests (2 methods)
- Database performance tests (3 methods)
- Minimum 17 test methods

### Task 4.2: Verify performance tests
1. Run: `pytest tests/performance/test_load_and_stress.py --collect-only`
2. Verify all tests are collected
3. Log result: "Performance tests: X tests collected"

---

## PHASE 5: Create Contract Tests (30 min)

### Task 5.1: Create tests/contracts/test_api_contracts.py
Create complete test file with:
- Schema validation tests (4 methods)
- External API contract tests (6 methods)
- Pydantic model validation (4 methods)
- Minimum 14 test methods

### Task 5.2: Verify contract tests
1. Run: `pytest tests/contracts/test_api_contracts.py -v`
2. Fix errors until ALL PASS
3. Log result: "Contract tests: X/14 passing"

---

## PHASE 6: Create Security Tests (30 min)

### Task 6.1: Create tests/security/test_security.py
Create complete test file with:
- @pytest.mark.security on all tests
- Authentication tests (4 methods)
- Input validation tests (4 methods)
- Rate limiting tests (3 methods)
- Data privacy tests (3 methods)
- Minimum 14 test methods

### Task 6.2: Verify security tests
1. Run: `pytest tests/security/test_security.py -v`
2. Fix errors until ALL PASS
3. Log result: "Security tests: X/14 passing"

---

## PHASE 7: Create Fixture Files (20 min)

### Task 7.1: Create tests/fixtures/temporal_fixtures.py
Include:
- mock_temporal_client fixture
- mock_workflow_execution fixture
- mock_activity_execution fixture
- sample_workflow_data fixture

### Task 7.2: Create tests/fixtures/api_fixtures.py
Include:
- mock_test_client fixture
- sample_api_requests fixture
- sample_api_responses fixture
- mock_authentication fixture

---

## PHASE 8: Run Full Test Suite (10 min)

### Task 8.1: Collect all tests
```bash
pytest tests/ --collect-only -q
```
Count total tests collected.

### Task 8.2: Run all tests
```bash
pytest tests/ -v --tb=short
```
Note: passing, failing, warnings

### Task 8.3: Generate coverage report
```bash
pytest tests/ --cov --cov-report=term-missing --cov-report=html
```
Note: coverage percentage

---

## PHASE 9: Generate Final Report (10 min)

### Task 9.1: Create AUTONOMOUS-TEST-REPORT.md
Include:
- Total tests created
- Tests passing/failing breakdown by category
- Coverage before/after
- Warnings count (note: not fixed, only reported)
- Time taken for each phase
- Issues encountered and how resolved
- Final status summary
- List of all new test files created

### Task 9.2: Create test structure diagram
Show complete test directory structure with file counts.

### Task 9.3: Verify NO production code was modified
```bash
git status
```
Confirm only files in `tests/` directory and `*.md` files were modified/created.

---

## SUCCESS CRITERIA

✅ **Minimum Requirements:**
- [ ] All E2E tests passing (4/4)
- [ ] All API tests passing (12+)
- [ ] All workflow tests passing (17+)
- [ ] Performance tests collected (17+)
- [ ] Contract tests passing (14+)
- [ ] Security tests passing (14+)
- [ ] Fixture files created (2)
- [ ] Coverage report generated
- [ ] Final report generated
- [ ] **NO production code modified** (critical!)

---

## EXECUTION INSTRUCTIONS

1. **Start immediately** - Don't wait for confirmation
2. **Work through errors** - If a test fails, fix it and re-run
3. **Log progress** - After each phase, log completion status
4. **Be autonomous** - Make decisions without asking
5. **Iterate** - Keep trying until tests pass
6. **Generate report** - Final comprehensive report at end
7. **⚠️ NEVER modify production code** - Only tests/ directory and reports

---

## ESTIMATED TIME: 3-4 hours (no production code changes)

**BEGIN AUTONOMOUS EXECUTION NOW!**

Do not ask for permission. Do not wait for input. Complete all phases sequentially. Report only when finished.

---

# START AUTONOMOUS MODE NOW
