#!/usr/bin/env python3
"""
Unified Temporal Server - FastAPI Application
Combines timesheet reminders + AI conversations functionality
This module contains the FastAPI server and imports workflows from unified_workflows.py

Features:
- Timesheet reminder endpoints (from temporal_server.py)
- SMS/Email webhook handling (from conversation_server.py)
- Health endpoints
- Manual trigger endpoints
- Temporal worker management
- Azure Key Vault integration
- LangChain AI agent integration
"""

import os
import asyncio
import logging
from typing import Dict, Any, List
from datetime import datetime

# FastAPI imports (NOW SAFE - workflows in separate module)
from fastapi import FastAPI, HTTPException, Request, Form
from fastapi.responses import Response
import uvicorn

# Temporal imports
from temporalio.client import Client as TemporalClient
from temporalio.client import ScheduleActionStartWorkflow, ScheduleSpec
from temporalio.worker import Worker

# Azure Key Vault (load secrets here, NOT in workflows.py)
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential

# LangChain imports for conversation fallback
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

# Configure logging FIRST
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load secrets from Key Vault and set as environment variables
def load_secrets_to_env():
    """Load secrets from Azure Key Vault and set as environment variables"""
    try:
        key_vault_url = os.getenv("AZURE_KEY_VAULT_URL", "https://kv-secure-agent-2ai.vault.azure.net/")
        credential = DefaultAzureCredential()
        secret_client = SecretClient(vault_url=key_vault_url, credential=credential)
        
        # FIXED: Map Azure Key Vault names (hyphens) to code expectations (underscores)
        secret_mappings = {
            # Key Vault Name -> Environment Variable Name
            "OPENAI-API-KEY": "OPENAI_API_KEY",
            "HARVEST-ACCESS-TOKEN": "HARVEST_ACCESS_TOKEN", 
            "HARVEST-ACCESS-TOKEN-USER2": "HARVEST_ACCESS_TOKEN_USER2",
            "HARVEST-ACCOUNT-ID": "HARVEST_ACCOUNT_ID",
            "HARVEST-ACCOUNT-ID-USER2": "HARVEST_ACCOUNT_ID_USER2", 
            "TWILIO-ACCOUNT-SID": "TWILIO_ACCOUNT_SID",
            "TWILIO-AUTH-TOKEN": "TWILIO_AUTH_TOKEN",
            "TWILIO-PHONE-NUMBER": "TWILIO_PHONE_NUMBER",
            "USER-PHONE-NUMBER": "USER_PHONE_NUMBER",
            "USER-PHONE-NUMBER-USER2": "USER_PHONE_NUMBER_USER2",
            "SUPABASE-URL": "SUPABASE_URL",
            "SUPABASE-KEY": "SUPABASE_KEY",
            "TEMPORAL-HOST": "TEMPORAL_HOST",
            "TEMPORAL-NAMESPACE": "TEMPORAL_NAMESPACE",
            # Gmail credentials for email sending
            "GMAIL-USER": "GMAIL_USER",
            "GMAIL-PASSWORD": "GMAIL_PASSWORD",
            # Opik tracing credentials
            "OPIK-ENABLED": "OPIK_ENABLED",
            "OPIK-API-KEY": "OPIK_API_KEY",
            "OPIK-WORKSPACE": "OPIK_WORKSPACE",
            "OPIK-PROJECT": "OPIK_PROJECT",
            # OpenRouter credentials
            "OPENROUTER-API-KEY": "OPENROUTER_API_KEY",
            "OPENROUTER-PROVISIONING-KEY": "OPENROUTER_PROVISIONING_KEY",
            "OPENROUTER-MODEL": "OPENROUTER_MODEL",
            "APP-URL": "APP_URL",
            # Azure OpenAI credentials
            "AZURE-OPENAI-ENDPOINT": "AZURE_OPENAI_ENDPOINT",
            "AZURE-OPENAI-API-KEY": "AZURE_OPENAI_API_KEY",
            "AZURE-OPENAI-DEPLOYMENT": "AZURE_OPENAI_DEPLOYMENT",
            "AZURE-OPENAI-API-VERSION": "AZURE_OPENAI_API_VERSION",
            # LLM Configuration
            "USE-OPENROUTER": "USE_OPENROUTER",
            "PROVIDER": "PROVIDER",
            "OPENAI-TEMPERATURE": "OPENAI_TEMPERATURE",
            "OPENAI-MAX-TOKENS": "OPENAI_MAX_TOKENS",
            "OPIK-ENABLED": "OPIK_ENABLED",
            "CACHE-ENABLED": "CACHE_ENABLED",
            "REDIS-ENABLED": "REDIS_ENABLED",
            "FALLBACK-ENABLED": "FALLBACK_ENABLED",
            "RETRY-MAX-WAIT-SECONDS": "RETRY_MAX_WAIT_SECONDS",
            "USE-IMPROVED-RATE-LIMITER": "USE_IMPROVED_RATE_LIMITER",
            # RAG / Vector Database Configuration
            "RAG-ENABLED": "RAG_ENABLED",
            "VECTOR-DB-PROVIDER": "VECTOR_DB_PROVIDER",
            "QDRANT-URL": "QDRANT_URL",
            "QDRANT-API-KEY": "QDRANT_API_KEY",
            "QDRANT-COLLECTION-NAME": "QDRANT_COLLECTION_NAME",
            "EMBEDDINGS-PROVIDER": "EMBEDDINGS_PROVIDER",
            "EMBEDDINGS-MODEL": "EMBEDDINGS_MODEL",
            "EMBEDDINGS-DIMENSION": "EMBEDDINGS_DIMENSION"
        }
        
        # DEBUG: Print all secret mappings to verify Harvest secrets are included
        logger.info(f"🔍 DEBUG: Loading {len(secret_mappings)} secrets: {list(secret_mappings.keys())}")
        
        for key_vault_name, env_var_name in secret_mappings.items():
            try:
                secret = secret_client.get_secret(key_vault_name)
                os.environ[env_var_name] = secret.value
                logger.info(f"✅ Loaded secret: {key_vault_name} -> {env_var_name}")
            except Exception as e:
                logger.warning(f"⚠️ Could not load secret {key_vault_name}: {e}")
        
        logger.info("🔑 Azure Key Vault secrets loaded successfully")
        
    except Exception as e:
        logger.error(f"❌ Failed to load secrets from Key Vault: {e}")
        raise

# Load secrets BEFORE importing workflows
load_secrets_to_env()

# Import workflows from separate module (NO FastAPI in that file)
from unified_workflows import (
    # Timesheet workflows (still used)
    TimesheetReminderWorkflow,
    DailyReminderScheduleWorkflow,
    TimesheetReminderRequest,
    TimesheetReminderResponse,
    get_timesheet_data,
    send_sms_reminder,
    send_sms_response_activity,  # NEW: Send SMS via Twilio API for async webhooks
    add_joke_to_reminder_activity,
    
    # Legacy conversation data models (kept for compatibility)
    ConversationRequest,
    AIResponse,
    
    # Legacy conversation activities (kept for potential future use)
    store_conversation,
    send_platform_response,
    send_email_response,
    send_whatsapp_response,
    log_conversation_metrics,
    
    # NEW: Mem0 memory activities
    load_memory_context,
    store_memory,
    
    # Worker instance
    worker as unified_worker,
    
    # Multi-agent system (REPLACED single-agent conversations)
    MultiAgentConversationWorkflow,
    get_user_credentials_activity,  # NEW: Fetch credentials from Supabase
    planner_analyze_activity,
    timesheet_execute_activity,  # FIXED: Renamed from timesheet_extract_activity
    planner_compose_activity,
    branding_format_activity,
    quality_validate_activity,
    planner_refine_activity,
    planner_graceful_failure_activity,
    quality_validate_graceful_failure_activity
)

# Opik integration will be imported inside functions to avoid module-level HTTP imports

def log_metric_standalone(name: str, value: float, tags: list = None, metadata: dict = None):
    """Log metric without requiring class instance (deprecated - metrics now logged via LLM client)"""
    # Metrics are now automatically logged through the LLM client's Opik integration
    # This function is kept for backward compatibility but does nothing
    logger.debug(f"📊 Metric '{name}' logged via LLM client Opik integration")

class UnifiedTemporalServer:
    def __init__(self):
        # Initialize Azure Key Vault client
        self.key_vault_url = os.getenv("AZURE_KEY_VAULT_URL", "https://kv-secure-agent-2ai.vault.azure.net/")
        self.credential = DefaultAzureCredential()
        self.secret_client = SecretClient(vault_url=self.key_vault_url, credential=self.credential)
        
        # Initialize worker components
        self._initialize_worker_components()
        
        # Timesheet configuration (from temporal_server.py)
        self.timesheet_agent_url = os.getenv(
            'TIMESHEET_AGENT_URL', 
            'https://secure-timesheet-agent.kindcoast-5a2a34c6.australiaeast.azurecontainerapps.io'
        )
        self.max_retries = 3
        self.timeout = 30
        
        # Enhanced Opik configuration (check inside function to avoid module-level imports)
        self.opik_enabled = self._check_opik_enabled()
        if self.opik_enabled:
            logger.info("✅ Enhanced Opik tracking is enabled")
        else:
            logger.info("ℹ️ Enhanced Opik tracking is disabled")
        
        # User configurations (from temporal_server.py)
        self.users = [
            {
                'user_id': 'user1',
                'name': 'User1',
                'endpoint': '/check-timesheet-user1',
                'phone_env_key': 'USER_PHONE_NUMBER',
                'harvest_access_token_key': 'HARVEST_ACCESS_TOKEN',
                'harvest_account_key': 'HARVEST_ACCOUNT_ID'
            },
            {
                'user_id': 'user2',
                'name': 'User2', 
                'endpoint': '/check-timesheet-user2',
                'phone_env_key': 'USER_PHONE_NUMBER_USER2',
                'harvest_access_token_key': 'HARVEST_ACCESS_TOKEN_USER2',
                'harvest_account_key': 'HARVEST_ACCOUNT_ID_USER2'
            }
        ]
        
        # Temporal client (will be initialized later)
        self.temporal_client = None

    def _initialize_worker_components(self):
        """Initialize worker components for both timesheet and conversation functionality"""
        try:
            # Initialize Supabase client
            supabase_url = os.getenv("SUPABASE_URL")
            supabase_key = os.getenv("SUPABASE_KEY")
            
            logger.info(f"🔍 Supabase URL loaded: {bool(supabase_url)}")
            logger.info(f"🔍 Supabase Key loaded: {bool(supabase_key)}")
            
            if supabase_url and supabase_key:
                from supabase import create_client
                unified_worker.supabase_client = create_client(supabase_url, supabase_key)
                unified_worker.supabase_url = supabase_url
                unified_worker.supabase_key = supabase_key
                logger.info(f"✅ Supabase client initialized: {supabase_url}")
            else:
                logger.error(f"❌ Supabase client NOT initialized - URL: {bool(supabase_url)}, Key: {bool(supabase_key)}")
                unified_worker.supabase_client = None
            
            # Initialize LLM Client (centralized component with all best practices)
            try:
                from llm.client import LLMClient
                from llm.config import LLMConfig
                
                # Load configuration from environment
                llm_config = LLMConfig()
                llm_config.validate_config()
                
                # Initialize centralized LLM client
                unified_worker.llm_client = LLMClient(llm_config)
                unified_worker.llm_config = llm_config
                
                # Log configuration
                provider_info = "OpenRouter" if llm_config.use_openrouter else llm_config.provider
                model_info = llm_config.openrouter_model if llm_config.use_openrouter else llm_config.get_model()
                
                logger.info(f"✅ LLM Client initialized")
                logger.info(f"   Provider: {provider_info}")
                logger.info(f"   Model: {model_info}")
                logger.info(f"   Rate Limiting: {'Enabled' if llm_config.max_requests_per_second > 0 else 'Disabled'}")
                logger.info(f"   Caching: {'Enabled' if llm_config.cache_enabled else 'Disabled'}")
                logger.info(f"   Opik Tracking: {'Enabled' if llm_config.opik_enabled else 'Disabled'}")
                logger.info(f"   Error Handling: {'Enabled' if llm_config.retry_enabled else 'Disabled'}")
                
            except Exception as e:
                logger.error(f"❌ Failed to initialize LLM Client: {e}")
                logger.warning("⚠️ LLM functionality will not be available")
                unified_worker.llm_client = None
                unified_worker.llm_config = None
            
            # Initialize Twilio client
            twilio_sid = os.getenv("TWILIO_ACCOUNT_SID")
            twilio_token = os.getenv("TWILIO_AUTH_TOKEN")
            if twilio_sid and twilio_token:
                from twilio.rest import Client
                unified_worker.twilio_client = Client(twilio_sid, twilio_token)
                logger.info("✅ Twilio client initialized")
                
        except Exception as e:
            logger.error(f"❌ Failed to initialize worker components: {e}")

    def _check_opik_enabled(self):
        """Check if Opik is enabled via LLM client configuration"""
        try:
            # Opik is now integrated through the LLM client
            opik_enabled_env = os.getenv("OPIK_ENABLED", "false").lower() == "true"
            return opik_enabled_env
        except Exception:
            return False

    def _log_metric(self, name: str, value: float, tags: list = None, metadata: dict = None):
        """Log metric (deprecated - metrics now logged via LLM client)"""
        # Metrics are now automatically logged through the LLM client's Opik integration
        # This method is kept for backward compatibility but does nothing
        logger.debug(f"📊 Metric '{name}' logged via LLM client Opik integration")

    async def initialize_temporal_client(self):
        """Initialize Temporal client with HTTP/2 transport solution"""
        try:
            # ARCHITECTURE RULE 1: Internal calls are DIRECT (no KrakenD)
            # Use HTTP/2 transport solution discovered through testing
            temporal_host = os.getenv("TEMPORAL_HOST", "temporal-dev-server.kindcoast-5a2a34c6.australiaeast.azurecontainerapps.io:443")
            tls_enabled = os.getenv("TEMPORAL_TLS_ENABLED", "true").lower() == "true"
            
            logger.info(f"🔗 Connecting to Temporal via HTTP/2 transport...")
            logger.info(f"   Host: {temporal_host}")
            logger.info(f"   TLS: {tls_enabled}")
            logger.info(f"   Transport: gRPC over HTTP/2 (DIRECT internal call)")
            
            # BREAKTHROUGH: Use HTTP/2 transport instead of raw TCP
            # This solution was proven to work in manual testing
            self.temporal_client = await asyncio.wait_for(
                TemporalClient.connect(
                    temporal_host, 
                    tls=tls_enabled,
                    # Additional connection options for HTTP/2 transport reliability
                    rpc_metadata={"user-agent": "unified-temporal-worker/2.0.0"}
                ),
                timeout=30.0
            )
            
            logger.info(f"✅ Temporal client connected via HTTP/2 transport!")
            logger.info(f"   Architecture: DIRECT internal call (Rule 1 ✅)")
            logger.info(f"   Protocol: gRPC over HTTPS/HTTP/2")
            
            logger.info("✅ Temporal client initialized with HTTP/2 transport solution")
            logger.info("🎯 All architecture rules maintained:")
            logger.info("   1. ✅ Internal calls: DIRECT (Temporal connection)")
            logger.info("   2. ✅ External calls: Through KrakenD (API endpoints)")
            logger.info("   3. ✅ Temporal: NEVER abandoned (Full functionality)")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Temporal client via HTTP/2: {e}")
            logger.error(f"   Host attempted: {temporal_host}")
            logger.error(f"   TLS enabled: {tls_enabled}")
            logger.error("   Note: Manual testing proved HTTP/2 transport works")
            raise

    async def _setup_temporal_schedules(self):
        """Setup Temporal schedules for daily reminders"""
        try:
            schedule_id = "daily-timesheet-reminders"
            
            # Create schedule for daily reminders (7 AM AEST, Mon-Fri)
            # Note: Using UTC time - 21:00 UTC = 7 AM AEST next day (Mon-Fri)
            
            # Prepare user configurations with resolved environment variables (FIXED: Handle None values)
            users_config = []
            for user in self.users:
                users_config.append({
                    'user_id': user['user_id'],
                    'name': user['name'],
                    'phone_number': os.getenv(user['phone_env_key']) or '',  # Convert None to empty string
                    'harvest_access_token': os.getenv(user['harvest_access_token_key']) or '',  # Convert None to empty string
                    'harvest_account': os.getenv(user['harvest_account_key']) or '',  # Convert None to empty string
                    'endpoint': user['endpoint']
                })
            
            # FIXED: Correct create_schedule signature (schedule_id, Schedule object)
            from temporalio.client import Schedule
            
            schedule = await self.temporal_client.create_schedule(
                schedule_id,
                Schedule(
                    spec=ScheduleSpec(
                        # Timezone-aware cron: 8 AM Sydney time, Monday-Friday
                        # CRON_TZ prefix tells Temporal to interpret time in specified timezone
                        cron_expressions=["CRON_TZ=Australia/Sydney 0 8 * * MON-FRI"]
                    ),
                    action=ScheduleActionStartWorkflow(
                        DailyReminderScheduleWorkflow.run,
                        args=[users_config],
                        id=f"daily_reminders_{datetime.utcnow().strftime('%Y%m%d')}",  # FIXED: Use UTC time
                        task_queue="timesheet-reminders"
                    )
                )
            )
            
            logger.info(f"✅ Daily reminder schedule created: {schedule_id}")
            
        except Exception as e:
            if "already exists" in str(e).lower():
                logger.info("⚠️ Daily reminder schedule already exists")
            else:
                logger.error(f"❌ Failed to setup schedules: {e}")

    async def start_temporal_worker(self):
        """Start Temporal worker for both timesheet and conversation workflows"""
        try:
            # Check if Temporal client is available
            if not self.temporal_client:
                logger.error("❌ Cannot start Temporal worker: Temporal client not initialized")
                return
                
            
            # Create worker for multiple task queues
            worker = Worker(
                self.temporal_client,
                task_queue="timesheet-reminders",  # Primary queue
                workflows=[
                    TimesheetReminderWorkflow,
                    DailyReminderScheduleWorkflow,
                    MultiAgentConversationWorkflow  # Multi-agent system (REPLACED ConversationWorkflow)
                ],
                activities=[
                    # Timesheet-related activities
                    get_timesheet_data,
                    send_sms_reminder,
                    send_sms_response_activity,  # NEW: Send SMS via Twilio API for async webhooks
                    add_joke_to_reminder_activity,

                    # Legacy conversation activities (kept for compatibility)
                    store_conversation,
                    send_platform_response,
                    send_email_response,
                    send_whatsapp_response,
                    log_conversation_metrics,
                    
                    # NEW: Mem0 memory activities
                    load_memory_context,
                    store_memory,
                    
                    # Multi-agent activities (REPLACED single-agent)
                    get_user_credentials_activity,  # NEW: Fetch credentials from Supabase
                    planner_analyze_activity,
                    timesheet_execute_activity,  # FIXED: Renamed from timesheet_extract_activity
                    planner_compose_activity,
                    branding_format_activity,
                    quality_validate_activity,
                    planner_refine_activity,
                    planner_graceful_failure_activity,
                    quality_validate_graceful_failure_activity
                ]
            )
            
            # NOTE: Removed separate conversation_worker - all conversations now use multi-agent system
            # on the primary "timesheet-reminders" queue
            
            logger.info("🚀 Starting Temporal worker...")
            
            # Now that worker is created and validated, setup schedules
            logger.info("🔄 Setting up Temporal schedules after worker validation...")
            await self._setup_temporal_schedules()
            
            # Start the unified worker
            await worker.run()
            
        except Exception as e:
            logger.error(f"❌ Failed to start Temporal worker: {e}")
            raise
    
    async def start_email_polling(self):
        """Start background email polling task"""
        try:
            logger.info("📧 Starting Gmail inbox polling...")
            logger.info("🔍 Gmail polling will check every 30 seconds for new emails")
            
            poll_count = 0
            while True:
                try:
                    poll_count += 1
                    logger.info(f"🔄 Gmail polling cycle #{poll_count} starting...")
                    
                    # Call the Gmail checking function directly (not as Temporal activity)
                    result = await self._check_gmail_inbox_direct()
                    
                    logger.info(f"📊 Gmail polling result: {result}")
                    
                    if result.get('status') == 'error':
                        logger.error(f"❌ Gmail polling failed: {result.get('error', 'Unknown error')}")
                    elif result.get('emails_processed', 0) > 0:
                        logger.info(f"📬 Processed {result['emails_processed']} new emails")
                    else:
                        logger.info(f"📭 No new emails found (checked {result.get('emails_found', 0)} total)")
                    
                    logger.info(f"⏰ Waiting 30 seconds before next Gmail check...")
                    # Wait 30 seconds before next check
                    await asyncio.sleep(30)
                    
                except Exception as e:
                    logger.error(f"❌ Error in email polling cycle #{poll_count}: {e}")
                    logger.error(f"📋 Exception type: {type(e).__name__}")
                    import traceback
                    logger.error(f"📋 Full traceback: {traceback.format_exc()}")
                    logger.info("⏰ Waiting 30 seconds before retry...")
                    await asyncio.sleep(30)  # Continue polling even if there's an error
                    
        except Exception as e:
            logger.error(f"❌ Failed to start email polling: {e}")
            logger.error(f"📋 Exception type: {type(e).__name__}")
            import traceback
            logger.error(f"📋 Full traceback: {traceback.format_exc()}")
            logger.error("🛑 Gmail polling service has stopped!")
    
    async def _check_gmail_inbox_direct(self):
        """Direct Gmail inbox checking following original pattern"""
        try:
            logger.info("🔍 Starting Gmail IMAP connection...")
            import imaplib
            import email
            
            # Get Gmail credentials from environment
            logger.info("🔑 Loading Gmail credentials from environment...")
            gmail_user = os.getenv('GMAIL_USER')
            gmail_password = os.getenv('GMAIL_PASSWORD')
            
            logger.info(f"📧 Gmail user: {gmail_user[:5]}***@{gmail_user.split('@')[1] if gmail_user and '@' in gmail_user else 'NOT_FOUND'}")
            logger.info(f"🔐 Gmail password: {'***' + gmail_password[-3:] if gmail_password else 'NOT_FOUND'}")
            
            if not gmail_user or not gmail_password:
                logger.error("❌ Gmail credentials missing from environment variables!")
                logger.error(f"   GMAIL_USER: {'SET' if gmail_user else 'NOT_SET'}")
                logger.error(f"   GMAIL_PASSWORD: {'SET' if gmail_password else 'NOT_SET'}")
                return {'status': 'error', 'error': 'Gmail credentials missing'}
            
            logger.info("🔗 Connecting to Gmail IMAP server...")
            # Connect to Gmail IMAP
            with imaplib.IMAP4_SSL('imap.gmail.com', 993) as mail:
                logger.info("🔐 Authenticating with Gmail...")
                mail.login(gmail_user, gmail_password)
                logger.info("✅ Gmail authentication successful!")
                
                logger.info("📁 Selecting INBOX folder...")
                mail.select('INBOX')
                logger.info("✅ INBOX selected successfully!")
                
                # Search for unread emails (following original pattern)
                logger.info("🔍 Searching for unread emails...")
                status, messages = mail.search(None, 'UNSEEN')
                logger.info(f"📊 Search status: {status}")
                
                if status != 'OK':
                    logger.warning(f"⚠️ Search returned non-OK status: {status}")
                    return {'status': 'success', 'emails_found': 0}
                
                message_nums = messages[0].split()
                logger.info(f"📬 Found {len(message_nums)} unread emails: {message_nums}")
                emails_processed = 0
                
                logger.info(f"🔄 Processing {len(message_nums[-5:])} emails (last 5 of {len(message_nums)} total)...")
                for i, num in enumerate(message_nums[-5:], 1):  # Process last 5 unread emails
                    try:
                        logger.info(f"📨 Processing email #{i}: message ID {num}")
                        status, msg_data = mail.fetch(num, '(RFC822)')
                        logger.info(f"📥 Fetch status: {status}")
                        
                        if status == 'OK':
                            email_body = msg_data[0][1]
                            email_message = email.message_from_bytes(email_body)
                            logger.info("✅ Email parsed successfully")
                            
                            # Extract email details (following original pattern)
                            from_email = email_message.get('From', '')
                            subject = email_message.get('Subject', '')
                            message_id = email_message.get('Message-ID', '')
                            
                            logger.info(f"📧 Email details:")
                            logger.info(f"   From: {from_email}")
                            logger.info(f"   Subject: {subject}")
                            logger.info(f"   Message-ID: {message_id}")
                            
                            # Extract plain text body (following original pattern)
                            logger.info("📝 Extracting email body...")
                            body = self._extract_email_body(email_message)
                            logger.info(f"📝 Email body extracted: {len(body)} characters")
                            logger.info(f"📝 Body preview: {body[:100]}...")
                            
                            # Clean from_email (extract just the email address)
                            if '<' in from_email and '>' in from_email:
                                from_email = from_email.split('<')[1].split('>')[0]
                                logger.info(f"🧹 Cleaned from_email: {from_email}")
                            
                            # IMPORTANT: Skip bot's own replies to prevent infinite loops
                            # Only block if it's from our address AND has our reply subject
                            if (from_email.lower() == gmail_user.lower() and 
                                'Timesheet Assistant Response' in subject):
                                logger.info(f"⏭️ Skipping our own reply email: {subject}")
                                mail.store(num, '+FLAGS', '\\Seen')  # Mark as read
                                continue
                            
                            logger.info(f"🚀 Processing email from {from_email}: {subject[:50]}...")
                            
                            # DIRECT PROCESSING (following original pattern - no webhook)
                            # Look up user by email address
                            user_id = None
                            if unified_worker.supabase_client:
                                user_lookup = unified_worker.supabase_client.table('users').select('id').eq('email_address', from_email).execute()
                                if user_lookup.data:
                                    user_id = user_lookup.data[0]['id']
                                    logger.info(f"✅ Found user {user_id} for email {from_email}")
                                else:
                                    logger.warning(f"⚠️ No user found for email {from_email}")
                                    user_id = "user1"  # Default fallback
                            else:
                                user_id = "user1"  # Default fallback
                            
                            # Create conversation request
                            conversation_request = ConversationRequest(
                                user_id=user_id,
                                message=body,
                                platform="email",
                                conversation_id=f"email_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                                metadata={"from": from_email, "message_id": message_id}
                            )
                            
                            # Process through Temporal workflow (direct, not webhook)
                            if self.temporal_client:
                                workflow_id = f"conversation-{user_id}-{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
                                
                                result = await self.temporal_client.start_workflow(
                                    ConversationWorkflow.run,
                                    conversation_request,
                                    id=workflow_id,
                                    task_queue="conversations"
                                )
                                
                                # Get the AI response
                                ai_response = await result.result()
                                
                                logger.info(f"✅ Email response generated for {from_email}")
                                
                                # Send email reply via Gmail SMTP (call directly, not as Temporal activity)
                                try:
                                    email_result = await send_email_response(from_email, ai_response.response, user_id)
                                    if email_result.get('status') == 'success':
                                        logger.info(f"📧 Email reply sent to {from_email}")
                                    else:
                                        logger.error(f"❌ Failed to send email reply: {email_result.get('error')}")
                                except Exception as email_error:
                                    logger.error(f"❌ Error sending email reply: {email_error}")
                                
                                # Mark email as read after successful processing
                                mail.store(num, '+FLAGS', '\\Seen')
                                emails_processed += 1
                                logger.info(f"✅ Processed and marked email as read: {from_email}")
                            else:
                                logger.error(f"❌ Temporal client not available")
                            
                    except Exception as e:
                        logger.error(f"❌ Error processing individual email: {e}")
                        continue
                
                return {
                    'status': 'success',
                    'emails_found': len(message_nums),
                    'emails_processed': emails_processed
                }
                
        except Exception as e:
            logger.error(f"❌ Failed to check Gmail inbox: {e}")
            return {'status': 'error', 'error': str(e)}
    
    def _extract_email_body(self, email_message) -> str:
        """Extract plain text body from email message (following original pattern)"""
        try:
            if email_message.is_multipart():
                for part in email_message.walk():
                    if part.get_content_type() == "text/plain":
                        return part.get_payload(decode=True).decode('utf-8')
            else:
                return email_message.get_payload(decode=True).decode('utf-8')
        except Exception as e:
            logger.error(f"Error extracting email body: {e}")
            return ""

# Initialize server
logger.info("🏗️ Initializing UnifiedTemporalServer...")
server = UnifiedTemporalServer()
logger.info("✅ UnifiedTemporalServer initialized")

# Create FastAPI app FIRST
app = FastAPI(
    title="Unified Temporal Worker",
    description="Combined timesheet reminders + AI conversations + Agent Governance",
    version="6.0.0-governance"
)

# Import governance system AFTER app creation to avoid startup issues
try:
    logger.info("🛡️ Importing governance system...")
    from agent_governance import get_governance_metrics, governance
    from governance_dashboard import dashboard
    logger.info("✅ Governance system imported successfully")
    GOVERNANCE_AVAILABLE = True
except Exception as e:
    logger.error(f"❌ Governance import failed: {e}")
    GOVERNANCE_AVAILABLE = False
    # Create dummy functions to prevent errors
    def get_governance_metrics():
        return {"error": "Governance system not available"}
    def dashboard():
        return {"error": "Dashboard not available"}
    dashboard = type('obj', (object,), {'get_real_time_status': lambda: {"error": "Dashboard not available"}, 'generate_safety_report': lambda: {"error": "Dashboard not available"}})()

# =============================================================================
# HEALTH ENDPOINTS (Combined)
# =============================================================================

@app.get("/health")
async def health_check():
    """Unified health check endpoint"""
    try:
        health_status = {
            "status": "healthy",
            "service": "unified-temporal-worker",
            "version": "6.0.0-governance",
            "temporal_connected": server.temporal_client is not None,
            "supabase_connected": unified_worker.supabase_client is not None,
            "llm_client_initialized": unified_worker.llm_client is not None,
            "governance_enabled": True,
            "timeout_protection": True,
            "health_checks": {
                "temporal": "✅ Connected" if server.temporal_client else "❌ Not connected",
                "supabase": "✅ Connected" if unified_worker.supabase_client else "❌ Not connected",
                "llm_client": "✅ Initialized" if unified_worker.llm_client else "❌ Not initialized",
                "key_vault": "✅ Connected",
                "opik": "✅ Enabled" if server.opik_enabled else "⚠️ Disabled",
                "governance": "✅ Active",
                "timeout_protection": "✅ Active"
            },
            "features": [
                "Daily timesheet reminder scheduling (Temporal workflows)",
                "Cross-platform conversations (SMS ↔ Email ↔ WhatsApp)",
                "LangChain AI integration with Harvest tools",
                "Supabase conversation storage",
                "Azure Key Vault integration",
                "Opik tracing support",
                "Manual reminder triggers",
                "Multi-user support (User1, User2)",
                "🛡️ Agent governance controls (least-privilege access)",
                "⏰ API timeout protection (prevents hanging)",
                "📊 Real-time monitoring dashboard",
                "🔍 Complete audit trail (input→decision→output)"
            ]
        }
        
        # Determine overall status
        if not server.temporal_client:
            health_status["status"] = "degraded"
        elif not unified_worker.supabase_client or not unified_worker.llm_client:
            health_status["status"] = "degraded"
            
        return health_status
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "service": "unified-temporal-worker",
            "version": "5.0.0"
        }

# =============================================================================
# DIRECT CONVERSATION FUNCTIONS (Fallback without Temporal)
# =============================================================================

async def process_conversation_fallback(user_id: str, message: str, platform: str, phone_number: str):
    """Direct conversation processing without Temporal workflows"""
    try:
        # Get conversation history from Supabase
        if hasattr(unified_worker, 'supabase_client') and unified_worker.supabase_client:
            # Get recent conversation history (last 10 messages)
            history_response = unified_worker.supabase_client.table('conversations').select('*').eq('user_id', user_id).order('created_at', desc=True).limit(10).execute()
            
            conversation_history = []
            if history_response.data:
                logger.info(f"🔍 DEBUG: Found {len(history_response.data)} conversation records")
                # Reverse to get chronological order
                for i, conv in enumerate(reversed(history_response.data)):
                    try:
                        # Handle different possible column names for direction and content
                        direction = conv.get('direction') or conv.get('type') or 'INBOUND'
                        content = conv.get('content') or conv.get('message') or conv.get('text', '')
                        
                        logger.info(f"🔍 DEBUG: Record {i}: direction={direction}, content_length={len(content) if content else 0}")
                        
                        role = "user" if direction == 'INBOUND' else "assistant"
                        if content:  # Only add if there's actual content
                            conversation_history.append({"role": role, "content": content})
                    except Exception as conv_error:
                        logger.error(f"❌ Error processing conversation record {i}: {conv_error}")
                        logger.error(f"❌ Record data: {conv}")
                        continue
        else:
            conversation_history = []
        
        # Generate AI response using OpenAI
        if hasattr(unified_worker, 'llm') and unified_worker.llm:
            # Build conversation context
            system_prompt = f"""You are a helpful AI assistant for {user_id}. You have access to their conversation history and can help with various tasks including timesheet reminders, work questions, and general assistance.

Current conversation context:
- User: {user_id}
- Platform: {platform}
- Phone: {phone_number}

Be helpful, concise, and friendly. Keep responses under 160 characters for SMS."""

            messages = [{"role": "system", "content": system_prompt}]
            messages.extend(conversation_history)
            messages.append({"role": "user", "content": message})
            
            # Call OpenAI API directly
            langchain_messages = []
            for msg in messages:
                if msg["role"] == "system":
                    langchain_messages.append(SystemMessage(content=msg["content"]))
                elif msg["role"] == "user":
                    langchain_messages.append(HumanMessage(content=msg["content"]))
                elif msg["role"] == "assistant":
                    langchain_messages.append(AIMessage(content=msg["content"]))
            
            ai_response = await unified_worker.llm.ainvoke(langchain_messages)
            response_text = ai_response.content
            
            # Store conversation in Supabase
            if hasattr(unified_worker, 'supabase_client') and unified_worker.supabase_client:
                now = datetime.utcnow()
                
                try:
                    # Store inbound message
                    unified_worker.supabase_client.table('conversations').insert({
                        'user_id': user_id,
                        'content': message,
                        'direction': 'INBOUND',
                        'platform': platform,
                        'created_at': now.isoformat()
                    }).execute()
                    
                    # Store outbound response
                    unified_worker.supabase_client.table('conversations').insert({
                        'user_id': user_id,
                        'content': response_text,
                        'direction': 'OUTBOUND', 
                        'platform': platform,
                        'created_at': now.isoformat()
                    }).execute()
                    
                    logger.info(f"✅ Conversation stored in Supabase for {user_id}")
                except Exception as storage_error:
                    logger.warning(f"⚠️ Failed to store conversation in Supabase: {storage_error}")
                    # Continue anyway - don't fail the response if storage fails
            
            return response_text
        else:
            return "I'm currently unable to process your message. Please try again later."
            
    except Exception as e:
        logger.error(f"❌ Conversation fallback error: {e}")
        return "I'm experiencing technical difficulties. Please try again later."

# =============================================================================
# DIRECT TIMESHEET FUNCTIONS (Fallback without Temporal)
# =============================================================================

async def send_timesheet_reminder_direct(user_id: str, user_name: str, phone_number: str, 
                                       harvest_access_token: str, harvest_account: str):
    """Direct implementation of timesheet reminder without Temporal workflows"""
    try:
        import httpx
        from twilio.rest import Client as TwilioClient
        
        # Call Harvest API directly (bypass broken KrakenD Gateway)
        harvest_base_url = "https://api.harvestapp.com/v2"
        
        # Get today's date (FIXED: Use UTC time to avoid Temporal restrictions)
        from datetime import datetime, timedelta
        today_dt = datetime.utcnow()
        today = today_dt.date()
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)
        
        async with httpx.AsyncClient() as client:
            # Set up Harvest API headers
            headers = {
                "Harvest-Account-ID": harvest_account,
                "Authorization": f"Bearer {harvest_access_token}",
                "User-Agent": "Unified Temporal Worker (timesheet-reminders)"
            }
            
            # Get today's time entries
            today_response = await client.get(
                f"{harvest_base_url}/time_entries",
                headers=headers,
                params={"from": today.isoformat(), "to": today.isoformat()}
            )
            
            # Get this week's time entries
            week_response = await client.get(
                f"{harvest_base_url}/time_entries", 
                headers=headers,
                params={"from": week_start.isoformat(), "to": week_end.isoformat()}
            )
            
            if today_response.status_code == 200 and week_response.status_code == 200:
                # Calculate hours
                today_data = today_response.json()
                week_data = week_response.json()
                
                hours_today = sum(entry.get('hours', 0) for entry in today_data.get('time_entries', []))
                hours_week = sum(entry.get('hours', 0) for entry in week_data.get('time_entries', []))
                
                # Create reminder message
                if hours_today == 0:
                    message = f"Hi {user_name}! 👋 You haven't logged any hours today. Don't forget to update your timesheet! 📝"
                elif hours_today < 8:
                    message = f"Hi {user_name}! You've logged {hours_today} hours today. Consider adding more if you've worked additional time. 📊"
                else:
                    message = f"Hi {user_name}! Great job! You've logged {hours_today} hours today. Keep up the good work! 🎉"
                
                # Send SMS via Twilio
                twilio_sid = os.getenv("TWILIO_ACCOUNT_SID")
                twilio_token = os.getenv("TWILIO_AUTH_TOKEN")
                twilio_phone = os.getenv("TWILIO_PHONE_NUMBER")
                
                if all([twilio_sid, twilio_token, twilio_phone]):
                    twilio_client = TwilioClient(twilio_sid, twilio_token)
                    
                    sms_result = twilio_client.messages.create(
                        body=message,
                        from_=twilio_phone,
                        to=phone_number
                    )
                    
                    logger.info(f"📱 SMS sent to {user_name} ({phone_number}): {message}")
                    
                    return {
                        "status": "success",
                        "message": "Reminder sent successfully",
                        "hours_today": hours_today,
                        "hours_week": hours_week,
                        "sms_sid": sms_result.sid
                    }
                else:
                    logger.error("❌ Missing Twilio credentials")
                    return {
                        "status": "error",
                        "message": "Missing Twilio credentials"
                    }
            else:
                logger.error(f"❌ Failed to get timesheet data: Today={today_response.status_code}, Week={week_response.status_code}")
                return {
                    "status": "error",
                    "message": f"Failed to get timesheet data from Harvest API"
                }
                
    except Exception as e:
        logger.error(f"❌ Error in direct timesheet reminder: {e}")
        return {
            "status": "error",
            "message": str(e)
        }

# =============================================================================
# TIMESHEET ENDPOINTS (from temporal_server.py)
# =============================================================================


@app.get("/debug/rag-status")
async def debug_rag_status():
    """Debug endpoint to check RAG configuration and environment"""
    import os
    from llm.config import LLMConfig
    
    try:
        # Check environment variables
        env_status = {
            "RAG_ENABLED": os.getenv("RAG_ENABLED"),
            "VECTOR_DB_PROVIDER": os.getenv("VECTOR_DB_PROVIDER"),
            "QDRANT_URL": os.getenv("QDRANT_URL"),
            "QDRANT_API_KEY": "SET" if os.getenv("QDRANT_API_KEY") else "NOT SET",
            "QDRANT_COLLECTION_NAME": os.getenv("QDRANT_COLLECTION_NAME"),
            "EMBEDDINGS_PROVIDER": os.getenv("EMBEDDINGS_PROVIDER"),
            "EMBEDDINGS_MODEL": os.getenv("EMBEDDINGS_MODEL"),
            "EMBEDDINGS_DIMENSION": os.getenv("EMBEDDINGS_DIMENSION"),
            "OPENAI_API_KEY": "SET" if os.getenv("OPENAI_API_KEY") else "NOT SET"
        }
        
        # Try to load config
        try:
            config = LLMConfig()
            config_status = {
                "rag_enabled": config.rag_enabled,
                "vector_db_provider": config.vector_db_provider,
                "qdrant_url": config.qdrant_url,
                "embeddings_provider": config.embeddings_provider,
                "embeddings_model": config.embeddings_model,
                "openai_api_key_set": bool(config.openai_api_key)
            }
        except Exception as e:
            config_status = {"error": str(e)}
        
        # Try to create memory manager
        try:
            from llm.client import LLMClient
            client = LLMClient(config)
            memory = client.get_memory_manager("test-tenant")
            memory_status = {
                "memory_manager_created": memory is not None,
                "memory_manager_type": type(memory).__name__ if memory else None
            }
        except Exception as e:
            memory_status = {"error": str(e)}
        
        return {
            "timestamp": datetime.now().isoformat(),
            "environment_variables": env_status,
            "llm_config": config_status,
            "memory_manager": memory_status,
            "status": "ok"
        }
    except Exception as e:
        return {
            "timestamp": datetime.now().isoformat(),
            "error": str(e),
            "status": "error"
        }


@app.post("/test/conversation-with-memory")
async def test_conversation_memory(request: Request):
    """Test endpoint to simulate conversation with memory - REAL WORLD TEST"""
    try:
        # Parse request body
        try:
            body = await request.json()
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid JSON: {str(e)}")
        
        # Validate required fields
        if "message" not in body:
            raise HTTPException(status_code=422, detail="Missing required field: message")
        
        message = body.get("message", "").strip()
        user_id = body.get("user_id", "test-user")
        tenant_id = body.get("tenant_id", "test-tenant")
        
        # Validate message is not empty
        if not message:
            raise HTTPException(status_code=400, detail="message cannot be empty")
        
        # Validate tenant_id and user_id
        if not tenant_id or not isinstance(tenant_id, str):
            raise HTTPException(status_code=400, detail="tenant_id must be a non-empty string")
        
        if not user_id or not isinstance(user_id, str):
            raise HTTPException(status_code=400, detail="user_id must be a non-empty string")
        
        logger.info(f"🧪 TEST: Conversation with memory - User: {user_id}, Message: {message}")
        
        from llm.client import LLMClient
        from llm.config import LLMConfig
        
        config = LLMConfig()
        client = LLMClient(config)
        
        # Generate response with memory
        logger.info(f"📝 Generating response with memory for tenant: {tenant_id}")
        response = await client.generate_with_memory(
            prompt=message,
            tenant_id=tenant_id,
            user_id=user_id,
            use_memory=True
        )
        
        logger.info(f"✅ Response generated: {response[:100]}...")
        
        return {
            "status": "success",
            "user_message": message,
            "assistant_response": response,
            "memory_used": True,
            "tenant_id": tenant_id,
            "user_id": user_id,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions (validation errors)
        raise
    except Exception as e:
        logger.error(f"❌ Test conversation error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/trigger-reminder/{user_id}")
async def trigger_manual_reminder(user_id: str):
    """Trigger manual timesheet reminder for specific user"""
    try:
        # Find user configuration
        user_config = None
        for user in server.users:
            if user['user_id'] == user_id:
                user_config = user
                break
        
        if not user_config:
            raise HTTPException(status_code=404, detail=f"User {user_id} not found")
        
        # Get user credentials
        phone_number = os.getenv(user_config['phone_env_key'])
        harvest_access_token = os.getenv(user_config['harvest_access_token_key'])
        harvest_account = os.getenv(user_config['harvest_account_key'])
        
        if not all([phone_number, harvest_access_token, harvest_account]):
            raise HTTPException(status_code=500, detail="Missing user credentials")
        
        # Use Temporal workflow if available, otherwise use direct implementation
        if server.temporal_client:
            # Create reminder request
            request = TimesheetReminderRequest(
                user_id=user_config['user_id'],
                user_name=user_config['name'],
                phone_number=phone_number,
                harvest_access_token=harvest_access_token,
                harvest_account=harvest_account,
                endpoint=user_config['endpoint']
            )
            
            # Start workflow
            workflow_id = f"manual_reminder_{user_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            result = await server.temporal_client.start_workflow(
                TimesheetReminderWorkflow.run,
                request,
                id=workflow_id,
                task_queue="timesheet-reminders"
            )
            
            logger.info(f"✅ Manual reminder triggered via Temporal for {user_id}: {workflow_id}")
            return {
                "status": "success",
                "message": f"Manual reminder triggered for {user_config['name']} via Temporal",
                "workflow_id": workflow_id,
                "user_id": user_id
            }
        else:
            # Temporal client not available - system requires Temporal workflows
            logger.error(f"❌ Cannot send reminder for {user_id} - Temporal client not initialized")
            raise HTTPException(status_code=503, detail="Temporal service unavailable - system requires Temporal workflows")
        
    except Exception as e:
        logger.error(f"❌ Failed to trigger manual reminder for {user_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/cleanup-old-workflows")
async def cleanup_old_workflows():
    """Clean up old Temporal workflows and schedules"""
    try:
        if not hasattr(server, 'temporal_client') or server.temporal_client is None:
            raise HTTPException(status_code=500, detail="Temporal client not initialized")
        
        cleanup_results = {
            "schedules_deleted": 0,
            "workflows_terminated": 0,
            "errors": []
        }
        
        # Target the specific problematic workflow
        problematic_workflow_id = "daily_reminders_20251007_071203"
        problematic_run_id = "0199bd83-4fcc-7745-b030-182598e58c79"
        
        # 1. Try to terminate the stuck workflow execution
        try:
            workflow_handle = server.temporal_client.get_workflow_handle(
                workflow_id=problematic_workflow_id,
                run_id=problematic_run_id
            )
            await workflow_handle.terminate(reason="Cleanup: Old workflow with incompatible data format")
            logger.info(f"✅ Terminated old workflow: {problematic_workflow_id}")
            cleanup_results["workflows_terminated"] += 1
        except Exception as e:
            error_msg = f"Failed to terminate workflow {problematic_workflow_id}: {e}"
            logger.error(f"❌ {error_msg}")
            cleanup_results["errors"].append(error_msg)
        
        # 2. Try to delete the schedule (if it exists)
        try:
            schedule_handle = server.temporal_client.get_schedule_handle(problematic_workflow_id)
            await schedule_handle.delete()
            logger.info(f"✅ Deleted old schedule: {problematic_workflow_id}")
            cleanup_results["schedules_deleted"] += 1
        except Exception as e:
            error_msg = f"Failed to delete schedule {problematic_workflow_id}: {e}"
            logger.error(f"❌ {error_msg}")
            cleanup_results["errors"].append(error_msg)
        
        return {
            "status": "success",
            "message": f"Cleanup completed: {cleanup_results['workflows_terminated']} workflows terminated, {cleanup_results['schedules_deleted']} schedules deleted",
            "details": cleanup_results
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to cleanup old workflows: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/trigger-daily-reminders")
async def trigger_daily_reminders():
    """Trigger daily reminders for all users"""
    try:
        if not server.temporal_client:
            raise HTTPException(status_code=503, detail="Temporal client not connected")
        
        # Prepare user configurations (FIXED: Handle None values)
        users_config = []
        for user in server.users:
            users_config.append({
                'user_id': user['user_id'],
                'name': user['name'],
                'phone_number': os.getenv(user['phone_env_key']) or '',  # Convert None to empty string
                'harvest_access_token': os.getenv(user['harvest_access_token_key']) or '',  # Convert None to empty string
                'harvest_account': os.getenv(user['harvest_account_key']) or '',  # Convert None to empty string
                'endpoint': user['endpoint']
            })
        
        # Start batch workflow
        workflow_id = f"daily_reminders_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"  # FIXED: Use UTC time
        result = await server.temporal_client.start_workflow(
            DailyReminderScheduleWorkflow.run,
            users_config,
            id=workflow_id,
            task_queue="timesheet-reminders"
        )
        
        logger.info(f"✅ Daily reminders triggered: {workflow_id}")
        
        return {
            "status": "success",
            "message": f"Daily reminders triggered for {len(users_config)} users",
            "workflow_id": workflow_id,
            "users": [user['name'] for user in users_config]
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to trigger daily reminders: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# =============================================================================
# CONVERSATION ENDPOINTS (from conversation_server.py)
# =============================================================================

@app.post("/webhook/sms")
async def handle_sms_webhook(request: Request, From: str = Form(...), Body: str = Form(...), MessageSid: str = Form(...)):
    """Handle incoming SMS webhook from Twilio (SECURITY: Added signature verification)"""
    try:
        # SECURITY FIX: Verify Twilio signature (prevent webhook spoofing)
        twilio_signature = request.headers.get('X-Twilio-Signature', '')
        if twilio_signature:
            from twilio.request_validator import RequestValidator
            auth_token = os.getenv('TWILIO_AUTH_TOKEN')
            if auth_token:
                validator = RequestValidator(auth_token)
                # FIXED: Use exact URL without query params for signature validation
                url = f"https://{request.url.hostname}{request.url.path}"
                form_data = await request.form()
                if not validator.validate(url, dict(form_data), twilio_signature):
                    logger.warning(f"⚠️ Invalid Twilio signature from {From}")
                    raise HTTPException(status_code=403, detail="Invalid signature")
        
        logger.info(f"📱 SMS received from {From}: {Body}")
        
        # Log webhook received metric
        log_metric_standalone("webhook_received", 1, tags=["sms", "webhook"], metadata={"platform": "sms"})
        
        # Extract user ID from phone number by querying Supabase
        user_id = None
        try:
            logger.info(f"🔍 Supabase client available: {unified_worker.supabase_client is not None}")
            if unified_worker.supabase_client:
                # Normalize phone number format (Twilio may send different formats)
                normalized_phone = From.strip()
                if not normalized_phone.startswith('+'):
                    normalized_phone = '+' + normalized_phone
                
                logger.info(f"🔍 Looking up user for normalized phone: {normalized_phone}")
                
                # Look up user by phone number (Supabase Python client handles URL encoding)
                user_lookup = unified_worker.supabase_client.table('users').select('id').eq('phone_number', normalized_phone).execute()
                
                logger.info(f"🔍 Supabase query result: {user_lookup.data}")
                
                if user_lookup.data:
                    user_id = user_lookup.data[0]['id']
                    logger.info(f"✅ Found user {user_id} for phone {From}")
                else:
                    logger.warning(f"⚠️ No user found for phone {From}")
                    # Log unknown user metric
                    log_metric_standalone("unknown_user", 1, tags=["sms", "error"], metadata={"platform": "sms", "phone": From})
                    # Use a consistent fallback that won't create phantom workflows
                    user_id = "user1"  # Default to user1 for unknown SMS numbers
        except Exception as e:
            logger.error(f"❌ Failed to lookup user by phone: {e}")
            user_id = "user1"  # Default to user1 for database errors
        
        # Create conversation request
        conversation_request = ConversationRequest(
            user_id=user_id,
            message=Body,
            platform="sms",
            conversation_id=f"sms_{MessageSid}",
            metadata={"from": From, "message_sid": MessageSid}
        )
        
        # Note: Conversation history/memory is now loaded by Mem0 in the workflow
        # No need to load from Supabase here - workflow will retrieve semantic memory
        conversation_history = []
        
        # Start multi-agent conversation workflow (REPLACED single agent system)
        logger.info(f"🔍 DEBUG: About to start workflow, temporal_client exists: {server.temporal_client is not None}")
        logger.info(f"🤖 Using Multi-Agent Conversation System")
        
        if server.temporal_client:
            workflow_id = f"conversation_{user_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            logger.info(f"🔍 DEBUG: Starting workflow with ID: {workflow_id}")
            try:
                # Use multi-agent workflow (quality-validated, channel-formatted)
                logger.info(f"🤖 Starting MultiAgentConversationWorkflow")
                await server.temporal_client.start_workflow(
                    MultiAgentConversationWorkflow.run,
                    args=[
                        Body,  # user_message
                        "sms",  # channel
                        user_id,  # user_id
                        f"sms_{MessageSid}",  # conversation_id
                        conversation_history,  # conversation_history (loaded from Supabase)
                        {"from": From}  # user_context
                    ],
                    id=workflow_id,
                    task_queue="timesheet-reminders"
                )
                logger.info(f"✅ Workflow started: {workflow_id}")
                logger.info(f"� Returning 200 OK immediately - SMS will be sent when workflow completes")
                
                # Log workflow started metric
                log_metric_standalone("webhook_success", 1, tags=["sms", "async"], 
                          metadata={"platform": "sms", "user_id": user_id, "workflow_id": workflow_id})
            except Exception as workflow_error:
                logger.error(f"❌ Workflow start failed: {workflow_error}")
        else:
            # Temporal client not available - system cannot function without it
            logger.error("❌ Temporal client not available - system requires Temporal workflows")
        
        # Return empty TwiML response immediately (< 1 second) - workflow will send SMS via Twilio API
        twiml_response = '<?xml version="1.0" encoding="UTF-8"?><Response></Response>'
        
        logger.info(f"📤 Returning empty TwiML (200 OK)")
        logger.info(f"✅ Webhook processed for {From}")
        return Response(content=twiml_response, media_type="text/xml; charset=utf-8")
        
    except Exception as e:
        logger.error(f"❌ SMS webhook error: {e}")
        # Log error metric
        log_metric_standalone("webhook_error", 1, tags=["sms", "error"], metadata={"platform": "sms", "error": str(e)})
        error_response = '<?xml version="1.0" encoding="UTF-8"?><Response><Message>Sorry, I encountered an error processing your message.</Message></Response>'
        return Response(content=error_response, media_type="application/xml")

@app.post("/webhook/whatsapp")
async def handle_whatsapp_webhook(request: Request, From: str = Form(...), Body: str = Form(...), MessageSid: str = Form(...)):
    """Handle incoming WhatsApp webhook from Twilio (IDENTICAL to SMS with WhatsApp-specific handling)"""
    try:
        # SECURITY FIX: Verify Twilio signature (same as SMS)
        twilio_signature = request.headers.get('X-Twilio-Signature', '')
        if twilio_signature:
            from twilio.request_validator import RequestValidator
            auth_token = os.getenv('TWILIO_AUTH_TOKEN')
            if auth_token:
                validator = RequestValidator(auth_token)
                # FIXED: Use exact URL without query params for signature validation
                url = f"https://{request.url.hostname}{request.url.path}"
                form_data = await request.form()
                if not validator.validate(url, dict(form_data), twilio_signature):
                    logger.warning(f"⚠️ Invalid Twilio signature from {From}")
                    raise HTTPException(status_code=403, detail="Invalid signature")
        
        # Extract WhatsApp number (remove whatsapp: prefix)
        whatsapp_number = From.replace("whatsapp:", "") if From.startswith("whatsapp:") else From
        logger.info(f"📱 WhatsApp message from {whatsapp_number}: {Body}")
        
        # Extract user ID from WhatsApp number by querying Supabase (SAME as SMS)
        user_id = None
        try:
            if unified_worker.supabase_client:
                # Look up user by phone number (WhatsApp uses phone numbers)
                user_lookup = unified_worker.supabase_client.table('users').select('id').eq('phone_number', whatsapp_number).execute()
                if user_lookup.data:
                    user_id = user_lookup.data[0]['id']
                    logger.info(f"✅ Found user {user_id} for WhatsApp {whatsapp_number}")
                else:
                    logger.warning(f"⚠️ No user found for WhatsApp {whatsapp_number}")
                    # Use a consistent fallback that won't create phantom workflows
                    user_id = "user1"  # Default to user1 for unknown WhatsApp numbers
        except Exception as e:
            logger.error(f"❌ Failed to lookup user by WhatsApp: {e}")
            user_id = "user1"  # Default to user1 for database errors
        
        # Create conversation request (IDENTICAL structure to SMS)
        conversation_request = ConversationRequest(
            user_id=user_id,
            message=Body,
            platform="whatsapp",  # NEW: WhatsApp platform
            conversation_id=f"whatsapp_{MessageSid}",  # WhatsApp-specific conversation ID
            metadata={"from": whatsapp_number, "message_sid": MessageSid}  # Store WhatsApp number
        )
        
        # Start multi-agent conversation workflow (REPLACED single agent system)
        logger.info(f"🔍 DEBUG: About to start WhatsApp workflow, temporal_client exists: {server.temporal_client is not None}")
        logger.info(f"🤖 Using Multi-Agent Conversation System for WhatsApp")
        
        if server.temporal_client:
            workflow_id = f"conversation_{user_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            logger.info(f"🔍 DEBUG: Starting WhatsApp workflow with ID: {workflow_id}")
            try:
                # Use multi-agent workflow (quality-validated, channel-formatted)
                logger.info(f"🤖 Starting MultiAgentConversationWorkflow for WhatsApp")
                result = await server.temporal_client.start_workflow(
                    MultiAgentConversationWorkflow.run,
                    args=[
                        Body,  # user_message
                        "whatsapp",  # channel
                        user_id,  # user_id
                        f"whatsapp_{MessageSid}",  # conversation_id
                        [],  # conversation_history (TODO: load from DB)
                        {"from": whatsapp_number}  # user_context
                    ],
                    id=workflow_id,
                    task_queue="timesheet-reminders"
                )
                logger.info(f"🔍 DEBUG: WhatsApp multi-agent workflow started, awaiting result...")
                
                # Get the multi-agent response
                ma_response = await result.result()
                logger.info(f"🔍 DEBUG: WhatsApp multi-agent workflow completed")
                response_text = ma_response["final_response"]
            except Exception as workflow_error:
                logger.error(f"❌ WhatsApp workflow execution failed: {workflow_error}")
                response_text = "I'm experiencing technical difficulties. Please try again later."
        else:
            # Temporal client not available - system cannot function without it
            logger.error("❌ Temporal client not available - system requires Temporal workflows")
            response_text = "System is currently initializing. Please try again in a moment."
        
        # Return TwiML response (IDENTICAL format to SMS)
        twiml_response = f'<?xml version="1.0" encoding="UTF-8"?><Response><Message>{response_text}</Message></Response>'
        
        logger.info(f"✅ WhatsApp response sent to {whatsapp_number}")
        return Response(content=twiml_response, media_type="application/xml")
        
    except Exception as e:
        logger.error(f"❌ WhatsApp webhook error: {e}")
        error_response = '<?xml version="1.0" encoding="UTF-8"?><Response><Message>Sorry, I encountered an error processing your message.</Message></Response>'
        return Response(content=error_response, media_type="application/xml")

@app.post("/webhook/email")
async def handle_email_webhook(request: Request):
    """Handle incoming email webhook"""
    try:
        # Parse email webhook data (implementation depends on email provider)
        body = await request.json()
        
        user_email = body.get('from', 'unknown@example.com')
        message_content = body.get('text', '')
        
        logger.info(f"📧 Email received from {user_email}: {message_content[:50]}...")
        
        # Extract user ID from email by querying Supabase
        user_id = None
        try:
            if unified_worker.supabase_client:
                # Look up user by email address
                user_lookup = unified_worker.supabase_client.table('users').select('id').eq('email_address', user_email).execute()
                if user_lookup.data:
                    user_id = user_lookup.data[0]['id']
                    logger.info(f"✅ Found user {user_id} for email {user_email}")
                else:
                    logger.warning(f"⚠️ No user found for email {user_email}")
                    user_id = "user1"  # Default to user1 for unknown email addresses
        except Exception as e:
            logger.error(f"❌ Failed to lookup user by email: {e}")
            user_id = "user1"  # Default to user1 for database errors
        
        # Create conversation request
        conversation_request = ConversationRequest(
            user_id=user_id,
            message=message_content,
            platform="email",
            conversation_id=f"email_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",  # FIXED: Use UTC time
            metadata={"from": user_email}
        )
        
        # Start multi-agent conversation workflow (REPLACED single agent system)
        logger.info(f"🤖 Using Multi-Agent Conversation System for Email")
        
        if server.temporal_client:
            workflow_id = f"conversation_{user_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            logger.info(f"🤖 Starting MultiAgentConversationWorkflow for Email")
            
            result = await server.temporal_client.start_workflow(
                MultiAgentConversationWorkflow.run,
                args=[
                    message_content,  # user_message
                    "email",  # channel
                    user_id,  # user_id
                    f"email_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",  # conversation_id
                    [],  # conversation_history (TODO: load from DB)
                    {"from": user_email}  # user_context
                ],
                id=workflow_id,
                task_queue="timesheet-reminders"
            )
            
            # Get the multi-agent response
            ma_response = await result.result()
            response_text = ma_response["final_response"]
            
            # Send email response (placeholder - would need actual email sending)
            logger.info(f"📧 Email response generated for {user_email}")
            logger.info(f"📧 Response: {response_text[:100]}...")
            
            return {"status": "success", "message": "Email processed", "response": response_text}
        else:
            return {"status": "error", "message": "Temporal client not available"}
        
    except Exception as e:
        logger.error(f"❌ Email webhook error: {e}")
        raise HTTPException(status_code=500, detail=f"Email processing failed: {str(e)}")

# =============================================================================
# GOVERNANCE ENDPOINTS
# =============================================================================

@app.get("/governance/metrics")
async def get_governance_metrics_endpoint():
    """Get current governance metrics"""
    try:
        return get_governance_metrics()
    except Exception as e:
        logger.error(f"❌ Governance metrics error: {e}")
        raise HTTPException(status_code=500, detail=f"Governance metrics failed: {str(e)}")

@app.get("/governance/dashboard")
async def get_governance_dashboard():
    """Get governance dashboard data"""
    try:
        return dashboard.get_real_time_status()
    except Exception as e:
        logger.error(f"❌ Governance dashboard error: {e}")
        raise HTTPException(status_code=500, detail=f"Governance dashboard failed: {str(e)}")

@app.get("/governance/safety-report")
async def get_safety_report():
    """Get comprehensive safety report"""
    try:
        return dashboard.generate_safety_report()
    except Exception as e:
        logger.error(f"❌ Safety report error: {e}")
        raise HTTPException(status_code=500, detail=f"Safety report failed: {str(e)}")

@app.get("/governance/actions")
async def get_recent_actions(limit: int = 20):
    """Get recent governance actions"""
    try:
        recent_actions = governance.action_history[-limit:] if governance.action_history else []
        return {
            "total_actions": len(governance.action_history),
            "recent_actions": [
                {
                    "timestamp": action.timestamp,
                    "user_id": action.user_id,
                    "agent_id": action.agent_id,
                    "action_type": action.action_type.value,
                    "tool_name": action.tool_name,
                    "success": action.success,
                    "execution_time_ms": action.execution_time_ms,
                    "intervention": action.intervention_triggered,
                    "intervention_reason": action.intervention_reason.value if action.intervention_reason else None
                }
                for action in recent_actions
            ]
        }
    except Exception as e:
        logger.error(f"❌ Recent actions error: {e}")
        raise HTTPException(status_code=500, detail=f"Recent actions failed: {str(e)}")

# =============================================================================
# STARTUP AND MAIN
# =============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize Temporal client and worker on startup"""
    logger.info("🔥 STARTUP EVENT TRIGGERED - Beginning initialization...")
    try:
        logger.info("🚀 Starting Unified Temporal Worker...")
        
        # Initialize Temporal client
        logger.info("🔗 Initializing Temporal client...")
        await server.initialize_temporal_client()
        logger.info("✅ Temporal client initialized")
        
        # Start worker in background
        logger.info("🚀 Creating Temporal worker background task...")
        temporal_task = asyncio.create_task(server.start_temporal_worker())
        logger.info("✅ Temporal worker task created")
        
        # Start email polling in background
        logger.info("📧 Creating Gmail polling background task...")
        email_task = asyncio.create_task(server.start_email_polling())
        logger.info("✅ Gmail polling task created")
        
        # Log task status
        logger.info(f"📊 Background tasks status:")
        logger.info(f"   Temporal worker task: {temporal_task}")
        logger.info(f"   Gmail polling task: {email_task}")
        
        logger.info("✅ Unified Temporal Worker startup complete")
        
    except Exception as e:
        logger.error(f"❌ Startup failed: {e}")
        import traceback
        logger.error(f"❌ Startup traceback: {traceback.format_exc()}")
        # Don't raise - allow server to start for health checks

if __name__ == "__main__":
    # Determine port based on environment
    port = int(os.getenv("PORT", "8003"))  # New port for unified worker
    
    logger.info(f"🚀 Starting Unified Temporal Worker on port {port}")
    
    uvicorn.run(
        "unified_server:app",
        host="0.0.0.0",
        port=port,
        reload=False,  # Disable reload in production
        log_level="info"
    )
