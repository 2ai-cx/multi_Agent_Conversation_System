"""
LangChain agent running inside Temporal activities.
Combines LangChain's agent capabilities with Temporal's reliability.
"""

from typing import Any, Dict, List, Optional
from temporalio import activity
from langchain.agents import create_react_agent, AgentExecutor
from langchain_core.prompts import PromptTemplate
from langchain_core.memory import ConversationBufferMemory
from llm.langchain_wrapper import CustomLangChainLLM
from llm.langchain_mem0_bridge import Mem0LangChainMemory
from llm.memory import LLMMemoryManager
from llm.config import LLMConfig
from agents.langchain_tools import HarvestLangChainTools
from monitoring.langchain_callbacks import ProductionCallbackHandler
import logging

logger = logging.getLogger(__name__)


# ReAct prompt template for Harvest timesheet agent
REACT_PROMPT = PromptTemplate.from_template("""
You are a Harvest Timesheet Assistant with access to 51 Harvest API tools.

Your goal is to help users manage their timesheets by:
- Retrieving time entries
- Creating new time entries
- Updating existing entries
- Getting project and task information
- Generating reports

You have access to the following tools:

{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Context from previous conversations:
{context}

Begin!

Question: {input}
Thought: {agent_scratchpad}
""")


@activity.defn
async def langchain_harvest_agent_activity(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    LangChain ReAct agent for Harvest operations running inside Temporal activity.
    
    This combines:
    - LangChain's agent reasoning (ReAct pattern)
    - Temporal's reliability (retries, timeouts, durability)
    - Mem0's memory (context retrieval)
    - Custom LLM client (rate limiting, caching)
    
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
        
        logger.info(f"🤖 LangChain agent started for tenant={tenant_id}, user={user_id}")
        logger.info(f"📝 Message: {message[:100]}...")
        
        # Initialize LangChain LLM wrapper
        llm = CustomLangChainLLM(config=config, tenant_id=tenant_id)
        
        # Initialize Mem0 memory manager
        mem0_manager = LLMMemoryManager(config or LLMConfig())
        
        # Create Mem0-LangChain memory bridge
        memory = Mem0LangChainMemory(
            mem0_manager=mem0_manager,
            tenant_id=tenant_id,
            user_id=user_id,
            k=10
        )
        
        # Create LangChain tools from Harvest MCP
        harvest_langchain_tools = HarvestLangChainTools(harvest_tools)
        tools = harvest_langchain_tools.get_tools()
        
        logger.info(f"🔧 Loaded {len(tools)} LangChain tools")
        
        # Create ReAct agent
        agent = create_react_agent(
            llm=llm,
            tools=tools,
            prompt=REACT_PROMPT
        )
        
        # Create callback handler for monitoring
        callback = ProductionCallbackHandler(
            tenant_id=tenant_id,
            user_id=user_id
        )
        
        # Create agent executor
        agent_executor = AgentExecutor(
            agent=agent,
            tools=tools,
            memory=memory,
            callbacks=[callback],
            verbose=True,
            max_iterations=5,
            handle_parsing_errors=True,
            return_intermediate_steps=True
        )
        
        # Execute agent
        logger.info("🚀 Executing LangChain agent...")
        result = await agent_executor.ainvoke({"input": message})
        
        # Extract tools used from intermediate steps
        tools_used = []
        if "intermediate_steps" in result:
            for step in result["intermediate_steps"]:
                if len(step) >= 1:
                    action = step[0]
                    tools_used.append(action.tool)
        
        logger.info(f"✅ Agent completed successfully")
        logger.info(f"🔧 Tools used: {tools_used}")
        
        # Get metrics from callback
        metrics = callback.get_metrics()
        
        return {
            "output": result.get("output", ""),
            "success": True,
            "tools_used": tools_used,
            "metrics": metrics,
            "error": None
        }
        
    except Exception as e:
        logger.error(f"❌ LangChain agent failed: {e}")
        import traceback
        traceback.print_exc()
        
        return {
            "output": "",
            "success": False,
            "tools_used": [],
            "metrics": {},
            "error": str(e)
        }


@activity.defn
async def langchain_refinement_agent_activity(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    LangChain agent for refining and improving responses.
    
    Args:
        input_data: Dict containing:
            - raw_response: Raw response from harvest agent
            - user_message: Original user message
            - tenant_id: Tenant identifier
            - user_id: User identifier
            - config: Optional LLM config
    
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
        
        # Initialize LangChain LLM
        llm = CustomLangChainLLM(config=config, tenant_id=tenant_id)
        
        # Create refinement prompt
        refinement_prompt = f"""You are a Response Refinement Specialist.

Your task is to improve the raw response from the Harvest agent to make it:
- Clear and easy to understand
- Well-formatted
- Professional but friendly
- Actionable

Original user message:
{user_message}

Raw response from Harvest agent:
{raw_response}

Provide a refined, improved version of this response.
Keep all important information but make it more user-friendly.

Refined response:"""
        
        # Generate refined response
        callback = ProductionCallbackHandler(tenant_id=tenant_id, user_id=user_id)
        refined = await llm._acall(refinement_prompt, run_manager=None)
        
        logger.info(f"✅ Refinement completed")
        
        return {
            "refined_response": refined,
            "success": True,
            "error": None
        }
        
    except Exception as e:
        logger.error(f"❌ Refinement agent failed: {e}")
        return {
            "refined_response": raw_response,  # Fallback to raw response
            "success": False,
            "error": str(e)
        }


@activity.defn
async def langchain_quality_agent_activity(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    LangChain agent for quality checking responses.
    
    Args:
        input_data: Dict containing:
            - response: Response to check
            - user_message: Original user message
            - tenant_id: Tenant identifier
            - user_id: User identifier
            - config: Optional LLM config
    
    Returns:
        Dict with quality score and feedback
    """
    try:
        response = input_data["response"]
        user_message = input_data["user_message"]
        tenant_id = input_data["tenant_id"]
        user_id = input_data["user_id"]
        config = input_data.get("config")
        
        logger.info(f"🔍 Quality check started")
        
        # Initialize LangChain LLM
        llm = CustomLangChainLLM(config=config, tenant_id=tenant_id)
        
        # Create quality check prompt
        quality_prompt = f"""You are a Quality Assurance Specialist.

Evaluate the following response for quality on a scale of 1-10.

Original user message:
{user_message}

Response to evaluate:
{response}

Evaluate based on:
1. Accuracy - Does it answer the question correctly?
2. Completeness - Is all necessary information included?
3. Clarity - Is it easy to understand?
4. Professionalism - Is the tone appropriate?

Provide your evaluation in this format:
Score: [1-10]
Feedback: [Brief explanation]
Pass: [YES/NO - Pass if score >= 7]

Evaluation:"""
        
        # Generate quality evaluation
        evaluation = await llm._acall(quality_prompt, run_manager=None)
        
        # Parse evaluation
        score = 8  # Default
        feedback = evaluation
        passed = True
        
        if "Score:" in evaluation:
            try:
                score_line = [line for line in evaluation.split("\n") if "Score:" in line][0]
                score = int(score_line.split(":")[1].strip().split()[0])
                passed = score >= 7
            except:
                pass
        
        logger.info(f"✅ Quality check completed: Score={score}, Pass={passed}")
        
        return {
            "score": score,
            "feedback": feedback,
            "passed": passed,
            "success": True,
            "error": None
        }
        
    except Exception as e:
        logger.error(f"❌ Quality check failed: {e}")
        return {
            "score": 5,
            "feedback": str(e),
            "passed": False,
            "success": False,
            "error": str(e)
        }
