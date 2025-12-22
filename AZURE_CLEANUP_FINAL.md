# 🧹 Azure Cleanup Report - FINAL (Timesheet Project ONLY)

**Generated:** December 1, 2025, 9:26 PM AEST  
**Project:** Timesheet Multi-Agent System  
**Owner:** Dongshu@2ai.cx  
**Filter:** ONLY timesheet project resources (rg-secure-timesheet-agent)

---

## ✅ THIS Timesheet Project's Resources

### Resource Group: rg-secure-timesheet-agent

**Created by:** Dongshu@2ai.cx  
**Created:** August 27, 2025  
**Status:** ✅ Active  
**Action:** KEEP

---

### Container Apps (6 - All Running)

All created by **Dongshu@2ai.cx** in **rg-secure-timesheet-agent**:

1. ✅ **unified-temporal-worker**
   - Created: October 7, 2025
   - Status: Running
   - Action: **KEEP** (main app)

2. ✅ **secure-timesheet-agent**
   - Created: August 27, 2025
   - Status: Running
   - Action: **KEEP** (legacy backup, consider removing after 1 month)

3. ✅ **krakend-gateway**
   - Created: August 28, 2025
   - Status: Running
   - Action: **KEEP**

4. ✅ **harvest-mcp**
   - Created: August 28, 2025
   - Status: Running
   - Action: **KEEP**

5. ✅ **temporal-dev-server**
   - Created: October 13, 2025
   - Status: Running
   - Action: **KEEP**

6. ✅ **temporal-postgres-v2**
   - Created: October 13, 2025
   - Status: Running
   - Action: **KEEP**

---

### Container Registry (1)

**secureagentreg2ai**
- Created by: Dongshu@2ai.cx
- Created: August 27, 2025
- Resource Group: rg-secure-timesheet-agent
- Status: ✅ Active
- Action: **KEEP**

---

### Docker Image Repositories (10 in secureagentreg2ai)

#### ✅ Active Repositories (6 - KEEP):

1. **multi-agent-system** (39 tags)
   - Latest: 1.0.0-20251201-185138
   - Action: KEEP repo, clean old tags

2. **unified-temporal-worker** (125 tags)
   - Action: KEEP repo, clean old tags

3. **harvest-mcp** (4 tags)
   - Latest: v1.1.0
   - Action: KEEP repo, clean old tags

4. **krakend-gateway** (17 tags)
   - Action: KEEP repo, clean old tags

5. **temporal-dev-server** (4 tags)
   - Latest: v1.0.3
   - Action: KEEP repo, clean old tags

6. **secure-timesheet-agent** (1 tag)
   - Action: KEEP repo (legacy backup)

#### ❌ Legacy Repositories (4 - DELETE):

7. **temporal-conversation-worker** (17 tags)
   - Status: Replaced by unified-temporal-worker
   - Action: **DELETE entire repository**

8. **temporal-timesheet-worker** (20+ tags)
   - Status: Replaced by unified-temporal-worker
   - Action: **DELETE entire repository**

9. **temporal-worker** (2 tags)
   - Status: Replaced by unified-temporal-worker
   - Action: **DELETE entire repository**

10. **daily-reminder-job** (5 tags)
    - Status: Functionality now in unified-temporal-worker
    - Action: **DELETE entire repository**

---

## ❌ YOUR Other Projects (NOT Timesheet - DO NOT TOUCH)

### Container Apps (9 stopped apps):

**In container-apps-env (different projects):**
1. ❌ autogenstudio2ai (Stopped) - Different project
2. ❌ autogenstudio2aiaddlist3 (Stopped) - Different project
3. ❌ budibaseredis-dev (Stopped) - Budibase project
4. ❌ budibaseminio-dev (Stopped) - Budibase project
5. ❌ budibaseapps-dev (Stopped) - Budibase project
6. ❌ budibaseworker-dev (Stopped) - Budibase project
7. ❌ budibaseproxy-dev (Stopped) - Budibase project
8. ❌ budibasecouchdb-dev (Stopped) - Budibase project
9. ❌ budibaseapp-dev1 (Stopped) - Budibase project

**Action:** These are YOUR other projects, not timesheet project - handle separately

### Container Registries (3):

1. ❌ opik2ai (container-apps-env) - Different project
2. ❌ 2aiContainerRegistry (containers) - Different project
3. ❌ budibase (containers) - Budibase project

**Action:** These are YOUR other projects - handle separately

---

## 🧹 Cleanup Actions - TIMESHEET PROJECT ONLY

### Priority 1: Clean Old Docker Image Tags

#### Script to Clean Old Tags (Keep Latest 5):

```bash
#!/bin/bash
# cleanup_timesheet_tags.sh
# ONLY touches timesheet project resources

REGISTRY="secureagentreg2ai"

echo "🧹 Cleaning old Docker image tags for TIMESHEET PROJECT..."
echo "Registry: $REGISTRY"
echo "Resource Group: rg-secure-timesheet-agent"
echo ""

# Function to keep only latest N tags
cleanup_repo() {
    local repo=$1
    local keep_count=$2
    
    echo "📦 Processing $repo (keeping latest $keep_count)..."
    
    # Get all tags sorted by date (newest first)
    tags=$(az acr repository show-tags \
        --name $REGISTRY \
        --repository $repo \
        --orderby time_desc \
        --output tsv)
    
    # Count total tags
    total=$(echo "$tags" | wc -l)
    to_delete=$((total - keep_count))
    
    echo "   Total tags: $total"
    echo "   Keeping: $keep_count"
    echo "   Deleting: $to_delete"
    
    if [ $to_delete -gt 0 ]; then
        # Skip the first N tags (keep them), delete the rest
        echo "$tags" | tail -n +$((keep_count + 1)) | while read tag; do
            echo "  ❌ Deleting $repo:$tag"
            az acr repository delete \
                --name $REGISTRY \
                --image $repo:$tag \
                --yes
        done
    else
        echo "   ✅ No tags to delete"
    fi
    echo ""
}

# Clean each active repository
cleanup_repo "multi-agent-system" 5
cleanup_repo "unified-temporal-worker" 5
cleanup_repo "harvest-mcp" 2
cleanup_repo "krakend-gateway" 3
cleanup_repo "temporal-dev-server" 2

echo "✅ Tag cleanup complete!"
echo ""
echo "📊 Summary:"
echo "  - Kept latest 5 versions of multi-agent-system"
echo "  - Kept latest 5 versions of unified-temporal-worker"
echo "  - Kept latest 2 versions of harvest-mcp"
echo "  - Kept latest 3 versions of krakend-gateway"
echo "  - Kept latest 2 versions of temporal-dev-server"
```

**Estimated Savings:** $10-20/month

---

### Priority 2: Delete Legacy Docker Repositories

```bash
#!/bin/bash
# delete_legacy_repos.sh
# ONLY touches timesheet project resources

REGISTRY="secureagentreg2ai"

echo "🧹 Deleting legacy Docker repositories for TIMESHEET PROJECT..."
echo "Registry: $REGISTRY"
echo "Resource Group: rg-secure-timesheet-agent"
echo ""

# Confirm before deleting
read -p "⚠️  This will DELETE 4 legacy repositories. Continue? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "❌ Cancelled"
    exit 1
fi

echo ""
echo "Deleting legacy repositories..."

# Delete legacy repositories
echo "1/4 Deleting temporal-conversation-worker..."
az acr repository delete --name $REGISTRY --repository temporal-conversation-worker --yes

echo "2/4 Deleting temporal-timesheet-worker..."
az acr repository delete --name $REGISTRY --repository temporal-timesheet-worker --yes

echo "3/4 Deleting temporal-worker..."
az acr repository delete --name $REGISTRY --repository temporal-worker --yes

echo "4/4 Deleting daily-reminder-job..."
az acr repository delete --name $REGISTRY --repository daily-reminder-job --yes

echo ""
echo "✅ Legacy repositories deleted!"
echo ""
echo "📊 Deleted:"
echo "  - temporal-conversation-worker (17 tags)"
echo "  - temporal-timesheet-worker (20+ tags)"
echo "  - temporal-worker (2 tags)"
echo "  - daily-reminder-job (5 tags)"
```

**Estimated Savings:** $5-10/month

---

### Priority 3: Delete Legacy Container App (After 1 Month)

```bash
#!/bin/bash
# delete_legacy_app.sh
# ONLY touches timesheet project resources

echo "🧹 Deleting legacy container app for TIMESHEET PROJECT..."
echo "Resource Group: rg-secure-timesheet-agent"
echo ""

# Verify unified-temporal-worker is running
status=$(az containerapp show \
    --name unified-temporal-worker \
    --resource-group rg-secure-timesheet-agent \
    --query "properties.runningStatus" \
    --output tsv)

if [ "$status" != "Running" ]; then
    echo "❌ ERROR: unified-temporal-worker is not running!"
    echo "   Status: $status"
    echo "   Cannot delete legacy app."
    exit 1
fi

echo "✅ unified-temporal-worker is running"
echo ""

# Confirm before deleting
read -p "⚠️  This will DELETE secure-timesheet-agent. Continue? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "❌ Cancelled"
    exit 1
fi

echo ""
echo "Deleting legacy app..."

az containerapp delete \
    --name secure-timesheet-agent \
    --resource-group rg-secure-timesheet-agent \
    --yes

echo ""
echo "✅ Legacy app deleted!"
echo ""
echo "📊 Remaining apps in rg-secure-timesheet-agent:"
az containerapp list \
    --resource-group rg-secure-timesheet-agent \
    --query "[].name" \
    --output table
```

**Estimated Savings:** $20-30/month (after 1 month of stable operation)

---

## 📊 Cleanup Impact - TIMESHEET PROJECT ONLY

### Summary:

| Priority | Action | Items | Savings/Month | When |
|----------|--------|-------|---------------|------|
| **Priority 1** | Clean old Docker tags | ~170 tags | $10-20 | This week |
| **Priority 2** | Delete legacy repos | 4 repos | $5-10 | Next week |
| **Priority 3** | Delete legacy app | 1 app | $20-30 | After 1 month |
| **TOTAL** | | **~175 items** | **$35-60** | |

### Current Monthly Cost (Timesheet Project):
- 6 Container Apps: ~$170-255/month
- 1 Container Registry: ~$5-10/month
- Docker Images Storage: ~$10-20/month
- **Total:** ~$185-285/month

### After Cleanup:
- 5 Container Apps: ~$150-225/month
- 1 Container Registry: ~$5-10/month
- Docker Images Storage: ~$5-10/month
- **Total:** ~$160-245/month

### **Savings: $25-40/month (10-15% reduction)**

---

## ⚠️ Safety Checklist

### Before Running Any Cleanup:

- [ ] Verify unified-temporal-worker has been running stable for 1+ week
- [ ] Check logs for any errors
- [ ] Verify all features working (jokes, minification, Opik)
- [ ] Backup current deployment configuration
- [ ] Document current image tags
- [ ] Test rollback procedure

### During Cleanup:

- [ ] Run scripts one at a time
- [ ] Monitor system after each step
- [ ] Check health endpoint after changes
- [ ] Verify no errors in logs
- [ ] Stop if any issues occur

### After Cleanup:

- [ ] Verify all services still running
- [ ] Test end-to-end functionality
- [ ] Monitor for 24-48 hours
- [ ] Document what was deleted

---

## 🎯 Recommended Timeline

### Week 1 (December 2-8, 2025):
```bash
# Day 1: Review and prepare
- Review this report
- Verify system is stable
- Backup configurations

# Day 2-3: Clean old tags
chmod +x cleanup_timesheet_tags.sh
./cleanup_timesheet_tags.sh

# Day 4-7: Monitor
- Check logs daily
- Verify no issues
- Confirm system stable
```

### Week 2 (December 9-15, 2025):
```bash
# Day 1: Delete legacy repos
chmod +x delete_legacy_repos.sh
./delete_legacy_repos.sh

# Day 2-7: Monitor
- Check logs daily
- Verify no issues
- Confirm system stable
```

### Month 2 (January 2026):
```bash
# After 1 month of stable operation
chmod +x delete_legacy_app.sh
./delete_legacy_app.sh

# Monitor for 1 week
- Verify no issues
- Confirm all features working
```

---

## 📝 Final Summary

### THIS Timesheet Project Has:

**Current State:**
- ✅ 1 Resource Group (rg-secure-timesheet-agent)
- ✅ 6 Container Apps (all running)
- ✅ 1 Container Registry (secureagentreg2ai)
- ✅ 10 Docker Repositories (6 active, 4 legacy)
- ✅ ~200 Docker Image Tags (only 6 in use)

**After Cleanup:**
- ✅ 1 Resource Group (same)
- ✅ 5 Container Apps (remove legacy after 1 month)
- ✅ 1 Container Registry (same)
- ✅ 6 Docker Repositories (remove 4 legacy)
- ✅ ~15-20 Docker Image Tags (remove ~180+)

**Savings:**
- Immediate: $10-20/month
- Short-term: +$5-10/month
- Long-term: +$20-30/month
- **Total: $35-60/month**

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

**Status:** ✅ Ready for Cleanup  
**Risk Level:** Low (only timesheet project resources)  
**Potential Savings:** $35-60/month  
**Owner:** Dongshu@2ai.cx  
**Project:** Timesheet Multi-Agent System ONLY

🧹 Clean, focused, and safe! 💰
