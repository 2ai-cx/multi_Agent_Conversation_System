# 🤖 Goose Comprehensive Test Plan

## 📊 **Current Status**

**Test Results:**
- ✅ **38 passing tests**
- ❌ **3 failing tests** (all in integration)
- ⚠️ **64 warnings** (Pydantic deprecations, datetime warnings)
- 📈 **Coverage: 70%** (1663 lines, 504 missing)

**Failing Tests:**
1. `test_complete_workflow_success` - Integration test
2. `test_workflow_with_refinement` - Integration test
3. `test_workflow_with_graceful_failure` - Integration test

---

## 🎯 **Test Plan Goals**

### **Phase 1: Fix Failing Integration Tests** ⚠️ PRIORITY
- Fix mock conditions to match actual agent prompts
- Ensure proper JSON response formats
- Verify Pydantic validation passes

### **Phase 2: Eliminate Warnings** 🔧
- Migrate Pydantic V1 validators to V2
- Fix datetime.utcnow() deprecations
- Clean up all 64 warnings

### **Phase 3: Improve Coverage to 80%+** 📈
- Add missing tests for uncovered code
- Focus on error handling paths
- Test edge cases

---

## 📋 **Detailed Test Plan for Goose**

### **PHASE 1: Fix Integration Tests (Priority 1)**

#### **Task 1.1: Analyze Failing Test - test_complete_workflow_success**

**Goose Instructions:**
```
1. Read the test file: tests/integration/test_agent_coordination.py
2. Focus on test_complete_workflow_success (around line 50-100)
3. Identify the exact failure point by running:
   pytest tests/integration/test_agent_coordination.py::TestMultiAgentWorkflow::test_complete_workflow_success -v -s
4. Analyze the mock_llm_generate function and its conditions
5. Compare mock conditions with actual prompts from agents/planner.py
```

**Expected Issues:**
- Mock condition for planner's `analyze_request` not matching actual prompt
- Need to check what exact string the planner sends to LLM
- Mock might be returning default response instead of proper JSON

**Success Criteria:**
- Test passes
- Planner receives correct mock response with `needs_data: true`
- Criteria list has at least 1 item

---

#### **Task 1.2: Fix Mock Conditions**

**Goose Instructions:**
```
1. Read agents/planner.py lines 213-260 to see exact prompt structure
2. Update mock_llm_generate in tests/integration/test_agent_coordination.py
3. Make conditions more specific:
   - Check for exact phrases from planner prompt
   - Ensure JSON response matches Scorecard model requirements
   - Add debug logging to see what prompt is actually sent

4. Test the fix:
   pytest tests/integration/test_agent_coordination.py::TestMultiAgentWorkflow::test_complete_workflow_success -v -s
```

**Mock Fix Strategy:**
```python
# Current issue: Mock condition too generic
if "analyze" in prompt.lower():
    # This matches too many things!

# Better approach: Check for specific planner phrases
if "analyze the user's request" in prompt.lower() and "return json" in prompt.lower():
    # This is definitely the planner
    return json.dumps({
        "needs_data": true,
        "message_to_timesheet": "Extract timesheet data",
        "criteria": [
            {
                "id": "answers_question",
                "description": "Response answers user question appropriately",
                "expected": "Contains timesheet hours"
            }
        ]
    })
```

**Files to Modify:**
- `tests/integration/test_agent_coordination.py` (lines 50-60)

---

#### **Task 1.3: Fix test_workflow_with_refinement**

**Goose Instructions:**
```
1. Run the test to see exact failure:
   pytest tests/integration/test_agent_coordination.py::TestMultiAgentWorkflow::test_workflow_with_refinement -v -s

2. This test involves:
   - Initial response fails quality check
   - Composer refines the response
   - Quality check passes on second attempt

3. Check mock conditions for:
   - Quality validator returning "no" first time
   - Composer refinement prompt
   - Quality validator returning "yes" second time

4. Update mocks to handle refinement flow properly
```

**Expected Mock Flow:**
```python
# Track call count for quality checks
quality_call_count = 0

def mock_llm_generate(messages, **kwargs):
    prompt = messages[-1]["content"]
    
    # Quality check - fail first, pass second
    if "evaluate" in prompt.lower() and "criterion" in prompt.lower():
        nonlocal quality_call_count
        quality_call_count += 1
        if quality_call_count == 1:
            return "no"  # First check fails
        else:
            return "yes"  # Second check passes
    
    # Composer refinement
    if "refine" in prompt.lower() and "feedback" in prompt.lower():
        return "Refined response with improvements"
```

**Files to Modify:**
- `tests/integration/test_agent_coordination.py` (lines 138-200)

---

#### **Task 1.4: Fix test_workflow_with_graceful_failure**

**Goose Instructions:**
```
1. Run the test:
   pytest tests/integration/test_agent_coordination.py::TestMultiAgentWorkflow::test_workflow_with_graceful_failure -v -s

2. This test simulates failure scenarios:
   - LLM returns invalid JSON
   - Agent handles error gracefully
   - Workflow continues with fallback

3. Update mocks to:
   - Return malformed JSON when appropriate
   - Ensure error handling is triggered
   - Verify fallback responses work

4. Check that assertions match actual error handling behavior
```

**Files to Modify:**
- `tests/integration/test_agent_coordination.py` (lines 219-280)

---

### **PHASE 2: Eliminate Warnings (Priority 2)**

#### **Task 2.1: Fix Pydantic V2 Validator Deprecations**

**Goose Instructions:**
```
1. Read agents/models.py and identify all @validator decorators
2. Migrate to @field_validator (Pydantic V2 style)
3. Update syntax according to Pydantic V2 migration guide

Example migration:
# OLD (V1):
@validator('content')
def validate_content(cls, v):
    if not v:
        raise ValueError('Content cannot be empty')
    return v

# NEW (V2):
@field_validator('content')
@classmethod
def validate_content(cls, v):
    if not v:
        raise ValueError('Content cannot be empty')
    return v
```

**Files to Modify:**
- `agents/models.py` (lines 177, 184, 207, 226, 307)

**Warnings to Fix:** 5 Pydantic validator warnings

---

#### **Task 2.2: Fix Pydantic Config Deprecation**

**Goose Instructions:**
```
1. Read llm/config.py line 13
2. Migrate from class-based config to ConfigDict

Example migration:
# OLD:
class LLMConfig(BaseSettings):
    class Config:
        env_file = ".env"
        case_sensitive = False

# NEW:
from pydantic import ConfigDict

class LLMConfig(BaseSettings):
    model_config = ConfigDict(
        env_file=".env",
        case_sensitive=False
    )
```

**Files to Modify:**
- `llm/config.py` (line 13)

**Warnings to Fix:** 1 config warning

---

#### **Task 2.3: Fix datetime.utcnow() Deprecations**

**Goose Instructions:**
```
1. Find all uses of datetime.utcnow()
2. Replace with datetime.now(datetime.UTC)

Example migration:
# OLD:
from datetime import datetime
self.evaluated_at = datetime.utcnow()

# NEW:
from datetime import datetime, UTC
self.evaluated_at = datetime.now(UTC)
```

**Files to Modify:**
- `agents/models.py` (line 117)
- Any other files using utcnow()

**Warnings to Fix:** ~58 datetime warnings

---

### **PHASE 3: Improve Coverage to 80%+ (Priority 3)**

#### **Task 3.1: Identify Low Coverage Modules**

**Goose Instructions:**
```
1. Run coverage report with details:
   pytest tests/ --cov --cov-report=term-missing --cov-report=html

2. Open htmlcov/index.html to see detailed coverage

3. Identify modules with <70% coverage:
   - Focus on critical paths
   - Identify untested error handlers
   - Find edge cases

4. Create a list of specific functions/methods needing tests
```

---

#### **Task 3.2: Add Tests for Error Handling**

**Goose Instructions:**
```
1. Review each agent's error handling:
   - agents/planner.py - LLM failures, JSON parsing errors
   - agents/timesheet.py - API failures, missing data
   - agents/branding.py - Invalid channel, formatting errors
   - agents/quality.py - Validation failures

2. Create test cases for each error scenario:
   - Mock LLM returning invalid JSON
   - Mock API returning errors
   - Test fallback behaviors
   - Verify error messages

3. Add tests to appropriate test files:
   - tests/unit/test_planner.py
   - tests/unit/test_timesheet.py
   - tests/unit/test_branding.py
   - tests/unit/test_quality.py
```

**Example Test Structure:**
```python
def test_planner_handles_invalid_json(mock_llm_client):
    """Test planner gracefully handles invalid JSON from LLM"""
    # Mock LLM returning malformed JSON
    mock_llm_client.generate.return_value = "not valid json"
    
    planner = PlannerAgent(mock_llm_client)
    result = planner.analyze_request("test request")
    
    # Should use fallback behavior
    assert result is not None
    assert "error" in result or result uses default values
```

---

#### **Task 3.3: Add Tests for Edge Cases**

**Goose Instructions:**
```
1. Test boundary conditions:
   - Empty strings
   - Very long inputs
   - Special characters
   - None values
   - Empty lists/dicts

2. Test concurrent scenarios:
   - Multiple requests at once
   - Rate limiting behavior
   - Cache hits/misses

3. Test configuration edge cases:
   - Missing environment variables
   - Invalid API keys
   - Timeout scenarios
```

---

#### **Task 3.4: Add Integration Tests for New Scenarios**

**Goose Instructions:**
```
1. Add tests for complete workflows:
   - Email-to-SMS conversation
   - WhatsApp conversation
   - Multi-turn conversations
   - Context persistence

2. Add tests for Temporal workflows:
   - Daily reminder workflow
   - Conversation workflow
   - Error recovery in workflows

3. Create tests/integration/test_workflows.py if needed
```

---

## 🎯 **Execution Plan for Goose**

### **Session 1: Fix Integration Tests (30-45 min)**

**Goose Prompt:**
```
I need you to fix the 3 failing integration tests in tests/integration/test_agent_coordination.py.

Current failures:
1. test_complete_workflow_success - Planner mock not matching actual prompt
2. test_workflow_with_refinement - Refinement flow not properly mocked
3. test_workflow_with_graceful_failure - Error handling assertions incorrect

Steps:
1. Run each test individually with -v -s to see exact failures
2. Read agents/planner.py to understand actual prompt structure
3. Update mock_llm_generate conditions to be more specific
4. Ensure JSON responses match Pydantic model requirements
5. Test each fix individually
6. Run all integration tests to confirm

Success criteria:
- All 3 tests pass
- No new failures introduced
- Mock conditions are clear and maintainable
```

---

### **Session 2: Eliminate Warnings (20-30 min)**

**Goose Prompt:**
```
I need you to eliminate all 64 warnings in the test suite.

Warnings to fix:
1. 5 Pydantic V1 @validator deprecations in agents/models.py
2. 1 Pydantic Config deprecation in llm/config.py
3. ~58 datetime.utcnow() deprecations in agents/models.py and tests

Steps:
1. Migrate @validator to @field_validator in agents/models.py
2. Migrate Config class to ConfigDict in llm/config.py
3. Replace datetime.utcnow() with datetime.now(UTC)
4. Run tests to ensure no functionality broken
5. Verify all warnings eliminated

Success criteria:
- 0 warnings when running pytest
- All tests still pass
- Code follows Pydantic V2 best practices
```

---

### **Session 3: Improve Coverage (45-60 min)**

**Goose Prompt:**
```
I need you to improve test coverage from 70% to 80%+.

Current coverage: 70% (504 lines missing)
Target: 80%+ (reduce missing to ~330 lines)

Steps:
1. Generate detailed coverage report: pytest --cov --cov-report=html
2. Identify modules with lowest coverage
3. Focus on:
   - Error handling paths
   - Edge cases
   - Fallback behaviors
4. Add tests for uncovered code
5. Prioritize critical paths over trivial code

Success criteria:
- Overall coverage >= 80%
- All critical error handlers tested
- Edge cases covered
- No decrease in existing test quality
```

---

## 📊 **Progress Tracking**

### **Phase 1: Integration Tests**
- [ ] Task 1.1: Analyze test_complete_workflow_success
- [ ] Task 1.2: Fix mock conditions
- [ ] Task 1.3: Fix test_workflow_with_refinement
- [ ] Task 1.4: Fix test_workflow_with_graceful_failure
- [ ] Verify: All integration tests pass

### **Phase 2: Warnings**
- [ ] Task 2.1: Fix Pydantic validator deprecations (5 warnings)
- [ ] Task 2.2: Fix Pydantic config deprecation (1 warning)
- [ ] Task 2.3: Fix datetime deprecations (~58 warnings)
- [ ] Verify: 0 warnings in test output

### **Phase 3: Coverage**
- [ ] Task 3.1: Identify low coverage modules
- [ ] Task 3.2: Add error handling tests
- [ ] Task 3.3: Add edge case tests
- [ ] Task 3.4: Add integration scenario tests
- [ ] Verify: Coverage >= 80%

---

## 📝 **Test Execution Commands**

### **Run Specific Tests:**
```bash
# Single test
pytest tests/integration/test_agent_coordination.py::TestMultiAgentWorkflow::test_complete_workflow_success -v -s

# All integration tests
pytest tests/integration/ -v

# All unit tests
pytest tests/unit/ -v

# Specific module
pytest tests/unit/test_planner.py -v
```

### **Coverage Reports:**
```bash
# Terminal report
pytest tests/ --cov --cov-report=term-missing

# HTML report
pytest tests/ --cov --cov-report=html
open htmlcov/index.html

# Focus on specific module
pytest tests/ --cov=agents.planner --cov-report=term-missing
```

### **Check Warnings:**
```bash
# Show all warnings
pytest tests/ -v

# Show warnings summary
pytest tests/ --tb=no -q

# Treat warnings as errors (for final check)
pytest tests/ -W error
```

---

## 🎯 **Success Metrics**

### **Phase 1 Complete:**
- ✅ 41/41 tests passing (0 failures)
- ✅ All integration tests green
- ✅ Mock conditions clear and maintainable

### **Phase 2 Complete:**
- ✅ 0 warnings in test output
- ✅ Pydantic V2 compliant
- ✅ Modern datetime usage

### **Phase 3 Complete:**
- ✅ Coverage >= 80%
- ✅ All critical paths tested
- ✅ Error handling verified
- ✅ Edge cases covered

### **Final Success:**
- ✅ 41+ tests passing
- ✅ 0 warnings
- ✅ 80%+ coverage
- ✅ All agents thoroughly tested
- ✅ Integration scenarios verified
- ✅ Production-ready test suite

---

## 🤖 **Ready for Goose Execution**

**Start with Phase 1:**
```
Read GOOSE-TEST-PLAN.md and execute Phase 1: Fix Integration Tests.
Follow the detailed instructions in Session 1.
Report progress after each task.
```

**Then Phase 2:**
```
Execute Phase 2: Eliminate Warnings.
Follow the detailed instructions in Session 2.
Verify 0 warnings remain.
```

**Finally Phase 3:**
```
Execute Phase 3: Improve Coverage to 80%+.
Follow the detailed instructions in Session 3.
Generate final coverage report.
```

---

**📋 This comprehensive test plan gives Goose clear, actionable steps to achieve 100% passing tests with 80%+ coverage and 0 warnings!**
