"""
Microsoft Agent Framework agents running inside Temporal activities.
Combines Agent Framework's capabilities with Temporal's reliability.
"""

from typing import Any, Dict, List, Optional
from temporalio import activity
from agent_framework.core import Agent, AgentThread, ChatMessage
from llm.agent_framework_connector import CustomAgentFrameworkLLM
from llm.agent_framework_mem0_bridge import Mem0AgentFrameworkMemory
from llm.memory import LLMMemoryManager
from llm.config import LLMConfig
from agents.agent_framework_mcp_tools import HarvestAgentFrameworkTools
import logging

logger = logging.getLogger(__name__)


@activity.defn
async def agent_framework_harvest_activity(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Microsoft Agent Framework agent for Harvest operations running inside Temporal activity.
    
    This combines:
    - Agent Framework's agent orchestration
    - Temporal's reliability (retries, timeouts, durability)
    - Mem0's memory (context retrieval)
    - Custom LLM client (rate limiting, caching)
    - Native MCP support
    
    Args:
        input_data: Dict containing:
            - message: User's message/query
            - tenant_id: Tenant identifier
            - user_id: User identifier
            - harvest_tools: Harvest API tools object
            - config: Optional LLM config
    
    Returns:
        Dict with:
            - output: Agent's response
            - success: Boolean success flag
            - tools_used: List of tools called
            - error: Error message if failed
    """
    try:
        message = input_data["message"]
        tenant_id = input_data["tenant_id"]
        user_id = input_data["user_id"]
        harvest_tools = input_data["harvest_tools"]
        config = input_data.get("config")
        
        logger.info(f"🤖 Agent Framework agent started for tenant={tenant_id}, user={user_id}")
        logger.info(f"📝 Message: {message[:100]}...")
        
        # Initialize custom LLM connector
        llm = CustomAgentFrameworkLLM(config=config, tenant_id=tenant_id)
        
        # Initialize Mem0 memory manager
        mem0_manager = LLMMemoryManager(config or LLMConfig())
        
        # Create Mem0 memory wrapper
        memory = Mem0AgentFrameworkMemory(
            mem0_manager=mem0_manager,
            tenant_id=tenant_id,
            user_id=user_id,
            k=10
        )
        
        # Create Harvest tools
        tools_wrapper = HarvestAgentFrameworkTools(harvest_tools)
        tools = tools_wrapper.get_tools()
        
        logger.info(f"🔧 Loaded {len(tools)} tools")
        
        # Retrieve context from Mem0
        context_memories = memory.retrieve(message)
        context_text = "\n".join(context_memories) if context_memories else ""
        
        # Create agent with system prompt
        system_prompt = f"""You are a Harvest Timesheet Assistant with access to Harvest API tools.

Your goal is to help users manage their timesheets by:
- Retrieving time entries
- Creating new time entries
- Updating existing entries
- Getting project and task information
- Generating reports

Context from previous conversations:
{context_text}

Use the available tools to complete the user's request."""
        
        # Create agent
        agent = Agent(
            name="HarvestAgent",
            model=llm,
            instructions=system_prompt,
            tools=tools
        )
        
        # Create agent thread for state management
        thread = AgentThread()
        
        # Add user message to thread
        thread.add_message(ChatMessage(role="user", content=message))
        
        # Run agent
        logger.info("🚀 Executing Agent Framework agent...")
        response = await agent.run(thread=thread)
        
        # Extract response
        output = response.messages[-1].content if response.messages else ""
        
        # Track tools used
        tools_used = []
        for msg in response.messages:
            if hasattr(msg, "tool_calls") and msg.tool_calls:
                for tool_call in msg.tool_calls:
                    tools_used.append(tool_call.function.name)
        
        # Save conversation to Mem0
        memory.add(user_message=message, ai_response=output)
        
        logger.info(f"✅ Agent completed successfully")
        logger.info(f"🔧 Tools used: {tools_used}")
        
        return {
            "output": output,
            "success": True,
            "tools_used": tools_used,
            "error": None
        }
        
    except Exception as e:
        logger.error(f"❌ Agent Framework agent failed: {e}")
        import traceback
        traceback.print_exc()
        
        return {
            "output": "",
            "success": False,
            "tools_used": [],
            "error": str(e)
        }


@activity.defn
async def agent_framework_workflow_activity(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Agent Framework workflow for multi-agent orchestration.
    
    Uses Agent Framework's workflow capabilities to coordinate multiple agents.
    
    Args:
        input_data: Dict containing workflow configuration
        
    Returns:
        Dict with workflow results
    """
    try:
        from agent_framework.core import Workflow, WorkflowNode
        
        message = input_data["message"]
        tenant_id = input_data["tenant_id"]
        user_id = input_data["user_id"]
        
        logger.info(f"🔄 Agent Framework workflow started")
        
        # Create workflow
        workflow = Workflow(name="HarvestWorkflow")
        
        # Define workflow nodes (agents)
        # Node 1: Planner agent
        planner_node = WorkflowNode(
            name="planner",
            agent=None,  # Would create planner agent here
            next_nodes=["executor"]
        )
        
        # Node 2: Executor agent
        executor_node = WorkflowNode(
            name="executor",
            agent=None,  # Would create executor agent here
            next_nodes=["quality"]
        )
        
        # Node 3: Quality agent
        quality_node = WorkflowNode(
            name="quality",
            agent=None,  # Would create quality agent here
            next_nodes=[]
        )
        
        # Add nodes to workflow
        workflow.add_node(planner_node)
        workflow.add_node(executor_node)
        workflow.add_node(quality_node)
        
        # Execute workflow
        result = await workflow.run(input_message=message)
        
        logger.info(f"✅ Workflow completed")
        
        return {
            "output": result.output,
            "success": True,
            "error": None
        }
        
    except Exception as e:
        logger.error(f"❌ Workflow failed: {e}")
        return {
            "output": "",
            "success": False,
            "error": str(e)
        }


@activity.defn
async def agent_framework_refinement_activity(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Agent Framework refinement agent.
    
    Args:
        input_data: Dict with raw_response, user_message, tenant_id, user_id
        
    Returns:
        Dict with refined response
    """
    try:
        raw_response = input_data["raw_response"]
        user_message = input_data["user_message"]
        tenant_id = input_data["tenant_id"]
        user_id = input_data["user_id"]
        config = input_data.get("config")
        
        logger.info(f"✨ Refinement agent started")
        
        # Initialize LLM
        llm = CustomAgentFrameworkLLM(config=config, tenant_id=tenant_id)
        
        # Create refinement agent
        refinement_prompt = f"""You are a Response Refinement Specialist.

Your task is to improve the raw response to make it:
- Clear and easy to understand
- Well-formatted
- Professional but friendly
- Actionable

Original user message:
{user_message}

Raw response:
{raw_response}

Provide a refined, improved version of this response."""
        
        agent = Agent(
            name="RefinementAgent",
            model=llm,
            instructions=refinement_prompt
        )
        
        thread = AgentThread()
        thread.add_message(ChatMessage(role="user", content="Please refine the response."))
        
        response = await agent.run(thread=thread)
        refined = response.messages[-1].content if response.messages else raw_response
        
        logger.info(f"✅ Refinement completed")
        
        return {
            "refined_response": refined,
            "success": True,
            "error": None
        }
        
    except Exception as e:
        logger.error(f"❌ Refinement failed: {e}")
        return {
            "refined_response": raw_response,
            "success": False,
            "error": str(e)
        }
