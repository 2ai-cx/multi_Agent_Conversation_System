# 🦢 Goose Testing Prompts

**For use with Goose Desktop App**  
**Project:** Timesheet Multi-Agent System  
**Date:** December 2, 2025

---

## 🎯 How to Use These Prompts

1. **Open Goose Desktop App**
2. **Navigate to project directory:**
   ```
   /Users/dongshulin/Library/CloudStorage/OneDrive-2ai.cx/Desktop/GitHub/multi_Agent_Conversation_System
   ```
3. **Copy and paste these prompts into Goose**
4. **Let Goose generate and run the tests**

---

## 📝 Prompt 1: Generate Tests for Planner Agent

```
Write comprehensive pytest unit tests for agents/planner.py. 

Requirements:
- Create tests/unit/test_planner.py
- Include test fixtures for LLMClient and PlannerAgent
- Test analyze_request() method with various user messages
- Test compose_response() method with mock Harvest data
- Test refine() method for response improvement
- Test graceful_failure() method for error handling
- Test JSON minification integration (verify minify_for_llm is called)
- Mock all LLM API calls to avoid actual API usage
- Use pytest-asyncio for async tests
- Aim for 80%+ code coverage
- Include edge cases and error scenarios

Save the tests to tests/unit/test_planner.py and run them with pytest.
```

---

## 📝 Prompt 2: Generate Tests for JSON Minifier

```
Write comprehensive pytest unit tests for llm/json_minifier.py.

Requirements:
- Create tests/unit/test_json_minifier.py
- Test minify_for_llm() function with various JSON structures
- Test key abbreviation (abbreviate_keys=True)
- Test without key abbreviation (abbreviate_keys=False)
- Test with nested JSON objects
- Test with arrays
- Test with mixed data types
- Verify token count reduction (should be ~50%)
- Test get_minification_instruction() function
- Include edge cases (empty objects, null values, special characters)
- Aim for 90%+ code coverage

Save the tests to tests/unit/test_json_minifier.py and run them with pytest.
```

---

## 📝 Prompt 3: Generate Tests for Timesheet Agent

```
Write comprehensive pytest unit tests for agents/timesheet.py.

Requirements:
- Create tests/unit/test_timesheet.py
- Include test fixtures for LLMClient and TimesheetAgent
- Test execute() method with various user requests
- Mock HarvestToolsWrapper responses
- Test tool selection logic
- Test parameter extraction from LLM responses
- Test error handling when tools fail
- Test response formatting
- Use pytest-asyncio for async tests
- Aim for 80%+ code coverage

Save the tests to tests/unit/test_timesheet.py and run them with pytest.
```

---

## 📝 Prompt 4: Generate Tests for Quality Agent

```
Write comprehensive pytest unit tests for agents/quality.py.

Requirements:
- Create tests/unit/test_quality.py
- Include test fixtures for LLMClient and QualityAgent
- Test validate() method with various responses
- Test _evaluate_criterion() method
- Mock LLM responses for quality evaluation
- Test pass/fail detection
- Test feedback generation
- Test with multiple quality criteria
- Use pytest-asyncio for async tests
- Aim for 80%+ code coverage

Save the tests to tests/unit/test_quality.py and run them with pytest.
```

---

## 📝 Prompt 5: Generate Tests for Branding Agent

```
Write comprehensive pytest unit tests for agents/branding.py.

Requirements:
- Create tests/unit/test_branding.py
- Include test fixtures for LLMClient and BrandingAgent
- Test apply_branding() method for different channels (sms, whatsapp, email)
- Mock LLM responses for formatting
- Test SMS formatting (160 char limit)
- Test WhatsApp formatting (emoji support)
- Test email formatting (HTML support)
- Test error handling
- Use pytest-asyncio for async tests
- Aim for 80%+ code coverage

Save the tests to tests/unit/test_branding.py and run them with pytest.
```

---

## 📝 Prompt 6: Generate Integration Tests for Workflows

```
Write pytest integration tests for unified_workflows.py.

Requirements:
- Create tests/integration/test_workflows.py
- Test MultiAgentConversationWorkflow end-to-end
- Mock all external services (Harvest API, Twilio, Supabase)
- Test data flow between agents (Planner → Timesheet → Planner → Quality → Branding)
- Test error propagation and handling
- Test conversation storage
- Test metrics logging
- Use pytest-asyncio for async tests
- Include fixtures for mock services
- Aim for 70%+ code coverage

Save the tests to tests/integration/test_workflows.py and run them with pytest.
```

---

## 📝 Prompt 7: Setup Test Infrastructure

```
Set up the complete test infrastructure for this project.

Requirements:
1. Create directory structure:
   - tests/
   - tests/unit/
   - tests/integration/
   - tests/fixtures/

2. Create tests/__init__.py with common imports

3. Create tests/conftest.py with shared fixtures:
   - llm_config fixture
   - llm_client fixture
   - mock_harvest_response fixture
   - mock_llm_response fixture

4. Create pytest.ini with configuration:
   - Test paths
   - Coverage settings
   - Async mode
   - Verbose output

5. Create tests/fixtures/harvest_responses.py with mock data:
   - MOCK_TIMESHEET_RESPONSE
   - MOCK_EMPTY_TIMESHEET
   - MOCK_ERROR_RESPONSE

6. Install required packages:
   pip install pytest pytest-asyncio pytest-cov pytest-mock

7. Create a README in tests/ explaining how to run tests

Execute all setup steps and confirm everything is ready.
```

---

## 📝 Prompt 8: Run All Tests and Generate Coverage Report

```
Run the complete test suite and generate a coverage report.

Requirements:
1. Run all unit tests: pytest tests/unit/ -v
2. Run all integration tests: pytest tests/integration/ -v
3. Run all tests with coverage: pytest tests/ --cov --cov-report=html --cov-report=term-missing
4. Show coverage summary
5. Identify areas with low coverage
6. Suggest additional tests for uncovered code

Generate a summary report showing:
- Total tests run
- Pass/fail status
- Coverage percentage by file
- Areas needing more tests
```

---

## 📝 Prompt 9: Fix Any Failing Tests

```
Analyze any failing tests and fix them.

Requirements:
1. Run pytest and identify failing tests
2. For each failing test:
   - Analyze the error message
   - Identify the root cause
   - Fix the test or the code
   - Re-run to verify fix
3. Ensure all tests pass
4. Maintain or improve coverage
5. Document any changes made

Provide a summary of:
- Tests that were failing
- Root causes
- Fixes applied
- Final test status
```

---

## 📝 Prompt 10: Generate Test Documentation

```
Generate comprehensive documentation for the test suite.

Requirements:
1. Create tests/README.md with:
   - Overview of test structure
   - How to run tests
   - How to add new tests
   - Coverage goals
   - CI/CD integration

2. Add docstrings to all test functions explaining:
   - What is being tested
   - Expected behavior
   - Edge cases covered

3. Create a test coverage report summary

4. Document any mock data and fixtures

Save documentation to tests/README.md
```

---

## 🎯 Recommended Order

Use these prompts in this order for best results:

1. **Prompt 7** - Setup infrastructure first
2. **Prompt 1** - Planner agent tests (most critical)
3. **Prompt 2** - JSON minifier tests (verify optimization)
4. **Prompt 3** - Timesheet agent tests
5. **Prompt 4** - Quality agent tests
6. **Prompt 5** - Branding agent tests
7. **Prompt 6** - Integration tests
8. **Prompt 8** - Run all tests and check coverage
9. **Prompt 9** - Fix any failures
10. **Prompt 10** - Generate documentation

---

## 💡 Tips for Using Goose

### Best Practices:

1. **Be Specific:** The more detailed your prompt, the better the results
2. **One Task at a Time:** Don't combine multiple prompts
3. **Review Output:** Always review generated tests before running
4. **Iterate:** If tests fail, ask Goose to fix them
5. **Save Progress:** Commit working tests to git frequently

### Common Commands:

```bash
# Run specific test file
pytest tests/unit/test_planner.py -v

# Run with coverage
pytest tests/unit/test_planner.py --cov=agents.planner --cov-report=term-missing

# Run only failed tests
pytest --lf

# Run tests matching pattern
pytest -k "test_analyze"
```

---

## 🚀 Quick Start

**Copy this into Goose to get started:**

```
I'm working on a Python project for a Timesheet Multi-Agent System. I need to set up comprehensive automated testing using pytest. 

The project structure is:
- agents/ (planner.py, timesheet.py, quality.py, branding.py)
- llm/ (client.py, json_minifier.py, config.py, opik_tracker.py)
- unified_server.py (FastAPI server)
- unified_workflows.py (Temporal workflows)

Please start by setting up the test infrastructure (directories, conftest.py, pytest.ini) and then generate comprehensive unit tests for agents/planner.py. Make sure to mock all external dependencies and LLM API calls.
```

---

**Ready to start testing with Goose!** 🦢🧪

Just open Goose Desktop, navigate to this project directory, and start with the prompts above!
