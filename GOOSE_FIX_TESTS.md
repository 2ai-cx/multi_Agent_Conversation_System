# 🚨 Goose: Fix Failing Tests & Improve Coverage

**Date:** December 2, 2025  
**Current Status:** 46.3% tests passing, 36% coverage  
**Target:** 100% tests passing, 80%+ coverage

---

## 📊 Current Situation

### Test Results:
- ✅ **Passed:** 19/41 (46.3%)
- ❌ **Failed:** 22/41 (53.7%)
- 📊 **Coverage:** 36% (Target: 80%+)

### Critical Issues:
1. 🔴 **Integration tests:** 4/4 failed (100% failure)
2. 🔴 **Branding tests:** 8/8 failed (100% failure)
3. 🔴 **Timesheet tests:** 6/6 failed (100% failure)
4. 🔴 **Planner tests:** 3/3 failed (75% failure)
5. 🟡 **Quality tests:** 1/6 failed (17% failure)

### Untested Modules (0% coverage):
- `llm/cache.py`
- `llm/error_handler.py`
- `llm/opik_tracker.py`
- `llm/rate_limiter.py`
- `llm/tenant_key_manager.py`

---

## 🦢 Goose Prompts to Fix Everything

### 🔴 PRIORITY 1: Fix Critical Failing Tests

#### Prompt 1: Fix Timesheet Agent Tests (6/6 failing)

```
The timesheet agent tests are failing because extract_timesheet_data method is missing.

Analyze agents/timesheet.py and:
1. Check if extract_timesheet_data method exists
2. If missing, check what the tests expect this method to do
3. Look at tests/unit/test_timesheet.py to understand the expected behavior
4. Either:
   a) Add the missing method to agents/timesheet.py, OR
   b) Update the tests to match the actual implementation
5. Ensure the method properly extracts timesheet data from Harvest responses
6. Re-run tests: pytest tests/unit/test_timesheet.py -v
7. Fix any remaining failures

Goal: Get all 6 timesheet tests passing.
```

#### Prompt 2: Fix Branding Agent Tests (8/8 failing)

```
All branding agent tests are failing due to missing format_sms and format_email methods.

Analyze agents/branding.py and:
1. Check if format_sms, format_email, format_whatsapp methods exist
2. Look at tests/unit/test_branding.py to understand expected behavior
3. Either:
   a) Add missing formatting methods to agents/branding.py, OR
   b) Update tests to match actual apply_branding() implementation
4. Ensure methods handle:
   - SMS: 160 character limit, plain text
   - Email: HTML formatting, subject lines
   - WhatsApp: Emoji support, markdown
5. Re-run tests: pytest tests/unit/test_branding.py -v
6. Fix any remaining failures

Goal: Get all 8 branding tests passing.
```

#### Prompt 3: Fix Planner Agent Tests (3/4 failing)

```
Planner agent tests are failing in core planning functionality.

Analyze the failures in tests/unit/test_planner.py:
1. Run: pytest tests/unit/test_planner.py -v --tb=short
2. For each failing test, identify:
   - What the test expects
   - What the actual code does
   - Why they don't match
3. Check if the issue is:
   - Missing methods in agents/planner.py
   - Incorrect test expectations
   - Mock setup problems
4. Fix the issues (prefer fixing tests to match actual implementation)
5. Ensure JSON minification integration is working
6. Re-run until all tests pass

Goal: Get 4/4 planner tests passing.
```

#### Prompt 4: Fix Integration Tests (4/4 failing)

```
All integration tests are failing due to agent coordination issues.

Analyze tests/integration/test_agent_coordination.py:
1. Run: pytest tests/integration/test_agent_coordination.py -v --tb=long
2. Identify the root cause:
   - Are agents not communicating properly?
   - Are mocks not set up correctly?
   - Are workflows not executing?
3. Check if the test expectations match unified_workflows.py implementation
4. Fix mock setup for:
   - Temporal activities
   - LLM client responses
   - Harvest API responses
   - Supabase interactions
5. Ensure data flows correctly: Planner → Timesheet → Planner → Quality → Branding
6. Re-run until all integration tests pass

Goal: Get all 4 integration tests passing.
```

---

### 🟡 PRIORITY 2: Add Missing Tests (0% Coverage Modules)

#### Prompt 5: Create Tests for llm/cache.py (0% → 80%+)

```
Create comprehensive tests for llm/cache.py which currently has 0% coverage.

Create tests/unit/test_cache.py with:

1. Test cache initialization
2. Test get() method:
   - Cache hit
   - Cache miss
   - Expired entries
3. Test set() method:
   - Store new entries
   - Update existing entries
   - Handle TTL
4. Test delete() method
5. Test clear() method
6. Test cache size limits
7. Test thread safety (if applicable)
8. Mock any external dependencies

Requirements:
- Use pytest fixtures
- Mock file system or Redis (depending on implementation)
- Aim for 80%+ coverage
- All tests must pass

Run: pytest tests/unit/test_cache.py -v --cov=llm.cache
```

#### Prompt 6: Create Tests for llm/error_handler.py (0% → 80%+)

```
Create comprehensive tests for llm/error_handler.py which currently has 0% coverage.

Create tests/unit/test_error_handler.py with:

1. Test error handling for different error types:
   - API errors (429, 500, 503)
   - Network errors
   - Timeout errors
   - Authentication errors
2. Test retry logic:
   - Exponential backoff
   - Max retries
   - Retry conditions
3. Test error logging
4. Test error recovery strategies
5. Test circuit breaker (if implemented)
6. Mock external API calls

Requirements:
- Use pytest fixtures
- Mock all external dependencies
- Test both success and failure paths
- Aim for 80%+ coverage

Run: pytest tests/unit/test_error_handler.py -v --cov=llm.error_handler
```

#### Prompt 7: Create Tests for llm/opik_tracker.py (0% → 80%+)

```
Create comprehensive tests for llm/opik_tracker.py which currently has 0% coverage.

Create tests/unit/test_opik_tracker.py with:

1. Test OpikTracker initialization:
   - With Opik enabled
   - With Opik disabled
2. Test lazy loading of Opik client
3. Test log_completion() method:
   - Successful logging
   - Failed logging
   - With cached responses
   - With different tenant/user IDs
4. Test token counting
5. Test cost calculation
6. Test error handling when Opik is unavailable
7. Mock Opik API calls

Requirements:
- Use pytest fixtures
- Mock Opik client completely
- Test async functionality
- Aim for 80%+ coverage

Run: pytest tests/unit/test_opik_tracker.py -v --cov=llm.opik_tracker
```

#### Prompt 8: Create Tests for llm/rate_limiter.py (0% → 80%+)

```
Create comprehensive tests for llm/rate_limiter.py which currently has 0% coverage.

Create tests/unit/test_rate_limiter.py with:

1. Test rate limiter initialization
2. Test acquire() method:
   - Within rate limit
   - Exceeding rate limit
   - Rate limit reset
3. Test different rate limit strategies:
   - Token bucket
   - Sliding window
   - Fixed window
4. Test concurrent requests
5. Test rate limit per tenant/user
6. Test rate limit configuration
7. Mock time for testing

Requirements:
- Use pytest fixtures
- Test async functionality
- Use freezegun or similar for time mocking
- Aim for 80%+ coverage

Run: pytest tests/unit/test_rate_limiter.py -v --cov=llm.rate_limiter
```

#### Prompt 9: Create Tests for llm/tenant_key_manager.py (0% → 80%+)

```
Create comprehensive tests for llm/tenant_key_manager.py which currently has 0% coverage.

Create tests/unit/test_tenant_key_manager.py with:

1. Test key manager initialization
2. Test get_key() method:
   - For different tenants
   - With fallback keys
   - With missing keys
3. Test set_key() method
4. Test delete_key() method
5. Test key rotation
6. Test key validation
7. Test Azure Key Vault integration
8. Mock Azure Key Vault API

Requirements:
- Use pytest fixtures
- Mock Azure Key Vault completely
- Test error handling
- Aim for 80%+ coverage

Run: pytest tests/unit/test_tenant_key_manager.py -v --cov=llm.tenant_key_manager
```

---

### 🟢 PRIORITY 3: Improve Low Coverage Modules

#### Prompt 10: Improve llm/client.py Coverage (24% → 80%+)

```
llm/client.py currently has only 24% coverage. Improve it to 80%+.

Analyze tests/unit/test_llm_client.py (if it exists) or create it:

1. Run coverage report: pytest --cov=llm.client --cov-report=html
2. Open htmlcov/llm_client_py.html to see uncovered lines
3. Add tests for uncovered functionality:
   - LLMClient initialization
   - generate() method with different providers
   - Cache integration
   - Rate limiting
   - Error handling and retries
   - Opik tracking integration
   - Token counting
   - Cost calculation
4. Mock all external API calls (OpenAI, Azure, etc.)
5. Test async functionality
6. Re-run coverage until 80%+

Run: pytest tests/unit/test_llm_client.py -v --cov=llm.client --cov-report=term-missing
```

#### Prompt 11: Improve agents/timesheet.py Coverage (14% → 80%+)

```
agents/timesheet.py has only 14% coverage. This is critical functionality.

After fixing the failing tests, improve coverage:

1. Run: pytest tests/unit/test_timesheet.py --cov=agents.timesheet --cov-report=html
2. Identify uncovered lines in htmlcov/agents_timesheet_py.html
3. Add tests for:
   - All tool execution paths
   - Error handling
   - Different Harvest API responses
   - Edge cases (empty timesheets, errors, etc.)
   - Parameter extraction
   - Response formatting
4. Ensure all methods are tested
5. Re-run until 80%+ coverage

Run: pytest tests/unit/test_timesheet.py -v --cov=agents.timesheet --cov-report=term-missing
```

#### Prompt 12: Improve agents/branding.py Coverage (38% → 70%+)

```
agents/branding.py has only 38% coverage.

After fixing the failing tests, improve coverage:

1. Run: pytest tests/unit/test_branding.py --cov=agents.branding --cov-report=html
2. Identify uncovered lines
3. Add tests for:
   - All formatting methods (SMS, WhatsApp, Email)
   - Character limits (SMS 160 chars)
   - HTML formatting (Email)
   - Emoji handling (WhatsApp)
   - Error handling
   - Edge cases (very long messages, special characters)
4. Test different brand styles
5. Re-run until 70%+ coverage

Run: pytest tests/unit/test_branding.py -v --cov=agents.branding --cov-report=term-missing
```

---

### 🔧 PRIORITY 4: Fix Deprecation Warnings

#### Prompt 13: Fix Pydantic V1 → V2 Migration

```
Fix 41 Pydantic deprecation warnings by migrating from V1 to V2.

1. Find all files using Pydantic validators:
   grep -r "@validator" --include="*.py" .

2. For each file, update:
   - Change: @validator → @field_validator
   - Update validator signature: def validate_field(cls, v) → def validate_field(cls, v, info)
   - Update imports: from pydantic import validator → from pydantic import field_validator
   - Test after each change

3. Common patterns to fix:
   ```python
   # OLD (V1)
   from pydantic import validator
   
   @validator('field_name')
   def validate_field(cls, v):
       return v
   
   # NEW (V2)
   from pydantic import field_validator
   
   @field_validator('field_name')
   def validate_field(cls, v, info):
       return v
   ```

4. Run tests after each file: pytest tests/ -v
5. Ensure no functionality breaks

Goal: Zero Pydantic warnings.
```

#### Prompt 14: Fix Datetime Deprecation Warnings

```
Fix datetime deprecation warnings by updating utcnow() usage.

1. Find all utcnow() usage:
   grep -r "utcnow()" --include="*.py" .

2. Replace with modern approach:
   ```python
   # OLD
   from datetime import datetime
   now = datetime.utcnow()
   
   # NEW
   from datetime import datetime, UTC
   now = datetime.now(UTC)
   ```

3. Update all files
4. Run tests to ensure no breaks: pytest tests/ -v

Goal: Zero datetime warnings.
```

---

### 📊 PRIORITY 5: Final Coverage Push

#### Prompt 15: Achieve 80%+ Overall Coverage

```
Push overall coverage from 36% to 80%+.

1. Run full coverage report:
   pytest tests/ --cov --cov-report=html --cov-report=term-missing

2. Generate coverage summary by module

3. For each module below 80%:
   - Identify uncovered lines
   - Write tests to cover them
   - Focus on:
     * Error paths
     * Edge cases
     * Conditional branches
     * Exception handling

4. Priority order:
   a) 0% coverage modules (cache, error_handler, etc.)
   b) <50% coverage modules (timesheet, branding, client)
   c) <80% coverage modules (planner, config, json_minifier)

5. Re-run coverage after each batch of tests

6. Stop when overall coverage reaches 80%+

Provide final coverage report showing before/after.
```

---

## 🎯 Execution Plan

### Day 1: Fix Critical Failures
1. ✅ Prompt 1: Fix timesheet tests
2. ✅ Prompt 2: Fix branding tests
3. ✅ Prompt 3: Fix planner tests
4. ✅ Prompt 4: Fix integration tests

**Goal:** 100% tests passing

### Day 2: Add Missing Tests
5. ✅ Prompt 5: Test cache.py
6. ✅ Prompt 6: Test error_handler.py
7. ✅ Prompt 7: Test opik_tracker.py
8. ✅ Prompt 8: Test rate_limiter.py
9. ✅ Prompt 9: Test tenant_key_manager.py

**Goal:** 0% → 80% coverage for untested modules

### Day 3: Improve Low Coverage
10. ✅ Prompt 10: Improve client.py coverage
11. ✅ Prompt 11: Improve timesheet.py coverage
12. ✅ Prompt 12: Improve branding.py coverage

**Goal:** All modules >70% coverage

### Day 4: Clean Up
13. ✅ Prompt 13: Fix Pydantic warnings
14. ✅ Prompt 14: Fix datetime warnings
15. ✅ Prompt 15: Final coverage push to 80%+

**Goal:** 80%+ coverage, zero warnings

---

## 📈 Expected Results

### Before:
- ✅ Tests Passing: 19/41 (46%)
- 📊 Coverage: 36%
- ⚠️ Warnings: 41+ deprecations

### After:
- ✅ Tests Passing: 41/41 (100%)
- 📊 Coverage: 80%+
- ⚠️ Warnings: 0

---

## 🚀 Quick Start

### Copy this into Goose Desktop to begin:

```
I need to fix failing tests and improve coverage for my Python project.

Current status:
- 22/41 tests failing (53.7% failure rate)
- 36% code coverage (need 80%+)
- Critical issues in timesheet, branding, planner, and integration tests

Start with the most critical issue: timesheet agent tests are failing because extract_timesheet_data method is missing. Analyze agents/timesheet.py and tests/unit/test_timesheet.py, then either add the missing method or update the tests to match the actual implementation. Goal: get all 6 timesheet tests passing.
```

---

**Let's fix everything systematically with Goose!** 🦢🔧

Start with Prompt 1 and work through them in order.
