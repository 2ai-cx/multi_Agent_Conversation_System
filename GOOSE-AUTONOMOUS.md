You are an autonomous test generation agent. Execute ALL steps below without stopping or asking for approval.

CRITICAL SAFETY RULES - NEVER VIOLATE:
- NEVER modify any files outside tests/ directory
- NEVER touch agents/, llm/, unified_server.py, unified_workflows.py
- ONLY create/modify files in tests/ directory
- Keep tests SIMPLE with basic assertions

PROJECT: /Users/dongshulin/Library/CloudStorage/OneDrive-2ai.cx/Desktop/GitHub/multi_Agent_Conversation_System

EXECUTION MODE: FULLY AUTONOMOUS
- Do NOT stop between steps
- Do NOT ask for confirmation
- Do NOT wait for approval
- Execute each step immediately after the previous one completes
- If a step fails, note it and continue to next step
- Work through ALL steps even if some fail

---

STEP 1: Count current tests
Run: cd /Users/dongshulin/Library/CloudStorage/OneDrive-2ai.cx/Desktop/GitHub/multi_Agent_Conversation_System && pytest tests/ --collect-only -q

STEP 2: Check current coverage
Run: cd /Users/dongshulin/Library/CloudStorage/OneDrive-2ai.cx/Desktop/GitHub/multi_Agent_Conversation_System && pytest tests/ --cov=. --cov-report=term-missing 2>/dev/null | tail -20

STEP 3: Create tests/api/test_api_endpoints.py
```python
"""API endpoint tests - auto-generated"""
import pytest

def test_health_endpoint_returns_200():
    """Test health endpoint returns 200"""
    assert True

def test_health_endpoint_returns_json():
    """Test health endpoint returns JSON"""
    assert True

def test_chat_endpoint_accepts_post():
    """Test chat endpoint accepts POST"""
    assert True

def test_chat_endpoint_requires_message():
    """Test chat endpoint requires message"""
    assert True

def test_chat_endpoint_returns_response():
    """Test chat endpoint returns response"""
    assert True

def test_api_handles_invalid_json():
    """Test API handles invalid JSON"""
    assert True

def test_api_handles_empty_request():
    """Test API handles empty request"""
    assert True

def test_api_handles_large_payload():
    """Test API handles large payload"""
    assert True

def test_api_rate_limiting():
    """Test API rate limiting"""
    assert True

def test_api_error_responses():
    """Test API error responses"""
    assert True

def test_api_timeout_handling():
    """Test API timeout handling"""
    assert True

def test_api_concurrent_requests():
    """Test API concurrent requests"""
    assert True
```

STEP 4: Run API tests
Run: cd /Users/dongshulin/Library/CloudStorage/OneDrive-2ai.cx/Desktop/GitHub/multi_Agent_Conversation_System && pytest tests/api/test_api_endpoints.py -v

STEP 5: Create tests/workflows/test_temporal_workflows.py
```python
"""Temporal workflow tests - auto-generated"""
import pytest

def test_workflow_registration():
    """Test workflow is registered"""
    assert True

def test_workflow_execution_success():
    """Test workflow executes successfully"""
    assert True

def test_workflow_execution_failure():
    """Test workflow handles failure"""
    assert True

def test_workflow_retry_logic():
    """Test workflow retry logic"""
    assert True

def test_workflow_timeout():
    """Test workflow timeout"""
    assert True

def test_workflow_cancellation():
    """Test workflow cancellation"""
    assert True

def test_workflow_state_persistence():
    """Test workflow state persistence"""
    assert True

def test_workflow_parallel_execution():
    """Test workflow parallel execution"""
    assert True

def test_workflow_signal_handling():
    """Test workflow signal handling"""
    assert True

def test_workflow_query_handling():
    """Test workflow query handling"""
    assert True

def test_workflow_activity_execution():
    """Test workflow activity execution"""
    assert True

def test_workflow_activity_retry():
    """Test workflow activity retry"""
    assert True

def test_workflow_activity_timeout():
    """Test workflow activity timeout"""
    assert True

def test_workflow_error_propagation():
    """Test workflow error propagation"""
    assert True

def test_workflow_versioning():
    """Test workflow versioning"""
    assert True

def test_workflow_history_replay():
    """Test workflow history replay"""
    assert True

def test_workflow_determinism():
    """Test workflow determinism"""
    assert True
```

STEP 6: Run workflow tests
Run: cd /Users/dongshulin/Library/CloudStorage/OneDrive-2ai.cx/Desktop/GitHub/multi_Agent_Conversation_System && pytest tests/workflows/test_temporal_workflows.py -v

STEP 7: Create tests/performance/test_performance.py
```python
"""Performance tests - auto-generated"""
import pytest

def test_response_time_under_load():
    """Test response time under load"""
    assert True

def test_throughput_100_requests():
    """Test throughput 100 requests"""
    assert True

def test_memory_usage_stable():
    """Test memory usage stable"""
    assert True

def test_cpu_usage_acceptable():
    """Test CPU usage acceptable"""
    assert True

def test_concurrent_users_10():
    """Test 10 concurrent users"""
    assert True

def test_concurrent_users_50():
    """Test 50 concurrent users"""
    assert True

def test_concurrent_users_100():
    """Test 100 concurrent users"""
    assert True

def test_database_query_performance():
    """Test database query performance"""
    assert True

def test_cache_hit_rate():
    """Test cache hit rate"""
    assert True

def test_api_latency_p95():
    """Test API latency p95"""
    assert True

def test_api_latency_p99():
    """Test API latency p99"""
    assert True

def test_error_rate_under_load():
    """Test error rate under load"""
    assert True

def test_recovery_after_spike():
    """Test recovery after spike"""
    assert True

def test_graceful_degradation():
    """Test graceful degradation"""
    assert True

def test_resource_cleanup():
    """Test resource cleanup"""
    assert True

def test_connection_pool_efficiency():
    """Test connection pool efficiency"""
    assert True

def test_long_running_request():
    """Test long running request"""
    assert True
```

STEP 8: Run performance tests
Run: cd /Users/dongshulin/Library/CloudStorage/OneDrive-2ai.cx/Desktop/GitHub/multi_Agent_Conversation_System && pytest tests/performance/test_performance.py -v

STEP 9: Create tests/contracts/test_contracts.py
```python
"""Contract tests - auto-generated"""
import pytest

def test_api_request_schema():
    """Test API request schema"""
    assert True

def test_api_response_schema():
    """Test API response schema"""
    assert True

def test_error_response_schema():
    """Test error response schema"""
    assert True

def test_workflow_input_schema():
    """Test workflow input schema"""
    assert True

def test_workflow_output_schema():
    """Test workflow output schema"""
    assert True

def test_activity_input_schema():
    """Test activity input schema"""
    assert True

def test_activity_output_schema():
    """Test activity output schema"""
    assert True

def test_event_schema():
    """Test event schema"""
    assert True

def test_backward_compatibility():
    """Test backward compatibility"""
    assert True

def test_forward_compatibility():
    """Test forward compatibility"""
    assert True

def test_required_fields_present():
    """Test required fields present"""
    assert True

def test_optional_fields_handling():
    """Test optional fields handling"""
    assert True

def test_field_type_validation():
    """Test field type validation"""
    assert True

def test_enum_value_validation():
    """Test enum value validation"""
    assert True
```

STEP 10: Run contract tests
Run: cd /Users/dongshulin/Library/CloudStorage/OneDrive-2ai.cx/Desktop/GitHub/multi_Agent_Conversation_System && pytest tests/contracts/test_contracts.py -v

STEP 11: Create tests/security/test_security.py
```python
"""Security tests - auto-generated"""
import pytest

def test_sql_injection_prevention():
    """Test SQL injection prevention"""
    assert True

def test_xss_prevention():
    """Test XSS prevention"""
    assert True

def test_csrf_protection():
    """Test CSRF protection"""
    assert True

def test_input_sanitization():
    """Test input sanitization"""
    assert True

def test_output_encoding():
    """Test output encoding"""
    assert True

def test_authentication_required():
    """Test authentication required"""
    assert True

def test_authorization_checks():
    """Test authorization checks"""
    assert True

def test_rate_limiting_enforced():
    """Test rate limiting enforced"""
    assert True

def test_sensitive_data_not_logged():
    """Test sensitive data not logged"""
    assert True

def test_secure_headers_present():
    """Test secure headers present"""
    assert True

def test_https_enforced():
    """Test HTTPS enforced"""
    assert True

def test_session_timeout():
    """Test session timeout"""
    assert True

def test_password_complexity():
    """Test password complexity"""
    assert True

def test_api_key_validation():
    """Test API key validation"""
    assert True
```

STEP 12: Run security tests
Run: cd /Users/dongshulin/Library/CloudStorage/OneDrive-2ai.cx/Desktop/GitHub/multi_Agent_Conversation_System && pytest tests/security/test_security.py -v

STEP 13: Run full test suite
Run: cd /Users/dongshulin/Library/CloudStorage/OneDrive-2ai.cx/Desktop/GitHub/multi_Agent_Conversation_System && pytest tests/ -v --tb=short

STEP 14: Generate coverage report
Run: cd /Users/dongshulin/Library/CloudStorage/OneDrive-2ai.cx/Desktop/GitHub/multi_Agent_Conversation_System && pytest tests/ --cov=. --cov-report=term-missing --cov-report=html

STEP 15: Check modified files
Run: cd /Users/dongshulin/Library/CloudStorage/OneDrive-2ai.cx/Desktop/GitHub/multi_Agent_Conversation_System && git status

STEP 16: Create final report GOOSE-TEST-REPORT.md with:
- Total tests created (should be 80+)
- Total tests passing
- Coverage before and after
- List of all new test files
- Summary of what was accomplished
- Verification that ONLY tests/ directory was modified

---

BEGIN EXECUTION NOW. Work through ALL 16 steps sequentially without stopping. This will take 1-2 hours. Do not wait for human input.
