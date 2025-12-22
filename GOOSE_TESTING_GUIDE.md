# 🦢 Goose Testing Guide - Existing Test Suite

**Date:** December 2, 2025  
**Status:** Tests Already Exist - Ready to Enhance  
**Project:** Timesheet Multi-Agent System

---

## ✅ Current Test Structure

You already have a comprehensive test suite!

```
tests/
├── __init__.py
├── unit/
│   ├── __init__.py
│   ├── test_planner.py       ✅ (9 KB)
│   ├── test_timesheet.py     ✅ (5.8 KB)
│   ├── test_quality.py       ✅ (9.2 KB)
│   └── test_branding.py      ✅ (7.7 KB)
├── integration/
│   ├── __init__.py
│   └── test_agent_coordination.py  ✅ (13.4 KB)
├── fixtures/
│   ├── __init__.py
│   ├── mock_harvest_data.py  ✅ (3.7 KB)
│   ├── sample_requests.py    ✅ (2.2 KB)
│   └── sample_scorecards.py  ✅ (4.3 KB)
└── test_json_minification_integration.py  ✅ (6.1 KB)
```

**Total:** ~60 KB of test code already written!

---

## 🎯 What's Missing

### 1. Test Configuration
- ❌ No `pytest.ini` configuration file
- ❌ No `conftest.py` for shared fixtures
- ❌ No coverage configuration

### 2. Additional Tests Needed
- ❌ Tests for `llm/json_minifier.py`
- ❌ Tests for `llm/client.py`
- ❌ Tests for `llm/opik_tracker.py`
- ❌ API endpoint tests for `unified_server.py`
- ❌ Workflow tests for `unified_workflows.py`

### 3. CI/CD Integration
- ❌ No GitHub Actions workflow
- ❌ No pre-commit hooks

---

## 🦢 Goose Prompts for Enhancement

### Prompt 1: Run Existing Tests

```
I have an existing test suite in the tests/ directory. Please:

1. Check if pytest is installed (pip list | grep pytest)
2. If not, install: pip install pytest pytest-asyncio pytest-cov pytest-mock
3. Run all existing tests: pytest tests/ -v
4. Show me the results (pass/fail count)
5. Identify any failing tests
6. Show test coverage: pytest tests/ --cov=agents --cov=llm --cov=unified_server --cov=unified_workflows --cov-report=term-missing

Provide a summary of:
- Total tests found
- Tests passed/failed
- Current coverage percentage
- Files with low coverage
```

### Prompt 2: Create Test Configuration

```
Create comprehensive test configuration files for this project.

Requirements:

1. Create pytest.ini with:
```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
asyncio_mode = auto
addopts = 
    --verbose
    --strict-markers
    --cov=agents
    --cov=llm
    --cov=unified_server
    --cov=unified_workflows
    --cov-report=html
    --cov-report=term-missing
    --cov-fail-under=75
markers =
    unit: Unit tests
    integration: Integration tests
    slow: Slow running tests
```

2. Create tests/conftest.py with shared fixtures:
   - llm_config fixture (mock LLM configuration)
   - llm_client fixture (mock LLM client)
   - mock_harvest_api fixture
   - mock_supabase fixture
   - event_loop fixture for async tests

3. Verify configuration works by running: pytest tests/ --collect-only
```

### Prompt 3: Analyze Existing Tests

```
Analyze the existing test files and provide a detailed report.

For each test file:
- tests/unit/test_planner.py
- tests/unit/test_timesheet.py
- tests/unit/test_quality.py
- tests/unit/test_branding.py
- tests/integration/test_agent_coordination.py
- tests/test_json_minification_integration.py

Report:
1. Number of test functions
2. What is being tested
3. Coverage gaps (what's not tested)
4. Any issues or improvements needed
5. Missing edge cases
6. Mock usage (are external dependencies properly mocked?)

Provide recommendations for improving each test file.
```

### Prompt 4: Generate Missing Unit Tests

```
Generate comprehensive unit tests for the LLM module files that don't have tests yet.

1. Create tests/unit/test_json_minifier.py:
   - Test minify_for_llm() with various JSON structures
   - Test key abbreviation
   - Test token count reduction
   - Test get_minification_instruction()
   - Aim for 90%+ coverage

2. Create tests/unit/test_llm_client.py:
   - Test LLMClient initialization
   - Test generate() method with mocked OpenAI responses
   - Test caching functionality
   - Test rate limiting
   - Test error handling
   - Mock all external API calls
   - Aim for 80%+ coverage

3. Create tests/unit/test_opik_tracker.py:
   - Test OpikTracker initialization
   - Test log_completion() method
   - Test lazy loading of Opik client
   - Mock Opik API calls
   - Aim for 80%+ coverage

Run the tests after creation and fix any failures.
```

### Prompt 5: Generate API Endpoint Tests

```
Generate comprehensive tests for the FastAPI endpoints in unified_server.py.

Create tests/integration/test_api_endpoints.py with:

1. Test fixtures:
   - FastAPI TestClient
   - Mock Temporal client
   - Mock Supabase client

2. Test all endpoints:
   - GET /health (verify all health checks)
   - POST /webhook/sms (test SMS webhook handling)
   - POST /webhook/whatsapp (test WhatsApp webhook)
   - POST /check-timesheet-user1 (test manual trigger)
   - POST /check-timesheet-user2
   - Test error responses (400, 500)
   - Test authentication/authorization

3. Use httpx.AsyncClient for async endpoint testing
4. Mock all external services
5. Aim for 80%+ coverage of unified_server.py

Run tests and verify all endpoints work correctly.
```

### Prompt 6: Generate Workflow Tests

```
Generate comprehensive tests for Temporal workflows in unified_workflows.py.

Create tests/integration/test_workflows.py with:

1. Test MultiAgentConversationWorkflow:
   - Test successful conversation flow
   - Test with different channels (sms, whatsapp, email)
   - Test error handling and retries
   - Test conversation storage
   - Mock all activities

2. Test TimesheetReminderWorkflow:
   - Test daily reminder generation
   - Test joke integration
   - Test SMS sending
   - Mock all external services

3. Test individual activities:
   - test_planner_analyze_activity
   - test_timesheet_execute_activity
   - test_quality_validate_activity
   - test_branding_apply_activity
   - test_add_joke_to_reminder_activity

4. Use Temporal testing framework
5. Mock all external dependencies
6. Aim for 70%+ coverage

Run tests and fix any failures.
```

### Prompt 7: Improve Test Coverage

```
Analyze current test coverage and improve it to reach 80%+ overall.

Steps:
1. Run coverage report: pytest tests/ --cov --cov-report=html
2. Open htmlcov/index.html and identify files with <80% coverage
3. For each file with low coverage:
   - Identify uncovered lines
   - Write tests to cover those lines
   - Focus on edge cases and error paths
4. Re-run coverage and verify improvement
5. Repeat until overall coverage is 80%+

Provide a before/after coverage comparison.
```

### Prompt 8: Fix Failing Tests

```
Run all tests and fix any failures.

Process:
1. Run: pytest tests/ -v
2. For each failing test:
   - Show the error message
   - Analyze the root cause
   - Determine if it's a test issue or code issue
   - Fix the problem
   - Re-run to verify
3. Ensure all tests pass
4. Run with coverage to verify no regression

Provide a summary of:
- Tests that were failing
- Root causes identified
- Fixes applied
- Final test status (all passing)
```

### Prompt 9: Setup CI/CD

```
Set up GitHub Actions for automated testing on every commit.

Create .github/workflows/tests.yml with:

```yaml
name: Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-asyncio pytest-cov pytest-mock
    
    - name: Run tests
      env:
        OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
        SUPABASE_KEY: ${{ secrets.SUPABASE_KEY }}
      run: |
        pytest tests/ --cov --cov-report=xml --cov-fail-under=75
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        fail_ci_if_error: true
```

Also create .github/workflows/lint.yml for code quality checks.
```

### Prompt 10: Generate Test Documentation

```
Create comprehensive documentation for the test suite.

Create tests/README.md with:

1. Overview
   - Test structure explanation
   - What each directory contains
   - Coverage goals

2. Running Tests
   - How to run all tests
   - How to run specific tests
   - How to run with coverage
   - How to run in watch mode

3. Writing New Tests
   - Test naming conventions
   - How to use fixtures
   - How to mock dependencies
   - Best practices

4. Current Coverage
   - Coverage by module
   - Areas needing improvement
   - Coverage goals

5. CI/CD Integration
   - GitHub Actions setup
   - How tests run on PR
   - Coverage requirements

6. Troubleshooting
   - Common issues
   - How to debug failing tests
   - Mock setup tips

Make it comprehensive and easy to follow for new developers.
```

---

## 🚀 Quick Start with Goose

### Step 1: Open Goose Desktop
Navigate to:
```
/Users/dongshulin/Library/CloudStorage/OneDrive-2ai.cx/Desktop/GitHub/multi_Agent_Conversation_System
```

### Step 2: Start with Prompt 1
Run existing tests to see current state:
```
Run all existing tests in tests/ directory and show me coverage report
```

### Step 3: Create Configuration (Prompt 2)
Set up pytest.ini and conftest.py

### Step 4: Generate Missing Tests (Prompts 4-6)
Fill in the gaps in test coverage

### Step 5: Improve Coverage (Prompt 7)
Get to 80%+ coverage

### Step 6: Setup CI/CD (Prompt 9)
Automate testing on every commit

---

## 📊 Expected Outcomes

### After Running All Prompts:

✅ **Complete test configuration** (pytest.ini, conftest.py)  
✅ **80%+ code coverage** across all modules  
✅ **All tests passing** (green build)  
✅ **Missing tests added** (LLM client, JSON minifier, API endpoints)  
✅ **CI/CD pipeline** (GitHub Actions)  
✅ **Comprehensive documentation** (tests/README.md)  

---

## 💡 Tips

1. **Run tests frequently** - After each Goose prompt
2. **Check coverage** - Use `--cov-report=html` to see visual coverage
3. **Fix failures immediately** - Don't let them pile up
4. **Review generated tests** - Ensure they make sense
5. **Commit often** - Save working tests to git

---

**Ready to enhance your test suite with Goose!** 🦢🧪

Start with Prompt 1 to see what you already have!
