# 🤖 Goose Prompt: Create Comprehensive Test Suite

## Copy this entire prompt into Goose:

---

Create a comprehensive test suite for this Multi-Agent Timesheet System. I need you to create multiple test files covering different testing types.

**Project Path:** `/Users/dongshulin/Library/CloudStorage/OneDrive-2ai.cx/Desktop/GitHub/multi_Agent_Conversation_System`

**Current Test Status:**
- ✅ 41/41 unit and integration tests passing
- 📊 72% coverage
- 🎯 Goal: Expand test coverage to 80%+ with diverse test types

---

## Task 1: Create E2E Tests

Create `tests/e2e/test_complete_conversation_flow.py` with:

1. **Test complete email-to-SMS flow:**
   - Receive email via API
   - Process through all agents (planner, timesheet, branding, quality)
   - Send SMS response
   - Verify delivery

2. **Test WhatsApp conversation flow:**
   - Receive WhatsApp message
   - Process and respond
   - Verify formatting

3. **Test multi-turn conversation:**
   - Send first message
   - Get response
   - Send follow-up with context
   - Verify context is maintained

4. **Test error recovery:**
   - Trigger error condition
   - Verify graceful degradation
   - Verify error notification sent

5. **Test concurrent conversations:**
   - Start 5 conversations simultaneously
   - Verify all complete successfully
   - Verify no cross-contamination

---

## Task 2: Create API Endpoint Tests

Create `tests/api/test_endpoints.py` with tests for:

1. **Health endpoints:**
   - `GET /health` returns 200
   - Response includes status, timestamp, agents

2. **System info endpoints:**
   - `GET /system-info` returns system details
   - Includes agent status, version info

3. **Conversation endpoints:**
   - `POST /conversation/start` creates new conversation
   - `POST /conversation/message` sends message
   - `GET /conversation/{id}/history` retrieves history

4. **Webhook endpoints:**
   - `POST /webhooks/twilio` handles Twilio webhooks
   - `POST /webhooks/sendgrid` handles SendGrid webhooks
   - Webhook signature verification works

5. **Error handling:**
   - 404 for invalid endpoints
   - 400 for bad request data
   - 500 error handling

6. **Rate limiting:**
   - Rate limits enforce correctly
   - Rate limit headers present

Use `TestClient` from FastAPI for all tests.

---

## Task 3: Create Temporal Workflow Tests

Create `tests/workflows/test_temporal_workflows.py` with:

1. **ConversationWorkflow tests:**
   - Workflow initializes correctly
   - Executes all steps in order
   - Handles refinement loop
   - Handles timeouts
   - Can be cancelled

2. **DailyReminderWorkflow tests:**
   - Executes daily reminder
   - Fetches all active users
   - Generates personalized messages
   - Handles individual user failures

3. **Activity tests:**
   - Each activity (planner_analyze, timesheet_fetch, etc.) works
   - Activities retry on failure
   - Activities handle timeouts

4. **Workflow signals/queries:**
   - Status query works
   - Cancel signal works
   - Update signal works

---

## Task 4: Create Performance Tests

Create `tests/performance/test_load_and_stress.py` with:

1. **Response time tests:**
   - Planner responds < 5 seconds
   - Timesheet fetch < 2 seconds
   - Branding format < 1 second
   - Quality validation < 3 seconds per criterion
   - End-to-end < 30 seconds

2. **Concurrent load tests:**
   - Handle 10 concurrent conversations
   - Handle 50 concurrent conversations
   - Handle 100 concurrent conversations
   - Rate limiting works under load

3. **Memory usage tests:**
   - Single conversation memory usage
   - 100 conversations don't leak memory
   - Cache respects memory limits

4. **Throughput tests:**
   - System handles 100 messages/minute
   - Sustained load for 5 minutes

5. **Database performance:**
   - User lookup < 100ms
   - History retrieval < 500ms for 100 messages
   - Bulk user fetch < 1 second for 1000 users

Mark all performance tests with `@pytest.mark.performance`

---

## Task 5: Create Contract Tests

Create `tests/contracts/test_api_contracts.py` with:

1. **Request/Response schema validation:**
   - All endpoints validate request schemas
   - All endpoints return correct response schemas

2. **External API contracts:**
   - Harvest API contract tests
   - Twilio API contract tests
   - SendGrid API contract tests

3. **Pydantic model validation:**
   - All models validate correctly
   - Invalid data raises ValidationError

---

## Task 6: Create Security Tests

Create `tests/security/test_security.py` with:

1. **Authentication tests:**
   - API key validation
   - Webhook signature verification
   - Unauthorized access blocked

2. **Input validation:**
   - SQL injection prevention
   - XSS prevention
   - Command injection prevention

3. **Rate limiting:**
   - Per-user rate limits
   - Global rate limits
   - Token bucket algorithm

4. **Data privacy:**
   - PII is not logged
   - Sensitive data encrypted
   - API keys not exposed

---

## Task 7: Create Fixture Files

Create `tests/fixtures/temporal_fixtures.py` with:

1. Mock Temporal client
2. Mock workflow execution
3. Mock activity execution
4. Sample workflow data

Create `tests/fixtures/api_fixtures.py` with:

1. Mock FastAPI test client
2. Sample API requests
3. Sample API responses
4. Mock authentication

---

## Requirements:

1. **Use proper pytest structure:**
   - Use `@pytest.mark.asyncio` for async tests
   - Use `@pytest.fixture` for reusable fixtures
   - Use `@pytest.mark.performance` for performance tests
   - Use `@pytest.mark.security` for security tests

2. **Use proper mocking:**
   - Mock external APIs (Harvest, Twilio, SendGrid)
   - Mock LLM client
   - Mock Temporal client
   - Use `unittest.mock.AsyncMock` for async mocks

3. **Include docstrings:**
   - Every test class has a docstring
   - Every test function has a docstring
   - Explain what is being tested

4. **Make tests realistic:**
   - Use actual data structures from the codebase
   - Test real scenarios
   - Include edge cases

5. **After creating all files:**
   - Run `pytest tests/ --collect-only` to verify all tests are discovered
   - Show me the count of new tests created
   - Show me the new test structure

---

## Start Now!

Begin with Task 1 (E2E tests) and work through all 7 tasks. Create all files with complete, working test code. Don't leave TODOs - implement the actual test logic using mocks where needed.

After completing all tasks, run:
```bash
pytest tests/ --collect-only -q | tail -20
```

And show me the results.
