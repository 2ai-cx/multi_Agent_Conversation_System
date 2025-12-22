# 🚀 Goose Test Quick Start

## 📊 Current Status
- ✅ **38 passing** / ❌ **3 failing** / ⚠️ **64 warnings**
- 📈 **Coverage: 70%** (Target: 80%+)

---

## 🎯 Quick Start: Copy-Paste These Prompts

### **Phase 1: Fix Failing Tests (PRIORITY)**

Copy this to Goose:

```
Read GOOSE-TEST-PLAN.md Phase 1 and fix the 3 failing integration tests.

Failing tests:
1. test_complete_workflow_success
2. test_workflow_with_refinement  
3. test_workflow_with_graceful_failure

All are in: tests/integration/test_agent_coordination.py

Steps:
1. Run each test with: pytest tests/integration/test_agent_coordination.py::TestMultiAgentWorkflow::test_complete_workflow_success -v -s
2. Analyze the mock_llm_generate function
3. Read agents/planner.py to see actual prompt structure
4. Update mock conditions to be more specific
5. Ensure JSON responses match Pydantic models
6. Test each fix individually

Success: All 3 tests pass, 41/41 total passing
```

---

### **Phase 2: Eliminate Warnings**

Copy this to Goose:

```
Read GOOSE-TEST-PLAN.md Phase 2 and eliminate all 64 warnings.

Warnings to fix:
1. 5 Pydantic @validator → @field_validator (agents/models.py)
2. 1 Pydantic Config → ConfigDict (llm/config.py)
3. ~58 datetime.utcnow() → datetime.now(UTC) (agents/models.py)

Steps:
1. Migrate validators in agents/models.py lines 177, 184, 207, 226, 307
2. Update Config in llm/config.py line 13
3. Replace all datetime.utcnow() with datetime.now(UTC)
4. Run tests to verify no breakage
5. Confirm 0 warnings

Success: pytest shows 0 warnings, all tests still pass
```

---

### **Phase 3: Improve Coverage**

Copy this to Goose:

```
Read GOOSE-TEST-PLAN.md Phase 3 and improve coverage from 70% to 80%+.

Current: 70% (504 lines missing)
Target: 80%+ (~330 lines missing)

Steps:
1. Run: pytest tests/ --cov --cov-report=html
2. Open htmlcov/index.html to identify low coverage areas
3. Focus on:
   - Error handling paths
   - Edge cases (empty strings, None values)
   - Fallback behaviors
4. Add tests to existing test files
5. Prioritize critical code over trivial code

Success: Coverage >= 80%, all critical paths tested
```

---

## 📋 Quick Commands

### **Check Current Status:**
```bash
# Quick test summary
pytest tests/ -v --tb=no -q

# With coverage
pytest tests/ --cov --cov-report=term-missing

# Count warnings
pytest tests/ -v 2>&1 | grep -c "warning"
```

### **Run Specific Tests:**
```bash
# Single failing test
pytest tests/integration/test_agent_coordination.py::TestMultiAgentWorkflow::test_complete_workflow_success -v -s

# All integration tests
pytest tests/integration/ -v

# All unit tests  
pytest tests/unit/ -v
```

### **After Fixes:**
```bash
# Verify all pass
pytest tests/ -v

# Verify no warnings
pytest tests/ --tb=no -q

# Check coverage
pytest tests/ --cov --cov-report=term-missing
```

---

## 🎯 Success Criteria

### **Phase 1 Done:**
- ✅ 41/41 tests passing
- ✅ 0 integration test failures

### **Phase 2 Done:**
- ✅ 0 warnings
- ✅ Pydantic V2 compliant

### **Phase 3 Done:**
- ✅ Coverage >= 80%
- ✅ Critical paths tested

---

## 💡 Tips for Goose

1. **One Phase at a Time** - Complete Phase 1 before Phase 2
2. **Test After Each Change** - Run tests to verify no breakage
3. **Read the Code** - Goose should read actual agent code to understand prompts
4. **Be Specific** - Mock conditions should match exact prompt phrases
5. **Report Progress** - Ask Goose to report after each task

---

## 🐛 If Something Goes Wrong

### **Tests Break After Fix:**
```
Goose, the tests are now failing. Please:
1. Show me what you changed
2. Run the specific failing test with -v -s
3. Revert the change if needed
4. Try a different approach
```

### **Coverage Not Improving:**
```
Goose, coverage is still low. Please:
1. Generate HTML coverage report
2. Identify the specific uncovered lines
3. Show me which functions/methods need tests
4. Add targeted tests for those areas
```

### **Warnings Still Showing:**
```
Goose, warnings remain. Please:
1. Show me the exact warning messages
2. Identify which files are causing them
3. Check if migration was done correctly
4. Verify imports are correct (e.g., from datetime import UTC)
```

---

## 📊 Progress Tracking

Use this checklist:

```
Phase 1: Fix Integration Tests
[ ] test_complete_workflow_success fixed
[ ] test_workflow_with_refinement fixed
[ ] test_workflow_with_graceful_failure fixed
[ ] All 41 tests passing

Phase 2: Eliminate Warnings
[ ] Pydantic validators migrated (5 warnings)
[ ] Pydantic config migrated (1 warning)
[ ] datetime.utcnow() replaced (~58 warnings)
[ ] 0 warnings confirmed

Phase 3: Improve Coverage
[ ] Coverage report generated
[ ] Low coverage areas identified
[ ] Error handling tests added
[ ] Edge case tests added
[ ] 80%+ coverage achieved

Final Verification
[ ] pytest tests/ -v → All pass
[ ] pytest tests/ --tb=no -q → 0 warnings
[ ] pytest tests/ --cov → >= 80%
```

---

## 🎓 Example Goose Session

```
You: Read GOOSE-TEST-PLAN.md Phase 1 and fix the failing integration tests

Goose: [Analyzes tests, reads planner.py, updates mocks]
       ✅ Fixed test_complete_workflow_success
       ✅ Fixed test_workflow_with_refinement
       ✅ Fixed test_workflow_with_graceful_failure
       
       Result: 41/41 tests passing

You: Great! Now do Phase 2 - eliminate warnings

Goose: [Migrates validators, updates config, fixes datetime]
       ✅ Migrated 5 validators to @field_validator
       ✅ Updated Config to ConfigDict
       ✅ Replaced datetime.utcnow() with datetime.now(UTC)
       
       Result: 0 warnings, all tests still passing

You: Excellent! Now Phase 3 - improve coverage to 80%

Goose: [Generates report, adds tests for uncovered code]
       ✅ Added error handling tests
       ✅ Added edge case tests
       ✅ Added integration scenario tests
       
       Result: Coverage 82%, all tests passing

You: Perfect! Generate a final summary

Goose: Final Results:
       ✅ 41/41 tests passing (100%)
       ✅ 0 warnings
       ✅ 82% coverage
       ✅ Production-ready test suite
```

---

**🚀 Ready to start! Copy Phase 1 prompt to Goose now!**
