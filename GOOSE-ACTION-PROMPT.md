I need you to execute these tasks autonomously. Start immediately and work through all phases.

**CRITICAL SAFETY RULES:**
- NEVER modify any Python files outside tests/ directory
- NEVER touch agents/, llm/, unified_server.py, unified_workflows.py
- ONLY create/modify files in tests/ directory
- Keep tests SIMPLE and REPETITIVE

**START NOW - PHASE 1:**

Run this command and show me the output:
```
pytest tests/ --collect-only -q
```

Then tell me:
1. How many tests currently exist?
2. Are there any collection errors?

After you report Phase 1 results, I'll ask you to continue to Phase 2.
