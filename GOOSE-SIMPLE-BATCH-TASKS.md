# 🤖 Goose Simple Batch Tasks - Multi-Hour Workflow

## Instructions for Goose

Work through ALL 50 tasks below. Do each task, then move to the next. Do NOT stop. Do NOT ask questions. Work for several hours until ALL tasks complete.

---

## 🚫 RULES
- Only modify files in `tests/` directory
- Never modify production code
- If a task fails, log the error and continue to next task
- Work through ALL 50 tasks sequentially

---

## TASK 1: Fix E2E Test - Remove SenderAgent Line 37
File: `tests/e2e/test_complete_conversation_flow.py`
Action: Delete line 37 that contains `patch("agents.sender.SenderAgent"`
Verify: File still has valid Python syntax

## TASK 2: Fix E2E Test - Remove SenderAgent Line 44
File: `tests/e2e/test_complete_conversation_flow.py`
Action: Delete line 44 that contains `sender = MockSender.return_value`
Verify: File still has valid Python syntax

## TASK 3: Fix E2E Test - Remove sender from yield
File: `tests/e2e/test_complete_conversation_flow.py`
Action: Remove `"sender": sender,` from the yield dictionary (around line 51)
Verify: File still has valid Python syntax

## TASK 4: Fix E2E Test - Fix timestamp line 109
File: `tests/e2e/test_complete_conversation_flow.py`
Action: Replace line 109 `timestamp=pytest.monkeypatch.setattr(...)` with `timestamp=unittest.mock.ANY`
Verify: File still has valid Python syntax

## TASK 5: Fix E2E Test - Fix timestamp line 180
File: `tests/e2e/test_complete_conversation_flow.py`
Action: Replace line 180 timestamp assertion with `timestamp=unittest.mock.ANY`
Verify: File still has valid Python syntax

## TASK 6: Fix E2E Test - Remove sender assertions
File: `tests/e2e/test_complete_conversation_flow.py`
Action: Remove all lines containing `sender.send.assert`
Verify: File still has valid Python syntax

## TASK 7: Run E2E tests
Command: `pytest tests/e2e/test_complete_conversation_flow.py -v`
Log: Record how many tests pass/fail

## TASK 8: Create API test file structure
Action: Create empty file `tests/api/test_health_endpoints.py`
Add: Docstring "Tests for health check endpoints"

## TASK 9: Add imports to API test
File: `tests/api/test_health_endpoints.py`
Add: `import pytest`, `from unittest.mock import AsyncMock, patch`

## TASK 10: Create health test class
File: `tests/api/test_health_endpoints.py`
Add: `class TestHealthEndpoints:` with docstring

## TASK 11: Create test_health_returns_200
File: `tests/api/test_health_endpoints.py`
Add: Empty test method `def test_health_returns_200(self): pass`

## TASK 12: Create test_health_has_status
File: `tests/api/test_health_endpoints.py`
Add: Empty test method `def test_health_has_status(self): pass`

## TASK 13: Create test_health_has_timestamp
File: `tests/api/test_health_endpoints.py`
Add: Empty test method `def test_health_has_timestamp(self): pass`

## TASK 14: Create test_health_has_agents
File: `tests/api/test_health_endpoints.py`
Add: Empty test method `def test_health_has_agents(self): pass`

## TASK 15: Run API health tests
Command: `pytest tests/api/test_health_endpoints.py --collect-only`
Log: Record test count

## TASK 16: Create workflow test file
Action: Create empty file `tests/workflows/test_conversation_workflow.py`
Add: Docstring "Tests for ConversationWorkflow"

## TASK 17: Add workflow test imports
File: `tests/workflows/test_conversation_workflow.py`
Add: `import pytest`, `from unittest.mock import AsyncMock, MagicMock, patch`

## TASK 18: Create workflow test class
File: `tests/workflows/test_conversation_workflow.py`
Add: `@pytest.mark.asyncio` and `class TestConversationWorkflow:`

## TASK 19: Create test_workflow_initializes
File: `tests/workflows/test_conversation_workflow.py`
Add: Empty async test method `async def test_workflow_initializes(self): pass`

## TASK 20: Create test_workflow_calls_planner
File: `tests/workflows/test_conversation_workflow.py`
Add: Empty async test method `async def test_workflow_calls_planner(self): pass`

## TASK 21: Create test_workflow_calls_timesheet
File: `tests/workflows/test_conversation_workflow.py`
Add: Empty async test method `async def test_workflow_calls_timesheet(self): pass`

## TASK 22: Create test_workflow_calls_branding
File: `tests/workflows/test_conversation_workflow.py`
Add: Empty async test method `async def test_workflow_calls_branding(self): pass`

## TASK 23: Create test_workflow_calls_quality
File: `tests/workflows/test_conversation_workflow.py`
Add: Empty async test method `async def test_workflow_calls_quality(self): pass`

## TASK 24: Run workflow tests
Command: `pytest tests/workflows/test_conversation_workflow.py --collect-only`
Log: Record test count

## TASK 25: Create performance test file
Action: Create empty file `tests/performance/test_response_times.py`
Add: Docstring "Tests for response time requirements"

## TASK 26: Add performance test imports
File: `tests/performance/test_response_times.py`
Add: `import pytest`, `from time import time`

## TASK 27: Create performance test class
File: `tests/performance/test_response_times.py`
Add: `@pytest.mark.performance` and `class TestResponseTimes:`

## TASK 28: Create test_planner_response_time
File: `tests/performance/test_response_times.py`
Add: Empty test method `def test_planner_response_time(self): pass`

## TASK 29: Create test_timesheet_fetch_time
File: `tests/performance/test_response_times.py`
Add: Empty test method `def test_timesheet_fetch_time(self): pass`

## TASK 30: Create test_branding_format_time
File: `tests/performance/test_response_times.py`
Add: Empty test method `def test_branding_format_time(self): pass`

## TASK 31: Run performance tests
Command: `pytest tests/performance/test_response_times.py --collect-only`
Log: Record test count

## TASK 32: Create security test file
Action: Create empty file `tests/security/test_authentication.py`
Add: Docstring "Tests for authentication and security"

## TASK 33: Add security test imports
File: `tests/security/test_authentication.py`
Add: `import pytest`, `from unittest.mock import Mock`

## TASK 34: Create security test class
File: `tests/security/test_authentication.py`
Add: `@pytest.mark.security` and `class TestAuthentication:`

## TASK 35: Create test_api_key_required
File: `tests/security/test_authentication.py`
Add: Empty test method `def test_api_key_required(self): pass`

## TASK 36: Create test_invalid_api_key_rejected
File: `tests/security/test_authentication.py`
Add: Empty test method `def test_invalid_api_key_rejected(self): pass`

## TASK 37: Create test_rate_limiting_enforced
File: `tests/security/test_authentication.py`
Add: Empty test method `def test_rate_limiting_enforced(self): pass`

## TASK 38: Run security tests
Command: `pytest tests/security/test_authentication.py --collect-only`
Log: Record test count

## TASK 39: Create contract test file
Action: Create empty file `tests/contracts/test_pydantic_models.py`
Add: Docstring "Tests for Pydantic model validation"

## TASK 40: Add contract test imports
File: `tests/contracts/test_pydantic_models.py`
Add: `import pytest`, `from pydantic import ValidationError`

## TASK 41: Create contract test class
File: `tests/contracts/test_pydantic_models.py`
Add: `class TestPydanticModels:`

## TASK 42: Create test_request_model_validation
File: `tests/contracts/test_pydantic_models.py`
Add: Empty test method `def test_request_model_validation(self): pass`

## TASK 43: Create test_response_model_validation
File: `tests/contracts/test_pydantic_models.py`
Add: Empty test method `def test_response_model_validation(self): pass`

## TASK 44: Run contract tests
Command: `pytest tests/contracts/test_pydantic_models.py --collect-only`
Log: Record test count

## TASK 45: Create fixture file
Action: Create file `tests/fixtures/common_fixtures.py`
Add: Docstring "Common test fixtures"

## TASK 46: Add fixture imports
File: `tests/fixtures/common_fixtures.py`
Add: `import pytest`, `from unittest.mock import Mock`

## TASK 47: Create mock_llm_client fixture
File: `tests/fixtures/common_fixtures.py`
Add: `@pytest.fixture` and `def mock_llm_client(): return Mock()`

## TASK 48: Run all tests
Command: `pytest tests/ --collect-only -q`
Log: Record total test count

## TASK 49: Generate coverage report
Command: `pytest tests/ --cov --cov-report=term-missing -q`
Log: Record coverage percentage

## TASK 50: Create final report
Action: Create file `GOOSE-BATCH-REPORT.md`
Content: List all tasks completed, tests created, any errors encountered

---

## COMPLETION

After finishing all 50 tasks, create GOOSE-BATCH-REPORT.md with:
- Tasks completed: X/50
- Tests created: X
- Files created: X
- Errors encountered: X
- Time taken: X hours

---

START TASK 1 NOW. Work through all 50 tasks without stopping.
