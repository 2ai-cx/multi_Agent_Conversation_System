"""Sample scorecards for testing quality validation"""

from agents.models import Scorecard, ScorecardCriterion

# Scorecard for timesheet query
TIMESHEET_QUERY_SCORECARD = Scorecard(
    request_id="req-test-001",
    criteria=[
        ScorecardCriterion(
            id="answers_question",
            description="Response answers user's question about timesheet hours",
            expected="Response includes hours logged information"
        ),
        ScorecardCriterion(
            id="includes_data",
            description="Response contains actual timesheet data",
            expected="Response has specific numbers (hours logged, target hours, etc.)"
        ),
        ScorecardCriterion(
            id="correct_format",
            description="Response is formatted correctly for channel",
            expected="Plain text for SMS, markdown for Email, etc."
        )
    ]
)

# Scorecard for SMS channel
SMS_FORMAT_SCORECARD = Scorecard(
    request_id="req-sms-001",
    criteria=[
        ScorecardCriterion(
            id="no_markdown",
            description="Response contains no markdown symbols",
            expected="No *, #, _, `, or other markdown characters"
        ),
        ScorecardCriterion(
            id="length_limit",
            description="Response is under 1600 characters",
            expected="Total character count <= 1600"
        ),
        ScorecardCriterion(
            id="plain_text",
            description="Response is plain text only",
            expected="No HTML, no special formatting"
        )
    ]
)

# Scorecard for Email channel
EMAIL_FORMAT_SCORECARD = Scorecard(
    request_id="req-email-001",
    criteria=[
        ScorecardCriterion(
            id="has_markdown",
            description="Response uses markdown for formatting",
            expected="Contains headers, bold, lists, or other markdown"
        ),
        ScorecardCriterion(
            id="well_structured",
            description="Response is well-structured with sections",
            expected="Has clear sections, headers, or organization"
        ),
        ScorecardCriterion(
            id="complete_info",
            description="Response provides complete information",
            expected="All requested data included with context"
        )
    ]
)

# Scorecard for complex query
COMPLEX_QUERY_SCORECARD = Scorecard(
    request_id="req-complex-001",
    criteria=[
        ScorecardCriterion(
            id="all_parts_answered",
            description="Response addresses all parts of the query",
            expected="Both hours AND projects information included"
        ),
        ScorecardCriterion(
            id="coherent",
            description="Response is coherent and unified",
            expected="Information flows logically, not just concatenated"
        ),
        ScorecardCriterion(
            id="accurate_data",
            description="All data is accurate and from correct sources",
            expected="Hours from timesheet, projects from project list"
        )
    ]
)

# Scorecard that will fail (for testing refinement)
FAILING_SCORECARD = Scorecard(
    request_id="req-fail-001",
    criteria=[
        ScorecardCriterion(
            id="impossible_criterion",
            description="Response must be both very short and very detailed",
            expected="Under 50 characters but includes full project breakdown",
            passed=False,
            feedback="Cannot be both short and detailed"
        ),
        ScorecardCriterion(
            id="contradictory",
            description="Response must use markdown and be plain text",
            expected="Has markdown formatting but no special characters",
            passed=False,
            feedback="Markdown requires special characters"
        )
    ]
)

# Scorecard with all criteria passing
PASSING_SCORECARD = Scorecard(
    request_id="req-pass-001",
    criteria=[
        ScorecardCriterion(
            id="simple_check",
            description="Response is not empty",
            expected="Response has content",
            passed=True
        ),
        ScorecardCriterion(
            id="reasonable_length",
            description="Response is reasonable length",
            expected="Between 10 and 5000 characters",
            passed=True
        )
    ]
)
