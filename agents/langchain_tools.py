"""
LangChain tools wrapper for Harvest MCP integration.
Converts existing Harvest API tools to LangChain Tool format.
"""

from typing import Any, Dict, List, Optional, Callable
from langchain_core.tools import Tool, StructuredTool
from pydantic import BaseModel, Field
import logging

logger = logging.getLogger(__name__)


class HarvestLangChainTools:
    """
    Wrapper that converts Harvest MCP tools to LangChain Tool format.
    Maintains compatibility with existing 51 Harvest API tools.
    """
    
    def __init__(self, harvest_tools: Any):
        """
        Initialize with existing Harvest tools object.
        
        Args:
            harvest_tools: Existing Harvest API tools from unified_workflows
        """
        self.harvest_tools = harvest_tools
        self.tools: List[Tool] = []
        self._create_langchain_tools()
    
    def _create_langchain_tools(self) -> None:
        """Create LangChain Tool objects from Harvest API methods"""
        
        # Time Entries Tools (7 tools)
        self.tools.extend([
            Tool(
                name="list_time_entries",
                func=self._wrap_async(self.harvest_tools.list_time_entries),
                description="List time entries in a date range. Args: from_date (YYYY-MM-DD), to_date (YYYY-MM-DD), user_id (optional)"
            ),
            Tool(
                name="get_time_entry",
                func=self._wrap_async(self.harvest_tools.get_time_entry),
                description="Get a specific time entry by ID. Args: time_entry_id"
            ),
            Tool(
                name="create_time_entry",
                func=self._wrap_async(self.harvest_tools.create_time_entry),
                description="Create a new time entry. Args: project_id, task_id, spent_date (YYYY-MM-DD), hours, notes (optional)"
            ),
            Tool(
                name="update_time_entry",
                func=self._wrap_async(self.harvest_tools.update_time_entry),
                description="Update an existing time entry. Args: time_entry_id, project_id (optional), task_id (optional), spent_date (optional), hours (optional), notes (optional)"
            ),
            Tool(
                name="delete_time_entry",
                func=self._wrap_async(self.harvest_tools.delete_time_entry),
                description="Delete a time entry. Args: time_entry_id"
            ),
            Tool(
                name="restart_time_entry",
                func=self._wrap_async(self.harvest_tools.restart_time_entry),
                description="Restart a timer for a time entry. Args: time_entry_id"
            ),
            Tool(
                name="stop_time_entry",
                func=self._wrap_async(self.harvest_tools.stop_time_entry),
                description="Stop a running timer. Args: time_entry_id"
            ),
        ])
        
        # Projects Tools (5 tools)
        self.tools.extend([
            Tool(
                name="list_projects",
                func=self._wrap_async(self.harvest_tools.list_projects),
                description="List all projects. Args: is_active (optional bool), client_id (optional), updated_since (optional)"
            ),
            Tool(
                name="get_project",
                func=self._wrap_async(self.harvest_tools.get_project),
                description="Get a specific project by ID. Args: project_id"
            ),
            Tool(
                name="create_project",
                func=self._wrap_async(self.harvest_tools.create_project),
                description="Create a new project. Args: client_id, name, is_billable (optional), bill_by (optional), budget (optional), is_active (optional)"
            ),
            Tool(
                name="update_project",
                func=self._wrap_async(self.harvest_tools.update_project),
                description="Update an existing project. Args: project_id, client_id (optional), name (optional), is_billable (optional), bill_by (optional), budget (optional), is_active (optional)"
            ),
            Tool(
                name="delete_project",
                func=self._wrap_async(self.harvest_tools.delete_project),
                description="Delete a project. Args: project_id"
            ),
        ])
        
        # Tasks Tools (5 tools)
        self.tools.extend([
            Tool(
                name="list_tasks",
                func=self._wrap_async(self.harvest_tools.list_tasks),
                description="List all tasks. Args: is_active (optional bool), updated_since (optional)"
            ),
            Tool(
                name="get_task",
                func=self._wrap_async(self.harvest_tools.get_task),
                description="Get a specific task by ID. Args: task_id"
            ),
            Tool(
                name="create_task",
                func=self._wrap_async(self.harvest_tools.create_task),
                description="Create a new task. Args: name, billable_by_default (optional), default_hourly_rate (optional), is_active (optional)"
            ),
            Tool(
                name="update_task",
                func=self._wrap_async(self.harvest_tools.update_task),
                description="Update an existing task. Args: task_id, name (optional), billable_by_default (optional), default_hourly_rate (optional), is_active (optional)"
            ),
            Tool(
                name="delete_task",
                func=self._wrap_async(self.harvest_tools.delete_task),
                description="Delete a task. Args: task_id"
            ),
        ])
        
        # Clients Tools (5 tools)
        self.tools.extend([
            Tool(
                name="list_clients",
                func=self._wrap_async(self.harvest_tools.list_clients),
                description="List all clients. Args: is_active (optional bool), updated_since (optional)"
            ),
            Tool(
                name="get_client",
                func=self._wrap_async(self.harvest_tools.get_client),
                description="Get a specific client by ID. Args: client_id"
            ),
            Tool(
                name="create_client",
                func=self._wrap_async(self.harvest_tools.create_client),
                description="Create a new client. Args: name, is_active (optional), address (optional), currency (optional)"
            ),
            Tool(
                name="update_client",
                func=self._wrap_async(self.harvest_tools.update_client),
                description="Update an existing client. Args: client_id, name (optional), is_active (optional), address (optional), currency (optional)"
            ),
            Tool(
                name="delete_client",
                func=self._wrap_async(self.harvest_tools.delete_client),
                description="Delete a client. Args: client_id"
            ),
        ])
        
        # Users Tools (5 tools)
        self.tools.extend([
            Tool(
                name="list_users",
                func=self._wrap_async(self.harvest_tools.list_users),
                description="List all users. Args: is_active (optional bool), updated_since (optional)"
            ),
            Tool(
                name="get_user",
                func=self._wrap_async(self.harvest_tools.get_user),
                description="Get a specific user by ID. Args: user_id"
            ),
            Tool(
                name="get_current_user",
                func=self._wrap_async(self.harvest_tools.get_current_user),
                description="Get the currently authenticated user. No args required."
            ),
            Tool(
                name="create_user",
                func=self._wrap_async(self.harvest_tools.create_user),
                description="Create a new user. Args: first_name, last_name, email, timezone (optional), is_active (optional)"
            ),
            Tool(
                name="update_user",
                func=self._wrap_async(self.harvest_tools.update_user),
                description="Update an existing user. Args: user_id, first_name (optional), last_name (optional), email (optional), timezone (optional), is_active (optional)"
            ),
        ])
        
        # Project Assignments Tools (5 tools)
        self.tools.extend([
            Tool(
                name="list_project_assignments",
                func=self._wrap_async(self.harvest_tools.list_project_assignments),
                description="List project assignments for a user. Args: user_id (optional), updated_since (optional)"
            ),
            Tool(
                name="get_project_assignment",
                func=self._wrap_async(self.harvest_tools.get_project_assignment),
                description="Get a specific project assignment. Args: project_assignment_id"
            ),
            Tool(
                name="create_project_assignment",
                func=self._wrap_async(self.harvest_tools.create_project_assignment),
                description="Create a project assignment. Args: project_id, user_id, is_active (optional), hourly_rate (optional)"
            ),
            Tool(
                name="update_project_assignment",
                func=self._wrap_async(self.harvest_tools.update_project_assignment),
                description="Update a project assignment. Args: project_assignment_id, is_active (optional), hourly_rate (optional)"
            ),
            Tool(
                name="delete_project_assignment",
                func=self._wrap_async(self.harvest_tools.delete_project_assignment),
                description="Delete a project assignment. Args: project_assignment_id"
            ),
        ])
        
        # Task Assignments Tools (5 tools)
        self.tools.extend([
            Tool(
                name="list_task_assignments",
                func=self._wrap_async(self.harvest_tools.list_task_assignments),
                description="List task assignments for a project. Args: project_id, updated_since (optional)"
            ),
            Tool(
                name="get_task_assignment",
                func=self._wrap_async(self.harvest_tools.get_task_assignment),
                description="Get a specific task assignment. Args: task_assignment_id"
            ),
            Tool(
                name="create_task_assignment",
                func=self._wrap_async(self.harvest_tools.create_task_assignment),
                description="Create a task assignment. Args: project_id, task_id, is_active (optional), hourly_rate (optional)"
            ),
            Tool(
                name="update_task_assignment",
                func=self._wrap_async(self.harvest_tools.update_task_assignment),
                description="Update a task assignment. Args: task_assignment_id, is_active (optional), hourly_rate (optional)"
            ),
            Tool(
                name="delete_task_assignment",
                func=self._wrap_async(self.harvest_tools.delete_task_assignment),
                description="Delete a task assignment. Args: task_assignment_id"
            ),
        ])
        
        # Reports Tools (5 tools)
        self.tools.extend([
            Tool(
                name="time_report",
                func=self._wrap_async(self.harvest_tools.time_report),
                description="Generate time report. Args: from_date (YYYY-MM-DD), to_date (YYYY-MM-DD), user_id (optional), client_id (optional), project_id (optional)"
            ),
            Tool(
                name="expense_report",
                func=self._wrap_async(self.harvest_tools.expense_report),
                description="Generate expense report. Args: from_date (YYYY-MM-DD), to_date (YYYY-MM-DD), user_id (optional), client_id (optional), project_id (optional)"
            ),
            Tool(
                name="project_budget_report",
                func=self._wrap_async(self.harvest_tools.project_budget_report),
                description="Generate project budget report. Args: project_id"
            ),
            Tool(
                name="uninvoiced_report",
                func=self._wrap_async(self.harvest_tools.uninvoiced_report),
                description="Generate uninvoiced hours report. Args: from_date (YYYY-MM-DD), to_date (YYYY-MM-DD)"
            ),
            Tool(
                name="team_time_report",
                func=self._wrap_async(self.harvest_tools.team_time_report),
                description="Generate team time report. Args: from_date (YYYY-MM-DD), to_date (YYYY-MM-DD)"
            ),
        ])
        
        # Invoices Tools (5 tools)
        self.tools.extend([
            Tool(
                name="list_invoices",
                func=self._wrap_async(self.harvest_tools.list_invoices),
                description="List invoices. Args: client_id (optional), project_id (optional), from_date (optional), to_date (optional)"
            ),
            Tool(
                name="get_invoice",
                func=self._wrap_async(self.harvest_tools.get_invoice),
                description="Get a specific invoice. Args: invoice_id"
            ),
            Tool(
                name="create_invoice",
                func=self._wrap_async(self.harvest_tools.create_invoice),
                description="Create an invoice. Args: client_id, issue_date (YYYY-MM-DD), subject (optional), notes (optional)"
            ),
            Tool(
                name="update_invoice",
                func=self._wrap_async(self.harvest_tools.update_invoice),
                description="Update an invoice. Args: invoice_id, subject (optional), notes (optional), issue_date (optional)"
            ),
            Tool(
                name="delete_invoice",
                func=self._wrap_async(self.harvest_tools.delete_invoice),
                description="Delete an invoice. Args: invoice_id"
            ),
        ])
        
        # Estimates Tools (4 tools)
        self.tools.extend([
            Tool(
                name="list_estimates",
                func=self._wrap_async(self.harvest_tools.list_estimates),
                description="List estimates. Args: client_id (optional), updated_since (optional)"
            ),
            Tool(
                name="get_estimate",
                func=self._wrap_async(self.harvest_tools.get_estimate),
                description="Get a specific estimate. Args: estimate_id"
            ),
            Tool(
                name="create_estimate",
                func=self._wrap_async(self.harvest_tools.create_estimate),
                description="Create an estimate. Args: client_id, issue_date (YYYY-MM-DD), subject (optional), notes (optional)"
            ),
            Tool(
                name="update_estimate",
                func=self._wrap_async(self.harvest_tools.update_estimate),
                description="Update an estimate. Args: estimate_id, subject (optional), notes (optional), issue_date (optional)"
            ),
        ])
        
        # Company Info Tool (1 tool)
        self.tools.append(
            Tool(
                name="get_company_info",
                func=self._wrap_async(self.harvest_tools.get_company_info),
                description="Get company information. No args required."
            )
        )
        
        logger.info(f"✅ Created {len(self.tools)} LangChain tools from Harvest MCP")
    
    def _wrap_async(self, func: Callable) -> Callable:
        """
        Wrap async function to be compatible with LangChain Tool.
        LangChain tools expect sync functions, so we need to handle async.
        """
        import asyncio
        
        def wrapper(*args, **kwargs):
            """Wrapper that runs async function in event loop"""
            try:
                # Try to get existing event loop
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # If loop is running, create a task
                    import nest_asyncio
                    nest_asyncio.apply()
                    return loop.run_until_complete(func(*args, **kwargs))
                else:
                    # If no loop running, run directly
                    return loop.run_until_complete(func(*args, **kwargs))
            except RuntimeError:
                # No event loop, create new one
                return asyncio.run(func(*args, **kwargs))
        
        return wrapper
    
    def get_tools(self) -> List[Tool]:
        """Get all LangChain tools"""
        return self.tools
    
    def get_tool_names(self) -> List[str]:
        """Get list of tool names"""
        return [tool.name for tool in self.tools]
    
    def get_tool_by_name(self, name: str) -> Optional[Tool]:
        """Get a specific tool by name"""
        for tool in self.tools:
            if tool.name == name:
                return tool
        return None
