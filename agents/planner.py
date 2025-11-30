"""
Planner Agent - Coordinator for Multi-Agent System

Responsibilities:
- Analyze user requests and create execution plans
- Generate scorecards for quality validation
- Compose responses from data and context
- Handle refinement requests from Quality Agent
- Compose graceful failure messages
"""

import json
from typing import Dict, Any, List
from agents.base import BaseAgent
from agents.models import ExecutionPlan, ExecutionStep, Scorecard, ScorecardCriterion, Channel


class PlannerAgent(BaseAgent):
    """
    Coordinator agent that orchestrates the multi-agent workflow.
    
    Creates execution plans, generates quality scorecards, composes responses,
    and handles refinement loops.
    """
    
    async def analyze_request(
        self,
        request_id: str,
        user_message: str,
        channel: str,
        conversation_history: List[Dict],
        user_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze user request and create execution plan + scorecard.
        
        Args:
            request_id: Unique request identifier
            user_message: User's message
            channel: Communication channel (sms, email, whatsapp, teams)
            conversation_history: Previous messages
            user_context: User information
            
        Returns:
            Dict with execution_plan and scorecard
        """
        self.logger.info(f"🎯 [Planner] Starting request analysis: {request_id}")
        self.logger.info(f"📝 [Planner] User message: '{user_message[:100]}...'" if len(user_message) > 100 else f"📝 [Planner] User message: '{user_message}'")
        self.logger.info(f"📱 [Planner] Channel: {channel}")
        self.logger.info(f"💬 [Planner] Conversation history: {len(conversation_history)} messages")
        
        # Standard Operating Procedures (SOPs) for common workflows
        sops = {
            "check_timesheet": {
                "triggers": ["check timesheet", "my timesheet", "hours logged", "time entries", "what did i log", "show my hours"],
                "needs_data": True,
                "message_to_timesheet": """Execute list_time_entries tool:

INPUT FORMAT:
- tool: list_time_entries
- from_date: Start of requested period in YYYY-MM-DD (parse from user request, default to current week start)
- to_date: End of requested period in YYYY-MM-DD (parse from user request, default to today)
- user_id: Current user's ID from context

OUTPUT FORMAT:
Return complete Harvest API response:
- time_entries: Array with all entries (each containing: spent_date, hours, project, task, notes)
- total_entries: Count
- All API metadata

Return everything unfiltered.""",
                "criteria": [
                    {"id": "data_completeness", "description": "Response includes all timesheet entries OR provides a summary if many entries OR clearly states if there are no entries", "expected": "For 1-5 entries: list all with details. For 6+ entries: provide summary (count, total hours, breakdown). For 0 entries: explicitly state 'no entries' or '0 hours'"},
                    {"id": "time_period_clarity", "description": "Response clearly states the time period covered", "expected": "Date range is mentioned (e.g., 'Oct 1-31' or 'last month')"},
                    {"id": "sms_format", "description": "Response is formatted appropriately for SMS", "expected": "Concise, clear, and easy to read on mobile"}
                ]
            },
            "weekly_summary": {
                "triggers": ["weekly summary", "this week", "week total", "hours this week"],
                "needs_data": True,
                "message_to_timesheet": "Retrieve the user's total hours for the current week, grouped by project.",
                "criteria": [
                    {"id": "total_hours", "description": "Response includes total hours worked", "expected": "Total hours clearly stated"},
                    {"id": "project_breakdown", "description": "Hours broken down by project", "expected": "Each project listed with hours"},
                    {"id": "sms_format", "description": "Response is formatted appropriately for SMS", "expected": "Concise summary format"}
                ]
            },
            "today_entries": {
                "triggers": ["today", "logged today", "hours today", "what did i do today"],
                "needs_data": True,
                "message_to_timesheet": "Retrieve the user's timesheet entries for today only.",
                "criteria": [
                    {"id": "today_only", "description": "Response only includes today's entries", "expected": "Only today's date is shown"},
                    {"id": "entry_details", "description": "Each entry shows project, hours, and description", "expected": "Complete entry information"},
                    {"id": "sms_format", "description": "Response is formatted appropriately for SMS", "expected": "Brief and clear"}
                ]
            },
            "last_entry": {
                "triggers": ["last entry", "most recent entry", "latest entry", "when was my last", "last time i logged"],
                "needs_data": True,
                "message_to_timesheet": """Execute list_time_entries tool with these parameters:

INPUT FORMAT:
- tool: list_time_entries
- from_date: Calculate as (today - 365 days) in YYYY-MM-DD format
- to_date: Today's date in YYYY-MM-DD format
- user_id: Use current user's ID from context

OUTPUT FORMAT:
Return the complete Harvest API response containing:
- time_entries: Array of all entries from last year (I will find the most recent)
- total_entries: Count
- All other metadata from API

Do not filter or process the data - return everything.""",
                "criteria": [
                    {"id": "response_completeness", "description": "Response includes the date and details of the last timesheet entry", "expected": "Includes the date of last entry, and may include hours/project for context"},
                    {"id": "clarity_and_conciseness", "description": "Response is clear and directly answers the question", "expected": "Clearly states when the last entry was, with brief supporting details"},
                    {"id": "channel_appropriateness", "description": "Response is appropriate for SMS", "expected": "Concise and readable on mobile"}
                ]
            }
        }
        
        # Check if request matches a known SOP
        user_message_lower = user_message.lower()
        matched_sop = None
        for sop_name, sop in sops.items():
            if any(trigger in user_message_lower for trigger in sop["triggers"]):
                matched_sop = sop
                self.logger.info(f"✅ [Planner] Matched SOP: {sop_name}")
                break
        
        # Build analysis prompt with SOP context
        if matched_sop:
            prompt = f"""You are a Planner Agent coordinating a multi-agent team.

User's request: "{user_message}"
Channel: {channel}
Conversation history: {json.dumps(conversation_history[-3:] if conversation_history else [])}

MATCHED STANDARD OPERATING PROCEDURE:
This request matches a known workflow pattern.

DECISION PROCESS - Follow this exactly:

Step 1: Understand the REQUEST TYPE
- Timesheet Check: User wants to see their logged hours/entries
- Weekly Summary: User wants total hours for the week
- Today's Entries: User wants today's specific entries
- Custom: User has specific variations (different dates, specific projects)

Step 2: Determine if you need Timesheet Agent
For this matched SOP:
- Needs data: {matched_sop['needs_data']}
- Standard message: "{matched_sop['message_to_timesheet']}"

Step 3: Adjust for USER VARIATIONS
- If user mentions specific dates → adjust message to include those dates
- If user mentions specific projects → adjust message to filter by project
- If user asks for different time period → adjust date range accordingly
- Otherwise → use the standard SOP message as-is

Step 4: Define QUALITY CRITERIA
Standard criteria for this workflow:
{json.dumps(matched_sop['criteria'], indent=2)}

Add additional criteria if user has special requirements.

ABSOLUTE RULES:
1. You CANNOT state any facts about current timesheet data without calling Timesheet Agent first
2. ALWAYS set needs_data=true for timesheet-related requests
3. Conversation history shows past context, NOT current Harvest data
4. Never invent project names, hours, dates, or entries
5. Be SPECIFIC in your message to Timesheet Agent (include dates, filters, project names)
6. Quality criteria must match the channel ({channel})
7. For SMS: responses must be concise, no markdown, use bullet points or short lines
8. If uncertain whether user wants data or just chat → treat it as data request (use Timesheet Agent)

ERROR PREVENTION:
- If date/time period unclear → default to "this_week" or "current week"
- If user mentions "last week" → specify exact date range in message
- If user mentions specific project → include project name filter in message
- If request is vague → ask Timesheet Agent for comprehensive data and let it decide

Example Patterns for this SOP:
- "check timesheet" → Standard SOP message for current week
- "check last week" → Adjust to "Retrieve timesheet for last week (Nov 18-24)"
- "hours on Project Alpha" → Adjust to "Retrieve hours for Project Alpha this week"
- "today's entries" → Adjust to "Retrieve today's timesheet entries only"

Return JSON:
{{
    "needs_data": true/false,
    "message_to_timesheet": "Your specific, detailed request to Timesheet Agent",
    "criteria": [
        {{
            "id": "unique_id",
            "description": "What to check",
            "expected": "What the response should contain"
        }}
    ]
}}

Return ONLY valid JSON, no other text."""
        else:
            prompt = f"""You are a Planner Agent coordinating a multi-agent team.

User's request: "{user_message}"
Channel: {channel}
Conversation history: {json.dumps(conversation_history[-3:] if conversation_history else [])}

Available agents:
- Timesheet Agent: Can retrieve data from Harvest API (51 tools available)
- Branding Agent: Can format responses for different channels
- Quality Agent: Can validate response quality

Your task:
1. Analyze the user's request
2. Decide if you need data from the Timesheet Agent
3. If yes, write a clear, specific message to the Timesheet Agent explaining what data you need
4. Create quality validation criteria for the final response

Think step by step. Consider:
- What is the user asking for?
- Do I need timesheet data to answer this?
- If yes, what specific data do I need? (be specific about dates, projects, etc.)
- What makes a good response for this channel?

Return JSON:
{{
    "needs_data": true/false,
    "message_to_timesheet": "Your specific request to Timesheet Agent (if needs_data is true)",
    "criteria": [
        {{
            "id": "unique_id",
            "description": "What to check",
            "expected": "What the response should contain"
        }}
    ]
}}

Return ONLY valid JSON, no other text."""
        
        # Call LLM
        self.logger.info(f"🤖 [Planner] Calling LLM for analysis (prompt length: {len(prompt)} chars)")
        llm_response = await self.llm_client.generate(prompt)
        self.logger.info(f"✅ [Planner] LLM response received (length: {len(str(llm_response))} chars)")
        self.logger.info(f"🔍 [Planner] RAW LLM response: {llm_response[:500]}")
        
        # Parse response
        self.logger.info(f"🔍 [Planner] Parsing LLM response...")
        if isinstance(llm_response, str):
            # Strip markdown code blocks if present
            llm_response_clean = llm_response.strip()
            if llm_response_clean.startswith('```'):
                # Remove opening ```json or ```
                llm_response_clean = llm_response_clean.split('\n', 1)[1] if '\n' in llm_response_clean else llm_response_clean[3:]
                # Remove closing ```
                if llm_response_clean.endswith('```'):
                    llm_response_clean = llm_response_clean.rsplit('```', 1)[0]
                llm_response_clean = llm_response_clean.strip()
                self.logger.info(f"🔧 [Planner] Stripped markdown code blocks from response")
            
            try:
                parsed = json.loads(llm_response_clean)
                self.logger.info(f"✅ [Planner] Successfully parsed JSON response")
                self.logger.info(f"🔍 [Planner] Parsed needs_data: {parsed.get('needs_data')}")
                self.logger.info(f"🔍 [Planner] Parsed message_to_timesheet: {parsed.get('message_to_timesheet', '')[:100]}")
            except json.JSONDecodeError as e:
                # Special handling for "last entry" queries
                if "last" in user_message.lower() and "entry" in user_message.lower() and "last month" not in user_message.lower():
                    # Find the most recent entry
                    if isinstance(harvest_response, dict) and 'time_entries' in harvest_response:
                        entries = harvest_response.get('time_entries', [])
                        if entries:
                            # Sort by spent_date descending to find the most recent
                            sorted_entries = sorted(entries, key=lambda x: x.get('spent_date', ''), reverse=True)
                            most_recent = sorted_entries[0]
                            self.logger.info(f"📊 [Planner] Found most recent entry: {most_recent.get('spent_date')}")
                            # Replace harvest_response with ONLY the most recent entry
                            # Remove total_entries to avoid mentioning it in response
                            harvest_response = {
                                'time_entries': [most_recent],
                                'most_recent_date': most_recent.get('spent_date')
                            }
                            self.logger.info(f"📊 [Planner] Filtered to single most recent entry")
                # Fallback if LLM doesn't return valid JSON
                self.logger.warning(f"⚠️ [Planner] JSON parse error: {e}. Using minimal fallback.")
                # NO HARDCODED LOGIC - just provide minimal structure
                parsed = {
                    "needs_data": False,  # Conservative fallback
                    "message_to_timesheet": "",
                    "criteria": [
                        {
                            "id": "answers_question",
                            "description": "Response answers user's question",
                            "expected": "Response addresses the user's query"
                        }
                    ]
                }
        else:
            parsed = llm_response
        
        # Create execution plan - simplified, no hardcoded steps
        self.logger.info(f"📋 [Planner] Creating execution plan")
        execution_plan = {
            "request_id": request_id,
            "needs_data": parsed.get("needs_data", False),
            "message_to_timesheet": parsed.get("message_to_timesheet", ""),
            "user_message": user_message,
            "channel": channel
        }
        
        # Create scorecard
        self.logger.info(f"📊 [Planner] Creating scorecard with {len(parsed.get('criteria', []))} criteria")
        criteria = [ScorecardCriterion(**c) for c in parsed.get("criteria", [])]
        for criterion in criteria:
            self.logger.info(f"  ✓ Criterion: {criterion.id} - {criterion.description}")
        scorecard = Scorecard(
            request_id=request_id,
            criteria=criteria
        )
        
        self.logger.info(f"✅ [Planner] Analysis complete. Needs data: {execution_plan['needs_data']}")
        if execution_plan['needs_data']:
            self.logger.info(f"📨 [Planner] Message to Timesheet: '{execution_plan['message_to_timesheet']}'")
        
        return {
            "execution_plan": execution_plan,
            "scorecard": scorecard.model_dump(mode='json')
        }
    
    async def compose_response(
        self,
        request_id: str,
        user_message: str,
        timesheet_data: Dict[str, Any],
        conversation_history: List[Dict],
        user_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Compose response from timesheet data and context.
        
        Args:
            request_id: Unique request identifier
            user_message: User's original message
            timesheet_data: Data from Timesheet Agent (or None)
            conversation_history: Previous messages
            user_context: User information
            
        Returns:
            Dict with response and metadata
        """
        self.logger.info(f"✍️ [Planner] Starting response composition: {request_id}")
        
        # Determine response type
        used_timesheet_data = timesheet_data is not None and len(timesheet_data) > 0
        self.logger.info(f"📊 [Planner] Timesheet data available: {used_timesheet_data}")
        self.logger.info(f"📊 [Planner] Timesheet data type: {type(timesheet_data)}")
        self.logger.info(f"📊 [Planner] Timesheet data keys: {list(timesheet_data.keys()) if isinstance(timesheet_data, dict) else 'not a dict'}")
        
        if used_timesheet_data:
            # Extract query parameters and harvest response
            # timesheet_data structure: {"harvest_response": {...}, "query_parameters": {...}, "tool_used": "..."}
            query_params = {}
            harvest_response = timesheet_data
            
            if isinstance(timesheet_data, dict):
                # Direct extraction - no nested 'data' key
                query_params = timesheet_data.get('query_parameters', {})
                harvest_response = timesheet_data.get('harvest_response', timesheet_data)
                self.logger.info(f"📊 [Planner] Extracted query_params: {query_params}")
                self.logger.info(f"📊 [Planner] Extracted harvest_response keys: {list(harvest_response.keys()) if isinstance(harvest_response, dict) else 'not a dict'}")
                
                # Special handling for "last entry" queries (but not "last month")
                if "last" in user_message.lower() and "entry" in user_message.lower() and "last month" not in user_message.lower() and "last week" not in user_message.lower():
                    # Find the most recent entry
                    if isinstance(harvest_response, dict) and 'time_entries' in harvest_response:
                        entries = harvest_response.get('time_entries', [])
                        if entries:
                            # Sort by spent_date descending to find the most recent
                            sorted_entries = sorted(entries, key=lambda x: x.get('spent_date', ''), reverse=True)
                            most_recent = sorted_entries[0]
                            self.logger.info(f"📊 [Planner] Found most recent entry: {most_recent.get('spent_date')}")
                            # Replace harvest_response with ONLY the most recent entry
                            # Do NOT include total_entries to avoid mentioning it
                            harvest_response = {
                                'time_entries': [most_recent],
                                'most_recent_date': most_recent.get('spent_date')
                            }
                            self.logger.info(f"📊 [Planner] Filtered to single most recent entry")
            
            # Compose data-driven response
            prompt = f"""Compose a helpful response to the user's question using the timesheet data.

User question: "{user_message}"
Timesheet data: {json.dumps(harvest_response, indent=2)}
Query parameters: {json.dumps(query_params, indent=2)}
User name: {user_context.get('full_name', 'there')}
Current date: {user_context.get('current_date', 'today')}

Create a friendly, informative response that:
1. Directly answers the user's question
2. EXPLICITLY states the TIME PERIOD covered using the query parameters (from_date to to_date)
   - Example: "for Oct 1-31, 2025" or "for Nov 21-27, 2025"
3. EXPLICITLY states the TOTAL number of entries
   - If 0 entries: MUST use exact phrase "no entries" or "0 hours logged"
   - If 1-5 entries: "You have X entries"
   - If 6+ entries: "You have X entries"
4. For entries:
   - If 1-5 entries: List EACH ONE with date, hours, project name
   - If 6+ entries: Provide SUMMARY (total hours, breakdown by project/week, key highlights)
5. Is conversational and encouraging
6. Keeps it concise and SMS-friendly

CRITICAL REQUIREMENTS:
- ALWAYS include the date range from query_parameters (from_date to to_date)
- ALWAYS state the total count
- If 0 entries: use phrase "no entries" or "0 hours logged"
- If 1-5 entries: list all with details
- If 6+ entries: summarize (don't list all - too long for SMS)

Example for 0 entries:
"Hi! For Oct 1-31, 2025, you have no entries (0 hours logged). Need help logging hours?"

Example for 3 entries:
"Hi! For Oct 1-31, 2025, you have 3 entries:
- Oct 5: 8h on Project A
- Oct 12: 6h on Project B
- Oct 20: 7h on Project A
Total: 21 hours"

Example for 11 entries:
"Hi! For Oct 1-31, 2025, you have 11 entries totaling 88 hours. All on Q3 2024 Autonomous Agents project, 8h each. Great consistency!"

Response:"""
            
            response_type = "data"
            self.logger.info(f"📊 [Planner] Using data-driven response with timesheet data")
        else:
            # Compose conversational response
            prompt = f"""Compose a helpful conversational response to the user.

User message: "{user_message}"
Conversation history: {json.dumps(conversation_history[-3:] if conversation_history else [])}
User name: {user_context.get('full_name', 'there')}

Create a friendly response that:
1. Acknowledges the user's message
2. Is helpful and conversational
3. Offers assistance if appropriate

Response:"""
            
            response_type = "conversational"
            self.logger.info(f"💬 [Planner] Using conversational response (no timesheet data)")
        
        # Call LLM
        self.logger.info(f"🤖 [Planner] Calling LLM for composition (prompt length: {len(prompt)} chars)")
        response = await self.llm_client.generate(prompt)
        self.logger.info(f"✅ [Planner] Response composed (length: {len(str(response))} chars)")
        
        # Clean up response
        if isinstance(response, dict):
            response = response.get("response", str(response))
        
        self.logger.info(f"✅ [Planner] Composition complete. Type: {response_type}, Confidence: {0.9 if used_timesheet_data else 0.7}")
        
        return {
            "response": response,
            "metadata": {
                "used_timesheet_data": used_timesheet_data,
                "response_type": response_type,
                "confidence": 0.9 if used_timesheet_data else 0.7
            }
        }
    
    async def refine_response(
        self,
        request_id: str,
        original_response: str,
        failed_criteria: List[Dict],
        attempt_number: int
    ) -> Dict[str, Any]:
        """
        Refine response based on quality validation feedback.
        
        Args:
            request_id: Unique request identifier
            original_response: Response that failed validation
            failed_criteria: List of failed criteria with feedback
            attempt_number: Refinement attempt number (must be 1)
            
        Returns:
            Dict with refined_response and changes_made
            
        Raises:
            ValueError: If attempt_number > 1
        """
        self.logger.info(f"🔄 [Planner] Starting response refinement: {request_id} (attempt {attempt_number})")
        self.logger.info(f"❌ [Planner] Original response failed {len(failed_criteria)} criteria")
        for criterion in failed_criteria:
            self.logger.info(f"  ✗ {criterion.get('id')}: {criterion.get('feedback', 'No feedback')}")
        
        if attempt_number > 1:
            raise ValueError("Maximum 1 refinement attempt allowed")
        
        # Build refinement prompt
        criteria_feedback = "\n".join([
            f"- {c.get('description', 'Unknown')}: {c.get('feedback', 'Failed')}"
            for c in failed_criteria
        ])
        
        prompt = f"""Refine this response based on the quality validation feedback.

Original response:
"{original_response}"

Failed criteria:
{criteria_feedback}

Create an improved response that:
1. Addresses all the failed criteria
2. Maintains the core message and information
3. Fixes the specific issues mentioned in the feedback

Refined response:"""
        
        # Call LLM
        refined = await self.llm_client.generate(prompt)
        
        # Extract changes made
        changes = []
        for criterion in failed_criteria:
            if "markdown" in criterion.get("description", "").lower():
                changes.append("Removed markdown formatting")
            if "length" in criterion.get("description", "").lower():
                changes.append("Shortened response to meet length limit")
            if "format" in criterion.get("description", "").lower():
                changes.append("Adjusted formatting for channel")
        
        if not changes:
            changes.append("Applied quality feedback")
        
        return {
            "refined_response": refined,
            "changes_made": changes,
            "confidence": 0.8
        }
    
    async def compose_graceful_failure(
        self,
        request_id: str,
        user_message: str,
        failure_reason: str,
        channel: str
    ) -> Dict[str, Any]:
        """
        Compose user-friendly graceful failure message.
        
        Args:
            request_id: Unique request identifier
            user_message: User's original message
            failure_reason: Why the request failed
            channel: Communication channel
            
        Returns:
            Dict with failure_message and metadata
        """
        # Build graceful failure prompt
        prompt = f"""Create a friendly, helpful error message for the user.

User's request: "{user_message}"
Failure reason: {failure_reason}
Channel: {channel}

Create a message that:
1. Is empathetic and friendly (not technical)
2. Apologizes for not being able to help
3. Suggests what the user could try instead
4. Keeps it brief and clear

Error message:"""
        
        # Call LLM
        failure_message = await self.llm_client.generate(prompt)
        
        # Ensure it's user-friendly
        if isinstance(failure_message, dict):
            failure_message = failure_message.get("message", "I can't help with that right now.")
        
        # Fallback to default if LLM returns something too technical
        if any(word in failure_message.lower() for word in ["exception", "error code", "stack trace", "null"]):
            failure_message = "I can't help with that right now. Please try rephrasing your question."
        
        return {
            "failure_message": failure_message,
            "metadata": {
                "failure_type": failure_reason,
                "logged": True
            }
        }
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute Planner agent action.
        
        Args:
            input_data: Must contain 'action' and action-specific parameters
            
        Returns:
            Action-specific output
        """
        action = input_data.get("action")
        
        if action == "analyze_request":
            return await self.analyze_request(
                input_data["request_id"],
                input_data["user_message"],
                input_data["channel"],
                input_data.get("conversation_history", []),
                input_data.get("user_context", {})
            )
        elif action == "compose_response":
            return await self.compose_response(
                input_data["request_id"],
                input_data["user_message"],
                input_data.get("timesheet_data"),
                input_data.get("conversation_history", []),
                input_data.get("user_context", {})
            )
        elif action == "refine_response":
            return await self.refine_response(
                input_data["request_id"],
                input_data["original_response"],
                input_data["failed_criteria"],
                input_data.get("attempt_number", 1)
            )
        elif action == "compose_graceful_failure":
            return await self.compose_graceful_failure(
                input_data["request_id"],
                input_data["user_message"],
                input_data["failure_reason"],
                input_data["channel"]
            )
        else:
            raise ValueError(f"Unknown action: {action}")
