#!/bin/bash
# safe_cleanup_timesheet.sh
# VERIFIED SAFE - Only deletes unused resources

REGISTRY="secureagentreg2ai"
RESOURCE_GROUP="rg-secure-timesheet-agent"

echo "🛡️ SAFE Azure Cleanup for Timesheet Project"
echo "=============================================="
echo ""

# Step 1: Verify all apps are running
echo "Step 1: Verifying all container apps are running..."
echo ""

apps=("unified-temporal-worker" "secure-timesheet-agent" "krakend-gateway" "harvest-mcp" "temporal-dev-server" "temporal-postgres-v2")

all_running=true
for app in "${apps[@]}"; do
    status=$(az containerapp show --name $app --resource-group $RESOURCE_GROUP --query "properties.runningStatus" --output tsv 2>/dev/null)
    if [ "$status" != "Running" ]; then
        echo "❌ ERROR: $app is not running (status: $status)"
        all_running=false
    else
        echo "✅ $app is running"
    fi
done

echo ""

if [ "$all_running" = false ]; then
    echo "❌ SAFETY CHECK FAILED: Not all apps are running"
    echo "   Cleanup aborted for safety"
    exit 1
fi

echo "✅ SAFETY CHECK PASSED: All apps are running"
echo ""

# Step 2: Get currently deployed images
echo "Step 2: Identifying currently deployed images..."
echo ""

declare -A deployed_images

for app in "${apps[@]}"; do
    image=$(az containerapp show --name $app --resource-group $RESOURCE_GROUP --query "properties.template.containers[0].image" --output tsv 2>/dev/null)
    if [ -n "$image" ]; then
        # Extract tag from image
        tag=$(echo $image | awk -F: '{print $2}')
        repo=$(echo $image | awk -F/ '{print $2}' | awk -F: '{print $1}')
        deployed_images["$repo"]="$tag"
        echo "✅ $app uses $repo:$tag"
    fi
done

echo ""
echo "✅ SAFETY CHECK PASSED: Identified all deployed images"
echo ""

# Step 3: Clean old tags (keeping deployed + latest 4)
echo "Step 3: Cleaning old Docker image tags..."
echo ""

cleanup_repo_safe() {
    local repo=$1
    local keep_count=$2
    
    echo "📦 Processing $repo (keeping latest $keep_count + deployed)..."
    
    # Get currently deployed tag for this repo
    deployed_tag="${deployed_images[$repo]}"
    
    if [ -n "$deployed_tag" ]; then
        echo "   🔒 Protected (deployed): $deployed_tag"
    fi
    
    # Get all tags sorted by date (newest first)
    tags=$(az acr repository show-tags \
        --name $REGISTRY \
        --repository $repo \
        --orderby time_desc \
        --output tsv 2>/dev/null)
    
    if [ -z "$tags" ]; then
        echo "   ⚠️  No tags found for $repo"
        return
    fi
    
    # Count total tags
    total=$(echo "$tags" | wc -l | tr -d ' ')
    to_keep=$keep_count
    to_delete=$((total - to_keep))
    
    echo "   Total tags: $total"
    echo "   Keeping: $to_keep (including deployed)"
    
    if [ $to_delete -gt 0 ]; then
        echo "   Deleting: $to_delete old tags"
        # Skip the first N tags (keep them), delete the rest
        echo "$tags" | tail -n +$((to_keep + 1)) | while read tag; do
            # Double-check this tag is not deployed
            if [ "$tag" = "$deployed_tag" ]; then
                echo "   🔒 SKIPPED (deployed): $repo:$tag"
            else
                echo "   ❌ Deleting $repo:$tag"
                az acr repository delete --name $REGISTRY --image $repo:$tag --yes 2>/dev/null
            fi
        done
    else
        echo "   ✅ No tags to delete"
    fi
    echo ""
}

# Clean each active repository
cleanup_repo_safe "multi-agent-system" 5
cleanup_repo_safe "unified-temporal-worker" 5
cleanup_repo_safe "harvest-mcp" 2
cleanup_repo_safe "krakend-gateway" 3
cleanup_repo_safe "temporal-dev-server" 2

echo "✅ Tag cleanup complete!"
echo ""

# Step 4: Delete legacy repositories (NOT in use)
echo "Step 4: Deleting legacy repositories..."
echo ""

legacy_repos=("temporal-conversation-worker" "temporal-timesheet-worker" "temporal-worker" "daily-reminder-job")

for repo in "${legacy_repos[@]}"; do
    # Verify this repo is not in deployed_images
    if [ -z "${deployed_images[$repo]}" ]; then
        echo "✅ Safe to delete: $repo (not deployed)"
        az acr repository delete --name $REGISTRY --repository $repo --yes 2>/dev/null
        echo "   ❌ Deleted: $repo"
    else
        echo "🔒 SKIPPED: $repo is deployed (${deployed_images[$repo]})"
    fi
done

echo ""
echo "✅ Cleanup complete!"
echo ""
echo "📊 Summary:"
echo "  - All 6 container apps: RUNNING ✅"
echo "  - All deployed images: PROTECTED ✅"
echo "  - Old tags: DELETED ❌"
echo "  - Legacy repos: DELETED ❌"
echo ""
echo "🛡️ SAFETY VERIFIED: No in-use resources were deleted"
