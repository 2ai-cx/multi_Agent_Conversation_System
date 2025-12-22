# Azure Container Apps Networking Issue - Debug Summary

## The Question: Sidecar vs Separate Service

**Your Question:** "Why listen to localhost when we deployed Qdrant in Azure?"

**Answer:** Because the separate Qdrant service has a networking problem!

---

## What We Have:

### 1. Separate Qdrant Service ✅ (Deployed but unreachable)
```
Name: qdrant-service
Status: Running
URL: http://qdrant-service.internal.kindcoast-5a2a34c6.australiaeast.azurecontainerapps.io:6333
Problem: Connection timeout from main app ❌
```

### 2. Sidecar Attempt ⚠️ (Deployed but stuck)
```
Name: qdrant (sidecar in unified-temporal-worker)
Status: Activating (stuck)
URL: http://localhost:6333
Problem: Container not starting ❌
```

---

## Root Cause Analysis:

### Why Separate Service Doesn't Work:

**Test Result:**
```bash
# From main app container:
curl http://qdrant-service.internal...:6333
# DNS resolves to: 100.100.0.209
# Result: Connection timed out after 30+ seconds
```

**Possible Causes:**
1. **Network Policy:** Azure Container Apps might have network policies blocking inter-app communication
2. **Ingress Configuration:** Internal ingress might not be properly configured
3. **Service Discovery:** DNS works but routing fails
4. **Firewall Rules:** Some security rule blocking the traffic

### Why Sidecar Should Work (But Isn't):

**Theory:** Containers in same pod share localhost - no network routing needed!

**Reality:** Qdrant sidecar stuck in "Activating" state

**Possible Causes:**
1. **Resource Constraints:** Not enough CPU/memory for both containers
2. **Health Probe:** Missing health probe causing activation failure
3. **Image Pull:** Issue pulling qdrant/qdrant:v1.16.2
4. **Command/Args:** Wrong startup command

---

## Solutions to Try:

### Option 1: Fix Separate Service Networking (Recommended)

**Why:** This is the proper architecture - separate services

**Steps:**
1. Check if Dapr is needed for service-to-service communication
2. Verify network security rules
3. Try using service name without FQDN: `http://qdrant-service:6333`
4. Enable Dapr sidecar for service mesh

```bash
# Enable Dapr
az containerapp dapr enable \
  --name unified-temporal-worker \
  --resource-group rg-secure-timesheet-agent \
  --dapr-app-id main-app

az containerapp dapr enable \
  --name qdrant-service \
  --resource-group rg-secure-timesheet-agent \
  --dapr-app-id qdrant
```

### Option 2: Fix Sidecar Deployment

**Why:** Guaranteed connectivity via localhost

**Steps:**
1. Add health probe for Qdrant container
2. Increase resources
3. Remove command/args (use default)
4. Check container logs for startup errors

```yaml
containers:
- name: qdrant
  image: qdrant/qdrant:v1.16.2
  resources:
    cpu: 1.0  # Increase from 0.5
    memory: 2Gi  # Increase from 1Gi
  probes:
  - type: liveness
    httpGet:
      path: /
      port: 6333
    initialDelaySeconds: 30
    periodSeconds: 10
```

### Option 3: Use Qdrant Cloud (Easiest)

**Why:** No networking issues, managed service

**Steps:**
1. Sign up for Qdrant Cloud
2. Get API URL and key
3. Update Key Vault secrets
4. No Azure networking issues!

---

## Recommendation:

**Try Option 1 First** - Fix the separate service networking

**Why:**
- ✅ Proper architecture (separation of concerns)
- ✅ Independent scaling
- ✅ Easier to manage
- ✅ Can add persistent storage easily

**How to Debug:**
```bash
# 1. Check if Dapr is available
az containerapp env dapr-component list \
  --name aca-env-secure-agent \
  --resource-group rg-secure-timesheet-agent

# 2. Try simpler URL
az keyvault secret set \
  --vault-name kv-secure-agent-2ai \
  --name "QDRANT-URL" \
  --value "http://qdrant-service:6333"

# 3. Check network policies
az containerapp env show \
  --name aca-env-secure-agent \
  --resource-group rg-secure-timesheet-agent \
  --query "properties.vnetConfiguration"
```

---

## Current Status:

| Component | Status | Issue |
|-----------|--------|-------|
| Main App | ✅ Running | None |
| Qdrant Service (separate) | ✅ Running | ❌ Unreachable |
| Qdrant Sidecar | ⚠️ Activating | ❌ Won't start |
| RAG Code | ✅ Working | Waiting for Qdrant |
| Configuration | ✅ Correct | All secrets loaded |

---

## Answer to Your Question:

**Q: "Can the localhost thing solve the root problem?"**

**A: YES, theoretically!** 

Sidecar with localhost **bypasses** the networking issue entirely. But currently the sidecar won't start, so we need to either:
1. Fix the sidecar startup issue, OR
2. Fix the original networking issue with the separate service

**The separate service is the better long-term solution** - we just need to figure out why Azure Container Apps internal networking isn't working.

---

## Next Steps:

1. ✅ Revert to separate service architecture
2. 🔍 Investigate Azure Container Apps networking requirements
3. 🧪 Try Dapr for service-to-service communication
4. 🧪 Try simpler service URL format
5. 📞 Consider Azure support if networking continues to fail

