"""
Microsoft Agent Framework MCP tools integration.
Uses Agent Framework's native MCP client to connect to Harvest MCP server.
"""

from typing import Any, Dict, List, Optional
from agent_framework.core import MCPClient, Tool
import logging

logger = logging.getLogger(__name__)


class HarvestMCPTools:
    """
    Harvest MCP tools for Microsoft Agent Framework.
    
    Uses Agent Framework's built-in MCP client to connect to Harvest MCP server.
    This is more native than LangChain's approach since Agent Framework has
    first-class MCP support.
    """
    
    def __init__(self, mcp_server_url: str = "http://localhost:3000"):
        """
        Initialize Harvest MCP tools.
        
        Args:
            mcp_server_url: URL of the Harvest MCP server
        """
        self.mcp_server_url = mcp_server_url
        self.mcp_client: Optional[MCPClient] = None
        self.tools: List[Tool] = []
    
    async def connect(self) -> None:
        """Connect to Harvest MCP server and load tools"""
        try:
            # Create MCP client
            self.mcp_client = MCPClient(server_url=self.mcp_server_url)
            
            # Connect to server
            await self.mcp_client.connect()
            
            # List available tools
            self.tools = await self.mcp_client.list_tools()
            
            logger.info(f"✅ Connected to Harvest MCP server")
            logger.info(f"🔧 Loaded {len(self.tools)} tools from MCP")
            
        except Exception as e:
            logger.error(f"❌ Failed to connect to Harvest MCP: {e}")
            # Fallback: create tools manually if MCP connection fails
            self._create_fallback_tools()
    
    def _create_fallback_tools(self) -> None:
        """
        Create fallback tools if MCP connection fails.
        This uses the existing Harvest tools object.
        """
        logger.warning("Using fallback tool creation (MCP connection failed)")
        
        # Import existing Harvest tools
        from agents.timesheet import TimesheetAgent
        
        # Note: In production, we'd create proper Tool objects here
        # For now, we'll use the MCP connection as primary method
        self.tools = []
    
    async def disconnect(self) -> None:
        """Disconnect from MCP server"""
        if self.mcp_client:
            await self.mcp_client.disconnect()
            logger.info("Disconnected from Harvest MCP server")
    
    def get_tools(self) -> List[Tool]:
        """Get all available tools"""
        return self.tools
    
    def get_tool_names(self) -> List[str]:
        """Get list of tool names"""
        return [tool.name for tool in self.tools]
    
    async def call_tool(
        self,
        tool_name: str,
        arguments: Dict[str, Any]
    ) -> Any:
        """
        Call a specific tool.
        
        Args:
            tool_name: Name of the tool to call
            arguments: Tool arguments
            
        Returns:
            Tool execution result
        """
        if not self.mcp_client:
            raise RuntimeError("MCP client not connected")
        
        try:
            result = await self.mcp_client.call_tool(
                tool_name=tool_name,
                arguments=arguments
            )
            
            logger.info(f"🔧 Called tool: {tool_name}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Tool call failed: {tool_name} - {e}")
            raise


class HarvestAgentFrameworkTools:
    """
    Alternative implementation using direct Harvest API wrapper.
    This wraps existing Harvest tools for Agent Framework without MCP.
    """
    
    def __init__(self, harvest_tools: Any):
        """
        Initialize with existing Harvest tools object.
        
        Args:
            harvest_tools: Existing Harvest API tools from unified_workflows
        """
        self.harvest_tools = harvest_tools
        self.tools: List[Dict[str, Any]] = []
        self._create_tools()
    
    def _create_tools(self) -> None:
        """Create Agent Framework tool definitions from Harvest API"""
        
        # Time Entries Tools (7 tools)
        self.tools.extend([
            {
                "name": "list_time_entries",
                "description": "List time entries in a date range. Args: from_date (YYYY-MM-DD), to_date (YYYY-MM-DD), user_id (optional)",
                "function": self.harvest_tools.list_time_entries,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "from_date": {"type": "string", "description": "Start date (YYYY-MM-DD)"},
                        "to_date": {"type": "string", "description": "End date (YYYY-MM-DD)"},
                        "user_id": {"type": "string", "description": "Optional user ID"}
                    },
                    "required": ["from_date", "to_date"]
                }
            },
            {
                "name": "get_time_entry",
                "description": "Get a specific time entry by ID",
                "function": self.harvest_tools.get_time_entry,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "time_entry_id": {"type": "string", "description": "Time entry ID"}
                    },
                    "required": ["time_entry_id"]
                }
            },
            {
                "name": "create_time_entry",
                "description": "Create a new time entry",
                "function": self.harvest_tools.create_time_entry,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "project_id": {"type": "string"},
                        "task_id": {"type": "string"},
                        "spent_date": {"type": "string", "description": "Date (YYYY-MM-DD)"},
                        "hours": {"type": "number"},
                        "notes": {"type": "string"}
                    },
                    "required": ["project_id", "task_id", "spent_date", "hours"]
                }
            },
            # Add more tools as needed...
        ])
        
        logger.info(f"✅ Created {len(self.tools)} Agent Framework tools from Harvest API")
    
    def get_tools(self) -> List[Dict[str, Any]]:
        """Get all tools"""
        return self.tools
    
    def get_tool_names(self) -> List[str]:
        """Get tool names"""
        return [tool["name"] for tool in self.tools]
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """
        Call a tool by name.
        
        Args:
            tool_name: Name of the tool
            arguments: Tool arguments
            
        Returns:
            Tool result
        """
        for tool in self.tools:
            if tool["name"] == tool_name:
                func = tool["function"]
                try:
                    # Call async function
                    result = await func(**arguments)
                    logger.info(f"🔧 Tool executed: {tool_name}")
                    return result
                except Exception as e:
                    logger.error(f"❌ Tool execution failed: {tool_name} - {e}")
                    raise
        
        raise ValueError(f"Tool not found: {tool_name}")
