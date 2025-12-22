# 🔐 Azure Key Vault - Environment Variables Checklist

**Key Vault URL**: `https://kv-secure-agent-2ai.vault.azure.net/`

This document lists ALL environment variables needed for the multi-agent system and their Azure Key Vault secret names.

---

## 📋 Complete Secret List (46 Secrets)

### ✅ Required Secrets (Must Have)

#### 1. LLM Provider (Choose One)

**Option A: OpenRouter (Recommended - Free Tier Available)**
- [ ] `OPENROUTER-API-KEY` → `OPENROUTER_API_KEY`
- [ ] `OPENROUTER-MODEL` → `OPENROUTER_MODEL` (e.g., `google/gemini-2.0-flash-exp:free`)
- [ ] `USE-OPENROUTER` → `USE_OPENROUTER` (set to `true`)
- [ ] `PROVIDER` → `PROVIDER` (set to `openrouter`)

**Option B: OpenAI Direct**
- [ ] `OPENAI-API-KEY` → `OPENAI_API_KEY`
- [ ] `USE-OPENROUTER` → `USE_OPENROUTER` (set to `false`)
- [ ] `PROVIDER` → `PROVIDER` (set to `openai`)

**Option C: Azure OpenAI**
- [ ] `AZURE-OPENAI-ENDPOINT` → `AZURE_OPENAI_ENDPOINT`
- [ ] `AZURE-OPENAI-API-KEY` → `AZURE_OPENAI_API_KEY`
- [ ] `AZURE-OPENAI-DEPLOYMENT` → `AZURE_OPENAI_DEPLOYMENT`
- [ ] `AZURE-OPENAI-API-VERSION` → `AZURE_OPENAI_API_VERSION`
- [ ] `PROVIDER` → `PROVIDER` (set to `azure-openai`)

#### 2. Database (Required)
- [ ] `SUPABASE-URL` → `SUPABASE_URL`
- [ ] `SUPABASE-KEY` → `SUPABASE_KEY`

#### 3. Harvest API (Required for Timesheet Data)
- [ ] `HARVEST-ACCESS-TOKEN` → `HARVEST_ACCESS_TOKEN`
- [ ] `HARVEST-ACCOUNT-ID` → `HARVEST_ACCOUNT_ID`

#### 4. Temporal (Required)
- [ ] `TEMPORAL-HOST` → `TEMPORAL_HOST`
- [ ] `TEMPORAL-NAMESPACE` → `TEMPORAL_NAMESPACE`

#### 5. Twilio (Required for SMS/WhatsApp)
- [ ] `TWILIO-ACCOUNT-SID` → `TWILIO_ACCOUNT_SID`
- [ ] `TWILIO-AUTH-TOKEN` → `TWILIO_AUTH_TOKEN`
- [ ] `TWILIO-PHONE-NUMBER` → `TWILIO_PHONE_NUMBER`

---

### ⚙️ Optional Secrets (Recommended)

#### 6. LLM Configuration
- [ ] `OPENAI-TEMPERATURE` → `OPENAI_TEMPERATURE` (default: `0.7`)
- [ ] `OPENAI-MAX-TOKENS` → `OPENAI_MAX_TOKENS` (default: `1000`)

#### 7. Performance & Caching
- [ ] `CACHE-ENABLED` → `CACHE_ENABLED` (default: `true`)
- [ ] `REDIS-ENABLED` → `REDIS_ENABLED` (default: `false`)
- [ ] `FALLBACK-ENABLED` → `FALLBACK_ENABLED` (default: `true`)
- [ ] `RETRY-MAX-WAIT-SECONDS` → `RETRY_MAX_WAIT_SECONDS` (default: `30`)
- [ ] `USE-IMPROVED-RATE-LIMITER` → `USE_IMPROVED_RATE_LIMITER` (default: `true`)

#### 8. Observability (Opik)
- [ ] `OPIK-ENABLED` → `OPIK_ENABLED` (default: `false`)
- [ ] `OPIK-API-KEY` → `OPIK_API_KEY` (if enabled)
- [ ] `OPIK-WORKSPACE` → `OPIK_WORKSPACE` (if enabled)
- [ ] `OPIK-PROJECT` → `OPIK_PROJECT` (if enabled)

#### 9. Multi-User Support
- [ ] `HARVEST-ACCESS-TOKEN-USER2` → `HARVEST_ACCESS_TOKEN_USER2`
- [ ] `HARVEST-ACCOUNT-ID-USER2` → `HARVEST_ACCOUNT_ID_USER2`
- [ ] `USER-PHONE-NUMBER` → `USER_PHONE_NUMBER`
- [ ] `USER-PHONE-NUMBER-USER2` → `USER_PHONE_NUMBER_USER2`

#### 10. Email Support (Gmail)
- [ ] `GMAIL-USER` → `GMAIL_USER`
- [ ] `GMAIL-PASSWORD` → `GMAIL_PASSWORD` (App Password)

#### 11. OpenRouter Advanced
- [ ] `OPENROUTER-PROVISIONING-KEY` → `OPENROUTER_PROVISIONING_KEY` (for tenant keys)

#### 12. Application
- [ ] `APP-URL` → `APP_URL` (your deployment URL)

#### 13. RAG / Vector Database (Qdrant)
- [ ] `RAG-ENABLED` → `RAG_ENABLED` (set to `true` to enable)
- [ ] `VECTOR-DB-PROVIDER` → `VECTOR_DB_PROVIDER` (set to `qdrant`)
- [ ] `QDRANT-URL` → `QDRANT_URL` (e.g., `http://qdrant:6333`)
- [ ] `QDRANT-API-KEY` → `QDRANT_API_KEY` (optional, empty for local)
- [ ] `QDRANT-COLLECTION-NAME` → `QDRANT_COLLECTION_NAME` (default: `timesheet_memory`)
- [ ] `EMBEDDINGS-PROVIDER` → `EMBEDDINGS_PROVIDER` (default: `openai`)
- [ ] `EMBEDDINGS-MODEL` → `EMBEDDINGS_MODEL` (default: `text-embedding-3-small`)
- [ ] `EMBEDDINGS-DIMENSION` → `EMBEDDINGS_DIMENSION` (default: `1536`)

---

## 🎯 Minimum Required for Multi-Agent System

**For local testing, you need at minimum:**

### Core (6 secrets)
1. ✅ `OPENROUTER-API-KEY` (or `OPENAI-API-KEY`)
2. ✅ `SUPABASE-URL`
3. ✅ `SUPABASE-KEY`
4. ✅ `HARVEST-ACCESS-TOKEN`
5. ✅ `HARVEST-ACCOUNT-ID`
6. ✅ `TEMPORAL-HOST`

### Configuration (4 secrets)
7. ✅ `USE-OPENROUTER` = `true`
8. ✅ `PROVIDER` = `openrouter`
9. ✅ `OPENROUTER-MODEL` = `google/gemini-2.0-flash-exp:free`
10. ✅ `TEMPORAL-NAMESPACE` = `default` (or your namespace)

### SMS/WhatsApp (3 secrets)
11. ✅ `TWILIO-ACCOUNT-SID`
12. ✅ `TWILIO-AUTH-TOKEN`
13. ✅ `TWILIO-PHONE-NUMBER`

**Total Minimum: 13 secrets**

---

## 📝 Azure Key Vault Secret Names

**Important**: Azure Key Vault uses **hyphens** (`-`) in secret names, but the code uses **underscores** (`_`).

The `unified_server.py` automatically maps them:

```python
secret_mappings = {
    # Key Vault Name (hyphens) -> Environment Variable (underscores)
    "OPENROUTER-API-KEY": "OPENROUTER_API_KEY",
    "SUPABASE-URL": "SUPABASE_URL",
    # ... etc
}
```

---

## 🔍 How to Check What's in Key Vault

### Option 1: Azure Portal
1. Go to https://portal.azure.com
2. Navigate to Key Vault: `kv-secure-agent-2ai`
3. Click "Secrets" in left menu
4. Check which secrets exist

### Option 2: Azure CLI
```bash
# List all secrets
az keyvault secret list --vault-name kv-secure-agent-2ai --query "[].name" -o table

# Get specific secret (without value)
az keyvault secret show --vault-name kv-secure-agent-2ai --name OPENROUTER-API-KEY --query "name"

# Get secret value
az keyvault secret show --vault-name kv-secure-agent-2ai --name OPENROUTER-API-KEY --query "value" -o tsv
```

### Option 3: Check Server Logs
When the server starts, it logs which secrets were loaded:

```
🔍 DEBUG: Loading 38 secrets: ['OPENAI-API-KEY', 'HARVEST-ACCESS-TOKEN', ...]
✅ Loaded secret: OPENROUTER-API-KEY -> OPENROUTER_API_KEY
✅ Loaded secret: SUPABASE-URL -> SUPABASE_URL
⚠️ Could not load secret OPIK-API-KEY: Secret not found
```

---

## ✅ Recommended Secrets to Add

### For Multi-Agent System

**High Priority** (Add these first):
1. ✅ `OPENROUTER-API-KEY` - For LLM calls
2. ✅ `OPENROUTER-MODEL` - Model to use
3. ✅ `USE-OPENROUTER` - Set to `true`
4. ✅ `PROVIDER` - Set to `openrouter`
5. ✅ `CACHE-ENABLED` - Set to `true` (saves costs)
6. ✅ `USE-IMPROVED-RATE-LIMITER` - Set to `true`

**Medium Priority** (Add for production):
7. ⚙️ `OPIK-ENABLED` - Set to `true` for monitoring
8. ⚙️ `OPIK-API-KEY` - Your Opik API key
9. ⚙️ `OPIK-WORKSPACE` - Your workspace name
10. ⚙️ `OPIK-PROJECT` - Project name (e.g., `multi-agent-production`)
11. ⚙️ `OPENAI-TEMPERATURE` - Set to `0.7`
12. ⚙️ `OPENAI-MAX-TOKENS` - Set to `1000`

**Low Priority** (Add if needed):
13. 📧 `GMAIL-USER` - For email responses
14. 📧 `GMAIL-PASSWORD` - Gmail app password
15. 👥 `HARVEST-ACCESS-TOKEN-USER2` - For second user
16. 👥 `HARVEST-ACCOUNT-ID-USER2` - For second user

---

## 🚀 Quick Setup Commands

### Add Secrets to Azure Key Vault

```bash
# Set Key Vault name
KV_NAME="kv-secure-agent-2ai"

# LLM Provider (OpenRouter)
az keyvault secret set --vault-name $KV_NAME --name "OPENROUTER-API-KEY" --value "sk-or-v1-xxxxx"
az keyvault secret set --vault-name $KV_NAME --name "OPENROUTER-MODEL" --value "google/gemini-2.0-flash-exp:free"
az keyvault secret set --vault-name $KV_NAME --name "USE-OPENROUTER" --value "true"
az keyvault secret set --vault-name $KV_NAME --name "PROVIDER" --value "openrouter"

# Database
az keyvault secret set --vault-name $KV_NAME --name "SUPABASE-URL" --value "https://xxxxx.supabase.co"
az keyvault secret set --vault-name $KV_NAME --name "SUPABASE-KEY" --value "xxxxx"

# Harvest
az keyvault secret set --vault-name $KV_NAME --name "HARVEST-ACCESS-TOKEN" --value "xxxxx"
az keyvault secret set --vault-name $KV_NAME --name "HARVEST-ACCOUNT-ID" --value "xxxxx"

# Temporal
az keyvault secret set --vault-name $KV_NAME --name "TEMPORAL-HOST" --value "your-namespace.tmprl.cloud:7233"
az keyvault secret set --vault-name $KV_NAME --name "TEMPORAL-NAMESPACE" --value "your-namespace"

# Twilio
az keyvault secret set --vault-name $KV_NAME --name "TWILIO-ACCOUNT-SID" --value "ACxxxxx"
az keyvault secret set --vault-name $KV_NAME --name "TWILIO-AUTH-TOKEN" --value "xxxxx"
az keyvault secret set --vault-name $KV_NAME --name "TWILIO-PHONE-NUMBER" --value "+1234567890"

# Performance
az keyvault secret set --vault-name $KV_NAME --name "CACHE-ENABLED" --value "true"
az keyvault secret set --vault-name $KV_NAME --name "USE-IMPROVED-RATE-LIMITER" --value "true"
az keyvault secret set --vault-name $KV_NAME --name "FALLBACK-ENABLED" --value "true"

# Opik (Optional)
az keyvault secret set --vault-name $KV_NAME --name "OPIK-ENABLED" --value "true"
az keyvault secret set --vault-name $KV_NAME --name "OPIK-API-KEY" --value "xxxxx"
az keyvault secret set --vault-name $KV_NAME --name "OPIK-WORKSPACE" --value "your-workspace"
az keyvault secret set --vault-name $KV_NAME --name "OPIK-PROJECT" --value "multi-agent-production"
```

---

## 🔒 Security Best Practices

### 1. Access Control
- ✅ Use Managed Identity for Azure Container Apps
- ✅ Grant only "Get" and "List" permissions on secrets
- ✅ Don't grant "Set" or "Delete" permissions to app

### 2. Secret Rotation
- ⚙️ Rotate API keys every 90 days
- ⚙️ Use Key Vault versioning
- ⚙️ Update secrets without redeploying app

### 3. Monitoring
- 📊 Enable Key Vault logging
- 📊 Monitor secret access
- 📊 Alert on failed access attempts

---

## 🧪 Testing Secret Loading

### Check if secrets are loaded correctly:

```python
# In unified_server.py, the load_secrets_to_env() function logs:
# ✅ Loaded secret: OPENROUTER-API-KEY -> OPENROUTER_API_KEY
# ⚠️ Could not load secret OPIK-API-KEY: Secret not found

# Check server logs on startup:
docker logs <container-id> | grep "Loaded secret"
```

### Verify environment variables are set:

```python
import os
print(os.getenv("OPENROUTER_API_KEY"))  # Should print the key
print(os.getenv("SUPABASE_URL"))  # Should print the URL
```

---

## 📊 Secret Status Checklist

Use this to track which secrets you've added:

### Core Secrets
- [ ] OPENROUTER-API-KEY
- [ ] OPENROUTER-MODEL
- [ ] USE-OPENROUTER
- [ ] PROVIDER
- [ ] SUPABASE-URL
- [ ] SUPABASE-KEY
- [ ] HARVEST-ACCESS-TOKEN
- [ ] HARVEST-ACCOUNT-ID
- [ ] TEMPORAL-HOST
- [ ] TEMPORAL-NAMESPACE
- [ ] TWILIO-ACCOUNT-SID
- [ ] TWILIO-AUTH-TOKEN
- [ ] TWILIO-PHONE-NUMBER

### Performance Secrets
- [ ] CACHE-ENABLED
- [ ] USE-IMPROVED-RATE-LIMITER
- [ ] FALLBACK-ENABLED
- [ ] OPENAI-TEMPERATURE
- [ ] OPENAI-MAX-TOKENS
- [ ] RETRY-MAX-WAIT-SECONDS

### Observability Secrets
- [ ] OPIK-ENABLED
- [ ] OPIK-API-KEY
- [ ] OPIK-WORKSPACE
- [ ] OPIK-PROJECT

### Optional Secrets
- [ ] GMAIL-USER
- [ ] GMAIL-PASSWORD
- [ ] HARVEST-ACCESS-TOKEN-USER2
- [ ] HARVEST-ACCOUNT-ID-USER2
- [ ] USER-PHONE-NUMBER
- [ ] USER-PHONE-NUMBER-USER2
- [ ] OPENROUTER-PROVISIONING-KEY
- [ ] APP-URL

### RAG / Vector Database Secrets
- [ ] RAG-ENABLED
- [ ] VECTOR-DB-PROVIDER
- [ ] QDRANT-URL
- [ ] QDRANT-API-KEY
- [ ] QDRANT-COLLECTION-NAME
- [ ] EMBEDDINGS-PROVIDER
- [ ] EMBEDDINGS-MODEL
- [ ] EMBEDDINGS-DIMENSION

---

## ✅ Summary

**Total Secrets Mapped**: 46  
**Minimum Required**: 13  
**Recommended**: 19  
**Optional**: 19  
**RAG/Qdrant**: 8  

**Key Vault**: `kv-secure-agent-2ai`  
**URL**: `https://kv-secure-agent-2ai.vault.azure.net/`

**Next Steps**:
1. Check which secrets exist in Key Vault
2. Add missing required secrets (minimum 13)
3. Add recommended secrets for production
4. Test secret loading on server startup
5. Monitor logs for "Could not load secret" warnings

---

**Ready to deploy once all required secrets are in Key Vault!** 🚀
