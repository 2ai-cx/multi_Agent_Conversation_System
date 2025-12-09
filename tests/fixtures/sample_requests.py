"""Sample user requests for testing"""

from agents.models import Channel

# Sample user messages for different scenarios
SAMPLE_MESSAGES = {
    "timesheet_check": "Check my timesheet",
    "timesheet_today": "How many hours did I log today?",
    "timesheet_week": "Show me my hours for this week",
    "project_list": "What projects am I working on?",
    "complex_query": "Show my hours and active projects",
    "log_time": "Log 8 hours to Alpha project",
    "ambiguous": "What's my status?",
    "greeting": "Hi there!",
}

# Sample conversation history
SAMPLE_CONVERSATION_HISTORY = [
    {
        "role": "user",
        "content": "Check my timesheet",
        "timestamp": "2025-11-24T10:00:00Z"
    },
    {
        "role": "assistant",
        "content": "You've logged 32/40 hours this week. Great progress!",
        "timestamp": "2025-11-24T10:00:05Z"
    },
    {
        "role": "user",
        "content": "And what about yesterday?",
        "timestamp": "2025-11-24T10:01:00Z"
    }
]

# Sample user context
SAMPLE_USER_CONTEXT = {
    "user_id": "test-user-123",
    "full_name": "Test User",
    "timezone": "Australia/Sydney",
    "preferences": {
        "language": "en",
        "notifications_enabled": True
    }
}

# Sample request for each channel
SAMPLE_SMS_REQUEST = {
    "request_id": "req-sms-001",
    "user_message": SAMPLE_MESSAGES["timesheet_check"],
    "channel": Channel.SMS,
    "conversation_history": SAMPLE_CONVERSATION_HISTORY,
    "user_context": SAMPLE_USER_CONTEXT
}

SAMPLE_EMAIL_REQUEST = {
    "request_id": "req-email-001",
    "user_message": SAMPLE_MESSAGES["complex_query"],
    "channel": Channel.EMAIL,
    "conversation_history": [],
    "user_context": SAMPLE_USER_CONTEXT
}

SAMPLE_WHATSAPP_REQUEST = {
    "request_id": "req-whatsapp-001",
    "user_message": SAMPLE_MESSAGES["project_list"],
    "channel": Channel.WHATSAPP,
    "conversation_history": SAMPLE_CONVERSATION_HISTORY[:1],
    "user_context": SAMPLE_USER_CONTEXT
}

SAMPLE_TEAMS_REQUEST = {
    "request_id": "req-teams-001",
    "user_message": SAMPLE_MESSAGES["timesheet_week"],
    "channel": Channel.TEAMS,
    "conversation_history": [],
    "user_context": SAMPLE_USER_CONTEXT
}
