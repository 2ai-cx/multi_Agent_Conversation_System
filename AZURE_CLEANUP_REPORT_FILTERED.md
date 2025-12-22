# 🧹 Azure Cleanup Report - THIS PROJECT ONLY

**Generated:** December 1, 2025, 9:21 PM AEST  
**Project:** Timesheet Multi-Agent System  
**Owner:** Dongshu@2ai.cx  
**Filter:** ONLY resources created by Dongshu@2ai.cx for THIS project

---

## 📊 Summary - THIS PROJECT ONLY

### What Belongs to THIS Project:

| Category | Total | Active | To Keep | To Clean |
|----------|-------|--------|---------|----------|
| **Resource Groups** | 1 | 1 | 1 | 0 |
| **Container Apps** | 6 | 6 | 6 | 0 |
| **Container Registries** | 1 | 1 | 1 | 0 |
| **Docker Images (Repos)** | 10 | 6 | 6 | 4 |
| **Docker Image Tags** | ~200+ | 6 | ~15 | ~185+ |

### 💰 Potential Savings (THIS PROJECT ONLY):

- **Old Docker Image Tags:** ~$10-20/month
- **Legacy Docker Repositories:** ~$5-10/month
- **Total Savings:** ~$15-30/month

---

## ✅ Resources Belonging to THIS Project

### 1. Resource Group (KEEP)

**rg-secure-timesheet-agent**
- **Created by:** Dongshu@2ai.cx
- **Created:** August 27, 2025
- **Status:** ✅ Active
- **Action:** KEEP

---

### 2. Container Apps (6 - ALL KEEP)

All in `rg-secure-timesheet-agent`, all created by **Dongshu@2ai.cx**:

#### ✅ **unified-temporal-worker** (Main App)
- **Created:** October 7, 2025
- **Status:** Running
- **Action:** KEEP

#### ✅ **secure-timesheet-agent** (Legacy)
- **Created:** August 27, 2025
- **Status:** Running
- **Action:** KEEP (for now, consider removing after 1 month)

#### ✅ **krakend-gateway**
- **Created:** August 28, 2025
- **Status:** Running
- **Action:** KEEP

#### ✅ **harvest-mcp**
- **Created:** August 28, 2025
- **Status:** Running
- **Action:** KEEP

#### ✅ **temporal-dev-server**
- **Created:** October 13, 2025
- **Status:** Running
- **Action:** KEEP

#### ✅ **temporal-postgres-v2**
- **Created:** October 13, 2025
- **Status:** Running
- **Action:** KEEP

---

### 3. Container Registry (KEEP)

**secureagentreg2ai**
- **Created by:** Dongshu@2ai.cx
- **Created:** August 27, 2025
- **Resource Group:** rg-secure-timesheet-agent
- **Status:** ✅ Active
- **Action:** KEEP

---

### 4. Docker Image Repositories (10 Total)

#### ✅ Current/Active Repositories (6 - KEEP):

1. **multi-agent-system** (39 tags)
   - Status: ✅ Active
   - Latest: 1.0.0-20251201-185138
   - Action: KEEP (but clean old tags)

2. **unified-temporal-worker** (125 tags!)
   - Status: ✅ Active
   - Action: KEEP (but clean old tags)

3. **harvest-mcp** (4 tags)
   - Status: ✅ Active
   - Latest: v1.1.0
   - Action: KEEP (but clean old tags)

4. **krakend-gateway** (17 tags)
   - Status: ✅ Active
   - Action: KEEP (but clean old tags)

5. **temporal-dev-server** (4 tags)
   - Status: ✅ Active
   - Latest: v1.0.3
   - Action: KEEP (but clean old tags)

6. **secure-timesheet-agent** (1 tag)
   - Status: ✅ Legacy backup
   - Action: KEEP (for now)

#### ❌ Legacy/Unused Repositories (4 - DELETE):

7. **temporal-conversation-worker** (17 tags)
   - Status: ❌ Replaced by unified-temporal-worker
   - Action: DELETE entire repository

8. **temporal-timesheet-worker** (20+ tags)
   - Status: ❌ Replaced by unified-temporal-worker
   - Action: DELETE entire repository

9. **temporal-worker** (2 tags)
   - Status: ❌ Replaced by unified-temporal-worker
   - Action: DELETE entire repository

10. **daily-reminder-job** (5 tags)
    - Status: ❌ Functionality now in unified-temporal-worker
    - Action: DELETE entire repository

---

## 🧹 Cleanup Actions - THIS PROJECT ONLY

### Priority 1: Clean Old Docker Image Tags

#### 1. **multi-agent-system** (39 tags → Keep 5)

**Keep:**
- `1.0.0-20251201-185138` (latest - deployed)
- `1.0.0-20251130-*` (last 2 versions)
- `1.0.0-20251129-*` (1 version)
- `1.0.0-20251128-*` (1 version)

**Delete:** ~34 old tags

**Command:**
```bash
# List all tags first
az acr repository show-tags --name secureagentreg2ai --repository multi-agent-system --output table

# Delete old tags (example - adjust dates)
az acr repository delete --name secureagentreg2ai --image multi-agent-system:1.0.0-20251125-085810 --yes
# ... repeat for other old tags
```

#### 2. **unified-temporal-worker** (125 tags → Keep 5)

**Keep:**
- Latest 5 versions only

**Delete:** ~120 old tags

**Command:**
```bash
# List all tags first
az acr repository show-tags --name secureagentreg2ai --repository unified-temporal-worker --output table --orderby time_desc

# Keep latest 5, delete the rest
```

#### 3. **harvest-mcp** (4 tags → Keep 2)

**Keep:**
- `v1.1.0` (latest)
- `v1` (backup)

**Delete:** 2 old tags

#### 4. **krakend-gateway** (17 tags → Keep 3)

**Keep:**
- Latest 3 versions

**Delete:** ~14 old tags

#### 5. **temporal-dev-server** (4 tags → Keep 2)

**Keep:**
- `v1.0.3` (latest)
- `v1.0.2` (backup)

**Delete:** 2 old tags

**Savings:** ~$10-20/month

---

### Priority 2: Delete Legacy Docker Repositories

#### Delete Entire Repositories:

```bash
# 1. temporal-conversation-worker (17 tags)
az acr repository delete --name secureagentreg2ai --repository temporal-conversation-worker --yes

# 2. temporal-timesheet-worker (20+ tags)
az acr repository delete --name secureagentreg2ai --repository temporal-timesheet-worker --yes

# 3. temporal-worker (2 tags)
az acr repository delete --name secureagentreg2ai --repository temporal-worker --yes

# 4. daily-reminder-job (5 tags)
az acr repository delete --name secureagentreg2ai --repository daily-reminder-job --yes
```

**Savings:** ~$5-10/month

---

### Priority 3: Consider Removing Legacy Container App

#### After 1 Month of Stable Operation:

```bash
# Delete legacy secure-timesheet-agent
az containerapp delete --name secure-timesheet-agent --resource-group rg-secure-timesheet-agent --yes
```

**Savings:** ~$20-30/month (after verification)

---

## ❌ Resources NOT Belonging to THIS Project

### Container Apps (15 apps - NOT OURS):

**Created by jude@2ai.cx:**
- improve1
- standard-chat
- lookup-vars
- 2aicontainers (registry)

**Created by graeme@2ai.cx:**
- guideme
- promptflow
- 11 promptflow registries

**Created by Dongshu@2ai.cx (but different projects):**
- autogenstudio2ai (different project)
- opik2ai (registry - different project)
- 2aiContainerRegistry (different project)
- budibase (different project)

**Action:** DO NOT TOUCH - These belong to other projects/people

---

## 📊 Cleanup Impact - THIS PROJECT ONLY

### Immediate Cleanup (Priority 1):

| Action | Items | Savings/Month |
|--------|-------|---------------|
| Delete old Docker tags | ~170 tags | $10-20 |
| **Total Priority 1** | **~170 tags** | **$10-20** |

### Medium-Term Cleanup (Priority 2):

| Action | Items | Savings/Month |
|--------|-------|---------------|
| Delete legacy Docker repos | 4 repos | $5-10 |
| **Total Priority 2** | **4 repos** | **$5-10** |

### Long-Term Cleanup (Priority 3):

| Action | Items | Savings/Month |
|--------|-------|---------------|
| Delete legacy container app | 1 app | $20-30 |
| **Total Priority 3** | **1 app** | **$20-30** |

### **Total Potential Savings (THIS PROJECT):**

- **Items to Clean:** ~175 items
- **Monthly Savings:** $35-60/month
- **Annual Savings:** $420-720/year

---

## 🎯 Recommended Cleanup Order - THIS PROJECT ONLY

### Week 1: Clean Old Docker Tags
```bash
# 1. Clean multi-agent-system (keep latest 5)
# 2. Clean unified-temporal-worker (keep latest 5)
# 3. Clean other repos (keep latest 2-3)
```
**Expected Savings:** $10-20/month

### Week 2: Delete Legacy Repositories
```bash
# 1. Delete temporal-conversation-worker
# 2. Delete temporal-timesheet-worker
# 3. Delete temporal-worker
# 4. Delete daily-reminder-job
```
**Expected Savings:** +$5-10/month

### Week 4+: After Verification
```bash
# 1. Delete secure-timesheet-agent (after 1 month of stable operation)
```
**Expected Savings:** +$20-30/month

---

## 📝 Cleanup Script - THIS PROJECT ONLY

### Step 1: Clean Old Docker Tags (Safe)

```bash
#!/bin/bash
# cleanup_old_tags.sh

REGISTRY="secureagentreg2ai"

echo "🧹 Cleaning old Docker image tags..."

# Function to keep only latest N tags
cleanup_repo() {
    local repo=$1
    local keep_count=$2
    
    echo "📦 Processing $repo (keeping latest $keep_count)..."
    
    # Get all tags sorted by date (newest first)
    tags=$(az acr repository show-tags --name $REGISTRY --repository $repo --orderby time_desc --output tsv)
    
    # Skip the first N tags (keep them), delete the rest
    echo "$tags" | tail -n +$((keep_count + 1)) | while read tag; do
        echo "  ❌ Deleting $repo:$tag"
        az acr repository delete --name $REGISTRY --image $repo:$tag --yes
    done
}

# Clean each repository
cleanup_repo "multi-agent-system" 5
cleanup_repo "unified-temporal-worker" 5
cleanup_repo "harvest-mcp" 2
cleanup_repo "krakend-gateway" 3
cleanup_repo "temporal-dev-server" 2

echo "✅ Cleanup complete!"
```

### Step 2: Delete Legacy Repositories (After Verification)

```bash
#!/bin/bash
# delete_legacy_repos.sh

REGISTRY="secureagentreg2ai"

echo "🧹 Deleting legacy Docker repositories..."

# Delete legacy repositories
az acr repository delete --name $REGISTRY --repository temporal-conversation-worker --yes
az acr repository delete --name $REGISTRY --repository temporal-timesheet-worker --yes
az acr repository delete --name $REGISTRY --repository temporal-worker --yes
az acr repository delete --name $REGISTRY --repository daily-reminder-job --yes

echo "✅ Legacy repositories deleted!"
```

### Step 3: Delete Legacy Container App (After 1 Month)

```bash
#!/bin/bash
# delete_legacy_app.sh

echo "🧹 Deleting legacy container app..."

# Delete legacy app
az containerapp delete --name secure-timesheet-agent --resource-group rg-secure-timesheet-agent --yes

echo "✅ Legacy app deleted!"
```

---

## ⚠️ Important Safety Notes

### Before Running Cleanup:

1. ✅ **Verify Current System is Stable**
   - unified-temporal-worker running for at least 1 week
   - No errors in logs
   - All features working

2. ✅ **Backup Current Configuration**
   - Export environment variables
   - Document current image tags
   - Save deployment scripts

3. ✅ **Test Rollback**
   - Ensure you can redeploy previous version
   - Keep latest 3-5 versions as backup

4. ✅ **Run Gradually**
   - Start with oldest tags
   - Monitor after each cleanup
   - Stop if any issues

### Rollback Plan:

If something goes wrong:
```bash
# Redeploy previous version
az containerapp update \
  --name unified-temporal-worker \
  --resource-group rg-secure-timesheet-agent \
  --image secureagentreg2ai.azurecr.io/multi-agent-system:1.0.0-20251130-XXXXXX
```

---

## 📊 Final Summary - THIS PROJECT ONLY

### Current State:
- ✅ 1 Resource Group (rg-secure-timesheet-agent)
- ✅ 6 Container Apps (all active)
- ✅ 1 Container Registry (secureagentreg2ai)
- ✅ 10 Docker Repositories
- ✅ ~200+ Docker Image Tags

### After Cleanup:
- ✅ 1 Resource Group (same)
- ✅ 5-6 Container Apps (possibly remove legacy)
- ✅ 1 Container Registry (same)
- ✅ 6 Docker Repositories (remove 4 legacy)
- ✅ ~15-20 Docker Image Tags (remove ~180+)

### Savings:
- **Immediate:** $10-20/month (clean old tags)
- **Short-term:** +$5-10/month (delete legacy repos)
- **Long-term:** +$20-30/month (delete legacy app)
- **Total:** $35-60/month (10-15% cost reduction)

### What to Keep:
- ✅ All 6 container apps (for now)
- ✅ secureagentreg2ai registry
- ✅ Latest 3-5 versions of each active image
- ✅ All current deployments

### What to Delete:
- ❌ ~170 old Docker image tags
- ❌ 4 legacy Docker repositories
- ❌ 1 legacy container app (after 1 month)

---

## 🎯 Action Plan

### This Week:
- [ ] Review this report
- [ ] Verify current system is stable
- [ ] Run cleanup script for old tags
- [ ] Monitor for issues

### Next Week:
- [ ] Delete 4 legacy repositories
- [ ] Verify no issues

### After 1 Month:
- [ ] Consider deleting secure-timesheet-agent
- [ ] Final verification

---

**Status:** ✅ Ready for Cleanup  
**Risk Level:** Low (only cleaning THIS project's resources)  
**Potential Savings:** $35-60/month  
**Owner:** Dongshu@2ai.cx

🧹 Clean and focused cleanup for THIS project only! 💰
