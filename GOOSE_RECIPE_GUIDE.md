# 🦢 Using Goose Test Coverage Optimizer Recipe

**Date:** December 2, 2025  
**Recipe:** Test Coverage Optimizer  
**Source:** https://block.github.io/goose/prompt-library

---

## 🎯 What This Recipe Does

The **Test Coverage Optimizer** is a pre-built Goose recipe that:

✅ **Analyzes** existing test patterns and learns your team's style  
✅ **Identifies** critical coverage gaps systematically  
✅ **Generates** targeted test suggestions with code examples  
✅ **Creates** ready-to-use test templates  
✅ **Learns** from each run to improve future suggestions  
✅ **Tracks** progress toward coverage goals  

---

## 🚀 How to Use It

### Method 1: Launch in Goose Desktop (Recommended)

1. **Open Goose Desktop App**

2. **Navigate to Recipe Library**
   - Look for "Test Coverage Optimizer" recipe
   - Or visit: https://block.github.io/goose/prompt-library

3. **Configure Parameters**
   ```yaml
   project_path: /Users/dongshulin/Library/CloudStorage/OneDrive-2ai.cx/Desktop/GitHub/multi_Agent_Conversation_System
   coverage_threshold: 80
   test_framework: auto  # Will detect pytest
   focus_areas: all  # or: core-logic, edge-cases, error-handling, integration
   generate_templates: true
   ```

4. **Launch Recipe**
   - Click "Launch in Goose Desktop"
   - Recipe will auto-start and run through all 8 steps

---

### Method 2: Use Goose CLI Command

```bash
# Copy the Goose CLI command from the recipe page
goose run test-coverage-optimizer \
  --project_path=/Users/dongshulin/Library/CloudStorage/OneDrive-2ai.cx/Desktop/GitHub/multi_Agent_Conversation_System \
  --coverage_threshold=80 \
  --test_framework=auto \
  --focus_areas=all \
  --generate_templates=true
```

---

## 📋 What the Recipe Will Do (8 Steps)

### **Step 1: Load Context from Memory** 🧠
- Retrieves previously learned testing patterns
- Loads your team's preferred test structure
- Gets common gap patterns from past analysis
- Loads testing best practices

**First Run:** Starts fresh, builds knowledge  
**Future Runs:** Uses learned patterns for better suggestions

---

### **Step 2: Detect Test Framework** 🔍
- Automatically detects pytest (from your test files)
- Finds `pytest.ini`, `tests/` directory
- Confirms framework with high confidence
- Reports: "Detected: pytest (high confidence)"

---

### **Step 3: Analyze Current Test Coverage** 📊
Will analyze your current state:

```
Test File Inventory:
- Unit tests: 4 files (test_planner.py, test_timesheet.py, etc.)
- Integration tests: 1 file (test_agent_coordination.py)
- Fixtures: 3 files (mock data, sample requests, scorecards)
- Total test cases: 41

Coverage Data:
- Overall: 36%
- Target: 80%
- Gap: 44%

Files with Low Coverage:
1. llm/cache.py - 0%
2. llm/error_handler.py - 0%
3. llm/opik_tracker.py - 0%
4. llm/rate_limiter.py - 0%
5. llm/tenant_key_manager.py - 0%
6. agents/timesheet.py - 14%
7. llm/client.py - 24%
8. agents/branding.py - 38%
```

---

### **Step 4: Identify Gaps Using Learned Patterns** 🎯

Will categorize missing tests:

**Core Logic Gaps:**
- `extract_timesheet_data()` - ✅ You just added this!
- `format_sms()`, `format_email()` in branding.py
- LLM client generation methods

**Edge Case Gaps:**
- Empty timesheet responses
- Invalid credentials
- Null/undefined inputs
- Rate limit exceeded scenarios

**Error Handling Gaps:**
- API timeout handling
- Network errors
- Authentication failures
- Cache failures

**Integration Gaps:**
- Full workflow tests (Planner → Timesheet → Quality → Branding)
- API endpoint tests
- Database interaction tests

---

### **Step 5: Generate Test Suggestions** 💡

Will create specific, actionable suggestions like:

```python
# ========================================
# CRITICAL PRIORITY - Implement First
# ========================================

Test: test_extract_timesheet_data_success
Purpose: Verify extract_timesheet_data returns correct structure
Priority: Critical (core-logic)
Estimated effort: 15 minutes
Coverage gain: +3%

Code example for pytest:
```python
@pytest.mark.asyncio
async def test_extract_timesheet_data_success(timesheet_agent, mock_harvest_response):
    """Test successful timesheet data extraction"""
    result = await timesheet_agent.extract_timesheet_data(
        request_id="test-123",
        user_id="user-456",
        query_type="hours_logged",
        parameters={"date_range": "this_week"},
        user_credentials={"access_token": "test_token"},
        timezone="UTC"
    )
    
    assert result["success"] is True
    assert result["error"] is None
    assert "data" in result
    assert "metadata" in result
    assert result["metadata"]["tools_used"] == ["check_my_timesheet"]
```

---

Test: test_cache_get_hit
Purpose: Verify cache returns stored values correctly
Priority: Critical (untested module)
Estimated effort: 10 minutes
Coverage gain: +2%

Code example for pytest:
```python
def test_cache_get_hit(cache_instance):
    """Test cache hit returns correct value"""
    # Setup
    cache_instance.set("test_key", "test_value", ttl=60)
    
    # Execute
    result = cache_instance.get("test_key")
    
    # Assert
    assert result == "test_value"
    assert cache_instance.stats["hits"] == 1
```

---

Test: test_rate_limiter_exceeds_limit
Purpose: Verify rate limiter blocks requests when limit exceeded
Priority: High (error-handling)
Estimated effort: 20 minutes
Coverage gain: +2%

Code example for pytest:
```python
@pytest.mark.asyncio
async def test_rate_limiter_exceeds_limit(rate_limiter):
    """Test rate limiter blocks when limit exceeded"""
    # Setup: Configure 5 requests per minute
    rate_limiter.configure(max_requests=5, window_seconds=60)
    
    # Execute: Make 5 successful requests
    for i in range(5):
        result = await rate_limiter.acquire("user-123")
        assert result is True
    
    # Execute: 6th request should be blocked
    result = await rate_limiter.acquire("user-123")
    
    # Assert
    assert result is False
    assert rate_limiter.get_remaining("user-123") == 0
```
```

---

### **Step 6: Create Test Templates** 📝

Will generate complete test files:

```python
# ========================================
# File: tests/unit/test_cache.py
# Framework: pytest
# Purpose: Tests for LLM cache module
# ========================================

import pytest
from llm.cache import Cache

@pytest.fixture
def cache_instance():
    """Create a test cache instance"""
    cache = Cache(max_size=100, default_ttl=300)
    yield cache
    cache.clear()

def test_cache_initialization():
    """Test cache initializes with correct defaults"""
    cache = Cache()
    assert cache.max_size > 0
    assert cache.default_ttl > 0
    assert len(cache) == 0

def test_cache_set_and_get():
    """Test basic cache set and get operations"""
    cache = Cache()
    cache.set("key1", "value1")
    assert cache.get("key1") == "value1"

def test_cache_get_miss():
    """Test cache miss returns None"""
    cache = Cache()
    assert cache.get("nonexistent") is None

def test_cache_expiration():
    """Test cache entries expire after TTL"""
    cache = Cache()
    cache.set("key1", "value1", ttl=1)
    time.sleep(2)
    assert cache.get("key1") is None

# TODO: Add more tests for:
# - Cache size limits
# - Cache clear operation
# - Cache statistics
# - Thread safety (if applicable)
```

---

### **Step 7: Store Patterns in Memory** 💾

Will save for future runs:

```yaml
testing_style:
  framework: pytest
  patterns:
    - Uses fixtures extensively
    - Prefers async tests with pytest-asyncio
    - Mocks external dependencies
    - Uses descriptive test names
  naming_convention: "test_<method>_<scenario>"
  
gap_patterns:
  - Untested error handlers (5 modules)
  - Missing edge case tests
  - Low integration test coverage
  - Cache and rate limiter not tested
  
coverage_baseline:
  current: 36%
  target: 80%
  date: 2025-12-02
  tests_suggested: 25
  
preferred_frameworks:
  - pytest
  - pytest-asyncio
  - pytest-cov
  - pytest-mock
```

---

### **Step 8: Present Final Report** 📊

Will provide comprehensive summary:

```
📊 Test Coverage Analysis for multi_Agent_Conversation_System

Current Coverage: 36%
Target Coverage: 80%
Coverage Gap: 44%

Framework Detected: pytest (high confidence)
Focus Areas: all
Tests Analyzed: 6 test files, 41 test cases

🎯 High-Priority Test Suggestions:

1. [CRITICAL] test_extract_timesheet_data_success
   - What: Verify new extract_timesheet_data method
   - Why: Core functionality just added, needs tests
   - Effort: ~15 minutes
   - Coverage gain: +3%

2. [CRITICAL] test_cache_basic_operations
   - What: Test cache get/set/delete operations
   - Why: 0% coverage on critical infrastructure
   - Effort: ~20 minutes
   - Coverage gain: +5%

3. [CRITICAL] test_error_handler_retry_logic
   - What: Test retry with exponential backoff
   - Why: 0% coverage on error handling
   - Effort: ~25 minutes
   - Coverage gain: +4%

4. [CRITICAL] test_rate_limiter_enforcement
   - What: Test rate limiting blocks excess requests
   - Why: 0% coverage on rate limiting
   - Effort: ~20 minutes
   - Coverage gain: +3%

5. [HIGH] test_branding_format_sms
   - What: Test SMS formatting with 160 char limit
   - Why: Method exists but not tested
   - Effort: ~15 minutes
   - Coverage gain: +2%

📝 Next Steps:

1. Start with CRITICAL tests (biggest impact)
2. Use the templates provided above - copy and customize
3. Run tests to verify: pytest tests/ -v
4. Run coverage: pytest tests/ --cov --cov-report=html
5. Re-run this recipe for additional suggestions

💡 Pro Tips:
- Implement tests iteratively (5-10 at a time)
- Run coverage after each batch to track progress
- For 80% target, focus on core-logic first
- This recipe learns - patterns will improve with each run

📈 Estimated Impact:

If you implement the top 5 suggested tests:
- Estimated coverage increase: +17%
- New coverage projection: 53%
- Remaining gap to target: 27%

Tests needed to reach 80%: approximately 15-20 more tests

🧠 Memory Updated:
- Stored testing style preferences
- Saved 4 gap patterns for future reference
- Updated coverage baseline
- Future runs will provide better suggestions
```

---

## 🎯 Recommended Usage for Your Project

### **Run 1: Initial Analysis**
```yaml
project_path: /Users/dongshulin/Library/CloudStorage/OneDrive-2ai.cx/Desktop/GitHub/multi_Agent_Conversation_System
coverage_threshold: 80
test_framework: auto
focus_areas: all
generate_templates: true
```

**Expected Output:**
- 25-30 test suggestions
- 5-10 ready-to-use templates
- Prioritized by impact
- Learned patterns stored

---

### **Run 2: After Implementing First Batch**
```yaml
# Same config, but now it will:
# - Use learned patterns from Run 1
# - Skip already-tested areas
# - Focus on remaining gaps
# - Provide more targeted suggestions
```

---

### **Run 3: Final Push to 80%**
```yaml
# Focus on specific areas:
focus_areas: edge-cases,error-handling
# Will target the last 10-15% needed
```

---

## 💡 Advantages Over Manual Prompts

| Feature | Manual Prompts | Recipe |
|---------|---------------|--------|
| **Learning** | No memory | ✅ Learns patterns |
| **Consistency** | Varies | ✅ Systematic |
| **Templates** | Manual creation | ✅ Auto-generated |
| **Prioritization** | Manual | ✅ Impact-based |
| **Progress Tracking** | Manual | ✅ Automated |
| **Framework Detection** | Manual | ✅ Automatic |
| **Coverage Analysis** | Manual | ✅ Integrated |
| **Improvement Over Time** | No | ✅ Gets smarter |

---

## 🚀 Quick Start

### Option 1: Goose Desktop (Easiest)

1. Open Goose Desktop
2. Go to Recipe Library
3. Find "Test Coverage Optimizer"
4. Set project path to: `/Users/dongshulin/Library/CloudStorage/OneDrive-2ai.cx/Desktop/GitHub/multi_Agent_Conversation_System`
5. Set coverage threshold: `80`
6. Click "Launch"

### Option 2: Direct URL

Visit: https://block.github.io/goose/prompt-library/detail?id=test-coverage-optimizer

Click "Launch in Goose Desktop →"

---

## 📊 Expected Timeline

### Day 1: Run Recipe + Implement Critical Tests
- Run recipe (5 minutes)
- Review suggestions (10 minutes)
- Implement top 5 critical tests (1-2 hours)
- **Coverage:** 36% → 53%

### Day 2: Run Recipe Again + Implement High Priority
- Run recipe with learned patterns (5 minutes)
- Implement next 10 tests (2-3 hours)
- **Coverage:** 53% → 70%

### Day 3: Final Push
- Run recipe focused on edge cases (5 minutes)
- Implement remaining tests (1-2 hours)
- **Coverage:** 70% → 80%+

---

## ✅ Why This is Better

1. **Systematic:** Follows proven 8-step process
2. **Learning:** Gets smarter with each run
3. **Practical:** Generates actual code, not just suggestions
4. **Prioritized:** Focuses on high-impact tests first
5. **Trackable:** Shows progress toward goal
6. **Automated:** Handles analysis, detection, generation
7. **Team-aware:** Learns your coding style

---

**Start now with the Test Coverage Optimizer recipe!** 🦢📊

It will handle everything from the GOOSE_FIX_TESTS.md plan automatically and intelligently!
