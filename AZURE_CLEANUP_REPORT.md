# 🧹 Azure Cleanup Report - Comprehensive Inventory

**Generated:** December 1, 2025, 9:09 PM AEST  
**Purpose:** Identify all old/unused resources for potential cleanup

---

## 📊 Summary

### What We Found:

| Category | Total | Active | Stopped | Old/Unused |
|----------|-------|--------|---------|------------|
| **Resource Groups** | 27 | 27 | 0 | ~15 potentially unused |
| **Container Apps** | 21 | 9 | 12 | 12 stopped |
| **Container Registries** | 16 | 16 | 0 | ~10 old/unused |
| **Docker Images (Tags)** | ~300+ | 6 | 0 | ~290+ old versions |
| **Web Apps** | 0 | 0 | 0 | 0 |
| **VMs** | 0 | 0 | 0 | 0 |

### 💰 Estimated Savings from Cleanup:

- **Stopped Container Apps:** ~$50-100/month
- **Old Container Registries:** ~$20-50/month
- **Old Docker Images:** ~$10-30/month (storage)
- **Unused Resource Groups:** ~$5-20/month
- **Total Potential Savings:** ~$85-200/month

---

## 🚀 Container Apps (21 Total)

### ✅ Active & In Use (9 apps)

#### **rg-secure-timesheet-agent** (6 apps - CURRENT PROJECT):
1. ✅ **unified-temporal-worker** - Main application (KEEP)
2. ✅ **krakend-gateway** - API gateway (KEEP)
3. ✅ **harvest-mcp** - Harvest MCP server (KEEP)
4. ✅ **temporal-dev-server** - Temporal server (KEEP)
5. ✅ **temporal-postgres-v2** - Temporal database (KEEP)
6. ✅ **secure-timesheet-agent** - Legacy backup (CONSIDER REMOVING)

#### **container-apps-env** (3 apps):
7. ✅ **improve1** - Running
8. ✅ **standard-chat** - Running
9. ✅ **guideme** - Running

---

### ❌ Stopped & Unused (12 apps - CANDIDATES FOR DELETION)

#### **container-apps-env** (12 stopped apps):

1. ❌ **lookup-vars-staging** - Stopped
2. ❌ **lookup-vars** - Stopped
3. ❌ **promptflow** - Stopped
4. ❌ **autogenstudio2ai** - Stopped
5. ❌ **autogenstudio2aiaddlist3** - Stopped
6. ❌ **budibaseredis-dev** - Stopped
7. ❌ **budibaseminio-dev** - Stopped
8. ❌ **budibaseapps-dev** - Stopped
9. ❌ **budibaseworker-dev** - Stopped
10. ❌ **budibaseproxy-dev** - Stopped
11. ❌ **budibasecouchdb-dev** - Stopped
12. ❌ **budibaseapp-dev1** - Stopped

**Recommendation:** Delete all 12 stopped apps  
**Savings:** ~$50-100/month

---

## 📦 Container Registries (16 Total)

### Current Project Registry (KEEP):
- ✅ **secureagentreg2ai** (rg-secure-timesheet-agent) - KEEP

### Active Registries (Consider Keeping):
- ✅ **opik2ai** (container-apps-env) - Standard tier
- ✅ **2aiContainerRegistry** (containers) - Standard tier
- ✅ **budibase** (containers) - Standard tier

### Old/Unused Registries (CANDIDATES FOR DELETION):

#### Promptflow Registries (11 registries - likely unused):
1. ❌ **promptflow4886aa** (container-apps-env) - Basic tier
2. ❌ **promptflow4c193b** (container-apps-env) - Basic tier
3. ❌ **promptflow6bde33** (container-apps-env) - Basic tier
4. ❌ **promptflow779421** (container-apps-env) - Basic tier
5. ❌ **promptflow7d7d36** (container-apps-env) - Basic tier
6. ❌ **promptflowa474e9** (container-apps-env) - Basic tier
7. ❌ **promptflowa67a1f** (container-apps-env) - Basic tier
8. ❌ **promptflowb0f553** (container-apps-env) - Basic tier
9. ❌ **promptflowd8ac22** (container-apps-env) - Basic tier
10. ❌ **promptflowf4158a** (container-apps-env) - Basic tier
11. ❌ **2aicontainers** (containers) - Basic tier

#### Other Old Registries:
12. ❌ **057db84654b84b6287a5151358798608** (2ai_cognitive) - Basic tier

**Recommendation:** Delete 11 promptflow registries + 1 old registry  
**Savings:** ~$20-50/month

---

## 🐳 Docker Images in secureagentreg2ai

### Current Project Images (KEEP):

#### 1. **multi-agent-system** (39 tags)
- ✅ **Latest:** 1.0.0-20251201-185138 (KEEP)
- ❌ **Old:** 38 previous versions (DELETE)

**Tags to keep:**
- `1.0.0-20251201-185138` (latest deployment)
- `1.0.0-20251130-*` (last 2-3 versions as backup)

**Tags to delete:** ~35 old versions

#### 2. **unified-temporal-worker** (125 tags!)
- ✅ **Latest:** (check current deployment)
- ❌ **Old:** ~120+ previous versions (DELETE)

**Tags to keep:**
- Latest 3-5 versions only

**Tags to delete:** ~120 old versions

#### 3. **harvest-mcp** (4 tags)
- ✅ **Latest:** v1.1.0 (KEEP)
- ❌ **Old:** 3 previous versions (DELETE)

#### 4. **krakend-gateway** (17 tags)
- ✅ **Latest:** (check current deployment)
- ❌ **Old:** ~15 previous versions (DELETE)

#### 5. **temporal-dev-server** (4 tags)
- ✅ **Latest:** v1.0.3 (KEEP)
- ❌ **Old:** 3 previous versions (DELETE)

---

### Legacy/Unused Images (CONSIDER DELETING):

#### 6. **secure-timesheet-agent** (1 tag)
- ❌ production-v1 (legacy system, replaced by unified-temporal-worker)
- **Recommendation:** Keep for now as backup, delete after 1 month

#### 7. **temporal-conversation-worker** (17 tags)
- ❌ All tags (replaced by unified-temporal-worker)
- **Recommendation:** DELETE entire repository

#### 8. **temporal-timesheet-worker** (20+ tags)
- ❌ All tags (replaced by unified-temporal-worker)
- **Recommendation:** DELETE entire repository

#### 9. **temporal-worker** (2 tags)
- ❌ All tags (replaced by unified-temporal-worker)
- **Recommendation:** DELETE entire repository

#### 10. **daily-reminder-job** (5 tags)
- ❌ All tags (functionality now in unified-temporal-worker)
- **Recommendation:** DELETE entire repository

---

## 📁 Resource Groups (27 Total)

### Current Project (KEEP):
- ✅ **rg-secure-timesheet-agent** - Current project (KEEP)

### Active Groups (Likely in Use):
- ✅ **container-apps-env** - Container apps environment
- ✅ **containers** - Container resources
- ✅ **2ai_databases** - Databases
- ✅ **2ai_cognitive** - Cognitive services
- ✅ **2ai_network** - Networking
- ✅ **2aiAdmin** - Admin resources

### Potentially Unused Groups (INVESTIGATE):

#### Development/Testing:
1. ❓ **rg-graemeai** (francecentral)
2. ❓ **rg-metahubusa** (eastus2)
3. ❓ **Open_Ai** (eastus)
4. ❓ **2a1_functions** (australiaeast)
5. ❓ **2ai_translate** (australiaeast)
6. ❓ **2ai_speech** (australiaeast)
7. ❓ **2ai_websearch** (australiaeast)

#### Auto-Generated/Monitoring:
8. ❓ **azureapp-auto-alerts-38ee3f-graeme_2ai_com_au** (eastus)
9. ❓ **azureapp-auto-alerts-38ee3f-graeme_2ai_cx** (eastus)
10. ❓ **azureapp-auto-alerts-fe316b-graeme_2ai_com_au** (eastus)
11. ❓ **azureapp-auto-alerts-fe316b-graeme_2ai_cx** (eastus)
12. ❓ **MA_defaultazuremonitorworkspace-eau_australiaeast_managed** (australiaeast)

#### System/Default:
13. ❓ **DefaultResourceGroup-eastus2** (eastus2)
14. ❓ **DefaultResourceGroup-EAU** (australiaeast)
15. ❓ **NetworkWatcherRG** (australiaeast)
16. ❓ **cloud-shell-storage-southeastasia** (southeastasia)
17. ❓ **dashboards** (australiaeast)
18. ❓ **2ai_managed_identities** (eastus)
19. ❓ **MC2_containers_opik-k8_australiaeast** (australiaeast) - Kubernetes cluster

**Recommendation:** Investigate each group, check resources, delete if unused

---

## 🎯 Cleanup Recommendations

### Priority 1: High Impact, Low Risk

#### 1. Delete Stopped Container Apps (12 apps)
```bash
# Delete all stopped apps in container-apps-env
az containerapp delete --name lookup-vars-staging --resource-group container-apps-env --yes
az containerapp delete --name lookup-vars --resource-group container-apps-env --yes
az containerapp delete --name promptflow --resource-group container-apps-env --yes
az containerapp delete --name autogenstudio2ai --resource-group container-apps-env --yes
az containerapp delete --name autogenstudio2aiaddlist3 --resource-group container-apps-env --yes
az containerapp delete --name budibaseredis-dev --resource-group container-apps-env --yes
az containerapp delete --name budibaseminio-dev --resource-group container-apps-env --yes
az containerapp delete --name budibaseapps-dev --resource-group container-apps-env --yes
az containerapp delete --name budibaseworker-dev --resource-group container-apps-env --yes
az containerapp delete --name budibaseproxy-dev --resource-group container-apps-env --yes
az containerapp delete --name budibasecouchdb-dev --resource-group container-apps-env --yes
az containerapp delete --name budibaseapp-dev1 --resource-group container-apps-env --yes
```
**Savings:** ~$50-100/month

#### 2. Delete Old Docker Image Tags (Keep Latest 3-5 Only)

**multi-agent-system** (delete ~35 old tags):
```bash
# Keep only latest 5 versions, delete the rest
# Manual review recommended
```

**unified-temporal-worker** (delete ~120 old tags):
```bash
# Keep only latest 5 versions, delete the rest
# Manual review recommended
```

**Savings:** ~$10-20/month (storage)

#### 3. Delete Legacy Docker Repositories
```bash
# Delete entire repositories that are no longer used
az acr repository delete --name secureagentreg2ai --repository temporal-conversation-worker --yes
az acr repository delete --name secureagentreg2ai --repository temporal-timesheet-worker --yes
az acr repository delete --name secureagentreg2ai --repository temporal-worker --yes
az acr repository delete --name secureagentreg2ai --repository daily-reminder-job --yes
```
**Savings:** ~$5-10/month

---

### Priority 2: Medium Impact, Medium Risk

#### 4. Delete Old Container Registries (11 promptflow registries)
```bash
# Delete all promptflow registries (after verifying they're not in use)
az acr delete --name promptflow4886aa --resource-group container-apps-env --yes
az acr delete --name promptflow4c193b --resource-group container-apps-env --yes
# ... (repeat for all 11 registries)
```
**Savings:** ~$20-40/month

#### 5. Delete Legacy Container App (secure-timesheet-agent)
```bash
# After 1 month of unified-temporal-worker running successfully
az containerapp delete --name secure-timesheet-agent --resource-group rg-secure-timesheet-agent --yes
```
**Savings:** ~$20-30/month

---

### Priority 3: Low Impact, High Risk (Investigate First)

#### 6. Investigate and Delete Unused Resource Groups

**Steps:**
1. List all resources in each group
2. Check last modified date
3. Verify not in use
4. Delete if confirmed unused

**Potential Savings:** ~$10-50/month

---

## 📊 Cleanup Impact Summary

### Immediate Cleanup (Priority 1):

| Action | Items | Savings/Month |
|--------|-------|---------------|
| Delete stopped container apps | 12 apps | $50-100 |
| Delete old Docker tags | ~155 tags | $10-20 |
| Delete legacy Docker repos | 4 repos | $5-10 |
| **Total Priority 1** | **171 items** | **$65-130** |

### Medium-Term Cleanup (Priority 2):

| Action | Items | Savings/Month |
|--------|-------|---------------|
| Delete old registries | 11 registries | $20-40 |
| Delete legacy container app | 1 app | $20-30 |
| **Total Priority 2** | **12 items** | **$40-70** |

### Long-Term Cleanup (Priority 3):

| Action | Items | Savings/Month |
|--------|-------|---------------|
| Delete unused resource groups | ~10 groups | $10-50 |
| **Total Priority 3** | **~10 groups** | **$10-50** |

### **Grand Total Potential Savings:**

- **Items to Clean:** ~193 items
- **Monthly Savings:** $115-250/month
- **Annual Savings:** $1,380-3,000/year

---

## ⚠️ Important Notes

### Before Deleting Anything:

1. ✅ **Backup Critical Data**
   - Export any important configurations
   - Save environment variables
   - Document current setup

2. ✅ **Verify Not In Use**
   - Check last access time
   - Review logs
   - Confirm with team

3. ✅ **Test Current System**
   - Ensure unified-temporal-worker is stable
   - Verify all features working
   - Monitor for 1-2 weeks

4. ✅ **Delete Gradually**
   - Start with stopped apps
   - Then old Docker tags
   - Finally registries and groups

### Rollback Plan:

- Keep latest 3-5 Docker image versions
- Keep legacy app for 1 month
- Document what was deleted
- Have restore procedure ready

---

## 🎯 Recommended Cleanup Order

### Week 1: Low-Risk Cleanup
1. ✅ Delete 12 stopped container apps
2. ✅ Delete old Docker tags (keep latest 5)
3. ✅ Delete 4 legacy Docker repositories

**Expected Savings:** $65-130/month

### Week 2-3: Medium-Risk Cleanup
4. ✅ Delete 11 old promptflow registries
5. ✅ Monitor unified-temporal-worker stability

**Expected Savings:** +$20-40/month

### Week 4+: After Verification
6. ✅ Delete legacy secure-timesheet-agent app
7. ✅ Investigate and delete unused resource groups

**Expected Savings:** +$30-80/month

---

## 📝 Cleanup Checklist

### Immediate Actions:
- [ ] Review this report
- [ ] Verify current system is stable
- [ ] Backup critical configurations
- [ ] Create cleanup script

### Week 1:
- [ ] Delete 12 stopped container apps
- [ ] Delete old Docker tags (multi-agent-system)
- [ ] Delete old Docker tags (unified-temporal-worker)
- [ ] Delete 4 legacy Docker repositories

### Week 2-3:
- [ ] Monitor system stability
- [ ] Delete 11 promptflow registries
- [ ] Verify no issues

### Week 4+:
- [ ] Delete legacy secure-timesheet-agent
- [ ] Investigate unused resource groups
- [ ] Delete confirmed unused groups
- [ ] Document final cleanup

---

## 💰 Final Summary

### Current Monthly Cost: ~$196-367
### After Cleanup: ~$81-117
### **Savings: $115-250/month (40-68% reduction!)**

### What to Keep:
- ✅ rg-secure-timesheet-agent (all 6 apps)
- ✅ secureagentreg2ai registry
- ✅ Latest 3-5 Docker image versions
- ✅ Active resource groups

### What to Delete:
- ❌ 12 stopped container apps
- ❌ ~155 old Docker image tags
- ❌ 4 legacy Docker repositories
- ❌ 11 old container registries
- ❌ ~10 unused resource groups

---

**Status:** ✅ Ready for Cleanup  
**Risk Level:** Low (if done gradually)  
**Potential Savings:** $115-250/month  
**Recommended Start:** Immediately (Priority 1 items)

🧹 Time to clean up and save money! 💰
