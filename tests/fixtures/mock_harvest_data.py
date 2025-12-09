"""Mock Harvest API data for testing"""

from datetime import datetime, timedelta

# Mock timesheet data - hours logged
MOCK_HOURS_LOGGED = {
    "hours_logged": 32.0,
    "hours_target": 40.0,
    "date_range": "this_week",
    "percentage": 80.0
}

# Mock project list
MOCK_PROJECTS = [
    {
        "id": 12345,
        "name": "Alpha Project",
        "client": "Acme Corp",
        "is_active": True,
        "billable": True
    },
    {
        "id": 12346,
        "name": "Beta Project",
        "client": "TechCo",
        "is_active": True,
        "billable": False
    },
    {
        "id": 12347,
        "name": "Internal - Training",
        "client": "Internal",
        "is_active": True,
        "billable": False
    }
]

# Mock time entries
MOCK_TIME_ENTRIES = [
    {
        "id": 1001,
        "project": "Alpha Project",
        "task": "Development",
        "hours": 8.0,
        "date": "2025-11-22",
        "notes": "Implemented new feature"
    },
    {
        "id": 1002,
        "project": "Alpha Project",
        "task": "Development",
        "hours": 6.5,
        "date": "2025-11-23",
        "notes": "Bug fixes and testing"
    },
    {
        "id": 1003,
        "project": "Beta Project",
        "task": "Planning",
        "hours": 4.0,
        "date": "2025-11-23",
        "notes": "Sprint planning meeting"
    },
    {
        "id": 1004,
        "project": "Alpha Project",
        "task": "Development",
        "hours": 7.5,
        "date": "2025-11-24",
        "notes": "Code review and deployment"
    },
    {
        "id": 1005,
        "project": "Internal - Training",
        "task": "Learning",
        "hours": 6.0,
        "date": "2025-11-24",
        "notes": "Python advanced training"
    }
]

# Mock summary data
MOCK_SUMMARY = {
    "total_hours": 32.0,
    "billable_hours": 22.0,
    "non_billable_hours": 10.0,
    "projects_worked": 3,
    "entries_count": 5,
    "average_hours_per_day": 6.4
}

# Mock API responses
MOCK_API_RESPONSES = {
    "hours_logged": {
        "data": MOCK_HOURS_LOGGED,
        "metadata": {
            "tools_used": ["check_my_timesheet"],
            "api_calls": 1,
            "cache_hit": False
        },
        "success": True,
        "error": None
    },
    "projects": {
        "data": {
            "projects": MOCK_PROJECTS
        },
        "metadata": {
            "tools_used": ["list_my_projects"],
            "api_calls": 1,
            "cache_hit": False
        },
        "success": True,
        "error": None
    },
    "time_entries": {
        "data": {
            "time_entries": MOCK_TIME_ENTRIES
        },
        "metadata": {
            "tools_used": ["get_time_entries"],
            "api_calls": 1,
            "cache_hit": False
        },
        "success": True,
        "error": None
    },
    "summary": {
        "data": MOCK_SUMMARY,
        "metadata": {
            "tools_used": ["check_my_timesheet", "list_my_projects"],
            "api_calls": 2,
            "cache_hit": False
        },
        "success": True,
        "error": None
    },
    "api_error": {
        "data": {},
        "metadata": {},
        "success": False,
        "error": "Harvest API connection timeout"
    },
    "no_data": {
        "data": {
            "hours_logged": 0.0,
            "hours_target": 40.0
        },
        "metadata": {
            "tools_used": ["check_my_timesheet"],
            "api_calls": 1,
            "cache_hit": False
        },
        "success": True,
        "error": None
    }
}

# Mock user credentials
MOCK_USER_CREDENTIALS = {
    "harvest_access_token": "mock_token_12345",
    "harvest_account_id": "mock_account_67890",
    "harvest_user_id": 999
}
