# Cleanup Plan - Remove Personal Details & Unrelated Files

## Files to Remove (Personal Details Found)

### Documentation with Personal Info:
- USER_INTERESTS_VERIFICATION.md (26 matches - personal interests)
- JOKE_GENERATOR_INTEGRATED.md (25 matches)
- JOKE_GENERATOR_DAILY_REMINDERS.md (5 matches)
- JOKE_GENERATOR_READY.md

### Test/Debug Files (Root Level):
- test_harvest_mcp.py
- test_harvest_token.py
- test_json_minification_standalone.py
- test_json_minification.py
- test_mem0_direct.py
- test_rag_benchmark_standalone.py
- test_rag_benchmark.py
- test_rag_functionality.py
- test_sms_memory.py
- add_debug_endpoint.py
- analyze_rag_from_logs.py
- check_rag_env.py
- diagnose_mem0.py
- joke_generator.py
- timeout_wrapper.py

### Deployment Scripts with Personal Info:
- check_keyvault.sh (25 matches - contains secrets/keys)
- test_deployment.sh (14 matches)
- test_webhook.sh
- test_sms_memory.sh
- test_real_world_rag.sh
- test-goose-cli.sh
- safe_cleanup_timesheet.sh
- monitor_goose_progress.sh

### Unrelated/Experimental Documentation:
- All GOOSE-*.md files (30+ files - experimental AI tool docs)
- All PASTE-*.md files (experimental prompts)
- DOLPHIN-*.md files (model testing)
- MISTRAL-*.md files (model testing)
- OLLAMA-*.md files (model testing)
- MODEL-*.md files (model testing)
- OPIK_*.md files (monitoring tool)
- TWILIO_*.md files (SMS debugging - contains phone numbers)
- SMS_*.md files (SMS debugging)

### Duplicate/Outdated Deployment Docs:
- DEPLOYMENT_COMPLETE_DEC1.md
- DEPLOYMENT_COMPLETE_FINAL.md
- DEPLOYMENT_SUMMARY_DEC1.md
- FINAL_DEPLOYMENT_DEC1.md
- FINAL-DEPLOYMENT-SUMMARY.md
- DEPLOYMENT-STATUS-VERIFIED.md
- CLEANUP_COMPLETE.md
- CLEANUP_SUMMARY_DEC1.md

### Azure Cleanup Reports:
- AZURE_CLEANUP_REPORT.md
- AZURE_CLEANUP_REPORT_FILTERED.md
- AZURE_CLEANUP_FINAL.md
- AZURE_CLEANUP_SAFE.md

### Documentation Analysis (Internal):
- DOCUMENTATION-ANALYSIS-PLAN.md
- DOCUMENTATION-ANALYSIS-REPORT.md
- DOCUMENTATION-FIXES-SUMMARY.md
- DOCUMENTATION-STANDARD-TEMPLATE.md

### Debugging/Investigation Files:
- ROOT-CAUSE-ANALYSIS.md
- NETWORKING-DEBUG-SUMMARY.md
- CONFIRMED_ROOT_CAUSE.md
- ISSUE_RESOLVED.md
- SYSTEM_ANALYSIS.md
- HARVEST_MCP_ISSUE_SUMMARY.md

### Test Status Files (Outdated):
- TEST_STATUS.md (duplicate)
- TEST-STATUS.md (duplicate)
- TEST_FIX_SUMMARY.md
- TEST_EXECUTION_CHECKLIST.md
- TESTING_SUMMARY.md
- TEST-RESULTS-COMPREHENSIVE.md

### Workflow/Architecture Analysis:
- CONVERSATION-FLOW-NOTION.md
- CONVERSATION-FLOW-SIMPLE.md
- FLOW_ANALYSIS.md
- FLOW_READY.md
- INTER_AGENT_COMMUNICATION_ANALYSIS.md
- ASYNC_TEMPORAL_IMPACT_ANALYSIS.md
- ASYNC_WEBHOOK_FIX.md
- ASYNC_WEBHOOK_IMPLEMENTATION.md

### Miscellaneous:
- ACTIVATED_FEATURES.md
- REMAINING_HARDCODED_LOGIC.md
- NO_HARDCODED_LOGIC.md
- ZERO_HARDCODED_LOGIC.md
- REQUIREMENTS_VERIFICATION.md
- VERIFICATION-REPORT.md
- verify_no_production_changes.sh

## Files to Keep

### Core Documentation:
- README.md
- FRAMEWORK_COMPARISON_GUIDE.md

### RAG Documentation:
- QDRANT-AZURE-SETUP.md (sanitize personal details)
- QDRANT-DEPLOYMENT-SUCCESS.md (sanitize)
- QDRANT-CURRENT-STATUS.md
- QDRANT-MIGRATION-COMPLETE.md
- QDRANT-TEST-RESULTS.md
- QDRANT-VERIFICATION-REPORT.md
- QDRANT_RETRIEVAL_EVALUATION.md
- RAG-TEST-STATUS.md
- RAG_BENCHMARK_FINAL_REPORT.md
- RAG_BENCHMARK_GUIDE.md
- MEM0_DEEP_ANALYSIS_AND_FIXES.md

### Deployment Documentation:
- AZURE-DEPLOYMENT-GUIDE.md (sanitize)
- AZURE_KEYVAULT_CHECKLIST.md (sanitize)
- DEPLOYMENT-COMPLETE.md (sanitize)
- DEPLOYMENT_GUIDE.md

### Architecture Documentation:
- MULTI_AGENT_ARCHITECTURE.md
- CORRECT_ARCHITECTURE.md
- BRANCH_STRATEGY_PLAN.md
- REVISED_BRANCH_STRATEGY.md

### Integration Status:
- AGENT_FRAMEWORK_INTEGRATION_STATUS.md
- AGENT_FRAMEWORK_API_NOTES.md

### Deployment Scripts (Keep but sanitize):
- deploy.sh
- deploy_configured.sh
- add_qdrant_secrets.sh (sanitize)
- build_and_deploy_with_qdrant.sh (sanitize)
- deploy_qdrant_separate.sh
- deploy_with_qdrant_sidecar.sh
- fix_qdrant_with_health_probes.sh
- run_mem0_tests.sh
- run_production_rag_benchmark.sh

### Core Application Files:
- unified_server.py (sanitize personal details in comments/logs)
- unified_workflows.py (sanitize)

## Action Plan

1. Remove all test files from root
2. Remove all GOOSE/experimental documentation
3. Remove duplicate deployment docs
4. Remove debugging/investigation files
5. Sanitize remaining files (replace personal details with placeholders)
6. Apply to all 4 branches:
   - feature/qdrant-mem0-rag
   - feature/langchain-integration
   - feature/agent-framework-integration
   - main
