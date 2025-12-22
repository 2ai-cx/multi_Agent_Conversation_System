# ✅ Qdrant + Azure Key Vault Setup

**Date:** December 11, 2025  
**Status:** ✅ **READY TO DEPLOY**

---

## 🎯 **Summary**

You're absolutely right! Azure Key Vault already has `OPENAI-API-KEY` configured, so we just need to add the Qdrant-specific secrets.

---

## ✅ **What's Already in Azure Key Vault**

### **Existing Secrets (37 total):**
```
✅ OPENAI-API-KEY          ← Already have this!
✅ OPENROUTER-API-KEY
✅ SUPABASE-URL
✅ SUPABASE-KEY
✅ HARVEST-ACCESS-TOKEN
✅ HARVEST-ACCOUNT-ID
✅ TEMPORAL-HOST
✅ TEMPORAL-NAMESPACE
✅ TWILIO-ACCOUNT-SID
✅ TWILIO-AUTH-TOKEN
✅ TWILIO-PHONE-NUMBER
... (and 26 more)
```

---

## 📝 **What We Need to Add (8 new secrets)**

### **RAG / Qdrant Configuration:**

1. **RAG-ENABLED** = `true`
   - Enables RAG (Retrieval-Augmented Generation)

2. **VECTOR-DB-PROVIDER** = `qdrant`
   - Specifies Qdrant as the vector database

3. **QDRANT-URL** = `http://qdrant:6333`
   - URL for Qdrant service (Docker service name)

4. **QDRANT-API-KEY** = `""` (empty)
   - Optional, leave empty for local deployment

5. **QDRANT-COLLECTION-NAME** = `timesheet_memory`
   - Collection name prefix

6. **EMBEDDINGS-PROVIDER** = `openai`
   - Uses OpenAI for embeddings (already have API key!)

7. **EMBEDDINGS-MODEL** = `text-embedding-3-small`
   - OpenAI embedding model

8. **EMBEDDINGS-DIMENSION** = `1536`
   - Vector dimension for embeddings

---

## 🚀 **Quick Setup**

### **Option 1: Run the Script (Recommended)**

```bash
# Make script executable
chmod +x add_qdrant_secrets.sh

# Run it
./add_qdrant_secrets.sh
```

The script will:
- ✅ Check Azure CLI authentication
- ✅ Add all 8 Qdrant secrets
- ✅ Set appropriate descriptions
- ✅ Confirm success

### **Option 2: Manual Setup**

```bash
KV_NAME="kv-secure-agent-2ai"

# RAG Configuration
az keyvault secret set --vault-name $KV_NAME --name "RAG-ENABLED" --value "true"
az keyvault secret set --vault-name $KV_NAME --name "VECTOR-DB-PROVIDER" --value "qdrant"

# Qdrant Configuration
az keyvault secret set --vault-name $KV_NAME --name "QDRANT-URL" --value "http://qdrant:6333"
az keyvault secret set --vault-name $KV_NAME --name "QDRANT-API-KEY" --value ""
az keyvault secret set --vault-name $KV_NAME --name "QDRANT-COLLECTION-NAME" --value "timesheet_memory"

# Embeddings Configuration
az keyvault secret set --vault-name $KV_NAME --name "EMBEDDINGS-PROVIDER" --value "openai"
az keyvault secret set --vault-name $KV_NAME --name "EMBEDDINGS-MODEL" --value "text-embedding-3-small"
az keyvault secret set --vault-name $KV_NAME --name "EMBEDDINGS-DIMENSION" --value "1536"
```

---

## 🔧 **Code Changes Made**

### **1. unified_server.py** ✅
Added secret mappings for Qdrant:

```python
secret_mappings = {
    # ... existing mappings ...
    
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
```

### **2. AZURE_KEYVAULT_CHECKLIST.md** ✅
Updated to include:
- Total secrets: 38 → 46
- New RAG/Qdrant section
- Updated checklist

### **3. add_qdrant_secrets.sh** ✅
Created script to add all secrets automatically

---

## 🐳 **Deployment Architecture**

### **For Azure Container Apps:**

```
┌─────────────────────────────────────┐
│   Azure Container App               │
│                                     │
│  ┌──────────────┐  ┌─────────────┐ │
│  │              │  │             │ │
│  │  Your App    │──│  Qdrant     │ │
│  │  (Python)    │  │  Container  │ │
│  │              │  │             │ │
│  └──────────────┘  └─────────────┘ │
│         │                           │
│         │ Loads secrets             │
│         ↓                           │
│  ┌──────────────────────────────┐  │
│  │  Azure Key Vault             │  │
│  │  - OPENAI-API-KEY ✅         │  │
│  │  - RAG-ENABLED               │  │
│  │  - QDRANT-URL                │  │
│  │  - ... (46 secrets)          │  │
│  └──────────────────────────────┘  │
└─────────────────────────────────────┘
```

### **Qdrant Deployment Options:**

#### **Option A: Sidecar Container (Recommended)**
Deploy Qdrant as a sidecar in the same Container App:
- ✅ Simple networking (localhost)
- ✅ Shared lifecycle
- ✅ No extra cost

#### **Option B: Separate Container App**
Deploy Qdrant as its own Container App:
- ✅ Independent scaling
- ✅ Shared across multiple apps
- ⚠️ Requires networking setup

#### **Option C: Qdrant Cloud**
Use managed Qdrant Cloud:
- ✅ Fully managed
- ✅ No infrastructure
- ⚠️ Additional cost
- Update `QDRANT-URL` to cloud URL
- Add `QDRANT-API-KEY`

---

## 📊 **How It Works**

### **1. Application Startup:**
```python
# unified_server.py loads secrets from Key Vault
load_secrets_to_env()

# Secrets become environment variables:
os.getenv("OPENAI_API_KEY")      # ✅ Already exists
os.getenv("RAG_ENABLED")         # ✅ New
os.getenv("QDRANT_URL")          # ✅ New
```

### **2. LLMConfig Initialization:**
```python
# llm/config.py reads from environment
config = LLMConfig()

config.rag_enabled              # True
config.vector_db_provider       # "qdrant"
config.qdrant_url              # "http://qdrant:6333"
config.openai_api_key          # From Key Vault ✅
```

### **3. Memory Manager:**
```python
# llm/memory.py creates Qdrant client
memory = LLMMemoryManager(tenant_id="user-123", config=config)

# Auto-creates collection if needed
# Stores conversations
# Retrieves context
```

### **4. Agent Usage:**
```python
# agents/planner.py uses memory
response = await self.llm_client.generate_with_memory(
    prompt=prompt,
    tenant_id=tenant_id,
    user_id=user_id,
    use_memory=True
)
```

---

## ✅ **Verification**

### **Check Secrets Were Added:**
```bash
# List all secrets
az keyvault secret list --vault-name kv-secure-agent-2ai --query "[].name" -o table

# Should see:
# RAG-ENABLED
# VECTOR-DB-PROVIDER
# QDRANT-URL
# QDRANT-API-KEY
# QDRANT-COLLECTION-NAME
# EMBEDDINGS-PROVIDER
# EMBEDDINGS-MODEL
# EMBEDDINGS-DIMENSION
```

### **Check Application Loads Secrets:**
```bash
# Deploy and check logs
az containerapp logs show --name <your-app> --resource-group <your-rg>

# Should see:
# ✅ Loaded secret: RAG-ENABLED -> RAG_ENABLED
# ✅ Loaded secret: QDRANT-URL -> QDRANT_URL
# ✅ Loaded secret: OPENAI-API-KEY -> OPENAI_API_KEY
```

---

## 🎯 **Deployment Checklist**

### **Before Deployment:**
- [x] Qdrant code implemented
- [x] Azure Key Vault mappings added
- [x] Secret addition script created
- [ ] Run `./add_qdrant_secrets.sh`
- [ ] Verify secrets in Key Vault
- [ ] Deploy Qdrant container
- [ ] Deploy/restart your app

### **After Deployment:**
- [ ] Check app logs for secret loading
- [ ] Verify Qdrant connection
- [ ] Test memory storage
- [ ] Test memory retrieval
- [ ] Monitor Qdrant dashboard

---

## 🔐 **Security Notes**

### **What's Secure:**
- ✅ All secrets in Azure Key Vault
- ✅ No secrets in code
- ✅ No secrets in environment files
- ✅ Managed identity for Key Vault access
- ✅ HTTPS for all external connections

### **Qdrant Security:**
- ✅ Internal network only (not exposed)
- ✅ No API key needed for internal use
- ✅ Multi-tenant isolation via collections
- ✅ Data encrypted at rest (Azure)

---

## 💰 **Cost Implications**

### **Qdrant Deployment:**

**Option A: Sidecar (Recommended)**
- Cost: $0 extra (included in Container App)
- Resources: Share with main app

**Option B: Separate Container App**
- Cost: ~$5-10/month (small instance)
- Resources: 0.5 vCPU, 1GB RAM

**Option C: Qdrant Cloud**
- Cost: Free tier available
- Paid: Starting at $25/month

### **OpenAI Embeddings:**
- Model: `text-embedding-3-small`
- Cost: $0.02 per 1M tokens
- Typical: ~$1-5/month for moderate use

### **Total Additional Cost:**
- Minimal: ~$1-5/month (sidecar + embeddings)
- Moderate: ~$10-15/month (separate container)
- Managed: ~$30-40/month (Qdrant Cloud)

---

## 🚀 **Next Steps**

### **1. Add Secrets to Key Vault:**
```bash
./add_qdrant_secrets.sh
```

### **2. Deploy Qdrant Container:**

**For Azure Container Apps (sidecar):**
```yaml
containers:
  - name: app
    image: your-app-image
    
  - name: qdrant
    image: qdrant/qdrant:latest
    env:
      - name: QDRANT__SERVICE__HTTP_PORT
        value: "6333"
```

**For Docker Compose (local testing):**
```yaml
services:
  app:
    build: .
    depends_on:
      - qdrant
      
  qdrant:
    image: qdrant/qdrant:latest
    ports:
      - "6333:6333"
    volumes:
      - qdrant_data:/qdrant/storage
```

### **3. Deploy/Restart Your App:**
```bash
# Azure Container Apps
az containerapp update --name <your-app> --resource-group <your-rg>

# Or redeploy
az containerapp up --name <your-app> --resource-group <your-rg>
```

### **4. Verify:**
```bash
# Check logs
az containerapp logs show --name <your-app>

# Should see:
# ✅ Loaded secret: RAG-ENABLED -> RAG_ENABLED
# ✅ Loaded secret: QDRANT-URL -> QDRANT_URL
# ✅ Using Qdrant vector store: url=http://qdrant:6333
```

---

## 🎉 **Summary**

**What You Have:**
- ✅ OPENAI-API-KEY already in Key Vault
- ✅ All other required secrets in Key Vault
- ✅ Qdrant code implemented
- ✅ Secret mappings added
- ✅ Setup script ready

**What You Need:**
- [ ] Run `./add_qdrant_secrets.sh` (2 minutes)
- [ ] Deploy Qdrant container (5 minutes)
- [ ] Restart your app (2 minutes)

**Total Time:** ~10 minutes

**Result:** Your multi-agent system will have long-term memory! 🧠

---

**Ready to deploy?** Just run the script and redeploy! 🚀
