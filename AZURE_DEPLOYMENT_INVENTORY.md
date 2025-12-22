# Azure Deployment Inventory

## 📊 Current Azure Infrastructure

**Resource Group:** `rg-secure-timesheet-agent`  
**Region:** Australia East  
**Last Updated:** December 1, 2025, 9:05 PM AEST

---

## 🚀 Container Apps (6 Services)

### 1. **unified-temporal-worker** ⭐ (Main Application)

**Purpose:** Multi-agent AI system with Temporal workflows

**Details:**
- **URL:** https://unified-temporal-worker.kindcoast-5a2a34c6.australiaeast.azurecontainerapps.io
- **Image:** secureagentreg2ai.azurecr.io/multi-agent-system:1.0.0-20251201-185138
- **Status:** ✅ Running
- **Version:** 6.0.0-governance
- **Resources:**
  - CPU: 1.25 cores
  - Memory: 2.5 GiB
  - Storage: 8 GiB ephemeral
- **Replicas:** Min 1, Max 3
- **Visibility:** Public (external ingress)

**Features:**
- ✅ Multi-agent conversation system (Planner, Timesheet, Quality, Branding)
- ✅ Temporal workflow orchestration
- ✅ Daily timesheet reminders (7 AM AEST)
- ✅ Cross-platform messaging (SMS, WhatsApp, Email)
- ✅ Harvest API integration via MCP
- ✅ Supabase conversation storage
- ✅ Azure Key Vault secrets management
- ✅ Opik LLM observability
- ✅ Agent governance controls
- ✅ API timeout protection
- ✅ **Joke generator** (personalized daily reminders)
- ✅ **JSON minification** (50% token savings)

**Health Status:**
```json
{
  "status": "healthy",
  "temporal": "✅ Connected",
  "supabase": "✅ Connected",
  "llm_client": "✅ Initialized",
  "key_vault": "✅ Connected",
  "opik": "✅ Enabled",
  "governance": "✅ Active",
  "timeout_protection": "✅ Active"
}
```

---

### 2. **krakend-gateway** (API Gateway)

**Purpose:** API gateway for routing and load balancing

**Details:**
- **URL:** https://krakend-gateway.kindcoast-5a2a34c6.australiaeast.azurecontainerapps.io
- **Status:** ✅ Running
- **Visibility:** Public (external ingress)

**Features:**
- API routing and aggregation
- Rate limiting
- Request/response transformation
- Load balancing

---

### 3. **harvest-mcp** (Harvest MCP Server)

**Purpose:** Model Context Protocol server for Harvest API

**Details:**
- **URL:** harvest-mcp.internal.kindcoast-5a2a34c6.australiaeast.azurecontainerapps.io
- **Status:** ✅ Running
- **Visibility:** Internal only

**Features:**
- Harvest API integration (51 tools)
- Time entries, projects, tasks, users
- Clients, invoices, expenses
- MCP protocol implementation

---

### 4. **temporal-dev-server** (Temporal Server)

**Purpose:** Temporal workflow orchestration server

**Details:**
- **URL:** https://temporal-dev-server.kindcoast-5a2a34c6.australiaeast.azurecontainerapps.io
- **Status:** ✅ Running
- **Visibility:** Public (external ingress)

**Features:**
- Workflow orchestration
- Activity execution
- Scheduling (daily reminders)
- Retry policies
- Durable execution

---

### 5. **temporal-postgres-v2** (Temporal Database)

**Purpose:** PostgreSQL database for Temporal

**Details:**
- **URL:** temporal-postgres-v2.internal.kindcoast-5a2a34c6.australiaeast.azurecontainerapps.io
- **Status:** ✅ Running
- **Visibility:** Internal only

**Features:**
- Workflow state persistence
- Event history storage
- Task queue management

---

### 6. **secure-timesheet-agent** (Legacy/Backup)

**Purpose:** Original single-agent timesheet system

**Details:**
- **URL:** https://secure-timesheet-agent.kindcoast-5a2a34c6.australiaeast.azurecontainerapps.io
- **Status:** ✅ Running
- **Visibility:** Public (external ingress)

**Note:** This is the legacy system, kept for backup. Main system is now `unified-temporal-worker`.

---

## 🔐 Supporting Azure Services

### Azure Key Vault
- **Name:** kv-secure-agent-2ai
- **Purpose:** Secrets management
- **Secrets Stored:**
  - Harvest API credentials (tokens, account IDs)
  - Twilio credentials (SMS/WhatsApp)
  - OpenAI API keys
  - Supabase credentials
  - Opik credentials
  - Gmail credentials
  - User phone numbers

### Azure Container Registry
- **Name:** secureagentreg2ai
- **Purpose:** Docker image storage
- **Latest Image:** multi-agent-system:1.0.0-20251201-185138

### Supabase (External)
- **Purpose:** Conversation storage, user profiles
- **Tables:**
  - `conversations` - Message history
  - `users` - User profiles with interests
  - `reminders` - Reminder schedules

### Temporal Cloud (External)
- **Purpose:** Workflow orchestration (alternative to self-hosted)
- **URL:** https://cloud.temporal.io
- **Namespace:** default

### Opik (External)
- **Purpose:** LLM observability and tracking
- **URL:** https://www.comet.com/opik
- **Workspace:** ds2ai
- **Project:** timesheet-ai-agent

---

## 💰 Cost Breakdown (Estimated)

### Container Apps:

| Service | CPU | Memory | Cost/Month |
|---------|-----|--------|------------|
| unified-temporal-worker | 1.25 cores | 2.5 GiB | ~$50-75 |
| krakend-gateway | 0.5 cores | 1 GiB | ~$20-30 |
| harvest-mcp | 0.5 cores | 1 GiB | ~$20-30 |
| temporal-dev-server | 1 core | 2 GiB | ~$40-60 |
| temporal-postgres-v2 | 0.5 cores | 1 GiB | ~$20-30 |
| secure-timesheet-agent | 0.5 cores | 1 GiB | ~$20-30 |

**Total Container Apps:** ~$170-255/month

### Other Services:

| Service | Cost/Month |
|---------|------------|
| Azure Key Vault | ~$1-2 |
| Azure Container Registry | ~$5-10 |
| Supabase (Free tier) | $0 |
| Temporal Cloud (if used) | $0 (dev tier) |
| Opik (Free tier) | $0 |
| **LLM API Calls (OpenAI)** | ~$10-50 (with 50% savings!) |

**Total Estimated:** ~$186-317/month

---

## 📊 Traffic & Usage

### Endpoints:

1. **Webhook Endpoints:**
   - `/webhook/sms` - Twilio SMS webhook
   - `/webhook/whatsapp` - Twilio WhatsApp webhook
   - `/webhook/email` - Email webhook

2. **API Endpoints:**
   - `/health` - Health check
   - `/check-timesheet-user1` - Manual check (User1)
   - `/check-timesheet-user2` - Manual check (User2)
   - `/trigger-reminder-user1` - Manual reminder (User1)
   - `/trigger-reminder-user2` - Manual reminder (User2)

3. **Temporal Endpoints:**
   - Workflow execution
   - Activity execution
   - Schedule management

### Daily Traffic (Estimated):

- **Daily Reminders:** 2 users × 1 reminder = 2 requests/day
- **Manual Checks:** ~5-10 requests/day
- **Webhook Messages:** ~10-20 messages/day
- **Total LLM Calls:** ~50-100 calls/day
- **Total Tokens:** ~10,000-20,000 tokens/day (with 50% savings!)

---

## 🔄 Deployment Pipeline

### Build Process:

1. **Source:** GitHub repository
2. **Build:** Docker image via `deploy_configured.sh`
3. **Registry:** Push to Azure Container Registry
4. **Deploy:** Update Container App with new image
5. **Verify:** Health check + smoke tests

### Latest Deployment:

- **Date:** December 1, 2025, 6:51 PM AEST
- **Build:** 1.0.0-20251201-185138
- **Status:** ✅ Successful
- **Changes:**
  - Added joke generator
  - Added JSON minification
  - Fixed Opik health check

---

## 🎯 Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     Azure Container Apps                     │
│                  (rg-secure-timesheet-agent)                 │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌──────────────┐    ┌──────────────────┐    ┌──────────────┐
│   KrakenD    │    │  Unified Worker  │    │  Harvest MCP │
│   Gateway    │◄───│  (Main App)      │───►│   Server     │
│   (Public)   │    │  (Public)        │    │  (Internal)  │
└──────────────┘    └──────────────────┘    └──────────────┘
                            │
                    ┌───────┼───────┐
                    ▼       ▼       ▼
            ┌──────────┐ ┌──────────┐ ┌──────────┐
            │ Temporal │ │ Temporal │ │   Key    │
            │  Server  │ │ Postgres │ │  Vault   │
            │ (Public) │ │(Internal)│ │ (Azure)  │
            └──────────┘ └──────────┘ └──────────┘

External Services:
┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐
│ Supabase │  │  Twilio  │  │  OpenAI  │  │   Opik   │
│   (DB)   │  │  (SMS)   │  │  (LLM)   │  │ (Trace)  │
└──────────┘  └──────────┘  └──────────┘  └──────────┘
```

---

## 🔒 Security

### Authentication & Authorization:
- ✅ Azure Managed Identity for Key Vault access
- ✅ API keys stored in Key Vault
- ✅ Twilio webhook signature validation
- ✅ Internal-only services (harvest-mcp, postgres)

### Network Security:
- ✅ HTTPS only (TLS 1.2+)
- ✅ Internal networking for sensitive services
- ✅ Rate limiting via KrakenD
- ✅ Timeout protection

### Data Security:
- ✅ Secrets in Key Vault (not in code)
- ✅ Encrypted at rest (Supabase)
- ✅ Encrypted in transit (HTTPS)
- ✅ Audit trail via Opik

---

## 📈 Monitoring & Observability

### Health Monitoring:
- ✅ `/health` endpoint on all services
- ✅ Azure Container Apps health probes
- ✅ Temporal workflow monitoring

### Logging:
- ✅ Azure Container Apps logs
- ✅ Structured logging (JSON)
- ✅ Log levels (INFO, WARNING, ERROR)

### Tracing:
- ✅ Opik LLM call tracing
- ✅ Token usage tracking
- ✅ Cost tracking
- ✅ Latency monitoring

### Metrics:
- ✅ Request count
- ✅ Error rate
- ✅ Response time
- ✅ Token usage
- ✅ Cost per request

---

## 🎯 Summary

### What We Have in Azure:

1. **6 Container Apps** running in Australia East
2. **1 Main Application** (unified-temporal-worker) with:
   - Multi-agent AI system
   - Temporal workflows
   - Daily reminders
   - Cross-platform messaging
   - Joke generator
   - JSON minification (50% token savings)
   - Opik tracking

3. **Supporting Services:**
   - API Gateway (KrakenD)
   - Harvest MCP Server
   - Temporal Server + Database
   - Azure Key Vault
   - Azure Container Registry

4. **External Integrations:**
   - Supabase (database)
   - Twilio (SMS/WhatsApp)
   - OpenAI (LLM)
   - Opik (observability)

### Current Status:

- ✅ All services running
- ✅ All health checks passing
- ✅ Latest deployment: 1.0.0-20251201-185138
- ✅ Opik tracking enabled
- ✅ JSON minification active
- ✅ Joke generator ready

### Monthly Cost:

- **Infrastructure:** ~$186-317/month
- **LLM Calls:** ~$10-50/month (with 50% savings!)
- **Total:** ~$196-367/month

---

**Last Updated:** December 1, 2025, 9:05 PM AEST  
**Status:** ✅ All Systems Operational
