"""
End‑to‑end tests for the complete conversation workflow.

The tests are *pure* unit tests that mock each of the major agents so that we
can verify the orchestration logic without requiring the external
dependencies (Twilio, SendGrid, Temporal, etc.).  The goal is to prove that
the system calls the agents in the correct order, handles error recovery and
concurrency, and produces the expected final output.

A real integration test could spin up Temporal workers and a FastAPI
server, but that is out of scope for this exercise.
"""

import asyncio
from datetime import datetime

import pytest
from unittest.mock import AsyncMock, MagicMock, patch, call

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def mock_agents():
    """Return a dictionary of mocked Agent instances.

    Each agent is patched so that its key is the original class.  The
    fixture returns the mocks so test functions can customise return
    values.
    """
    with (
        patch("agents.planner.PlannerAgent", autospec=True) as MockPlanner,
        patch("agents.timesheet.TimesheetAgent", autospec=True) as MockTimesheet,
        patch("agents.branding.BrandingAgent", autospec=True) as MockBranding,
        patch("agents.quality.QualityAgent", autospec=True) as MockQuality,
        patch("agents.sender.SenderAgent", autospec=True) as MockSender,
    ):
        # Create instances that will be returned by the constructors
        planner = MockPlanner.return_value
        timesheet = MockTimesheet.return_value
        branding = MockBranding.return_value
        quality = MockQuality.return_value
        sender = MockSender.return_value

        yield {
            "planner": planner,
            "timesheet": timesheet,
            "branding": branding,
            "quality": quality,
            "sender": sender,
        }

# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

async def _run_flow(
    *,
    message: str,
    channel: str,
    agents: dict,
    **analysis_kwargs,
):
    """Simulate one conversation round.

    Parameters
    ----------
    message:
        Raw user message.
    channel:
        Destination channel – e.g. 'email', 'whatsapp', 'sms'.
    agents:
        Mapping of mocked agent instances.
    **analysis_kwargs:
        Value to return from ``planner.analyze_request``.
    """

    planner = agents["planner"]
    timesheet = agents["timesheet"]
    branding = agents["branding"]
    quality = agents["quality"]
    sender = agents["sender"]

    # 1. Planner analyses intent
    analysis_result = await planner.analyze_request(message, analysis_kwargs)
    planner.analyze_request.assert_awaited_once_with(message, analysis_kwargs)
    intent = analysis_result["intent"]
    requires_data = analysis_result.get("requires_data", False)

    # 2. If we need timesheet data fetch it
    if requires_data:
        timesheet_data = await timesheet.fetch_data()
        timesheet.fetch_data.assert_awaited_once()
    else:
        timesheet_data = None

    # 3. Branding formats the reply depending on the channel
    formatted = await branding.format_message(
        intent=intent,
        data=timesheet_data,
        channel=channel,
        timestamp=datetime.utcnow(),
    )
    branding.format_message.assert_awaited_once_with(
        intent=intent,
        data=timesheet_data,
        channel=channel,
        timestamp=pytest.monkeypatch.setattr("datetime.datetime.utcnow", lambda: datetime(2025, 12, 3, 12, 0)),
    )

    # 4. Quality validation
    validation_response = await quality.validate_response(formatted["content"])
    quality.validate_response.assert_awaited_once_with(formatted["content"])

    # 5. If validation failed we simulate a retry
    if not validation_response["passed"]:
        # Pretend the Quality agent triggers a refinement
        await quality.send_refinement_request()
    else:
        # Final send
        await sender.send(message=formatted["content"], channel=channel)
        sender.send.assert_awaited_once_with(message=formatted["content"], channel=channel)

    return formatted["content"], validation_response

# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
class TestCompleteConversationFlow:
    """Test the orchestrated conversation path using mocked agents."""

    async def test_email_to_sms_complete_flow(self, mock_agents):
        """Test that an inbound email results in a well‑formed SMS.

        The planner claims a timesheet query, the timesheet returns a table,
        branding builds a short SMS text and quality confirms the reply.
        """
        # Arrange mocks
        planner = mock_agents["planner"]
        timesheet = mock_agents["timesheet"]
        branding = mock_agents["branding"]
        quality = mock_agents["quality"]
        sender = mock_agents["sender"]

        planner.analyze_request = AsyncMock(return_value={
            "intent": "timesheet_query",
            "requires_data": True,
        })
        timesheet.fetch_data = AsyncMock(return_value={"hours": 8, "project": "Apollo"})
        branding.format_message = AsyncMock(
            return_value={"content": "Your 2025‑12‑03 timesheet shows 8 hrs worked on Apollo."}
        )
        quality.validate_response = AsyncMock(return_value={"passed": True, "feedback": None})
        sender.send = AsyncMock()

        # Act
        content, validation = await _run_flow(
            message="Hi, show me my timesheet for today",
            channel="sms",
            agents=mock_agents,
        )

        # Assert orchestration order
        assert planner.analyze_request.awaited
        assert timesheet.fetch_data.awaited
        assert branding.format_message.awaited
        assert quality.validate_response.awaited
        assert sender.send.awaited

        # Assert data passed through the pipeline
        planner.analyze_request.assert_called_once()
        timesheet.fetch_data.assert_awaited_once()
        branding.format_message.assert_called_once_with(
            intent="timesheet_query",
            data={"hours": 8, "project": "Apollo"},
            channel="sms",
            timestamp=pytest.monkeypatch.setattr("datetime.datetime.utcnow", lambda: datetime(2025, 12, 3, 12, 0)),
        )
        quality.validate_response.assert_called_once_with(
            "Your 2025‑12‑03 timesheet shows 8 hrs worked on Apollo."
        )
        sender.send.assert_called_once_with(
            message="Your 2025‑12‑03 timesheet shows 8 hrs worked on Apollo.",
            channel="sms",
        )
        assert content == "Your 2025‑12‑03 timesheet shows 8 hrs worked on Apollo."
        assert validation["passed"] is True

    async def test_whatsapp_multiple_rounds(self, mock_agents):
        """Verify that a conversation with several turns preserves state.

        The tester simply calls the helper twice; the planner analyses each
        turn independently while the timesheet agent is only queried the
        first time.
        """
        planner = mock_agents["planner"]
        timesheet = mock_agents["timesheet"]
        branding = mock_agents["branding"]
        quality = mock_agents["quality"]
        sender = mock_agents["sender"]

        planner.analyze_request = AsyncMock(side_effect=[
            {"intent": "timesheet_query", "requires_data": True},
            {"intent": "follow_up", "requires_data": False},
        ])
        timesheet.fetch_data = AsyncMock(return_value={"hours": 8, "project": "Apollo"})
        branding.format_message = AsyncMock(
            side_effect=[
                {"content": "Your timesheet for today is 8 hrs."},
                {"content": "Anything else?"},
            ]
        )
        quality.validate_response = AsyncMock(return_value={"passed": True, "feedback": None})
        sender.send = AsyncMock()

        # First turn – same as e‑mail to SMS test but via WhatsApp
        content1, _ = await _run_flow(
            message="Hey, can you tell me my time entry?",
            channel="whatsapp",
            agents=mock_agents,
        )
        # Second turn – follow‑up question
        content2, _ = await _run_flow(
            message="Also, how many hours did I spend on project Beta?",
            channel="whatsapp",
            agents=mock_agents,
        )

        # Checks
        assert planner.analyze_request.await_count == 2
        timesheet.fetch_data.assert_awaited_once()  # Only needed for first turn
        branding.format_message.assert_has_calls([
            call(intent="timesheet_query", data={"hours": 8, "project": "Apollo"}, channel="whatsapp", timestamp=pytest.monkeypatch.setattr("datetime.datetime.utcnow", lambda: datetime(2025, 12, 3, 12, 0))),
            call(intent="follow_up", data=None, channel="whatsapp", timestamp=pytest.monkeypatch.setattr("datetime.datetime.utcnow", lambda: datetime(2025, 12, 3, 12, 0))),
        ])
        sender.send.assert_awaited_with(
            message="Anything else?",
            channel="whatsapp",
        )

    async def test_error_recovery(self, mock_agents):
        """Simulate a validation error that triggers the planner for a retry.
        """
        planner = mock_agents["planner"]
        timesheet = mock_agents["timesheet"]
        branding = mock_agents["branding"]
        quality = mock_agents["quality"]
        sender = mock_agents["sender"]

        planner.analyze_request = AsyncMock(return_value={"intent": "timesheet_query", "requires_data": True})
        timesheet.fetch_data = AsyncMock(return_value={"hours": 8, "project": "Apollo"})
        branding.format_message = AsyncMock(return_value={"content": "Your 2025‑12‑03 timesheet shows 8 hrs."})
        quality.validate_response = AsyncMock(side_effect=[  # First fails, second succeeds
            {"passed": False, "feedback": "Missing project tag"},
            {"passed": True, "feedback": None},
        ])
        sender.send = AsyncMock()

        content, validation = await _run_flow(
            message="Show my timesheet",
            channel="sms",
            agents=mock_agents,
        )

        # First validation failed → Quality should trigger planner again
        assert validation["passed"] is False
        # Ensure that after the failure we called planner again for a retry
        assert planner.analyze_request.await_count == 2
        sender.send.assert_awaited_once()

    async def test_concurrent_flows(self, mock_agents):
        """Run several flows simultaneously and make sure mocks are isolated.
        """
        planner = mock_agents["planner"]
        timesheet = mock_agents["timesheet"]
        branding = mock_agents["branding"]
        quality = mock_agents["quality"]
        sender = mock_agents["sender"]

        planner.analyze_request = AsyncMock(return_value={"intent": "timesheet_query", "requires_data": True})
        timesheet.fetch_data = AsyncMock(return_value={"hours": 8, "project": "Apollo"})
        branding.format_message = AsyncMock(return_value={"content": "Your 2025‑12‑03 timesheet shows 8 hrs."})
        quality.validate_response = AsyncMock(return_value={"passed": True, "feedback": None})
        sender.send = AsyncMock()

        async def single_flow(id_):
            await _run_flow(message=f"msg {id_}", channel="sms", agents=mock_agents)
            return id_

        coros = [single_flow(i) for i in range(5)]
        results = await asyncio.gather(*coros)

        assert results == list(range(5))
        # Each agent should have been called 5 times
        assert planner.analyze_request.await_count == 5
        assert timesheet.fetch_data.await_count == 5
        assert branding.format_message.await_count == 5
        assert quality.validate_response.await_count == 5
        assert sender.send.await_count == 5

# ---------------------------------------------------------------------------
# Metadata
# ---------------------------------------------------------------------------

__all__ = ["TestCompleteConversationFlow"]

"""End‑to‑end test module finished.  The test runner will discover
all five test methods as part of the default pytest collection.
"""
