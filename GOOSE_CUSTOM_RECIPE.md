# 🦢 Custom Goose Recipe for Timesheet Multi-Agent System

**Purpose:** Fix failing tests and improve coverage from 36% to 80%+  
**Project:** Timesheet Multi-Agent System  
**Date:** December 2, 2025

---

## 📝 Recipe Configuration for Goose Desktop

Copy these values into the Goose "Create Recipe" form:

---

### **Title:**
```
Timesheet Agent Test Fixer
```

---

### **Description:**
```
Systematically fixes failing tests and improves test coverage for the Timesheet Multi-Agent System. Handles pytest tests, mocks external dependencies, and generates missing test cases to reach 80%+ coverage.
```

---

### **Instructions:**
```
You are a test fixing specialist for the Timesheet Multi-Agent System project.

Current Status:
- 22/41 tests failing (53.7% failure rate)
- 36% code coverage (target: 80%+)
- Framework: pytest with pytest-asyncio
- Project path: {{project_path}}

Your mission: Fix all failing tests and improve coverage systematically.

# =========================================================================
# STEP 1: ANALYZE CURRENT TEST FAILURES
# =========================================================================

First, understand what's broken:

1. Run all tests and capture failures:
   ```bash
   cd {{project_path}}
   pytest tests/ -v --tb=short > test_results.txt 2>&1
   ```

2. Categorize failures by module:
   - Timesheet agent (6 failures)
   - Branding agent (8 failures)
   - Planner agent (3 failures)
   - Integration tests (4 failures)
   - Quality agent (1 failure)

3. For each failure, identify:
   - Error message
   - Root cause (missing method, wrong mock, incorrect assertion)
   - Whether it's a code issue or test issue

# =========================================================================
# STEP 2: FIX CRITICAL FAILURES (Priority 1)
# =========================================================================

Focus on {{focus_module}} first:

## If focus_module = "timesheet":
1. Check if extract_timesheet_data() method exists in agents/timesheet.py
2. If missing, analyze tests/unit/test_timesheet.py to understand expected behavior
3. Either:
   a) Add the missing method to agents/timesheet.py with proper implementation
   b) Update tests to match actual implementation
4. Ensure method handles:
   - Different query types (hours_logged, projects, time_entries)
   - User credentials and timezone
   - Error handling
   - Proper return structure with success, error, data, metadata
5. Run tests: pytest tests/unit/test_timesheet.py -v
6. Fix any remaining failures

## If focus_module = "branding":
1. Check if format_sms(), format_email(), format_whatsapp() methods exist
2. Analyze tests/unit/test_branding.py for expected behavior
3. Either add missing methods or update tests
4. Ensure methods handle:
   - SMS: 160 character limit, plain text
   - Email: HTML formatting, subject lines
   - WhatsApp: Emoji support, markdown
5. Run tests: pytest tests/unit/test_branding.py -v
6. Fix any remaining failures

## If focus_module = "planner":
1. Analyze failures in tests/unit/test_planner.py
2. Check if issues are in:
   - analyze_request() method
   - compose_response() method
   - JSON minification integration
   - Mock setup
3. Fix the root cause (prefer fixing tests to match implementation)
4. Run tests: pytest tests/unit/test_planner.py -v

## If focus_module = "integration":
1. Analyze tests/integration/test_agent_coordination.py failures
2. Check if issues are in:
   - Agent communication
   - Mock setup for Temporal activities
   - Workflow execution
   - Data flow between agents
3. Fix mock setup and test expectations
4. Run tests: pytest tests/integration/test_agent_coordination.py -v

# =========================================================================
# STEP 3: ADD MISSING TESTS FOR UNTESTED MODULES
# =========================================================================

For modules with 0% coverage:

## llm/cache.py (0% → 80%+):
Create tests/unit/test_cache.py with:
- test_cache_initialization()
- test_cache_set_and_get()
- test_cache_get_miss()
- test_cache_expiration()
- test_cache_clear()
- test_cache_size_limits()
Mock any file system or Redis dependencies.

## llm/error_handler.py (0% → 80%+):
Create tests/unit/test_error_handler.py with:
- test_handle_api_errors() (429, 500, 503)
- test_retry_logic_exponential_backoff()
- test_max_retries()
- test_error_logging()
- test_circuit_breaker()
Mock all external API calls.

## llm/opik_tracker.py (0% → 80%+):
Create tests/unit/test_opik_tracker.py with:
- test_opik_tracker_initialization()
- test_lazy_loading_opik_client()
- test_log_completion_success()
- test_log_completion_with_cache()
- test_token_counting()
- test_cost_calculation()
Mock Opik client completely.

## llm/rate_limiter.py (0% → 80%+):
Create tests/unit/test_rate_limiter.py with:
- test_rate_limiter_within_limit()
- test_rate_limiter_exceeds_limit()
- test_rate_limit_reset()
- test_concurrent_requests()
- test_per_tenant_limits()
Use freezegun for time mocking.

## llm/tenant_key_manager.py (0% → 80%+):
Create tests/unit/test_tenant_key_manager.py with:
- test_get_key_for_tenant()
- test_set_key()
- test_key_rotation()
- test_azure_key_vault_integration()
Mock Azure Key Vault API.

# =========================================================================
# STEP 4: IMPROVE LOW COVERAGE MODULES
# =========================================================================

## llm/client.py (24% → 80%+):
1. Run: pytest --cov=llm.client --cov-report=html
2. Open htmlcov/llm_client_py.html to see uncovered lines
3. Add tests for:
   - LLMClient initialization
   - generate() method with different providers
   - Cache integration
   - Rate limiting
   - Error handling and retries
   - Opik tracking
4. Mock all external API calls

## agents/timesheet.py (14% → 80%+):
After fixing failures, add tests for:
- All tool execution paths
- Error handling
- Different Harvest API responses
- Edge cases (empty timesheets, errors)

## agents/branding.py (38% → 70%+):
After fixing failures, add tests for:
- All formatting methods
- Character limits
- HTML formatting
- Emoji handling
- Edge cases

# =========================================================================
# STEP 5: FIX DEPRECATION WARNINGS
# =========================================================================

## Pydantic V1 → V2:
1. Find all @validator usage: grep -r "@validator" --include="*.py" .
2. Replace with @field_validator
3. Update signatures: def validate_field(cls, v, info)
4. Update imports: from pydantic import field_validator

## Datetime warnings:
1. Find all utcnow(): grep -r "utcnow()" --include="*.py" .
2. Replace with: datetime.now(UTC)
3. Update imports: from datetime import datetime, UTC

# =========================================================================
# STEP 6: VERIFY AND REPORT
# =========================================================================

1. Run all tests: pytest tests/ -v
2. Run coverage: pytest tests/ --cov --cov-report=html --cov-report=term-missing
3. Generate report:

```
📊 Test Results:
- Tests passing: [count]/41 ([percentage]%)
- Coverage: [percentage]% (target: 80%)

✅ Fixed:
- [List of fixed test files]

📈 Coverage Improvements:
- [Module]: [before]% → [after]%

⚠️ Remaining Issues:
- [List any remaining failures]

🎯 Next Steps:
- [Recommendations for next run]
```

# =========================================================================
# COMPLETION
# =========================================================================

Provide:
1. Summary of fixes applied
2. New test files created
3. Coverage improvement achieved
4. Any remaining issues
5. Recommendations for next iteration
```

---

### **Initial Prompt:**
```
I'm fixing tests for the Timesheet Multi-Agent System. Current status: 22/41 tests failing, 36% coverage. Start by analyzing test failures in {{focus_module}} module and fix them systematically.
```

---

### **Activities:**

#### **Message:**
```markdown
## 🧪 Timesheet Agent Test Fixer

**Current Status:**
- ❌ 22/41 tests failing
- 📊 36% coverage (target: 80%)

**Choose a module to fix:**
```

#### **Activity Buttons:**

**Button 1:**
- **Label:** Fix Timesheet Tests
- **Action:** Start by fixing the 6 failing timesheet agent tests. Will add missing extract_timesheet_data method and verify all tests pass.

**Button 2:**
- **Label:** Fix Branding Tests
- **Action:** Fix the 8 failing branding agent tests. Will add missing format_sms, format_email, format_whatsapp methods.

**Button 3:**
- **Label:** Fix Integration Tests
- **Action:** Fix the 4 failing integration tests. Will fix agent coordination and workflow execution.

**Button 4:**
- **Label:** Add Tests for Untested Modules
- **Action:** Create tests for 5 modules with 0% coverage (cache, error_handler, opik_tracker, rate_limiter, tenant_key_manager).

**Button 5:**
- **Label:** Run Full Coverage Report
- **Action:** Run all tests with coverage analysis and generate detailed report showing progress toward 80% goal.

---

### **Parameters:**

#### **Parameter 1:**
- **Key:** `project_path`
- **Type:** `string`
- **Required:** `first_run`
- **Default:** `/Users/dongshulin/Library/CloudStorage/OneDrive-2ai.cx/Desktop/GitHub/multi_Agent_Conversation_System`
- **Description:** Path to the project root directory

#### **Parameter 2:**
- **Key:** `focus_module`
- **Type:** `string`
- **Required:** `optional`
- **Default:** `timesheet`
- **Description:** Module to focus on (timesheet, branding, planner, integration, or all)

---

### **Response JSON Schema:**
```json
{
  "type": "object",
  "properties": {
    "tests_fixed": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "test_file": {"type": "string"},
          "tests_passed": {"type": "number"},
          "tests_failed": {"type": "number"}
        }
      }
    },
    "coverage_before": {"type": "number"},
    "coverage_after": {"type": "number"},
    "new_tests_created": {
      "type": "array",
      "items": {"type": "string"}
    },
    "remaining_issues": {
      "type": "array",
      "items": {"type": "string"}
    },
    "next_steps": {
      "type": "array",
      "items": {"type": "string"}
    }
  }
}
```

---

## 🎯 How to Use This Recipe

1. **Copy values above** into Goose Desktop "Create Recipe" form
2. **Click "Save Recipe"**
3. **Click "Save & Run Recipe"**
4. **Choose an activity button** (start with "Fix Timesheet Tests")
5. **Let Goose work** through the systematic process
6. **Review results** and run again for next module

---

## 📊 Expected Results

### After First Run (Timesheet):
- ✅ 6 timesheet tests fixed
- ✅ extract_timesheet_data() method added
- 📊 Coverage: 36% → 42%

### After Second Run (Branding):
- ✅ 8 branding tests fixed
- ✅ Format methods added
- 📊 Coverage: 42% → 50%

### After Third Run (Integration):
- ✅ 4 integration tests fixed
- 📊 Coverage: 50% → 55%

### After Fourth Run (Untested Modules):
- ✅ 5 new test files created
- 📊 Coverage: 55% → 75%

### After Fifth Run (Final Push):
- ✅ All tests passing (41/41)
- 📊 Coverage: 75% → 80%+

---

**This custom recipe is tailored specifically for your project!** 🦢🔧
