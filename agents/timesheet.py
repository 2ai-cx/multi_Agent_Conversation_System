"""
Timesheet Agent - Data Specialist for Harvest API

Responsibilities:
- Extract timesheet data using existing 51 Harvest API tools
- Handle API errors gracefully
- Return structured data to Planner Agent
- Use user-specific credentials
- Respect user timezone settings
"""

from typing import Dict, Any
from agents.base import BaseAgent


class TimesheetAgent(BaseAgent):
    """
    Data specialist agent that extracts timesheet information.
    
    Reuses existing 51 Harvest API tools from unified_workflows.py without modification.
    """
    
    def __init__(self, llm_client, harvest_tools):
        """
        Initialize Timesheet Agent.
        
        Args:
            llm_client: Centralized LLM client
            harvest_tools: Existing Harvest API tools object
        """
        super().__init__(llm_client)
        self.harvest_tools = harvest_tools
    
    async def execute(
        self,
        request_id: str,
        planner_message: str,
        user_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute data retrieval based on Planner's natural language instruction.
        
        NO HARDCODED LOGIC. Agent uses LLM to:
        1. Understand what Planner is asking for
        2. Decide which Harvest tool to call
        3. Extract parameters from the instruction
        
        Args:
            request_id: Unique request identifier
            planner_message: Natural language instruction from Planner
                Examples:
                - "Get time entries for November 18-24, 2025"
                - "Get all projects for this user"
                - "Get time entries for last week"
            user_context: User credentials, timezone, etc.
            
        Returns:
            Dict with data, tool_used, success flag, and error (if any)
        """
        self.logger.info(f"📊 [Timesheet] Received instruction from Planner")
        self.logger.info(f"� [Timesheet] Message: '{planner_message}'")
        
        try:
            # Step 1: Use LLM to decide which tool to call
            import json
            
            prompt = f"""You are a Timesheet Tool Execution Specialist with access to ALL 51 Harvest API tools.

PLANNER'S INSTRUCTION:
"{planner_message}"

CONTEXT:
- User's timezone: {user_context.get('timezone', 'UTC')}
- Today's date: {user_context.get('current_date', 'unknown')}

COMPLETE HARVEST API TOOL CATALOG (51 tools):

TIME ENTRIES (7 tools):
- list_time_entries(from_date, to_date, user_id=None) - List entries in date range
- get_time_entry(time_entry_id) - Get specific entry
- create_time_entry(project_id, task_id, spent_date, hours, notes=None) - Create entry
- update_time_entry(time_entry_id, project_id=None, task_id=None, spent_date=None, hours=None, notes=None) - Update entry
- delete_time_entry(time_entry_id) - Delete entry
- restart_time_entry(time_entry_id) - Restart timer
- stop_time_entry(time_entry_id) - Stop timer

PROJECTS (5 tools):
- list_projects(is_active=None, client_id=None, updated_since=None) - List all projects
- get_project(project_id) - Get specific project
- create_project(client_id, name, is_billable=True, bill_by=None, budget=None, is_active=True) - Create project
- update_project(project_id, client_id=None, name=None, is_billable=None, bill_by=None, budget=None, is_active=None) - Update project
- delete_project(project_id) - Delete project

TASKS (5 tools):
- list_tasks(is_active=None, updated_since=None) - List all tasks
- get_task(task_id) - Get specific task
- create_task(name, billable_by_default=True, default_hourly_rate=None, is_active=True) - Create task
- update_task(task_id, name=None, billable_by_default=None, default_hourly_rate=None, is_active=None) - Update task
- delete_task(task_id) - Delete task

USERS (5 tools):
- get_current_user() - Get current user info
- list_users(is_active=None, updated_since=None) - List all users
- get_user(user_id) - Get specific user
- create_user(first_name, last_name, email, timezone=None, has_access_to_all_future_projects=None, is_contractor=False, is_active=True) - Create user
- update_user(user_id, first_name=None, last_name=None, email=None, timezone=None, has_access_to_all_future_projects=None, is_contractor=None, is_active=None) - Update user

CLIENTS (5 tools):
- list_clients(is_active=None, updated_since=None) - List all clients
- get_client(client_id) - Get specific client
- create_client(name, is_active=True, address=None, currency=None) - Create client
- update_client(client_id, name=None, is_active=None, address=None, currency=None) - Update client
- delete_client(client_id) - Delete client

CONTACTS (5 tools):
- list_contacts(client_id=None, updated_since=None) - List contacts
- get_contact(contact_id) - Get specific contact
- create_contact(client_id, first_name, last_name=None, email=None, phone_office=None, phone_mobile=None, fax=None) - Create contact
- update_contact(contact_id, first_name=None, last_name=None, email=None, phone_office=None, phone_mobile=None, fax=None) - Update contact
- delete_contact(contact_id) - Delete contact

EXPENSES (5 tools):
- list_expenses(user_id=None, client_id=None, project_id=None, is_billed=None, updated_since=None, from_date=None, to_date=None) - List expenses
- get_expense(expense_id) - Get specific expense
- create_expense(project_id, expense_category_id, spent_date, units=None, total_cost=None, notes=None) - Create expense
- update_expense(expense_id, project_id=None, expense_category_id=None, spent_date=None, units=None, total_cost=None, notes=None) - Update expense
- delete_expense(expense_id) - Delete expense

INVOICES (5 tools):
- list_invoices(client_id=None, project_id=None, updated_since=None, from_date=None, to_date=None, state=None) - List invoices
- get_invoice(invoice_id) - Get specific invoice
- create_invoice(client_id, subject=None, notes=None, currency=None, issue_date=None, due_date=None) - Create invoice
- update_invoice(invoice_id, client_id=None, subject=None, notes=None, currency=None, issue_date=None, due_date=None) - Update invoice
- delete_invoice(invoice_id) - Delete invoice

ESTIMATES (5 tools):
- list_estimates(client_id=None, updated_since=None, from_date=None, to_date=None, state=None) - List estimates
- get_estimate(estimate_id) - Get specific estimate
- create_estimate(client_id, subject=None, notes=None, currency=None, issue_date=None) - Create estimate
- update_estimate(estimate_id, client_id=None, subject=None, notes=None, currency=None, issue_date=None) - Update estimate
- delete_estimate(estimate_id) - Delete estimate

COMPANY (1 tool):
- get_company() - Get company information

PROJECT ASSIGNMENTS (2 tools):
- list_project_assignments(is_active=None, updated_since=None) - List project assignments
- list_project_task_assignments(project_id) - List task assignments for project

TASK ASSIGNMENTS (1 tool):
- list_task_assignments(is_active=None, updated_since=None) - List task assignments

YOUR EXECUTION PROTOCOL:
1. Parse the Planner's instruction to identify the tool name and parameters
2. The Planner's instruction will specify INPUT FORMAT (exact parameters with values)
3. Execute the tool call with those exact parameters
4. Return ALL raw data in the OUTPUT FORMAT the Planner specified
5. Do NOT filter, aggregate, or transform data - return everything as-is

Return JSON:
{{
    "tool_to_call": "exact_tool_name",
    "parameters": {{"param1": "value1", "param2": "value2"}},
    "reasoning": "brief explanation of what you're executing"
}}

Return ONLY valid JSON, no other text."""

            self.logger.info(f" [Timesheet] Asking LLM to decide which tool to use...")
            llm_response = await self.llm_client.generate(prompt)
            self.logger.info(f" [Timesheet] LLM raw response: {llm_response[:500]}")
            self.logger.info(f"📝 [Timesheet] LLM raw response: {llm_response[:500]}")
            
            # Parse LLM decision
            try:
                decision = json.loads(llm_response)
                self.logger.info(f"✅ [Timesheet] Successfully parsed JSON decision")
            except json.JSONDecodeError:
                # Try to extract JSON from response
                import re
                json_match = re.search(r'\{.*\}', llm_response, re.DOTALL)
                if json_match:
                    decision = json.loads(json_match.group())
                else:
                    raise ValueError(f"LLM did not return valid JSON: {llm_response[:200]}")
            
            tool_name = decision['tool_to_call']
            params = decision.get('parameters', {})
            reasoning = decision.get('reasoning', '')
            
            self.logger.info(f"📋 [Timesheet] LLM decided to use: {tool_name}")
            self.logger.info(f"💭 [Timesheet] Reasoning: {reasoning}")
            self.logger.info(f"🔧 [Timesheet] Parameters: {params}")
            
            # Step 2: Call the tool
            if hasattr(self.harvest_tools, tool_name):
                tool_func = getattr(self.harvest_tools, tool_name)
                self.logger.info(f"🔧 [Timesheet] Calling {tool_name}...")
                
                result = await tool_func(**params)
                
                self.logger.info(f"✅ [Timesheet] Tool call successful")
                self.logger.info(f"📊 [Timesheet] Result type: {type(result)}")
                self.logger.info(f"📊 [Timesheet] Result keys: {list(result.keys()) if isinstance(result, dict) else 'not a dict'}")
                if isinstance(result, dict) and 'time_entries' in result:
                    self.logger.info(f"📊 [Timesheet] Number of time entries: {len(result.get('time_entries', []))}")
                
                # Enrich the result with query parameters for Planner context
                enriched_data = {
                    "harvest_response": result,
                    "query_parameters": params,  # Include the dates/params used
                    "tool_used": tool_name
                }
                
                self.logger.info(f"📊 [Timesheet] Enriched data with query params: {params}")
                
                return {
                    "data": enriched_data,
                    "tool_used": tool_name,
                    "reasoning": reasoning,
                    "success": True,
                    "error": None
                }
            else:
                raise ValueError(f"Tool '{tool_name}' not found in harvest_tools")
        
        except Exception as e:
            # Handle errors gracefully
            self.logger.error(f"❌ [Timesheet] Execution failed: {str(e)}")
            self.logger.error(f"🐛 [Timesheet] Error type: {type(e).__name__}")
            import traceback
            self.logger.error(f"📜 [Timesheet] Traceback: {traceback.format_exc()[:500]}...")
            
            return {
                "data": {},
                "tool_used": None,
                "reasoning": None,
                "success": False,
                "error": str(e)
            }
