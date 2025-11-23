#!/usr/bin/env python3
"""
Unified Temporal Workflows Module - NO FASTAPI
Combines timesheet reminders + AI conversations workflows
This module contains ONLY workflow and activity definitions.
FastAPI is imported in the server module to avoid workflow sandbox restrictions.

Features:
- Timesheet reminder workflows (from temporal_workflows.py)
- AI conversation workflows (from conversation_workflows.py)
- Activities for timesheet data and SMS sending
- LangChain agent integration with Harvest tools
- Cross-platform conversation handling
"""

import os
import logging
import functools
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime, timedelta

# Temporal imports ONLY
from temporalio import workflow, activity
from temporalio.common import RetryPolicy

# Import only types needed for function signatures (no runtime imports)
from agent_governance import PrivilegeLevel, ActionType

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Opik tracing (completely lazy to avoid module-level HTTP imports)
def opik_trace(name: str):
    """Opik tracing decorator with completely lazy import"""
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Import opik only when the function is actually called
            try:
                import opik as _opik_module
                # Apply opik tracking
                tracked_func = _opik_module.track(name=name)(func)
                return await tracked_func(*args, **kwargs)
            except ImportError:
                # Opik not available, just run the function
                return await func(*args, **kwargs)
            except Exception:
                # Any other opik error, just run the function
                return await func(*args, **kwargs)
        return wrapper
    return decorator

# =============================================================================
# DATA MODELS (Combined from both modules)
# =============================================================================

@dataclass
class TimesheetReminderRequest:
    """Request for timesheet reminder (from temporal_workflows.py)"""
    user_id: str
    user_name: str
    phone_number: Optional[str] = None  # FIXED: Make optional to handle None values
    harvest_access_token: Optional[str] = None  # FIXED: Make optional to handle None values
    harvest_account: Optional[str] = None  # FIXED: Make optional to handle None values
    endpoint: Optional[str] = None  # FIXED: Make optional to handle None values

@dataclass
class TimesheetReminderResponse:
    """Response from timesheet reminder (from temporal_workflows.py)"""
    user: str
    status: str
    sms_sid: Optional[str] = None
    timestamp: Optional[str] = None
    error: Optional[str] = None

@dataclass
class ConversationRequest:
    """Request for conversation handling (from conversation_workflows.py)"""
    user_id: str
    message: str
    platform: str  # 'sms', 'email', or 'whatsapp'
    conversation_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class AIResponse:
    """AI response data (from conversation_workflows.py)"""
    response: str
    conversation_id: str
    platform: str
    timestamp: str
    metadata: Optional[Dict[str, Any]] = None

# =============================================================================
# GLOBAL WORKER INSTANCE (Shared between modules)
# =============================================================================

class UnifiedTemporalWorker:
    """Unified worker instance for both timesheet and conversation functionality"""
    def __init__(self):
        # Timesheet worker attributes
        self.users = []
        self.timesheet_agent_url = ""
        self.max_retries = 3
        self.timeout = 30
        
        # Conversation worker attributes  
        self.supabase_client = None
        self.llm = None
        self.openai_api_key = ""
        self.supabase_url = ""
        self.supabase_key = ""
        self.twilio_client = None
        
        # Shared attributes
        self.opik_enabled = False
        
        logger.info("🚀 Unified Temporal Worker initialized")

# Global worker instance
worker = UnifiedTemporalWorker()

# =============================================================================
# TIMESHEET ACTIVITIES (from temporal_workflows.py)
# =============================================================================

@activity.defn
@opik_trace("get_timesheet_data")
async def get_timesheet_data(request: TimesheetReminderRequest) -> Dict[str, Any]:
    """
    Get timesheet data for a user (STRICT ARCHITECTURE: via KrakenD Gateway)
    Enhanced with Harvest MCP direct integration
    """
    # OPIK tracing configuration
    opik_enabled = os.getenv("OPIK_ENABLED", "false").lower() == "true"
    
    # KrakenD Gateway configuration
    krakend_gateway_url = os.getenv(
        'KRAKEND_GATEWAY_URL',
        'https://krakend-gateway.kindcoast-5a2a34c6.australiaeast.azurecontainerapps.io'
    )
    
    if opik_enabled:
        try:
            import opik
            opik.opik_context.update_current_trace(
                tags=["timesheet_data", "api_call", "krakend_gateway"],
                metadata={
                    "user_id": request.user_id,
                    "user_name": request.user_name,
                    "gateway_url": krakend_gateway_url
                }
            )
        except ImportError:
            logger.debug("📊 Opik not available - context not updated")
        except Exception as opik_error:
            logger.warning(f"⚠️ Opik context update failed: {opik_error}")
    
    try:
        # Import requests inside activity to avoid workflow sandbox restrictions
        import requests
        from datetime import datetime, timedelta
        
        # ARCHITECTURE COMPLIANCE: Use KrakenD Gateway (NEVER direct service calls)
        krakend_url = os.getenv('KRAKEND_GATEWAY_URL', 'https://krakend-gateway.kindcoast-5a2a34c6.australiaeast.azurecontainerapps.io')
        
        # Use new unified routing system only
        logger.info(f"📊 Using unified routing for {request.user_name}")
        
        # Get user-specific Harvest credentials from Supabase (DATABASE-DRIVEN: No hardcoded logic)
        if not worker.supabase_client:
            raise Exception("Supabase client not available for credential lookup")
        
        # Query user credentials and timezone from database
        user_profile = worker.supabase_client.table('users').select('id,full_name,harvest_account_id,harvest_access_token,harvest_user_id,timezone').eq('id', request.user_id).execute()
        
        if not user_profile.data:
            raise Exception(f"User {request.user_id} not found in database")
        
        user_data = user_profile.data[0]
        harvest_account = user_data.get('harvest_account_id')
        harvest_token = user_data.get('harvest_access_token')
        harvest_user_id = user_data.get('harvest_user_id')
        user_timezone = user_data.get('timezone', 'UTC')
        
        logger.info(f"🔍 Retrieved credentials for user: {user_data.get('full_name', request.user_id)} (Timezone: {user_timezone})")
        
        # Validate credentials are not None
        if not harvest_account or not harvest_token:
            logger.error(f"❌ Missing Harvest credentials for {request.user_name}: account={harvest_account}, token={'***' if harvest_token else None}")
            raise Exception(f"Missing Harvest credentials for {request.user_name}")
        
        # Calculate current week date range in user's timezone
        from zoneinfo import ZoneInfo
        
        # Get current time in user's timezone
        user_tz = ZoneInfo(user_timezone)
        today = datetime.now(user_tz)
        
        # Calculate week start (Monday) and end (Sunday) in user's timezone
        week_start = (today - timedelta(days=today.weekday())).strftime('%Y-%m-%d')
        week_end = (today + timedelta(days=6-today.weekday())).strftime('%Y-%m-%d')
        
        # Call Harvest MCP (Smart Routing: Direct internal, KrakenD for external)
        use_direct_internal = os.getenv('USE_DIRECT_INTERNAL_CALLS', 'true').lower() == 'true'
        
        if use_direct_internal:
            # Direct internal call to MCP server
            harvest_mcp_url = os.getenv('HARVEST_MCP_INTERNAL_URL', 'http://harvest-mcp.internal.kindcoast-5a2a34c6.australiaeast.azurecontainerapps.io')
            url = f"{harvest_mcp_url}/api/list_time_entries"
            logger.info("🔗 Direct internal MCP call: list_time_entries")
        else:
            # External call via KrakenD Gateway
            krakend_url = os.getenv('KRAKEND_GATEWAY_URL', 'https://krakend-gateway.kindcoast-5a2a34c6.australiaeast.azurecontainerapps.io')
            url = f"{krakend_url}/harvest/api/list_time_entries"
            logger.info("🌐 External MCP call via KrakenD: list_time_entries")
        payload = {
            "harvest_account": harvest_account,
            "harvest_token": harvest_token,
            "from_date": week_start,
            "to_date": week_end,
            "user_id": harvest_user_id
        }
        
        # Import timeout functions inside activity to avoid sandbox restrictions
        from timeout_wrapper import create_requests_session, APITimeoutConfig
        
        # Use configured session with timeout protection
        session = create_requests_session(timeout=APITimeoutConfig.HARVEST_MCP_TIMEOUT)
        response = session.post(url, json=payload)
        
        if response.status_code == 200:
            mcp_data = response.json()
            time_entries = mcp_data.get('time_entries', [])
            
            # Calculate total hours
            total_hours = sum(entry.get('hours', 0) for entry in time_entries)
            
            # Format response
            return {
                "status": "success",
                "source": "harvest_mcp_direct",  
                "total_hours": total_hours,
                "entries_count": len(time_entries),
                "week_start": week_start,
                "week_end": week_end,
                "time_entries": time_entries,
                "user_full_name": user_data.get('full_name', request.user_name),  
                "timezone": user_timezone  
            }
        else:
            logger.error(f"❌ MCP API error: HTTP {response.status_code} - {response.text}")
            raise Exception(f"MCP API error: HTTP {response.status_code}")
                
    except Exception as e:
        logger.error(f"❌ Failed to get timesheet data: {e}")
        return {
            'source': 'error',
            'error': str(e),
            'sms_content': f"Error retrieving timesheet for {request.user_name}: {str(e)}"
        }

@activity.defn
@opik_trace("send_sms_reminder")
async def send_sms_reminder(phone_number: str, message: str, user_name: str, agent_id: str = "sms_agent", agent_privilege: PrivilegeLevel = PrivilegeLevel.LIMITED_WRITE) -> Dict[str, Any]:
    """Send SMS reminder using Twilio"""
    try:
        # Import timeout wrapper and governance inside activity to avoid workflow sandbox restrictions
        from timeout_wrapper import twilio_timeout
        from agent_governance import limited_write_tool, ActionType, PrivilegeLevel
        
        # Apply governance check
        governance_check = limited_write_tool(ActionType.SEND_MESSAGE)
        
        # Import Twilio inside activity to avoid workflow sandbox restrictions
        from twilio.rest import Client
        
        # Get Twilio credentials from environment
        account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        from_number = os.getenv('TWILIO_PHONE_NUMBER')
        
        # DEBUG: Log what values we actually got
        logger.info(f"🔍 DEBUG - Twilio credentials loaded:")
        logger.info(f"  - Account SID: {account_sid[:10]}..." if account_sid else "  - Account SID: None")
        logger.info(f"  - Auth Token: {'***' if auth_token else 'None'}")
        logger.info(f"  - From Number: {from_number}")
        
        if not all([account_sid, auth_token, from_number]):
            raise Exception(f"Missing Twilio credentials - SID: {bool(account_sid)}, Token: {bool(auth_token)}, Number: {bool(from_number)}")
        
        # Create Twilio client
        client = Client(account_sid, auth_token)
        
        # Send SMS
        sms_message = client.messages.create(
            body=message,
            from_=from_number,
            to=phone_number
        )
        
        logger.info(f"✅ SMS sent to {user_name} ({phone_number}): {sms_message.sid}")
        
        return {
            'status': 'success',
            'sms_sid': sms_message.sid,
            'timestamp': datetime.utcnow().isoformat()  # FIXED: Use UTC time in activities
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to send SMS to {user_name}: {e}")
        return {
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()  # FIXED: Use UTC time in activities
        }

@activity.defn
async def add_joke_to_reminder_activity(timesheet_content: str, user_name: str, user_id: str) -> str:
    """
    Activity to add contextual joke to timesheet reminder
    
    Args:
        timesheet_content: Original timesheet content
        user_name: User's name
        user_id: User ID for tracking
    
    Returns:
        Enhanced content with joke
    """
    try:
        logger.info(f"🎭 Generating joke for {user_name}'s reminder")

        # Import inside activity to avoid workflow sandbox issues
        from joke_generator import add_joke_to_timesheet_response

        # Use global UnifiedTemporalWorker instance (same one configured in unified_server)
        global worker
        if not worker:
            logger.warning("⚠️ Global worker instance is not available, skipping joke")
            return timesheet_content

        # Ensure LLM client is available
        llm_client = getattr(worker, "llm_client", None)
        llm_config = getattr(worker, "llm_config", None)
        if not llm_client or not llm_config:
            logger.warning("⚠️ Worker LLM client/config missing, skipping joke generation")
            return timesheet_content

        # Fetch user's interests from Supabase for personalization
        user_interests = []
        try:
            if worker.supabase_client:
                user_profile = worker.supabase_client.table('users').select('interests').eq('id', user_id).execute()
                if user_profile.data and user_profile.data[0].get('interests'):
                    user_interests = user_profile.data[0]['interests']
                    logger.info(f"📋 User interests: {user_interests}")
        except Exception as e:
            logger.warning(f"⚠️ Could not fetch user interests: {e}")

        # Add joke using LLM client with personalization
        enhanced_content = await add_joke_to_timesheet_response(
            timesheet_result=timesheet_content,
            user_name=user_name,
            user_id=user_id,
            llm_client=llm_client,
            llm_config=llm_config,
            user_interests=user_interests,
            humor_style="witty",
        )

        logger.info(f"✅ Joke added successfully for {user_name}")
        return enhanced_content

    except Exception as e:
        logger.error(f"❌ Failed to add joke: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        # Return original content if joke generation fails
        return timesheet_content

# =============================================================================
# TIMESHEET WORKFLOWS (from temporal_workflows.py)
# =============================================================================

@workflow.defn
class TimesheetReminderWorkflow:
    """Individual timesheet reminder workflow"""
    
    @workflow.run
    async def run(self, request: TimesheetReminderRequest) -> TimesheetReminderResponse:
        """Execute timesheet reminder workflow"""
        try:
            logger.info(f"🚀 Starting timesheet reminder for {request.user_name}")
            
            # Step 1: Get timesheet data via KrakenD Gateway
            timesheet_data = await workflow.execute_activity(
                get_timesheet_data,
                request,
                start_to_close_timeout=timedelta(seconds=60),
                retry_policy=RetryPolicy(maximum_attempts=3)
            )
            
            # Step 2: Generate SMS content based on data source
            if timesheet_data.get('source') == 'harvest_mcp_direct':
                # Format MCP data into REMINDER content (focus on what's missing)
                total_hours = timesheet_data.get('total_hours', 0)
                entries_count = timesheet_data.get('entries_count', 0)
                week_start = timesheet_data.get('week_start', 'this week')
                week_end = timesheet_data.get('week_end', '')
                time_entries = timesheet_data.get('time_entries', [])
                target_hours = 40  # Standard work week
                
                # Calculate missing hours
                missing_hours = max(0, target_hours - total_hours)
                
                # Prepare data for unified formatter
                format_data = {
                    'user_name': timesheet_data.get('user_full_name', request.user_name),  # Use full name from database
                    'week_start': week_start,
                    'week_end': week_end,
                    'total_hours': total_hours,
                    'target_hours': target_hours,
                    'entries_count': entries_count,
                    'time_entries': time_entries,
                    'timezone': timesheet_data.get('timezone', 'UTC')  # Include timezone
                }
                
                # Use unified formatter for consistent messaging
                sms_content = format_check_timesheet_message(format_data, "reminder")
            else:
                # Handle error cases with unified formatter
                if timesheet_data.get('source') == 'error':
                    # Use unified formatter for error messages
                    error_data = {
                        'user_name': request.user_name,  # Use user_name from request (already contains full name)
                        'week_start': 'this week',
                        'week_end': '',
                        'total_hours': 0,
                        'target_hours': 40,
                        'entries_count': 0,
                        'time_entries': [],
                        'timezone': 'UTC'
                    }
                    error_message = format_check_timesheet_message(error_data, "error")
                    sms_content = f"{error_message}\n\n⚠️ **Technical Issue**: Unable to retrieve timesheet data. Please try again later or contact support."
                else:
                    # Use legacy format (has sms_content already)
                    sms_content = timesheet_data.get('sms_content', f"Timesheet reminder for {request.user_name}")
            
            # Step 2.5: Add joke to reminder (NEW!)
            try:
                # Add joke via activity
                sms_content = await workflow.execute_activity(
                    add_joke_to_reminder_activity,
                    args=[sms_content, request.user_name, request.user_id],
                    start_to_close_timeout=timedelta(seconds=10),
                    retry_policy=RetryPolicy(maximum_attempts=2)
                )
                logger.info(f"🎭 Added joke to reminder for {request.user_name}")
            except Exception as joke_error:
                # If joke generation fails, continue with original content
                logger.warning(f"⚠️ Failed to add joke to reminder: {joke_error}")
                # Continue with original sms_content
            
            # Step 3: Send SMS reminder
            sms_result = await workflow.execute_activity(
                send_sms_reminder,
                args=[request.phone_number, sms_content, request.user_name],
                start_to_close_timeout=timedelta(seconds=30),
                retry_policy=RetryPolicy(maximum_attempts=3)
            )
            
            logger.info(f"✅ Timesheet reminder completed for {request.user_name}")
            
            return TimesheetReminderResponse(
                user=request.user_name,
                status=sms_result['status'],
                sms_sid=sms_result.get('sms_sid'),
                timestamp=sms_result.get('timestamp')
            )
            
        except Exception as e:
            logger.error(f"❌ Timesheet reminder failed for {request.user_name}: {e}")
            return TimesheetReminderResponse(
                user=request.user_name,
                status='error',
                error=str(e),
                timestamp=workflow.now().isoformat()  # FIXED: Use workflow.now() instead of datetime.now()
            )

@workflow.defn
class DailyReminderScheduleWorkflow:
    """Daily batch reminder workflow for all users"""
    
    @workflow.run
    async def run(self, users_config: List[Dict[str, str]]) -> Dict[str, Any]:
        """Execute daily reminders for all configured users (FIXED: match original structure)"""
        workflow.logger.info("🔔 Starting daily reminder schedule workflow")
        
        results = []
        for user in users_config:
            try:
                # Create reminder request (FIXED: include endpoint field)
                reminder_request = TimesheetReminderRequest(
                    user_id=user['user_id'],
                    user_name=user['name'],
                    phone_number=user['phone_number'],
                    harvest_access_token=user.get('harvest_access_token', ''),
                    harvest_account=user.get('harvest_account', ''),
                    endpoint=user.get('endpoint', f"/check-timesheet-{user['user_id']}")
                )
                
                # Execute as child workflow for parallel processing (FIXED: use workflow.now())
                workflow_id = f"reminder_{user['user_id']}_{workflow.now().strftime('%Y%m%d')}"
                result = await workflow.execute_child_workflow(
                    TimesheetReminderWorkflow.run,
                    reminder_request,
                    id=workflow_id,
                    task_queue="timesheet-reminders"
                )
                
                results.append(result.__dict__)
                
            except Exception as e:
                workflow.logger.error(f"❌ Failed reminder workflow for {user['name']}: {e}")
                results.append({
                    "status": "error",
                    "user": user['name'], 
                    "error": str(e)
                })
        
        return {
            "status": "completed",
            "total_users": len(users_config),
            "successful": len([r for r in results if r.get('status') != 'error']),
            "failed": len([r for r in results if r.get('status') == 'error']),
            "results": results
        }

# =============================================================================
# CONVERSATION ACTIVITIES (from conversation_workflows.py)
# =============================================================================

@activity.defn
async def load_conversation_history(user_id: str, limit: int = 5, agent_id: str = "conversation_agent", agent_privilege: PrivilegeLevel = PrivilegeLevel.LIMITED_WRITE) -> List[Dict[str, Any]]:
    """Load conversation history from Supabase with timeout protection"""
    logger.info(f"Loading conversation history for {user_id} (limit: {limit})")
    
    def _load_from_supabase():
        """Internal function to load from Supabase"""
        return _supabase_query(user_id, limit)
    
    def _supabase_query(user_id: str, limit: int):
        """Execute Supabase query with error handling"""
        if not worker.supabase_client:
            logger.warning("⚠️ Supabase client not initialized - conversation history unavailable")
            return []
        
        try:
            # Get recent conversations in descending order, then reverse for chronological context
            response = worker.supabase_client.table('conversations').select('user_id,content,platform,message_type,created_at').eq('user_id', user_id).order('created_at', desc=True).limit(limit * 2).execute()
            
            if response.data:
                logger.info(f"✅ Loaded {len(response.data)} conversation messages for {user_id}")
                return response.data
            else:
                logger.info(f"📝 No conversation history found for {user_id}")
                return []
        except Exception as schema_error:
            logger.error(f"❌ Supabase schema error in load_conversation_history: {schema_error}")
            return []
    
    try:
        return _load_from_supabase()
    except Exception as e:
        logger.error(f"❌ Failed to load conversation history: {e}")
        logger.error(f"🔍 DEBUG: General error type: {type(e)}")
        return []

# Harvest MCP Tool Functions (Smart Routing: Direct Internal, KrakenD External)
async def call_harvest_mcp_tool(tool_name: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """Call Harvest MCP tool with smart routing and timeout protection"""
    
    def _make_harvest_call():
        """Internal function to make the actual HTTP call"""
        return _harvest_http_call(tool_name, payload)
    
    def _harvest_http_call(tool_name: str, payload: Dict[str, Any]):
        """Make HTTP call to Harvest MCP with timeout protection"""
        # Import timeout functions inside activity to avoid sandbox restrictions
        from timeout_wrapper import create_requests_session, APITimeoutConfig
        
        # Create session with timeout configuration
        session = create_requests_session(timeout=APITimeoutConfig.HARVEST_MCP_TIMEOUT)
        
        # SMART ROUTING: Direct internal calls, KrakenD for external
        use_direct_internal = os.getenv('USE_DIRECT_INTERNAL_CALLS', 'true').lower() == 'true'
        
        if use_direct_internal:
            # Direct internal call to MCP server (FASTER, MORE RELIABLE)
            harvest_mcp_url = os.getenv('HARVEST_MCP_INTERNAL_URL', 'http://harvest-mcp.internal.kindcoast-5a2a34c6.australiaeast.azurecontainerapps.io')
            url = f"{harvest_mcp_url}/api/{tool_name}"
            logger.info(f"🔗 Direct internal MCP call: {tool_name}")
        else:
            # External call via KrakenD Gateway (for external traffic)
            krakend_url = os.getenv('KRAKEND_GATEWAY_URL', 'https://krakend-gateway.kindcoast-5a2a34c6.australiaeast.azurecontainerapps.io')
            url = f"{krakend_url}/harvest/api/{tool_name}"
            logger.info(f"🌐 External MCP call via KrakenD: {tool_name}")
        
        try:
            response = session.post(url, json=payload)
            response.raise_for_status()  # Raises exception for bad status codes
            
            return response.json()
            
        except Exception as e:
            logger.error(f"❌ Harvest MCP HTTP call failed ({tool_name}): {e}")
            raise
        finally:
            session.close()
    
    # Execute the call (timeout wrapper will handle the timeout)
    return _make_harvest_call()

def format_check_timesheet_message(data: dict, message_type: str = "check") -> str:
    """
    SPECIFIC FORMATTER FOR SEARCH_MY_TIMESHEET TOOL ONLY
    Creates beautifully formatted timesheet messages with emojis and structure
    Used by: search_my_timesheet tool, timesheet reminders, error messages
    
    Args:
        data: Dictionary containing timesheet data
        message_type: "reminder", "check", "complete", "error"
    
    Returns:
        Formatted message string
    """
    try:
        # Extract data with safe defaults
        user_name = data.get('user_name', 'User')
        week_start = data.get('week_start', 'Unknown')
        week_end = data.get('week_end', 'Unknown')
        total_hours = data.get('total_hours', 0)
        target_hours = data.get('target_hours', 40)
        entries_count = data.get('entries_count', 0)
        time_entries = data.get('time_entries', [])
        timezone = data.get('timezone', 'UTC')  # Get timezone from data
        period_label = data.get('period_label', 'Week')  # Get period label (Week/Month/Year/Period)
        missing_hours = max(0, target_hours - total_hours)
        
        # Header with context
        if message_type == "reminder" and missing_hours > 0:
            header = f"⏰ **Timesheet Alert** • {user_name}"
            status_emoji = "🔴"
            status_text = f"Missing {missing_hours}h"
        elif message_type == "reminder" and missing_hours == 0:
            header = f"✅ **Timesheet Complete** • {user_name}"
            status_emoji = "🟢"
            status_text = "All caught up!"
        elif message_type == "check":
            header = f"📊 **Timesheet Summary** • {user_name}"
            status_emoji = "🔵" if total_hours > 0 else "⚪"
            status_text = f"{total_hours}h logged" if total_hours > 0 else "No hours logged"
        elif message_type == "error":
            header = f"⚠️ **Timesheet Error** • {user_name}"
            status_emoji = "🔴"
            status_text = "Service unavailable"
        else:
            header = f"📋 **Timesheet Update** • {user_name}"
            status_emoji = "🔵"
            status_text = "Status update"
        
        # Build message
        message = f"{header}\n"
        message += f"{'─' * 25}\n"
        message += f"📅 **{period_label}:** {week_start} → {week_end} ({timezone})\n"
        message += f"{status_emoji} **Status:** {status_text}\n"
        # Only show progress bar if target_hours is set (> 0)
        if target_hours > 0:
            message += f"⏱️ **Progress:** {total_hours}h / {target_hours}h ({int(total_hours/target_hours*100)}%)\n"
        else:
            message += f"⏱️ **Total Hours:** {total_hours}h\n"
        message += f"📝 **Entries:** {entries_count}\n\n"
        
        # Recent entries (if any) - entries are already sorted by caller
        if time_entries and len(time_entries) > 0:
            message += "**📋 Recent Activity:**\n"
            for i, entry in enumerate(time_entries[:3]):  # Show top 3 (already sorted by date)
                date = entry.get('spent_date', 'Unknown')
                hours = entry.get('hours', 0)
                project = entry.get('project', {}).get('name', 'Unknown')[:20]
                task = entry.get('task', {}).get('name', '')[:15]
                task_display = f" • {task}" if task else ""
                message += f"• **{date}:** {hours}h - {project}{task_display}\n"
            message += "\n"
        
        # Action section based on context
        if message_type == "reminder" and missing_hours > 0:
            message += "**🎯 Action Needed:**\n"
            if entries_count == 0:
                message += f"• Start logging your time entries\n"
                message += f"• Add {missing_hours}h to reach target\n"
            else:
                message += f"• Add {missing_hours}h more to complete week\n"
                message += f"• Update recent project work\n"
            message += "\n💬 Reply with questions or 'help' for commands"
        elif message_type == "reminder" and missing_hours == 0:
            message += "**🎉 Great Work!**\n"
            message += "• Timesheet is complete for this week\n"
            message += "• Keep up the excellent tracking!\n\n"
            message += "💬 Reply 'summary' for detailed breakdown"
        elif message_type == "check":
            if total_hours == 0:
                message += "**💡 Quick Actions:**\n"
                message += "• Reply 'log [hours] [project]' to add time\n"
                message += "• Reply 'projects' to see available projects\n"
            else:
                message += "**💡 Available Commands:**\n"
                message += "• 'log [hours] [project]' - Add time entry\n"
                message += "• 'summary' - Detailed breakdown\n"
            message += "• 'help' - See all commands"
        
        return message
        
    except Exception as e:
        # Fallback to simple format if formatter fails
        logger.error(f"❌ Formatter error: {e}")
        return f"📊 Timesheet for {data.get('user_name', 'User')}: {data.get('total_hours', 0)}h logged this week"

def create_harvest_tools(user_id: str):
    """Create LangChain tools for Harvest MCP integration"""
    from langchain_core.tools import tool
    from datetime import datetime, timedelta
    
    # Get user-specific Harvest credentials from Supabase database (DATABASE-DRIVEN: No hardcoded logic)
    harvest_account = None
    harvest_token = None
    harvest_user_id = None
    user_name = user_id
    user_timezone = 'UTC'  # Default timezone
    
    try:
        if worker.supabase_client:
            # Query user profile, credentials, and timezone from Supabase
            user_profile = worker.supabase_client.table('users').select('id,full_name,phone_number,harvest_account_id,harvest_access_token,harvest_user_id,timezone').eq('id', user_id).execute()
            if user_profile.data:
                user_data = user_profile.data[0]
                user_name = user_data.get('full_name', user_id)
                harvest_account = user_data.get('harvest_account_id')
                harvest_token = user_data.get('harvest_access_token')
                harvest_user_id = user_data.get('harvest_user_id')
                user_timezone = user_data.get('timezone', 'UTC')
                logger.info(f"🔍 Retrieved credentials for user: {user_name} (Timezone: {user_timezone})")
            else:
                logger.error(f"⚠️ User {user_id} not found in database")
                raise Exception(f"User {user_id} not found in database")
    except Exception as e:
        logger.error(f"⚠️ Could not query user profile for {user_id}: {e}")
        raise Exception(f"Failed to retrieve user credentials: {e}")
    
    @tool
    async def check_my_timesheet(date_range: str = "this_week") -> str:
        """
        Check my timesheet hours and entries for a date range.
        
        Use 'this_week', 'last_week', 'this_month', 'last_month', or 'YYYY-MM-DD to YYYY-MM-DD'.
        Returns a summary with total hours and recent entries.
        """
        try:
            # Use credentials retrieved from database
            if not harvest_account or not harvest_token:
                return f"❌ Missing Harvest credentials for {user_id}"
            
            # Calculate date range in user's timezone
            from datetime import datetime, timedelta
            from zoneinfo import ZoneInfo
            user_tz = ZoneInfo(user_timezone)
            today = datetime.now(user_tz)
            
            # Parse date_range parameter (keep user-friendly date parsing)
            if date_range == "this_week":
                week_start = (today - timedelta(days=today.weekday())).strftime('%Y-%m-%d')
                week_end = today.strftime('%Y-%m-%d')  # FIX: Use today, not end of week (future)
            elif date_range == "last_week":
                last_week = today - timedelta(weeks=1)
                week_start = (last_week - timedelta(days=last_week.weekday())).strftime('%Y-%m-%d')
                week_end = (last_week + timedelta(days=6-last_week.weekday())).strftime('%Y-%m-%d')
            elif date_range == "this_month":
                week_start = today.replace(day=1).strftime('%Y-%m-%d')
                week_end = today.strftime('%Y-%m-%d')  # FIX: Use today, not last day of month (future)
            elif date_range == "last_month":
                from calendar import monthrange
                first_of_this_month = today.replace(day=1)
                last_month = first_of_this_month - timedelta(days=1)
                week_start = last_month.replace(day=1).strftime('%Y-%m-%d')
                last_day = monthrange(last_month.year, last_month.month)[1]
                week_end = last_month.replace(day=last_day).strftime('%Y-%m-%d')
            else:
                # Custom range format: "2025-10-01 to 2025-10-07"
                dates = date_range.split(" to ")
                if len(dates) == 2:
                    try:
                        # Validate date format
                        start = datetime.strptime(dates[0].strip(), '%Y-%m-%d')
                        end = datetime.strptime(dates[1].strip(), '%Y-%m-%d')
                        
                        if end < start:
                            return f"❌ End date ({dates[1]}) cannot be before start date ({dates[0]})"
                        
                        week_start, week_end = dates[0].strip(), dates[1].strip()
                    except ValueError:
                        return f"❌ Invalid date format in custom range. Use 'YYYY-MM-DD to YYYY-MM-DD' (e.g., '2025-11-01 to 2025-11-21')"
                else:
                    return f"❌ Invalid date_range. Use 'this_week', 'last_week', 'this_month', 'last_month', or 'YYYY-MM-DD to YYYY-MM-DD'."
            
            # Call MCP tool to get entries
            payload = {
                "harvest_account": harvest_account,
                "harvest_token": harvest_token,
                "from_date": week_start,
                "to_date": week_end,
                "user_id": harvest_user_id
            }
            
            logger.info(f"📅 Checking timesheet for {week_start} to {week_end} ({user_timezone})")
            result = await call_harvest_mcp_tool("list_time_entries", payload)
            
            time_entries = result.get('time_entries', [])
            total_hours = sum(entry.get('hours', 0) for entry in time_entries)
            
            # Calculate target hours based on working days in range
            start_date = datetime.strptime(week_start, '%Y-%m-%d')
            end_date = datetime.strptime(week_end, '%Y-%m-%d')
            working_days = 0
            current = start_date
            while current <= end_date:
                if current.weekday() < 5:  # Monday=0, Friday=4
                    working_days += 1
                current += timedelta(days=1)
            target_hours = working_days * 8  # 8 hours per working day
            
            # Prepare data for unified formatter
            format_data = {
                'user_name': user_name,
                'week_start': week_start,
                'week_end': week_end,
                'total_hours': total_hours,
                'target_hours': target_hours,  # FIX: Calculate based on actual working days
                'entries_count': len(time_entries),
                'time_entries': time_entries,
                'timezone': user_timezone
            }
            
            # Use unified formatter for consistent messaging
            return format_check_timesheet_message(format_data, "check")
            
        except Exception as e:
            error_data = {
                'user_name': user_name,
                'week_start': 'this week',
                'week_end': '',
                'total_hours': 0,
                'target_hours': 40,
                'entries_count': 0,
                'time_entries': [],
                'timezone': user_timezone
            }
            
            error_str = str(e).lower()
            if 'unauthorized' in error_str or 'forbidden' in error_str or '401' in error_str or '403' in error_str:
                error_message = format_check_timesheet_message(error_data, "error")
                return f"{error_message}\n\n⚠️ **Credential Issue**: Please contact your administrator to update your Harvest API credentials."
            else:
                error_message = format_check_timesheet_message(error_data, "error") 
                return f"{error_message}\n\n❌ **Technical Error**: {str(e)}"
    
    @tool
    async def log_time_entry(project_name: str, hours: float, date: str = "today", notes: str = "") -> str:
        """Log a time entry. Date format: 'today', 'yesterday', or 'YYYY-MM-DD'"""
        try:
            # Import datetime here for nested function scope
            from datetime import datetime, timedelta
            from zoneinfo import ZoneInfo
            
            # Validate hours
            if hours <= 0:
                return f"❌ Hours must be greater than 0. You entered: {hours}"
            if hours > 24:
                return f"❌ Hours cannot exceed 24 in a single day. You entered: {hours}"
            if hours < 0.25:
                return f"❌ Minimum time entry is 0.25 hours (15 minutes). You entered: {hours}"
            
            # Convert date using user timezone (not UTC!)
            user_tz = ZoneInfo(user_timezone)
            now = datetime.now(user_tz)
            
            if date == "today":
                spent_date = now.strftime('%Y-%m-%d')  # FIX: Use user timezone
            elif date == "yesterday":
                spent_date = (now - timedelta(days=1)).strftime('%Y-%m-%d')  # FIX: Use user timezone
            else:
                # Validate custom date format
                try:
                    datetime.strptime(date, '%Y-%m-%d')
                    spent_date = date
                except ValueError:
                    return f"❌ Invalid date format: '{date}'. Use 'today', 'yesterday', or 'YYYY-MM-DD' (e.g., '2025-11-21')"
            
            # Use credentials retrieved from database (no more hardcoded environment variables)
            if not harvest_account or not harvest_token:
                return f"❌ Missing Harvest credentials for {user_id}"
            
            # First, get projects to find the right project ID
            projects_payload = {
                "harvest_account": harvest_account,
                "harvest_token": harvest_token,
                "is_active": True
            }
            
            projects_result = await call_harvest_mcp_tool("list_projects", projects_payload)
            projects = projects_result.get('projects', [])
            
            # Find matching project (exact match first, then partial)
            project_id = None
            task_id = None
            matched_project = None
            
            # Try exact match first
            for project in projects:
                if project_name.lower() == project.get('name', '').lower():
                    matched_project = project
                    break
            
            # If no exact match, try partial match
            if not matched_project:
                for project in projects:
                    if project_name.lower() in project.get('name', '').lower():
                        matched_project = project
                        break
            
            if not matched_project:
                return f"❌ Project '{project_name}' not found. Available projects: {[p.get('name') for p in projects[:5]]}"
            
            project_id = matched_project.get('id')
            
            # Get task assignments
            task_assignments = matched_project.get('task_assignments', [])
            if not task_assignments:
                return f"❌ Project '{matched_project.get('name')}' has no available tasks. Please contact your administrator."
            
            # Try to find Programming/Development task first (most common)
            for assignment in task_assignments:
                task = assignment.get('task', {})
                task_name = task.get('name', '').lower()
                if 'programming' in task_name or 'development' in task_name or 'dev' in task_name:
                    task_id = task.get('id')
                    break
            
            # If no programming task, use first available
            if not task_id:
                task_id = task_assignments[0].get('task', {}).get('id')
            
            if not task_id:
                return f"❌ Could not find a valid task for project '{matched_project.get('name')}'"
            
            # Create time entry
            entry_payload = {
                "harvest_account": harvest_account,
                "harvest_token": harvest_token,
                "project_id": project_id,
                "task_id": task_id,
                "spent_date": spent_date,
                "hours": hours,
                "notes": notes
            }
            
            result = await call_harvest_mcp_tool("create_time_entry", entry_payload)
            
            return f"✅ Logged {hours}h to '{project_name}' on {spent_date}"
            
        except Exception as e:
            # Provide helpful error messages based on error type
            error_str = str(e).lower()
            if 'unauthorized' in error_str or 'forbidden' in error_str or '401' in error_str or '403' in error_str:
                return f"❌ **Permission Error**: Cannot log time due to insufficient Harvest API permissions.\n\n💡 **Solution**: Please contact your administrator to:\n• Update your Harvest API credentials\n• Ensure you have time tracking permissions\n• Verify your account access"
            elif 'project' in error_str and 'not found' in error_str:
                return f"❌ **Project Error**: Project '{project_name}' not found.\n\n💡 **Try**: Use 'projects' command to see available projects"
            else:
                return f"❌ **Technical Error**: {str(e)}\n\n💡 **Help**: Try again or contact support if the issue persists"
    
    @tool
    async def list_my_projects() -> str:
        """List all active projects available for time tracking"""
        try:
            # Use credentials retrieved from database (no more hardcoded environment variables)
            if not harvest_account or not harvest_token:
                return f"❌ Missing Harvest credentials for {user_id}"
            
            payload = {
                "harvest_account": harvest_account,
                "harvest_token": harvest_token,
                "is_active": True
            }
            
            result = await call_harvest_mcp_tool("list_projects", payload)
            projects = result.get('projects', [])
            
            if not projects:
                return "No active projects found."
            
            project_list = "📋 Your Active Projects:\n"
            for project in projects:
                name = project.get('name', 'Unknown')
                client = project.get('client', {}).get('name', 'No Client')
                project_list += f"• {name} (Client: {client})\n"
            
            return project_list
            
        except Exception as e:
            return f"❌ Error listing projects: {str(e)}"
    
    @tool
    async def get_current_user_info() -> str:
        """Get current user information from Harvest"""
        try:
            # Use credentials retrieved from database (no more hardcoded environment variables)
            if not harvest_account or not harvest_token:
                return f"❌ Missing Harvest credentials for {user_id}"
            
            payload = {
                "harvest_account": harvest_account,
                "harvest_token": harvest_token
            }
            
            result = await call_harvest_mcp_tool("get_current_user", payload)
            
            user_info = f"👤 Your Harvest Info:\n"
            user_info += f"Name: {result.get('first_name', '')} {result.get('last_name', '')}\n"
            user_info += f"Email: {result.get('email', '')}\n"
            user_info += f"Role: {result.get('roles', ['Unknown'])[0] if result.get('roles') else 'Unknown'}\n"
            
            return user_info
            
        except Exception as e:
            return f"❌ Error getting user info: {str(e)}"
    
    # ==========================================
    # NEW TIME ENTRY TOOLS (Phase 1)
    # ==========================================
    
    @tool
    async def get_time_entry(entry_id: str) -> str:
        """Get details of a specific time entry by ID."""
        try:
            if not harvest_account or not harvest_token:
                return f"❌ Missing Harvest credentials for {user_id}"
            
            payload = {
                "time_entry_id": entry_id,
                "harvest_account": harvest_account,
                "harvest_token": harvest_token
            }
            
            result = await call_harvest_mcp_tool("get_time_entry", payload)
            
            if "error" in result or "detail" in result:
                return f"❌ Error: {result.get('detail', result.get('error'))}"
            
            # Format response
            entry_info = f"⏱️ Time Entry Details:\n"
            entry_info += f"ID: {result.get('id', 'N/A')}\n"
            entry_info += f"Date: {result.get('spent_date', 'N/A')}\n"
            entry_info += f"Hours: {result.get('hours', 0)}\n"
            entry_info += f"Project: {result.get('project', {}).get('name', 'N/A')}\n"
            entry_info += f"Task: {result.get('task', {}).get('name', 'N/A')}\n"
            entry_info += f"Notes: {result.get('notes', 'No notes')}\n"
            entry_info += f"Running: {'Yes' if result.get('is_running') else 'No'}\n"
            
            return entry_info
            
        except Exception as e:
            return f"❌ Error getting time entry: {str(e)}"
    
    @tool
    async def update_time_entry(entry_id: str, notes: str = None, hours: float = None) -> str:
        """Update an existing time entry. Provide entry_id and fields to update (notes, hours)."""
        try:
            if not harvest_account or not harvest_token:
                return f"❌ Missing Harvest credentials for {user_id}"
            
            payload = {
                "time_entry_id": entry_id,
                "harvest_account": harvest_account,
                "harvest_token": harvest_token
            }
            
            # Add optional fields
            if notes is not None:
                payload["notes"] = notes
            if hours is not None:
                payload["hours"] = hours
            
            result = await call_harvest_mcp_tool("update_time_entry", payload)
            
            if "error" in result or "detail" in result:
                return f"❌ Error: {result.get('detail', result.get('error'))}"
            
            return f"✅ Updated time entry {entry_id}\nHours: {result.get('hours', 'N/A')}\nNotes: {result.get('notes', 'No notes')}"
            
        except Exception as e:
            return f"❌ Error updating time entry: {str(e)}"
    
    @tool
    async def delete_time_entry(entry_id: str) -> str:
        """Delete a time entry by ID. Use with caution - this cannot be undone."""
        try:
            if not harvest_account or not harvest_token:
                return f"❌ Missing Harvest credentials for {user_id}"
            
            payload = {
                "time_entry_id": entry_id,
                "harvest_account": harvest_account,
                "harvest_token": harvest_token
            }
            
            result = await call_harvest_mcp_tool("delete_time_entry", payload)
            
            if "error" in result or "detail" in result:
                return f"❌ Error: {result.get('detail', result.get('error'))}"
            
            return f"✅ Deleted time entry {entry_id}"
            
        except Exception as e:
            return f"❌ Error deleting time entry: {str(e)}"
    
    @tool
    async def restart_time_entry(entry_id: str) -> str:
        """Restart a stopped time entry timer."""
        try:
            if not harvest_account or not harvest_token:
                return f"❌ Missing Harvest credentials for {user_id}"
            
            payload = {
                "time_entry_id": entry_id,
                "harvest_account": harvest_account,
                "harvest_token": harvest_token
            }
            
            result = await call_harvest_mcp_tool("restart_time_entry", payload)
            
            if "error" in result or "detail" in result:
                return f"❌ Error: {result.get('detail', result.get('error'))}"
            
            return f"✅ Restarted timer for entry {entry_id}\nProject: {result.get('project', {}).get('name', 'N/A')}\nTask: {result.get('task', {}).get('name', 'N/A')}"
            
        except Exception as e:
            return f"❌ Error restarting timer: {str(e)}"
    
    @tool
    async def stop_time_entry(entry_id: str) -> str:
        """Stop a running time entry timer."""
        try:
            if not harvest_account or not harvest_token:
                return f"❌ Missing Harvest credentials for {user_id}"
            
            payload = {
                "time_entry_id": entry_id,
                "harvest_account": harvest_account,
                "harvest_token": harvest_token
            }
            
            result = await call_harvest_mcp_tool("stop_time_entry", payload)
            
            if "error" in result or "detail" in result:
                return f"❌ Error: {result.get('detail', result.get('error'))}"
            
            return f"✅ Stopped timer for entry {entry_id}\nTotal hours: {result.get('hours', 'N/A')}"
            
        except Exception as e:
            return f"❌ Error stopping timer: {str(e)}"
    
    # ==========================================
    # PROJECT TOOLS (Phase 2)
    # ==========================================
    
    @tool
    async def get_project(project_id: str) -> str:
        """Get details of a specific project by ID."""
        try:
            if not harvest_account or not harvest_token:
                return f"❌ Missing Harvest credentials for {user_id}"
            
            payload = {
                "project_id": project_id,
                "harvest_account": harvest_account,
                "harvest_token": harvest_token
            }
            
            result = await call_harvest_mcp_tool("get_project", payload)
            
            if "error" in result or "detail" in result:
                return f"❌ Error: {result.get('detail', result.get('error'))}"
            
            # Format response
            project_info = f"📁 Project Details:\n"
            project_info += f"ID: {result.get('id', 'N/A')}\n"
            project_info += f"Name: {result.get('name', 'N/A')}\n"
            project_info += f"Client: {result.get('client', {}).get('name', 'N/A')}\n"
            project_info += f"Code: {result.get('code', 'N/A')}\n"
            project_info += f"Active: {'Yes' if result.get('is_active') else 'No'}\n"
            project_info += f"Billable: {'Yes' if result.get('is_billable') else 'No'}\n"
            if result.get('budget'):
                project_info += f"Budget: ${result.get('budget', 0):,.2f}\n"
            
            return project_info
            
        except Exception as e:
            return f"❌ Error getting project: {str(e)}"
    
    @tool
    async def create_project(client_id: int, name: str, is_billable: bool = True, budget: float = None) -> str:
        """Create a new project. Requires client_id and project name."""
        try:
            if not harvest_account or not harvest_token:
                return f"❌ Missing Harvest credentials for {user_id}"
            
            payload = {
                "client_id": client_id,
                "name": name,
                "is_billable": is_billable,
                "harvest_account": harvest_account,
                "harvest_token": harvest_token
            }
            
            if budget is not None:
                payload["budget"] = budget
            
            result = await call_harvest_mcp_tool("create_project", payload)
            
            if "error" in result or "detail" in result:
                return f"❌ Error: {result.get('detail', result.get('error'))}"
            
            return f"✅ Created project: {result.get('name', 'N/A')} (ID: {result.get('id', 'N/A')})\nClient: {result.get('client', {}).get('name', 'N/A')}"
            
        except Exception as e:
            return f"❌ Error creating project: {str(e)}"
    
    @tool
    async def update_project(project_id: str, name: str = None, is_billable: bool = None, budget: float = None, is_active: bool = None) -> str:
        """Update an existing project. Provide project_id and fields to update."""
        try:
            if not harvest_account or not harvest_token:
                return f"❌ Missing Harvest credentials for {user_id}"
            
            payload = {
                "project_id": project_id,
                "harvest_account": harvest_account,
                "harvest_token": harvest_token
            }
            
            # Add optional fields
            if name is not None:
                payload["name"] = name
            if is_billable is not None:
                payload["is_billable"] = is_billable
            if budget is not None:
                payload["budget"] = budget
            if is_active is not None:
                payload["is_active"] = is_active
            
            result = await call_harvest_mcp_tool("update_project", payload)
            
            if "error" in result or "detail" in result:
                return f"❌ Error: {result.get('detail', result.get('error'))}"
            
            return f"✅ Updated project: {result.get('name', 'N/A')} (ID: {project_id})"
            
        except Exception as e:
            return f"❌ Error updating project: {str(e)}"
    
    @tool
    async def delete_project(project_id: str) -> str:
        """Delete a project by ID. Use with caution - this cannot be undone."""
        try:
            if not harvest_account or not harvest_token:
                return f"❌ Missing Harvest credentials for {user_id}"
            
            payload = {
                "project_id": project_id,
                "harvest_account": harvest_account,
                "harvest_token": harvest_token
            }
            
            result = await call_harvest_mcp_tool("delete_project", payload)
            
            if "error" in result or "detail" in result:
                return f"❌ Error: {result.get('detail', result.get('error'))}"
            
            return f"✅ Deleted project {project_id}"
            
        except Exception as e:
            return f"❌ Error deleting project: {str(e)}"
    
    # ==========================================
    # CLIENT TOOLS (Phase 2)
    # ==========================================
    
    @tool
    async def list_clients(is_active: bool = True) -> str:
        """List all clients. Set is_active=False to include inactive clients."""
        try:
            if not harvest_account or not harvest_token:
                return f"❌ Missing Harvest credentials for {user_id}"
            
            payload = {
                "is_active": is_active,
                "harvest_account": harvest_account,
                "harvest_token": harvest_token
            }
            
            result = await call_harvest_mcp_tool("list_clients", payload)
            
            if "error" in result or "detail" in result:
                return f"❌ Error: {result.get('detail', result.get('error'))}"
            
            clients = result.get('clients', [])
            if not clients:
                return "📋 No clients found."
            
            # Format response
            client_list = f"📋 Clients ({len(clients)} total):\n\n"
            for client in clients[:20]:  # Limit to 20
                client_list += f"• {client.get('name', 'N/A')} (ID: {client.get('id', 'N/A')})\n"
                if client.get('currency'):
                    client_list += f"  Currency: {client.get('currency')}\n"
            
            if len(clients) > 20:
                client_list += f"\n... and {len(clients) - 20} more clients"
            
            return client_list
            
        except Exception as e:
            return f"❌ Error listing clients: {str(e)}"
    
    @tool
    async def get_client(client_id: str) -> str:
        """Get details of a specific client by ID."""
        try:
            if not harvest_account or not harvest_token:
                return f"❌ Missing Harvest credentials for {user_id}"
            
            payload = {
                "client_id": client_id,
                "harvest_account": harvest_account,
                "harvest_token": harvest_token
            }
            
            result = await call_harvest_mcp_tool("get_client", payload)
            
            if "error" in result or "detail" in result:
                return f"❌ Error: {result.get('detail', result.get('error'))}"
            
            # Format response
            client_info = f"🏢 Client Details:\n"
            client_info += f"ID: {result.get('id', 'N/A')}\n"
            client_info += f"Name: {result.get('name', 'N/A')}\n"
            client_info += f"Currency: {result.get('currency', 'N/A')}\n"
            client_info += f"Active: {'Yes' if result.get('is_active') else 'No'}\n"
            if result.get('address'):
                client_info += f"Address: {result.get('address')}\n"
            
            return client_info
            
        except Exception as e:
            return f"❌ Error getting client: {str(e)}"
    
    @tool
    async def create_client(name: str, currency: str = "USD", address: str = None) -> str:
        """Create a new client. Requires client name."""
        try:
            if not harvest_account or not harvest_token:
                return f"❌ Missing Harvest credentials for {user_id}"
            
            payload = {
                "name": name,
                "currency": currency,
                "harvest_account": harvest_account,
                "harvest_token": harvest_token
            }
            
            if address:
                payload["address"] = address
            
            result = await call_harvest_mcp_tool("create_client", payload)
            
            if "error" in result or "detail" in result:
                return f"❌ Error: {result.get('detail', result.get('error'))}"
            
            return f"✅ Created client: {result.get('name', 'N/A')} (ID: {result.get('id', 'N/A')})"
            
        except Exception as e:
            return f"❌ Error creating client: {str(e)}"
    
    @tool
    async def update_client(client_id: str, name: str = None, currency: str = None, address: str = None, is_active: bool = None) -> str:
        """Update an existing client. Provide client_id and fields to update."""
        try:
            if not harvest_account or not harvest_token:
                return f"❌ Missing Harvest credentials for {user_id}"
            
            payload = {
                "client_id": client_id,
                "harvest_account": harvest_account,
                "harvest_token": harvest_token
            }
            
            # Add optional fields
            if name is not None:
                payload["name"] = name
            if currency is not None:
                payload["currency"] = currency
            if address is not None:
                payload["address"] = address
            if is_active is not None:
                payload["is_active"] = is_active
            
            result = await call_harvest_mcp_tool("update_client", payload)
            
            if "error" in result or "detail" in result:
                return f"❌ Error: {result.get('detail', result.get('error'))}"
            
            return f"✅ Updated client: {result.get('name', 'N/A')} (ID: {client_id})"
            
        except Exception as e:
            return f"❌ Error updating client: {str(e)}"
    
    @tool
    async def delete_client(client_id: str) -> str:
        """Delete a client by ID. Use with caution - this cannot be undone."""
        try:
            if not harvest_account or not harvest_token:
                return f"❌ Missing Harvest credentials for {user_id}"
            
            payload = {
                "client_id": client_id,
                "harvest_account": harvest_account,
                "harvest_token": harvest_token
            }
            
            result = await call_harvest_mcp_tool("delete_client", payload)
            
            if "error" in result or "detail" in result:
                return f"❌ Error: {result.get('detail', result.get('error'))}"
            
            return f"✅ Deleted client {client_id}"
            
        except Exception as e:
            return f"❌ Error deleting client: {str(e)}"
    
    # ==========================================
    # CONTACT TOOLS (Phase 3a)
    # ==========================================
    
    @tool
    async def list_contacts(client_id: int = None) -> str:
        """List all contacts. Optionally filter by client_id."""
        try:
            if not harvest_account or not harvest_token:
                return f"❌ Missing Harvest credentials for {user_id}"
            
            payload = {
                "harvest_account": harvest_account,
                "harvest_token": harvest_token
            }
            
            if client_id:
                payload["client_id"] = client_id
            
            result = await call_harvest_mcp_tool("list_contacts", payload)
            
            if "error" in result or "detail" in result:
                return f"❌ Error: {result.get('detail', result.get('error'))}"
            
            contacts = result.get('contacts', [])
            if not contacts:
                return "📇 No contacts found."
            
            contact_list = f"📇 Contacts ({len(contacts)} total):\n\n"
            for contact in contacts[:20]:
                contact_list += f"• {contact.get('first_name', '')} {contact.get('last_name', '')}\n"
                contact_list += f"  Email: {contact.get('email', 'N/A')}\n"
                contact_list += f"  Client: {contact.get('client', {}).get('name', 'N/A')}\n"
            
            if len(contacts) > 20:
                contact_list += f"\n... and {len(contacts) - 20} more contacts"
            
            return contact_list
            
        except Exception as e:
            return f"❌ Error listing contacts: {str(e)}"
    
    @tool
    async def get_contact(contact_id: str) -> str:
        """Get details of a specific contact by ID."""
        try:
            if not harvest_account or not harvest_token:
                return f"❌ Missing Harvest credentials for {user_id}"
            
            payload = {
                "contact_id": contact_id,
                "harvest_account": harvest_account,
                "harvest_token": harvest_token
            }
            
            result = await call_harvest_mcp_tool("get_contact", payload)
            
            if "error" in result or "detail" in result:
                return f"❌ Error: {result.get('detail', result.get('error'))}"
            
            contact_info = f"📇 Contact Details:\n"
            contact_info += f"Name: {result.get('first_name', '')} {result.get('last_name', '')}\n"
            contact_info += f"Email: {result.get('email', 'N/A')}\n"
            contact_info += f"Phone: {result.get('phone_office', 'N/A')}\n"
            contact_info += f"Mobile: {result.get('phone_mobile', 'N/A')}\n"
            contact_info += f"Client: {result.get('client', {}).get('name', 'N/A')}\n"
            
            return contact_info
            
        except Exception as e:
            return f"❌ Error getting contact: {str(e)}"
    
    @tool
    async def create_contact(client_id: int, first_name: str, last_name: str = None, email: str = None) -> str:
        """Create a new contact. Requires client_id and first_name."""
        try:
            if not harvest_account or not harvest_token:
                return f"❌ Missing Harvest credentials for {user_id}"
            
            payload = {
                "client_id": client_id,
                "first_name": first_name,
                "harvest_account": harvest_account,
                "harvest_token": harvest_token
            }
            
            if last_name:
                payload["last_name"] = last_name
            if email:
                payload["email"] = email
            
            result = await call_harvest_mcp_tool("create_contact", payload)
            
            if "error" in result or "detail" in result:
                return f"❌ Error: {result.get('detail', result.get('error'))}"
            
            return f"✅ Created contact: {result.get('first_name', '')} {result.get('last_name', '')} (ID: {result.get('id', 'N/A')})"
            
        except Exception as e:
            return f"❌ Error creating contact: {str(e)}"
    
    @tool
    async def update_contact(contact_id: str, first_name: str = None, last_name: str = None, email: str = None) -> str:
        """Update an existing contact."""
        try:
            if not harvest_account or not harvest_token:
                return f"❌ Missing Harvest credentials for {user_id}"
            
            payload = {
                "contact_id": contact_id,
                "harvest_account": harvest_account,
                "harvest_token": harvest_token
            }
            
            if first_name:
                payload["first_name"] = first_name
            if last_name:
                payload["last_name"] = last_name
            if email:
                payload["email"] = email
            
            result = await call_harvest_mcp_tool("update_contact", payload)
            
            if "error" in result or "detail" in result:
                return f"❌ Error: {result.get('detail', result.get('error'))}"
            
            return f"✅ Updated contact {contact_id}"
            
        except Exception as e:
            return f"❌ Error updating contact: {str(e)}"
    
    @tool
    async def delete_contact(contact_id: str) -> str:
        """Delete a contact by ID."""
        try:
            if not harvest_account or not harvest_token:
                return f"❌ Missing Harvest credentials for {user_id}"
            
            payload = {
                "contact_id": contact_id,
                "harvest_account": harvest_account,
                "harvest_token": harvest_token
            }
            
            result = await call_harvest_mcp_tool("delete_contact", payload)
            
            if "error" in result or "detail" in result:
                return f"❌ Error: {result.get('detail', result.get('error'))}"
            
            return f"✅ Deleted contact {contact_id}"
            
        except Exception as e:
            return f"❌ Error deleting contact: {str(e)}"
    
    # ==========================================
    # TASK TOOLS (Phase 3a)
    # ==========================================
    
    @tool
    async def list_tasks(is_active: bool = True) -> str:
        """List all tasks."""
        try:
            if not harvest_account or not harvest_token:
                return f"❌ Missing Harvest credentials for {user_id}"
            
            payload = {
                "is_active": is_active,
                "harvest_account": harvest_account,
                "harvest_token": harvest_token
            }
            
            result = await call_harvest_mcp_tool("list_tasks", payload)
            
            if "error" in result or "detail" in result:
                return f"❌ Error: {result.get('detail', result.get('error'))}"
            
            tasks = result.get('tasks', [])
            if not tasks:
                return "📋 No tasks found."
            
            task_list = f"📋 Tasks ({len(tasks)} total):\n\n"
            for task in tasks[:20]:
                task_list += f"• {task.get('name', 'N/A')} (ID: {task.get('id', 'N/A')})\n"
                if task.get('default_hourly_rate'):
                    task_list += f"  Rate: ${task.get('default_hourly_rate')}/hr\n"
            
            if len(tasks) > 20:
                task_list += f"\n... and {len(tasks) - 20} more tasks"
            
            return task_list
            
        except Exception as e:
            return f"❌ Error listing tasks: {str(e)}"
    
    @tool
    async def get_task(task_id: str) -> str:
        """Get details of a specific task by ID."""
        try:
            if not harvest_account or not harvest_token:
                return f"❌ Missing Harvest credentials for {user_id}"
            
            payload = {
                "task_id": task_id,
                "harvest_account": harvest_account,
                "harvest_token": harvest_token
            }
            
            result = await call_harvest_mcp_tool("get_task", payload)
            
            if "error" in result or "detail" in result:
                return f"❌ Error: {result.get('detail', result.get('error'))}"
            
            task_info = f"📋 Task Details:\n"
            task_info += f"Name: {result.get('name', 'N/A')}\n"
            task_info += f"Billable: {'Yes' if result.get('billable_by_default') else 'No'}\n"
            task_info += f"Active: {'Yes' if result.get('is_active') else 'No'}\n"
            if result.get('default_hourly_rate'):
                task_info += f"Rate: ${result.get('default_hourly_rate')}/hr\n"
            
            return task_info
            
        except Exception as e:
            return f"❌ Error getting task: {str(e)}"
    
    @tool
    async def create_task(name: str, billable_by_default: bool = True, default_hourly_rate: float = None) -> str:
        """Create a new task."""
        try:
            if not harvest_account or not harvest_token:
                return f"❌ Missing Harvest credentials for {user_id}"
            
            payload = {
                "name": name,
                "billable_by_default": billable_by_default,
                "harvest_account": harvest_account,
                "harvest_token": harvest_token
            }
            
            if default_hourly_rate:
                payload["default_hourly_rate"] = default_hourly_rate
            
            result = await call_harvest_mcp_tool("create_task", payload)
            
            if "error" in result or "detail" in result:
                return f"❌ Error: {result.get('detail', result.get('error'))}"
            
            return f"✅ Created task: {result.get('name', 'N/A')} (ID: {result.get('id', 'N/A')})"
            
        except Exception as e:
            return f"❌ Error creating task: {str(e)}"
    
    @tool
    async def update_task(task_id: str, name: str = None, billable_by_default: bool = None, default_hourly_rate: float = None) -> str:
        """Update an existing task."""
        try:
            if not harvest_account or not harvest_token:
                return f"❌ Missing Harvest credentials for {user_id}"
            
            payload = {
                "task_id": task_id,
                "harvest_account": harvest_account,
                "harvest_token": harvest_token
            }
            
            if name:
                payload["name"] = name
            if billable_by_default is not None:
                payload["billable_by_default"] = billable_by_default
            if default_hourly_rate:
                payload["default_hourly_rate"] = default_hourly_rate
            
            result = await call_harvest_mcp_tool("update_task", payload)
            
            if "error" in result or "detail" in result:
                return f"❌ Error: {result.get('detail', result.get('error'))}"
            
            return f"✅ Updated task {task_id}"
            
        except Exception as e:
            return f"❌ Error updating task: {str(e)}"
    
    @tool
    async def delete_task(task_id: str) -> str:
        """Delete a task by ID."""
        try:
            if not harvest_account or not harvest_token:
                return f"❌ Missing Harvest credentials for {user_id}"
            
            payload = {
                "task_id": task_id,
                "harvest_account": harvest_account,
                "harvest_token": harvest_token
            }
            
            result = await call_harvest_mcp_tool("delete_task", payload)
            
            if "error" in result or "detail" in result:
                return f"❌ Error: {result.get('detail', result.get('error'))}"
            
            return f"✅ Deleted task {task_id}"
            
        except Exception as e:
            return f"❌ Error deleting task: {str(e)}"
    
    # ==========================================
    # USER TOOLS (Phase 3b)
    # ==========================================
    
    @tool
    async def list_users(is_active: bool = True) -> str:
        """List all users."""
        try:
            if not harvest_account or not harvest_token:
                return f"❌ Missing Harvest credentials for {user_id}"
            
            payload = {
                "is_active": is_active,
                "harvest_account": harvest_account,
                "harvest_token": harvest_token
            }
            
            result = await call_harvest_mcp_tool("list_users", payload)
            
            if "error" in result or "detail" in result:
                return f"❌ Error: {result.get('detail', result.get('error'))}"
            
            users = result.get('users', [])
            if not users:
                return "👥 No users found."
            
            user_list = f"👥 Users ({len(users)} total):\n\n"
            for usr in users[:20]:
                user_list += f"• {usr.get('first_name', '')} {usr.get('last_name', '')}\n"
                user_list += f"  Email: {usr.get('email', 'N/A')}\n"
            
            if len(users) > 20:
                user_list += f"\n... and {len(users) - 20} more users"
            
            return user_list
            
        except Exception as e:
            return f"❌ Error listing users: {str(e)}"
    
    @tool
    async def get_user(user_id_param: str) -> str:
        """Get details of a specific user by ID."""
        try:
            if not harvest_account or not harvest_token:
                return f"❌ Missing Harvest credentials for {user_id}"
            
            payload = {
                "user_id": user_id_param,
                "harvest_account": harvest_account,
                "harvest_token": harvest_token
            }
            
            result = await call_harvest_mcp_tool("get_user", payload)
            
            if "error" in result or "detail" in result:
                return f"❌ Error: {result.get('detail', result.get('error'))}"
            
            user_info = f"👤 User Details:\n"
            user_info += f"Name: {result.get('first_name', '')} {result.get('last_name', '')}\n"
            user_info += f"Email: {result.get('email', 'N/A')}\n"
            user_info += f"Timezone: {result.get('timezone', 'N/A')}\n"
            user_info += f"Active: {'Yes' if result.get('is_active') else 'No'}\n"
            user_info += f"Contractor: {'Yes' if result.get('is_contractor') else 'No'}\n"
            
            return user_info
            
        except Exception as e:
            return f"❌ Error getting user: {str(e)}"
    
    @tool
    async def create_user(first_name: str, last_name: str, email: str, is_contractor: bool = False) -> str:
        """Create a new user."""
        try:
            if not harvest_account or not harvest_token:
                return f"❌ Missing Harvest credentials for {user_id}"
            
            payload = {
                "first_name": first_name,
                "last_name": last_name,
                "email": email,
                "is_contractor": is_contractor,
                "harvest_account": harvest_account,
                "harvest_token": harvest_token
            }
            
            result = await call_harvest_mcp_tool("create_user", payload)
            
            if "error" in result or "detail" in result:
                return f"❌ Error: {result.get('detail', result.get('error'))}"
            
            return f"✅ Created user: {result.get('first_name', '')} {result.get('last_name', '')} (ID: {result.get('id', 'N/A')})"
            
        except Exception as e:
            return f"❌ Error creating user: {str(e)}"
    
    @tool
    async def update_user(user_id_param: str, first_name: str = None, last_name: str = None, email: str = None) -> str:
        """Update an existing user."""
        try:
            if not harvest_account or not harvest_token:
                return f"❌ Missing Harvest credentials for {user_id}"
            
            payload = {
                "user_id": user_id_param,
                "harvest_account": harvest_account,
                "harvest_token": harvest_token
            }
            
            if first_name:
                payload["first_name"] = first_name
            if last_name:
                payload["last_name"] = last_name
            if email:
                payload["email"] = email
            
            result = await call_harvest_mcp_tool("update_user", payload)
            
            if "error" in result or "detail" in result:
                return f"❌ Error: {result.get('detail', result.get('error'))}"
            
            return f"✅ Updated user {user_id_param}"
            
        except Exception as e:
            return f"❌ Error updating user: {str(e)}"
    
    @tool
    async def delete_user(user_id_param: str) -> str:
        """Delete a user by ID."""
        try:
            if not harvest_account or not harvest_token:
                return f"❌ Missing Harvest credentials for {user_id}"
            
            payload = {
                "user_id": user_id_param,
                "harvest_account": harvest_account,
                "harvest_token": harvest_token
            }
            
            result = await call_harvest_mcp_tool("delete_user", payload)
            
            if "error" in result or "detail" in result:
                return f"❌ Error: {result.get('detail', result.get('error'))}"
            
            return f"✅ Deleted user {user_id_param}"
            
        except Exception as e:
            return f"❌ Error deleting user: {str(e)}"
    
    # ==========================================
    # COMPANY TOOL (Phase 3b)
    # ==========================================
    
    @tool
    async def get_company() -> str:
        """Get company information for the authenticated account."""
        try:
            if not harvest_account or not harvest_token:
                return f"❌ Missing Harvest credentials for {user_id}"
            
            payload = {
                "harvest_account": harvest_account,
                "harvest_token": harvest_token
            }
            
            result = await call_harvest_mcp_tool("get_company", payload)
            
            if "error" in result or "detail" in result:
                return f"❌ Error: {result.get('detail', result.get('error'))}"
            
            company_info = f"🏢 Company Information:\n"
            company_info += f"Name: {result.get('name', 'N/A')}\n"
            company_info += f"Base Currency: {result.get('base_currency', 'N/A')}\n"
            company_info += f"Full Domain: {result.get('full_domain', 'N/A')}\n"
            company_info += f"Time Format: {result.get('time_format', 'N/A')}\n"
            company_info += f"Week Start: {result.get('week_start_day', 'N/A')}\n"
            
            return company_info
            
        except Exception as e:
            return f"❌ Error getting company: {str(e)}"
    
    # ==========================================
    # EXPENSE TOOLS (Phase 3c)
    # ==========================================
    
    @tool
    async def list_expenses(project_id: int = None, from_date: str = None, to_date: str = None) -> str:
        """List expenses. Optionally filter by project_id and date range."""
        try:
            if not harvest_account or not harvest_token:
                return f"❌ Missing Harvest credentials for {user_id}"
            
            payload = {
                "harvest_account": harvest_account,
                "harvest_token": harvest_token
            }
            
            if project_id:
                payload["project_id"] = project_id
            if from_date:
                payload["from_date"] = from_date
            if to_date:
                payload["to_date"] = to_date
            
            result = await call_harvest_mcp_tool("list_expenses", payload)
            
            if "error" in result or "detail" in result:
                return f"❌ Error: {result.get('detail', result.get('error'))}"
            
            expenses = result.get('expenses', [])
            if not expenses:
                return "💰 No expenses found."
            
            expense_list = f"💰 Expenses ({len(expenses)} total):\n\n"
            for expense in expenses[:20]:
                expense_list += f"• ${expense.get('total_cost', 0):.2f} - {expense.get('notes', 'No notes')}\n"
                expense_list += f"  Date: {expense.get('spent_date', 'N/A')}\n"
            
            if len(expenses) > 20:
                expense_list += f"\n... and {len(expenses) - 20} more expenses"
            
            return expense_list
            
        except Exception as e:
            return f"❌ Error listing expenses: {str(e)}"
    
    @tool
    async def get_expense(expense_id: str) -> str:
        """Get details of a specific expense by ID."""
        try:
            if not harvest_account or not harvest_token:
                return f"❌ Missing Harvest credentials for {user_id}"
            
            payload = {
                "expense_id": expense_id,
                "harvest_account": harvest_account,
                "harvest_token": harvest_token
            }
            
            result = await call_harvest_mcp_tool("get_expense", payload)
            
            if "error" in result or "detail" in result:
                return f"❌ Error: {result.get('detail', result.get('error'))}"
            
            expense_info = f"💰 Expense Details:\n"
            expense_info += f"Amount: ${result.get('total_cost', 0):.2f}\n"
            expense_info += f"Date: {result.get('spent_date', 'N/A')}\n"
            expense_info += f"Notes: {result.get('notes', 'No notes')}\n"
            expense_info += f"Project: {result.get('project', {}).get('name', 'N/A')}\n"
            
            return expense_info
            
        except Exception as e:
            return f"❌ Error getting expense: {str(e)}"
    
    @tool
    async def create_expense(project_id: int, expense_category_id: int, spent_date: str, total_cost: float, notes: str = None) -> str:
        """Create a new expense."""
        try:
            if not harvest_account or not harvest_token:
                return f"❌ Missing Harvest credentials for {user_id}"
            
            payload = {
                "project_id": project_id,
                "expense_category_id": expense_category_id,
                "spent_date": spent_date,
                "total_cost": total_cost,
                "harvest_account": harvest_account,
                "harvest_token": harvest_token
            }
            
            if notes:
                payload["notes"] = notes
            
            result = await call_harvest_mcp_tool("create_expense", payload)
            
            if "error" in result or "detail" in result:
                return f"❌ Error: {result.get('detail', result.get('error'))}"
            
            return f"✅ Created expense: ${result.get('total_cost', 0):.2f} (ID: {result.get('id', 'N/A')})"
            
        except Exception as e:
            return f"❌ Error creating expense: {str(e)}"
    
    @tool
    async def update_expense(expense_id: str, total_cost: float = None, notes: str = None) -> str:
        """Update an existing expense."""
        try:
            if not harvest_account or not harvest_token:
                return f"❌ Missing Harvest credentials for {user_id}"
            
            payload = {
                "expense_id": expense_id,
                "harvest_account": harvest_account,
                "harvest_token": harvest_token
            }
            
            if total_cost:
                payload["total_cost"] = total_cost
            if notes:
                payload["notes"] = notes
            
            result = await call_harvest_mcp_tool("update_expense", payload)
            
            if "error" in result or "detail" in result:
                return f"❌ Error: {result.get('detail', result.get('error'))}"
            
            return f"✅ Updated expense {expense_id}"
            
        except Exception as e:
            return f"❌ Error updating expense: {str(e)}"
    
    @tool
    async def delete_expense(expense_id: str) -> str:
        """Delete an expense by ID."""
        try:
            if not harvest_account or not harvest_token:
                return f"❌ Missing Harvest credentials for {user_id}"
            
            payload = {
                "expense_id": expense_id,
                "harvest_account": harvest_account,
                "harvest_token": harvest_token
            }
            
            result = await call_harvest_mcp_tool("delete_expense", payload)
            
            if "error" in result or "detail" in result:
                return f"❌ Error: {result.get('detail', result.get('error'))}"
            
            return f"✅ Deleted expense {expense_id}"
            
        except Exception as e:
            return f"❌ Error deleting expense: {str(e)}"
    
    # ==========================================
    # INVOICE TOOLS (Phase 3d)
    # ==========================================
    
    @tool
    async def list_invoices(client_id: int = None, from_date: str = None, to_date: str = None) -> str:
        """List invoices. Optionally filter by client_id and date range."""
        try:
            if not harvest_account or not harvest_token:
                return f"❌ Missing Harvest credentials for {user_id}"
            
            payload = {
                "harvest_account": harvest_account,
                "harvest_token": harvest_token
            }
            
            if client_id:
                payload["client_id"] = client_id
            if from_date:
                payload["from_date"] = from_date
            if to_date:
                payload["to_date"] = to_date
            
            result = await call_harvest_mcp_tool("list_invoices", payload)
            
            if "error" in result or "detail" in result:
                return f"❌ Error: {result.get('detail', result.get('error'))}"
            
            invoices = result.get('invoices', [])
            if not invoices:
                return "🧾 No invoices found."
            
            invoice_list = f"🧾 Invoices ({len(invoices)} total):\n\n"
            for invoice in invoices[:20]:
                invoice_list += f"• #{invoice.get('number', 'N/A')} - ${invoice.get('amount', 0):.2f}\n"
                invoice_list += f"  Client: {invoice.get('client', {}).get('name', 'N/A')}\n"
                invoice_list += f"  Status: {invoice.get('state', 'N/A')}\n"
            
            if len(invoices) > 20:
                invoice_list += f"\n... and {len(invoices) - 20} more invoices"
            
            return invoice_list
            
        except Exception as e:
            return f"❌ Error listing invoices: {str(e)}"
    
    @tool
    async def get_invoice(invoice_id: str) -> str:
        """Get details of a specific invoice by ID."""
        try:
            if not harvest_account or not harvest_token:
                return f"❌ Missing Harvest credentials for {user_id}"
            
            payload = {
                "invoice_id": invoice_id,
                "harvest_account": harvest_account,
                "harvest_token": harvest_token
            }
            
            result = await call_harvest_mcp_tool("get_invoice", payload)
            
            if "error" in result or "detail" in result:
                return f"❌ Error: {result.get('detail', result.get('error'))}"
            
            invoice_info = f"🧾 Invoice Details:\n"
            invoice_info += f"Number: #{result.get('number', 'N/A')}\n"
            invoice_info += f"Amount: ${result.get('amount', 0):.2f}\n"
            invoice_info += f"Client: {result.get('client', {}).get('name', 'N/A')}\n"
            invoice_info += f"Status: {result.get('state', 'N/A')}\n"
            invoice_info += f"Issue Date: {result.get('issue_date', 'N/A')}\n"
            
            return invoice_info
            
        except Exception as e:
            return f"❌ Error getting invoice: {str(e)}"
    
    @tool
    async def create_invoice(client_id: int, subject: str = None, notes: str = None) -> str:
        """Create a new invoice."""
        try:
            if not harvest_account or not harvest_token:
                return f"❌ Missing Harvest credentials for {user_id}"
            
            payload = {
                "client_id": client_id,
                "harvest_account": harvest_account,
                "harvest_token": harvest_token
            }
            
            if subject:
                payload["subject"] = subject
            if notes:
                payload["notes"] = notes
            
            result = await call_harvest_mcp_tool("create_invoice", payload)
            
            if "error" in result or "detail" in result:
                return f"❌ Error: {result.get('detail', result.get('error'))}"
            
            return f"✅ Created invoice #{result.get('number', 'N/A')} (ID: {result.get('id', 'N/A')})"
            
        except Exception as e:
            return f"❌ Error creating invoice: {str(e)}"
    
    @tool
    async def update_invoice(invoice_id: str, subject: str = None, notes: str = None) -> str:
        """Update an existing invoice."""
        try:
            if not harvest_account or not harvest_token:
                return f"❌ Missing Harvest credentials for {user_id}"
            
            payload = {
                "invoice_id": invoice_id,
                "harvest_account": harvest_account,
                "harvest_token": harvest_token
            }
            
            if subject:
                payload["subject"] = subject
            if notes:
                payload["notes"] = notes
            
            result = await call_harvest_mcp_tool("update_invoice", payload)
            
            if "error" in result or "detail" in result:
                return f"❌ Error: {result.get('detail', result.get('error'))}"
            
            return f"✅ Updated invoice {invoice_id}"
            
        except Exception as e:
            return f"❌ Error updating invoice: {str(e)}"
    
    @tool
    async def delete_invoice(invoice_id: str) -> str:
        """Delete an invoice by ID."""
        try:
            if not harvest_account or not harvest_token:
                return f"❌ Missing Harvest credentials for {user_id}"
            
            payload = {
                "invoice_id": invoice_id,
                "harvest_account": harvest_account,
                "harvest_token": harvest_token
            }
            
            result = await call_harvest_mcp_tool("delete_invoice", payload)
            
            if "error" in result or "detail" in result:
                return f"❌ Error: {result.get('detail', result.get('error'))}"
            
            return f"✅ Deleted invoice {invoice_id}"
            
        except Exception as e:
            return f"❌ Error deleting invoice: {str(e)}"
    
    # ==========================================
    # ESTIMATE TOOLS (Phase 3d)
    # ==========================================
    
    @tool
    async def list_estimates(client_id: int = None, from_date: str = None, to_date: str = None) -> str:
        """List estimates. Optionally filter by client_id and date range."""
        try:
            if not harvest_account or not harvest_token:
                return f"❌ Missing Harvest credentials for {user_id}"
            
            payload = {
                "harvest_account": harvest_account,
                "harvest_token": harvest_token
            }
            
            if client_id:
                payload["client_id"] = client_id
            if from_date:
                payload["from_date"] = from_date
            if to_date:
                payload["to_date"] = to_date
            
            result = await call_harvest_mcp_tool("list_estimates", payload)
            
            if "error" in result or "detail" in result:
                return f"❌ Error: {result.get('detail', result.get('error'))}"
            
            estimates = result.get('estimates', [])
            if not estimates:
                return "📋 No estimates found."
            
            estimate_list = f"📋 Estimates ({len(estimates)} total):\n\n"
            for estimate in estimates[:20]:
                estimate_list += f"• #{estimate.get('number', 'N/A')} - ${estimate.get('amount', 0):.2f}\n"
                estimate_list += f"  Client: {estimate.get('client', {}).get('name', 'N/A')}\n"
                estimate_list += f"  Status: {estimate.get('state', 'N/A')}\n"
            
            if len(estimates) > 20:
                estimate_list += f"\n... and {len(estimates) - 20} more estimates"
            
            return estimate_list
            
        except Exception as e:
            return f"❌ Error listing estimates: {str(e)}"
    
    @tool
    async def get_estimate(estimate_id: str) -> str:
        """Get details of a specific estimate by ID."""
        try:
            if not harvest_account or not harvest_token:
                return f"❌ Missing Harvest credentials for {user_id}"
            
            payload = {
                "estimate_id": estimate_id,
                "harvest_account": harvest_account,
                "harvest_token": harvest_token
            }
            
            result = await call_harvest_mcp_tool("get_estimate", payload)
            
            if "error" in result or "detail" in result:
                return f"❌ Error: {result.get('detail', result.get('error'))}"
            
            estimate_info = f"📋 Estimate Details:\n"
            estimate_info += f"Number: #{result.get('number', 'N/A')}\n"
            estimate_info += f"Amount: ${result.get('amount', 0):.2f}\n"
            estimate_info += f"Client: {result.get('client', {}).get('name', 'N/A')}\n"
            estimate_info += f"Status: {result.get('state', 'N/A')}\n"
            estimate_info += f"Issue Date: {result.get('issue_date', 'N/A')}\n"
            
            return estimate_info
            
        except Exception as e:
            return f"❌ Error getting estimate: {str(e)}"
    
    @tool
    async def create_estimate(client_id: int, subject: str = None, notes: str = None) -> str:
        """Create a new estimate."""
        try:
            if not harvest_account or not harvest_token:
                return f"❌ Missing Harvest credentials for {user_id}"
            
            payload = {
                "client_id": client_id,
                "harvest_account": harvest_account,
                "harvest_token": harvest_token
            }
            
            if subject:
                payload["subject"] = subject
            if notes:
                payload["notes"] = notes
            
            result = await call_harvest_mcp_tool("create_estimate", payload)
            
            if "error" in result or "detail" in result:
                return f"❌ Error: {result.get('detail', result.get('error'))}"
            
            return f"✅ Created estimate #{result.get('number', 'N/A')} (ID: {result.get('id', 'N/A')})"
            
        except Exception as e:
            return f"❌ Error creating estimate: {str(e)}"
    
    @tool
    async def update_estimate(estimate_id: str, subject: str = None, notes: str = None) -> str:
        """Update an existing estimate."""
        try:
            if not harvest_account or not harvest_token:
                return f"❌ Missing Harvest credentials for {user_id}"
            
            payload = {
                "estimate_id": estimate_id,
                "harvest_account": harvest_account,
                "harvest_token": harvest_token
            }
            
            if subject:
                payload["subject"] = subject
            if notes:
                payload["notes"] = notes
            
            result = await call_harvest_mcp_tool("update_estimate", payload)
            
            if "error" in result or "detail" in result:
                return f"❌ Error: {result.get('detail', result.get('error'))}"
            
            return f"✅ Updated estimate {estimate_id}"
            
        except Exception as e:
            return f"❌ Error updating estimate: {str(e)}"
    
    @tool
    async def delete_estimate(estimate_id: str) -> str:
        """Delete an estimate by ID."""
        try:
            if not harvest_account or not harvest_token:
                return f"❌ Missing Harvest credentials for {user_id}"
            
            payload = {
                "estimate_id": estimate_id,
                "harvest_account": harvest_account,
                "harvest_token": harvest_token
            }
            
            result = await call_harvest_mcp_tool("delete_estimate", payload)
            
            if "error" in result or "detail" in result:
                return f"❌ Error: {result.get('detail', result.get('error'))}"
            
            return f"✅ Deleted estimate {estimate_id}"
            
        except Exception as e:
            return f"❌ Error deleting estimate: {str(e)}"
    
    # ==========================================
    # EXTRA TIME ENTRY TOOLS (Phase 3d)
    # ==========================================
    
    @tool
    async def create_time_entry_via_start_end(project_id: int, task_id: int, spent_date: str, started_time: str, ended_time: str, notes: str = None) -> str:
        """Create a time entry using start and end times instead of duration."""
        try:
            if not harvest_account or not harvest_token:
                return f"❌ Missing Harvest credentials for {user_id}"
            
            payload = {
                "project_id": project_id,
                "task_id": task_id,
                "spent_date": spent_date,
                "started_time": started_time,
                "ended_time": ended_time,
                "harvest_account": harvest_account,
                "harvest_token": harvest_token
            }
            
            if notes:
                payload["notes"] = notes
            
            result = await call_harvest_mcp_tool("create_time_entry_via_start_end", payload)
            
            if "error" in result or "detail" in result:
                return f"❌ Error: {result.get('detail', result.get('error'))}"
            
            return f"✅ Created time entry: {result.get('hours', 0)}h (ID: {result.get('id', 'N/A')})"
            
        except Exception as e:
            return f"❌ Error creating time entry: {str(e)}"
    
    @tool
    async def delete_time_entry_external_reference(entry_id: str) -> str:
        """Delete external reference from a time entry."""
        try:
            if not harvest_account or not harvest_token:
                return f"❌ Missing Harvest credentials for {user_id}"
            
            payload = {
                "time_entry_id": entry_id,
                "harvest_account": harvest_account,
                "harvest_token": harvest_token
            }
            
            result = await call_harvest_mcp_tool("delete_time_entry_external_reference", payload)
            
            if "error" in result or "detail" in result:
                return f"❌ Error: {result.get('detail', result.get('error'))}"
            
            return f"✅ Deleted external reference from entry {entry_id}"
            
        except Exception as e:
            return f"❌ Error deleting external reference: {str(e)}"
    
    return [
        # Original 4 tools (simplified check_my_timesheet)
        check_my_timesheet, log_time_entry, list_my_projects, get_current_user_info,
        # Phase 1: Time Entry tools (5) - each tool handles a specific task
        get_time_entry, update_time_entry, delete_time_entry, restart_time_entry, stop_time_entry,
        # Phase 2: Project tools (4) - each tool handles a specific task
        get_project, create_project, update_project, delete_project,
        # Phase 2: Client tools (5) - each tool handles a specific task
        list_clients, get_client, create_client, update_client, delete_client,
        # Phase 3a: Contact tools (5) - each tool handles a specific task
        list_contacts, get_contact, create_contact, update_contact, delete_contact,
        # Phase 3a: Task tools (5) - each tool handles a specific task
        list_tasks, get_task, create_task, update_task, delete_task,
        # Phase 3b: User tools (5) - each tool handles a specific task
        list_users, get_user, create_user, update_user, delete_user,
        # Phase 3b: Company tool (1) - handles a specific task
        get_company,
        # Phase 3c: Expense tools (5) - each tool handles a specific task
        list_expenses, get_expense, create_expense, update_expense, delete_expense,
        # Phase 3d: Invoice tools (5) - each tool handles a specific task
        list_invoices, get_invoice, create_invoice, update_invoice, delete_invoice,
        # Phase 3d: Estimate tools (5) - each tool handles a specific task
        list_estimates, get_estimate, create_estimate, update_estimate, delete_estimate,
        # Phase 3d: Extra Time Entry tools (2) - each tool handles a specific task
        create_time_entry_via_start_end, delete_time_entry_external_reference
    ]

@activity.defn
@opik_trace("generate_ai_response_with_langchain")
async def generate_ai_response_with_langchain(request: ConversationRequest) -> AIResponse:
    """Generate AI response using centralized LLM Client with Harvest MCP tools and all best practices"""
    try:
        # Import inside activity to avoid Temporal sandbox restrictions
        from datetime import datetime, timedelta
        from langchain_core.messages import HumanMessage, AIMessage
        
        # Validate LLM client is initialized
        if not worker.llm_client:
            raise Exception("LLM Client not initialized")
        if not worker.llm_config:
            raise Exception("LLM Config not initialized")
        
        # Load conversation history
        history = await load_conversation_history(request.user_id, limit=10)
        chat_history = []
        
        # Reverse to get chronological order (oldest first)
        for msg in reversed(history):
            content = msg.get('content', '')
            message_type = msg.get('message_type', '')
            
            if message_type == 'INBOUND':
                chat_history.append(HumanMessage(content=content))
            elif message_type == 'OUTBOUND':
                chat_history.append(AIMessage(content=content))
        
        logger.info(f"Loaded {len(chat_history)} messages from conversation history")
        
        # Create Harvest MCP tools
        tools = create_harvest_tools(request.user_id)
        logger.info(f"🔧 Created {len(tools)} tools: {[t.name for t in tools]}")
        
        # Build tool descriptions for LLM
        tool_descriptions = []
        for tool in tools:
            tool_descriptions.append(f"- {tool.name}: {tool.description}")
        tools_text = "\n".join(tool_descriptions)
        
        # Create system message with tool information
        system_message_content = f"""You are a helpful timesheet assistant with cross-platform conversation capabilities.

You have access to {len(tools)} Harvest tools. Each tool handles a SPECIFIC task independently.

Available Tools:
{tools_text}

To use a tool, respond with JSON in this format:
{{"tool": "tool_name", "args": {{"arg1": "value1"}}}}

DECISION PROCESS - Follow this exactly:

Step 1: Use conversation history to understand CONTEXT
- What projects has the user mentioned?
- What are they currently working on?
- What time periods are they interested in?
- What was their previous question or concern?
Use this context to understand what they REALLY want

Step 2: Categorize the user's request
- Type A: Questions about their CURRENT work data (hours, entries, timesheet status, projects, clients, tasks, users, expenses, invoices, estimates, company info, contacts)
- Type B: Questions about PAST CONVERSATIONS themselves (what we discussed, what they said before)
- Type C: GENERAL chat (greetings, help, capabilities, casual conversation)

Step 3: Act based on type
- Type A → You MUST use a tool. Choose the RIGHT tool for the specific task. You CANNOT answer without fresh tool data.
- Type B → Use conversation history to answer about past discussions
- Type C → Respond naturally, using context to be helpful

Step 4: For Type A questions - Choose the RIGHT tool by category:

TIME ENTRIES (7 tools):
- Check timesheet summary → check_my_timesheet(date_range="this_week")
- Log new time entry → log_time_entry(project_name="X", hours=5, date="today", notes="...")
- Get specific entry → get_time_entry(entry_id="12345")
- Update entry → update_time_entry(entry_id="12345", hours=6, notes="...")
- Delete entry → delete_time_entry(entry_id="12345")
- Restart timer → restart_time_entry(entry_id="12345")
- Stop timer → stop_time_entry(entry_id="12345")

PROJECTS (5 tools):
- List all projects → list_my_projects()
- Get project details → get_project(project_id="456")
- Create project → create_project(client_id=123, name="New Project")
- Update project → update_project(project_id="456", name="Updated Name")
- Delete project → delete_project(project_id="456")

CLIENTS (5 tools):
- List all clients → list_clients()
- Get client details → get_client(client_id="789")
- Create client → create_client(name="New Client")
- Update client → update_client(client_id="789", name="Updated Name")
- Delete client → delete_client(client_id="789")

CONTACTS (5 tools):
- List contacts → list_contacts(client_id=789)
- Get contact → get_contact(contact_id="111")
- Create contact → create_contact(client_id=789, first_name="John", last_name="Doe")
- Update contact → update_contact(contact_id="111", email="new@email.com")
- Delete contact → delete_contact(contact_id="111")

TASKS (5 tools):
- List all tasks → list_tasks()
- Get task details → get_task(task_id="222")
- Create task → create_task(name="Development")
- Update task → update_task(task_id="222", name="Updated Task")
- Delete task → delete_task(task_id="222")

USERS (5 tools):
- List all users → list_users()
- Get user details → get_user(user_id="333")
- Create user → create_user(first_name="Jane", last_name="Smith", email="jane@example.com")
- Update user → update_user(user_id="333", email="updated@example.com")
- Delete user → delete_user(user_id="333")

COMPANY (1 tool):
- Get company info → get_company()

EXPENSES (5 tools):
- List expenses → list_expenses(project_id=456, from_date="2025-01-01", to_date="2025-12-31")
- Get expense → get_expense(expense_id="444")
- Create expense → create_expense(project_id=456, expense_category_id=123, spent_date="2025-11-20", total_cost=100.00)
- Update expense → update_expense(expense_id="444", total_cost=150.00)
- Delete expense → delete_expense(expense_id="444")

INVOICES (5 tools):
- List invoices → list_invoices(client_id=789, from_date="2025-01-01", to_date="2025-12-31")
- Get invoice → get_invoice(invoice_id="555")
- Create invoice → create_invoice(client_id=789)
- Update invoice → update_invoice(invoice_id="555", subject="Updated Invoice")
- Delete invoice → delete_invoice(invoice_id="555")

ESTIMATES (5 tools):
- List estimates → list_estimates(client_id=789, from_date="2025-01-01", to_date="2025-12-31")
- Get estimate → get_estimate(estimate_id="666")
- Create estimate → create_estimate(client_id=789)
- Update estimate → update_estimate(estimate_id="666", subject="Updated Estimate")
- Delete estimate → delete_estimate(estimate_id="666")

ADVANCED TIME ENTRY (2 tools):
- Create via start/end times → create_time_entry_via_start_end(project_id=456, task_id=222, spent_date="2025-11-20", started_time="09:00", ended_time="17:00")
- Delete external reference → delete_time_entry_external_reference(entry_id="12345")
- Get current user info → get_current_user_info()

Step 5: When you use check_my_timesheet
- Return its formatted output EXACTLY as-is
- Do NOT summarize, rephrase, or add commentary
- The tool already provides beautifully formatted responses

ABSOLUTE RULES:
1. You CANNOT state any facts about their current work without calling a tool first
2. If uncertain whether it's Type A or B → treat it as Type A (use tool)
3. Conversation history shows past context, NOT current Harvest data
4. Never invent project names, hours, dates, or entries
5. Each tool does ONE thing - use the right tool for the task
6. For check_my_timesheet output, return it exactly as-is
7. Always validate required parameters exist before calling a tool
8. Use conversation context to infer missing parameters when reasonable

ERROR PREVENTION:
- If user says "update entry" without ID → ask for entry_id
- If user says "create project" without client → ask for client_id
- If user says "log time" without project → ask for project_name
- If user says "delete" without ID → ask which item to delete
- If date format unclear → use "today" or "this_week" as default
- If hours not specified → ask for hours value

Example Patterns:
Type A - Timesheet: "check timesheet" → check_my_timesheet(date_range="this_week")
Type A - Log Time: "log 8 hours to Alpha" → log_time_entry(project_name="Alpha", hours=8)
Type A - Projects: "show projects" → list_my_projects()
Type A - Clients: "list clients" → list_clients()
Type A - Tasks: "what tasks are available" → list_tasks()
Type A - Users: "show team members" → list_users()
Type A - Company: "company info" → get_company()
Type A - Expenses: "show expenses for project 456" → list_expenses(project_id=456)
Type A - Invoices: "list invoices for client 789" → list_invoices(client_id=789)
Type A - Estimates: "show estimates" → list_estimates()
Type A - Get Entry: "show entry 12345" → get_time_entry(entry_id="12345")
Type A - Update: "update entry 12345 to 6 hours" → update_time_entry(entry_id="12345", hours=6)
Type A - Delete: "delete entry 12345" → delete_time_entry(entry_id="12345")
Type A - Monthly: "this month's hours" → check_my_timesheet(date_range="this_month")
Type A - Last Week: "last week's timesheet" → check_my_timesheet(date_range="last_week")
Type B - Past Conversations: "what did we discuss" → Use conversation history
Type C - General: "hello", "help", "thanks" → Respond naturally

Remember: You have 51 tools across 11 categories. Each does ONE thing. Use the right tool for each task.
"""
        
        # Convert LangChain messages to dict format for LLMClient
        llm_messages = [{"role": "system", "content": system_message_content}]
        
        # Add conversation history
        for msg in chat_history:
            if isinstance(msg, HumanMessage):
                llm_messages.append({"role": "user", "content": msg.content})
            elif isinstance(msg, AIMessage):
                llm_messages.append({"role": "assistant", "content": msg.content})
        
        # Add current message
        llm_messages.append({"role": "user", "content": request.message})
        
        # Call LLM using centralized client (with rate limiting, caching, error handling, Opik tracking)
        logger.info(f"🤖 Calling LLM with {len(llm_messages)} messages")
        llm_response = await worker.llm_client.chat_completion(
            messages=llm_messages,
            tenant_id=request.user_id,
            user_id=request.user_id,
            temperature=worker.llm_config.openai_temperature,
            max_tokens=worker.llm_config.openai_max_tokens
        )
        
        logger.info(f"📥 LLM response: {llm_response.total_tokens} tokens, ${llm_response.cost_usd:.4f}, cached={llm_response.cached}")
        
        # Check if response contains tool call
        ai_response_text = llm_response.content
        logger.info(f"🔍 Raw LLM output (first 200 chars): {ai_response_text[:200]}...")
        
        # Try to parse tool call from response
        import json
        import re
        
        # Look for JSON tool call in response - extract JSON object
        # Try to find complete JSON object with balanced braces
        tool_call_json = None
        try:
            # First, try to parse the entire response as JSON
            if ai_response_text.strip().startswith('{'):
                # Handle Python dict syntax (single quotes) by converting to JSON (double quotes)
                json_str = ai_response_text.strip().replace("'", '"')
                tool_call_json = json.loads(json_str)
            else:
                # Look for JSON embedded in text
                # Find opening brace and match balanced braces
                start_idx = ai_response_text.find('{')
                if start_idx != -1:
                    brace_count = 0
                    end_idx = start_idx
                    for i in range(start_idx, len(ai_response_text)):
                        if ai_response_text[i] == '{':
                            brace_count += 1
                        elif ai_response_text[i] == '}':
                            brace_count -= 1
                            if brace_count == 0:
                                end_idx = i + 1
                                break
                    
                    if end_idx > start_idx:
                        json_str = ai_response_text[start_idx:end_idx]
                        # Handle Python dict syntax (single quotes) by converting to JSON (double quotes)
                        json_str = json_str.replace("'", '"')
                        tool_call_json = json.loads(json_str)
        except (json.JSONDecodeError, ValueError) as e:
            logger.warning(f"Failed to parse JSON from response: {e}")
            tool_call_json = None
        
        # If JSON parsing failed, try to parse Python function call syntax
        # e.g., "search_my_timesheet(date_range="last_180_days", limit=1)"
        if not tool_call_json:
            func_match = re.match(r'(\w+)\((.*)\)', ai_response_text.strip())
            if func_match:
                tool_name = func_match.group(1)
                args_str = func_match.group(2)
                
                # Check if this is a valid tool name
                if any(t.name == tool_name for t in tools):
                    logger.info(f"🔍 Detected Python function call syntax: {tool_name}")
                    
                    # Parse arguments - simple key=value parsing
                    tool_args = {}
                    if args_str:
                        # Split by comma, but respect quotes
                        import ast
                        try:
                            # Use ast.literal_eval to safely parse the arguments
                            # Wrap in dict() to make it valid Python
                            args_dict_str = f"dict({args_str})"
                            tool_args = ast.literal_eval(args_dict_str)
                        except:
                            # Fallback: manual parsing
                            for arg in re.findall(r'(\w+)=(["\'].*?["\']|\d+\.?\d*|\w+)', args_str):
                                key, value = arg
                                # Remove quotes if present
                                if value.startswith('"') or value.startswith("'"):
                                    value = value[1:-1]
                                # Try to convert to number
                                try:
                                    if '.' in value:
                                        value = float(value)
                                    else:
                                        value = int(value)
                                except:
                                    pass
                                tool_args[key] = value
                    
                    tool_call_json = {"tool": tool_name, "args": tool_args}
                    logger.info(f"✅ Parsed function call: {tool_call_json}")
        
        if tool_call_json and "tool" in tool_call_json:
            try:
                tool_name = tool_call_json.get("tool")
                tool_args = tool_call_json.get("args", {})
                
                logger.info(f"🛠️ Tool call detected: {tool_name}")
                
                # Find and execute the tool
                tool_result = None
                tool_found = False
                for tool in tools:
                    if tool.name == tool_name:
                        tool_found = True
                        try:
                            tool_result = await tool.ainvoke(tool_args)
                            logger.info(f"✅ Tool {tool_name} executed successfully")
                            
                            # For search_my_timesheet, return result directly (no jokes here)
                            if tool_name == "search_my_timesheet":
                                ai_response_text = str(tool_result)
                            else:
                                # For other tools, ask LLM to format the response
                                llm_messages.append({"role": "assistant", "content": ai_response_text})
                                llm_messages.append({"role": "user", "content": f"Tool result: {tool_result}\n\nPlease provide a helpful response to the user based on this result."})
                                
                                final_response = await worker.llm_client.chat_completion(
                                    messages=llm_messages,
                                    tenant_id=request.user_id,
                                    user_id=request.user_id
                                )
                                ai_response_text = final_response.content
                        except Exception as e:
                            logger.error(f"❌ Tool {tool_name} failed: {e}")
                            ai_response_text = f"I encountered an error while using the {tool_name} tool: {str(e)}"
                        break
                
                # Handle tool not found
                if not tool_found:
                    logger.error(f"❌ Tool '{tool_name}' not found. Available tools: {[t.name for t in tools]}")
                    ai_response_text = f"I tried to use a tool called '{tool_name}', but it's not available. Let me help you differently."
            except Exception as e:
                logger.error(f"❌ Error executing tool: {e}")
                ai_response_text = f"I encountered an error while processing your request: {str(e)}"
        
        # Ensure we have a response
        if not ai_response_text or len(ai_response_text.strip()) == 0:
            ai_response_text = "I apologize, but I wasn't able to generate a proper response. Please try again."
            logger.warning(f"⚠️ Empty response generated, using fallback message")
        
        logger.info(f"✅ Generated AI response for {request.user_id}, length: {len(ai_response_text)}")
        
        return AIResponse(
            response=ai_response_text,
            conversation_id=request.conversation_id or f"conv_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            platform=request.platform,
            timestamp=datetime.utcnow().isoformat(),  # FIXED: Use UTC time in activities
            metadata={"model": "gpt-4-with-tools", "user_id": request.user_id, "tools_available": len(tools)}
        )
        
    except Exception as e:
        logger.error(f"❌ Failed to generate AI response with tools: {e}")
        return AIResponse(
            response=f"Sorry, I encountered an error: {str(e)}",
            conversation_id=request.conversation_id or "error",
            platform=request.platform,
            timestamp=datetime.utcnow().isoformat(),  # FIXED: Use UTC time in activities
            metadata={"error": str(e)}
        )

@activity.defn
async def store_conversation(user_id: str, message: str, response: str, platform: str, conversation_id: str, metadata: Optional[Dict[str, Any]] = None, agent_id: str = "conversation_agent", agent_privilege: PrivilegeLevel = PrivilegeLevel.LIMITED_WRITE) -> Dict[str, Any]:
    """Store conversation in Supabase (FIXED: Correct schema with INBOUND/OUTBOUND records)"""
    try:
        if not worker.supabase_client:
            logger.warning("⚠️ Supabase client not initialized")
            return {"status": "error", "error": "Supabase not available"}
        
        # Resolve the actual user_id that exists in the database
        # User ID should already be resolved from webhook, just use it directly
        actual_user_id = user_id
        logger.info(f"📝 Storing conversation for user: {actual_user_id}")
        
        stored_records = []
        
        # Store INBOUND message (user's message) using resolved user_id
        inbound_data = {
            "user_id": actual_user_id,  # Use resolved user ID
            "platform": platform.upper(),  # SMS or EMAIL
            "message_type": "INBOUND",
            "content": message,
            "metadata": {"conversation_id": conversation_id}
            # REMOVED: created_at - let Supabase auto-generate timestamp
        }
        
        # Add platform-specific fields (SCHEMA COMPLIANCE)
        if platform.lower() == "sms":
            if conversation_id.startswith("sms_"):
                inbound_data["sms_sid"] = conversation_id.replace("sms_", "")
            # Add phone_number from metadata if available
            if metadata and "from" in metadata:
                inbound_data["phone_number"] = metadata["from"]
        elif platform.lower() == "email":
            # Add email_address from metadata if available
            if metadata and "from" in metadata:
                inbound_data["email_address"] = metadata["from"]
        elif platform.lower() == "whatsapp":
            # NEW: WhatsApp platform support
            if conversation_id.startswith("whatsapp_"):
                inbound_data["sms_sid"] = conversation_id.replace("whatsapp_", "")  # Reuse sms_sid field for WhatsApp MessageSid
            # Add phone_number from metadata (WhatsApp uses phone numbers)
            if metadata and "from" in metadata:
                inbound_data["phone_number"] = metadata["from"]
        
        result1 = worker.supabase_client.table('conversations').insert(inbound_data).execute()
        stored_records.append("INBOUND")
        
        # Store OUTBOUND message (assistant's response) using resolved user_id
        if response:
            outbound_data = {
                "user_id": actual_user_id,  # Use resolved user ID
                "platform": platform.upper(),
                "message_type": "OUTBOUND", 
                "content": response,
                "metadata": {"conversation_id": conversation_id}
                # REMOVED: created_at - let Supabase auto-generate timestamp
            }
            
            # Add platform-specific fields (SCHEMA COMPLIANCE)
            if platform.lower() == "sms":
                if conversation_id.startswith("sms_"):
                    outbound_data["sms_sid"] = conversation_id.replace("sms_", "")
                # Add phone_number from metadata if available
                if metadata and "from" in metadata:
                    outbound_data["phone_number"] = metadata["from"]
            elif platform.lower() == "email":
                # Add email_address from metadata if available
                if metadata and "from" in metadata:
                    outbound_data["email_address"] = metadata["from"]
            elif platform.lower() == "whatsapp":
                # NEW: WhatsApp platform support (same as SMS structure)
                if conversation_id.startswith("whatsapp_"):
                    outbound_data["sms_sid"] = conversation_id.replace("whatsapp_", "")  # Reuse sms_sid field
                # Add phone_number from metadata (WhatsApp uses phone numbers)
                if metadata and "from" in metadata:
                    outbound_data["phone_number"] = metadata["from"]
            
            result2 = worker.supabase_client.table('conversations').insert(outbound_data).execute()
            stored_records.append("OUTBOUND")
        
        logger.info(f"✅ Stored conversation for {user_id}: {', '.join(stored_records)}")
        return {"status": "success", "records": stored_records}
        
    except Exception as e:
        logger.error(f"❌ Failed to store conversation: {e}")
        return {"status": "error", "error": str(e)}

@activity.defn
async def log_conversation_metrics(platform: str, input_length: int, output_length: int) -> Dict[str, Any]:
    """Log conversation metrics to Opik for monitoring and analytics"""
    try:
        # Log metrics using opik_integration wrapper
        try:
            from opik_integration import log_metric
            # Log platform usage metrics
            log_metric("conversation_count", 1, 
                      tags=["conversation", platform], 
                      metadata={"platform": platform})
            
            # Log message length metrics
            log_metric("input_message_length", input_length,
                      tags=["message_length", "input", platform],
                      metadata={"platform": platform, "type": "input"})
            
            log_metric("output_message_length", output_length,
                      tags=["message_length", "output", platform], 
                      metadata={"platform": platform, "type": "output"})
            
            # Log response ratio (output/input)
            if input_length > 0:
                response_ratio = output_length / input_length
                log_metric("response_ratio", response_ratio,
                          tags=["efficiency", platform],
                          metadata={"platform": platform, "input_length": input_length, "output_length": output_length})
        except ImportError:
            logger.debug("📊 Opik not available - metrics not logged")
        except Exception as opik_error:
            logger.warning(f"⚠️ Opik metric logging failed: {opik_error}")
        
        logger.info(f"📊 Logged conversation metrics for {platform}: input={input_length}, output={output_length}")
        return {"status": "success", "platform": platform, "metrics_logged": 4}
        
    except Exception as e:
        logger.error(f"❌ Failed to log conversation metrics: {e}")
        return {"status": "error", "error": str(e)}

@activity.defn
async def send_email_response(to_email: str, message: str, user_id: str) -> Dict[str, Any]:
    """Send email response via Gmail SMTP"""
    try:
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        
        # Get Gmail credentials from environment (loaded from Azure Key Vault)
        gmail_user = os.getenv('GMAIL_USER')
        gmail_password = os.getenv('GMAIL_PASSWORD')
        
        if not gmail_user or not gmail_password:
            logger.error("Gmail credentials not configured")
            return {'status': 'error', 'error': 'Gmail credentials missing', 'platform': 'email'}
        
        # Create email message
        msg = MIMEMultipart()
        msg['From'] = gmail_user
        msg['To'] = to_email
        msg['Subject'] = "Timesheet Assistant Response"
        msg.attach(MIMEText(message, 'plain'))
        
        # Send via Gmail SMTP with TLS encryption
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(gmail_user, gmail_password)
        server.sendmail(gmail_user, to_email, msg.as_string())
        server.quit()
        
        logger.info(f"✅ Email sent to {user_id} at {to_email}")
        return {
            'status': 'success',
            'platform': 'email',
            'recipient': to_email,
            'user_id': user_id,
            'timestamp': datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to send email to {user_id}: {e}")
        return {
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }

@activity.defn
async def send_whatsapp_response(to_whatsapp: str, message: str, user_id: str) -> Dict[str, Any]:
    """Send WhatsApp response via Twilio (IDENTICAL to SMS but with WhatsApp formatting)"""
    try:
        # Get Twilio credentials from environment (same as SMS)
        account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        
        if not account_sid or not auth_token:
            raise Exception("Missing Twilio credentials")
        
        # Initialize Twilio client (same as SMS)
        from twilio.rest import Client
        client = Client(account_sid, auth_token)
        
        # Send WhatsApp message via Twilio Sandbox
        whatsapp_message = client.messages.create(
            body=message,
            from_='whatsapp:+14155238886',  # Twilio WhatsApp Sandbox number
            to=f'whatsapp:{to_whatsapp}'    # Add whatsapp: prefix to recipient
        )
        
        logger.info(f"✅ WhatsApp sent to {to_whatsapp}: {whatsapp_message.sid}")
        
        return {
            'status': 'success',
            'message_sid': whatsapp_message.sid,
            'to': to_whatsapp,
            'platform': 'whatsapp',
            'timestamp': datetime.utcnow().isoformat()  # FIXED: Use UTC time in activities
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to send WhatsApp to {to_whatsapp}: {e}")
        return {
            'status': 'error',
            'error': str(e),
            'to': to_whatsapp,
            'platform': 'whatsapp',
            'timestamp': datetime.utcnow().isoformat()
        }


@activity.defn
async def send_platform_response(platform: str, response_text: str, user_contact: str, user_id: str) -> Dict[str, Any]:
    """Send response via appropriate platform (SMS, Email, or WhatsApp)"""
    try:
        if platform.lower() == 'sms':
            # Send SMS via Twilio (reuse existing SMS function)
            return await send_sms_reminder(user_contact, response_text, user_id)
        elif platform.lower() == 'email':
            # Gmail SMTP implementation
            return await send_email_response(user_contact, response_text, user_id)
        elif platform.lower() == 'whatsapp':
            # NEW: WhatsApp via Twilio
            return await send_whatsapp_response(user_contact, response_text, user_id)
        else:
            raise Exception(f"Unsupported platform: {platform}")
            
    except Exception as e:
        logger.error(f"❌ Failed to send {platform} response: {e}")
        return {
            'status': 'error',
            'error': str(e),
            'platform': platform,
            'timestamp': datetime.utcnow().isoformat()  # FIXED: Use UTC time in activities
        }

# =============================================================================
# CONVERSATION WORKFLOWS (from conversation_workflows.py)
# =============================================================================

@workflow.defn
class ConversationWorkflow:
    """Handle cross-platform conversations with AI agent"""
    
    @workflow.run
    @opik_trace("conversation_workflow")
    async def run(self, request: ConversationRequest) -> AIResponse:
        """Execute conversation workflow"""
        try:
            logger.info(f"🚀 Starting conversation for {request.user_id} via {request.platform}")
            
            # Step 1: Generate AI response using LangChain agent with tools
            ai_response = await workflow.execute_activity(
                generate_ai_response_with_langchain,
                request,
                start_to_close_timeout=timedelta(seconds=120),  # Longer timeout for AI processing
                retry_policy=RetryPolicy(maximum_attempts=2)
            )
            
            # Step 2: Store conversation in database
            storage_result = await workflow.execute_activity(
                store_conversation,
                args=[
                    request.user_id,
                    request.message,
                    ai_response.response,
                    request.platform,
                    ai_response.conversation_id,
                    request.metadata  # Pass metadata for schema compliance
                ],
                start_to_close_timeout=timedelta(seconds=30),
                retry_policy=RetryPolicy(maximum_attempts=2)
            )
            
            # Log custom metrics for monitoring
            await workflow.execute_activity(
                log_conversation_metrics,
                args=[
                    request.platform,
                    len(request.message),
                    len(ai_response.response) if ai_response.response else 0
                ],
                start_to_close_timeout=timedelta(seconds=10)
            )
            
            # Step 3: Response will be handled by the calling webhook
            # (Removed duplicate response sending to prevent double SMS/messages)
            logger.info(f"📤 AI response generated, will be sent by webhook handler")
            
            logger.info(f"✅ Conversation workflow completed for {request.user_id}")
            return ai_response
            
        except Exception as e:
            logger.error(f"❌ Conversation workflow failed for {request.user_id}: {e}")
            return AIResponse(
                response=f"I apologize, but I'm experiencing technical difficulties. Please try again later.",
                conversation_id=request.conversation_id or "error",
                platform=request.platform,
                timestamp=workflow.now().isoformat(),  # FIXED: Use workflow.now() instead of datetime.now()
                metadata={"error": str(e)}
            )

@workflow.defn
class CrossPlatformRoutingWorkflow:
    """Handle cross-platform conversation routing (MISSING from unified version)"""
    
    @workflow.run
    async def run(self, request: ConversationRequest) -> Dict[str, Any]:
        """Route conversation across platforms"""
        workflow.logger.info(f"🔀 Cross-platform routing for {request.user_id}")
        
        try:
            # Execute conversation workflow
            ai_response = await workflow.execute_activity(
                generate_ai_response_with_langchain,
                request,
                start_to_close_timeout=timedelta(seconds=30)
            )
            
            # Send response via platform (FIXED: use correct parameters)
            send_result = await workflow.execute_activity(
                send_platform_response,
                args=[request.platform, ai_response.response, request.metadata.get('from', ''), request.user_id],
                start_to_close_timeout=timedelta(seconds=15)
            )
            
            return {
                "status": "success",
                "response": ai_response.response,
                "send_result": send_result,
                "user_id": request.user_id
            }
            
        except Exception as e:
            workflow.logger.error(f"❌ Cross-platform routing failed: {e}")
            return {
                "status": "error",
                "message": str(e),
                "user_id": request.user_id
            }
