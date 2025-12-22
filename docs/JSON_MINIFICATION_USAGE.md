# JSON Minification - Usage Guide

## Overview

JSON minification saves **30-50% tokens** by:
1. Removing whitespace (compact JSON)
2. Abbreviating common keys (e.g., `time_entries` → `te`)
3. Instructing LLM to respond in minified format

**Files:**
- `llm/json_minifier.py` - Core minification logic
- `llm/client.py` - Integration with LLM client
- `llm/__init__.py` - Exported functions

---

## Quick Start

### Option 1: Use LLM Client (Recommended)

```python
from llm.client import get_llm_client

client = get_llm_client()

# Minify data before sending to LLM
data = {"time_entries": [{"spent_date": "2025-11-13", "hours": 8}]}
minified = client.minify_json_data(data)
# Result: {"te":[{"sd":"2025-11-13","h":8}]}

# Expand LLM response
llm_response = '{"te":[{"sd":"2025-11-13","h":8}]}'
expanded = client.expand_json_response(llm_response)
# Result: {"time_entries": [{"spent_date": "2025-11-13", "hours": 8}]}
```

### Option 2: Direct Import

```python
from llm.json_minifier import minify_for_llm, expand_from_llm

# Minify
minified = minify_for_llm(data, abbreviate_keys=True)

# Expand
expanded = expand_from_llm(minified)
```

---

## Integration Examples

### 1. Planner Agent - Response Composition

**Before (Current):**
```python
# agents/planner.py - compose_response()
prompt = f"""Compose a response to: "{user_message}"

Timesheet data:
{json.dumps(harvest_response, indent=2)}  # ❌ Verbose, ~200 tokens

Create a friendly response."""
```

**After (With Minification):**
```python
# agents/planner.py - compose_response()
from llm.json_minifier import minify_for_llm, get_minification_instruction

minified_data = minify_for_llm(harvest_response)  # ✅ Compact, ~100 tokens

prompt = f"""Compose a response to: "{user_message}"

Timesheet data (minified):
{minified_data}

{get_minification_instruction()}

Create a friendly response."""
```

**Savings:** ~100 tokens per call (50% reduction)

---

### 2. Timesheet Agent - Structured Tool Calls

**Before (Current):**
```python
# Planner sends natural language instruction
message_to_timesheet = """Execute list_time_entries tool with these parameters:

INPUT FORMAT:
- tool: list_time_entries
- from_date: 2024-12-01
- to_date: 2025-12-01
- user_id: 789

OUTPUT FORMAT:
Return complete Harvest API response...
"""  # ❌ ~200 tokens, requires LLM to parse
```

**After (With Structured JSON):**
```python
# Planner sends structured JSON
from llm.json_minifier import minify_for_llm

tool_call = {
    "tool": "list_time_entries",
    "parameters": {
        "from_date": "2024-12-01",
        "to_date": "2025-12-01",
        "user_id": 789
    }
}

message_to_timesheet = minify_for_llm(tool_call, abbreviate_keys=False)
# Result: {"tool":"list_time_entries","parameters":{"from_date":"2024-12-01",...}}
# ✅ ~50 tokens, no LLM parsing needed!
```

**Savings:** ~150 tokens + eliminates LLM call in Timesheet agent

---

### 3. Quality Agent - Validation Results

**Before:**
```python
# Return validation results
return {
    "request_id": "abc123",
    "scorecard": {
        "criteria": [
            {
                "id": "data_completeness",
                "description": "Response includes all data",
                "passed": True,
                "feedback": ""
            }
        ],
        "overall_passed": True
    }
}  # ❌ Verbose
```

**After:**
```python
from llm.json_minifier import minify_for_llm

result = {...}  # Same structure
minified_result = minify_for_llm(result)
# ✅ 40% smaller for logging/storage
```

---

## Key Abbreviations

The system uses these common abbreviations:

| Original | Abbreviated | Savings |
|----------|-------------|---------|
| `time_entries` | `te` | 11 chars |
| `spent_date` | `sd` | 8 chars |
| `hours` | `h` | 4 chars |
| `project` | `p` | 6 chars |
| `project_id` | `pid` | 7 chars |
| `task` | `t` | 3 chars |
| `task_id` | `tid` | 4 chars |
| `notes` | `n` | 4 chars |
| `user_id` | `uid` | 4 chars |
| `from_date` | `fd` | 7 chars |
| `to_date` | `td` | 5 chars |
| `total_entries` | `tot` | 10 chars |
| `total_hours` | `th` | 8 chars |

**Total:** ~81 chars saved per typical timesheet entry

---

## LLM Instruction

To get LLM to respond in minified format, add this to your prompt:

```python
from llm.json_minifier import get_minification_instruction

prompt = f"""Your task here...

{get_minification_instruction()}

Now respond:"""
```

This adds:
```
RESPONSE FORMAT: Return minified JSON using these abbreviations:
- time_entries→te, spent_date→sd, hours→h, project→p, task→t, notes→n
- from_date→fd, to_date→td, user_id→uid, total_entries→tot
- Use compact format (no spaces): {"te":[{"sd":"2025-11-13","h":8}]}
```

---

## Token Savings Calculator

```python
from llm.json_minifier import calculate_token_savings
import json

original = json.dumps(data, indent=2)
minified = minify_for_llm(data)

savings = calculate_token_savings(original, minified)
print(f"Saved: {savings['percent_saved']}% ({savings['tokens_saved_est']} tokens)")
```

---

## Testing

Run the example:
```bash
cd llm
python3 json_minifier.py
```

Expected output:
```
ORIGINAL JSON:
{...}  # 862 chars

MINIFIED JSON:
{...}  # 429 chars

SAVINGS:
  Characters: 433 saved (50.2%)
  Tokens (est): 108 saved

ROUND-TRIP TEST:
  Original == Expanded: True
```

---

## Best Practices

### ✅ DO:
- Use minification for large JSON payloads (>100 chars)
- Use for repeated data structures (timesheet entries)
- Test round-trip (minify → expand) to ensure correctness
- Log token savings for monitoring

### ❌ DON'T:
- Minify tiny JSON (<50 chars) - overhead not worth it
- Minify user-facing responses (keep readable)
- Abbreviate keys that aren't in the default map (won't expand correctly)
- Skip testing - always verify round-trip works

---

## Custom Key Mappings

If you need custom abbreviations:

```python
from llm.json_minifier import minify_for_llm, expand_from_llm

custom_map = {
    "custom_field": "cf",
    "another_field": "af"
}

minified = minify_for_llm(data, key_map=custom_map)
expanded = expand_from_llm(minified, key_map=custom_map)
```

---

## Performance Impact

### Token Savings
- **Planner agent**: ~100 tokens/call (50% reduction)
- **Timesheet agent**: ~150 tokens/call + no LLM needed
- **Quality agent**: ~50 tokens/call (40% reduction)

### Cost Savings (at $0.50/1M tokens)
- **Per call**: ~$0.0001 saved
- **1,000 calls/day**: ~$0.10/day = $3/month
- **10,000 calls/day**: ~$1/day = $30/month
- **100,000 calls/day**: ~$10/day = $300/month

### Latency Impact
- **Minification**: <1ms (negligible)
- **Expansion**: <1ms (negligible)
- **Net effect**: Faster (fewer tokens to process)

---

## Monitoring

Track minification effectiveness:

```python
import logging

logger = logging.getLogger(__name__)

# The LLM client automatically logs savings
client = get_llm_client()
minified = client.minify_json_data(data)
# Logs: "JSON minified: 433 chars saved (50.2%), ~108 tokens"
```

View in Opik dashboard:
- Token usage trends
- Cost per conversation
- Minification adoption rate

---

## Migration Path

### Phase 1: Planner Agent (Week 1)
1. Update `compose_response()` to minify timesheet data
2. Add minification instruction to prompts
3. Monitor token savings in Opik

### Phase 2: Timesheet Agent (Week 2)
1. Update Planner to send structured JSON tool calls
2. Update Timesheet to parse JSON directly (no LLM)
3. Measure latency improvement

### Phase 3: Quality Agent (Week 3)
1. Minify validation results for logging
2. Optimize scorecard storage
3. Review overall impact

---

## Troubleshooting

### Issue: Round-trip fails
**Cause:** Using keys not in DEFAULT_KEY_MAP  
**Solution:** Add custom keys to map or disable abbreviation

### Issue: LLM doesn't return minified JSON
**Cause:** Missing minification instruction  
**Solution:** Add `get_minification_instruction()` to prompt

### Issue: Expansion fails
**Cause:** LLM wrapped JSON in markdown  
**Solution:** Use `extract_json_from_response()` first

---

## Summary

✅ **Implemented**: JSON minification in `llm/json_minifier.py`  
✅ **Integrated**: Helper methods in `llm/client.py`  
✅ **Tested**: Round-trip verified, 30-50% savings confirmed  
✅ **Ready**: Can be adopted incrementally by agents

**Next Steps:**
1. Update Planner agent to use minification
2. Update Timesheet agent to use structured JSON
3. Monitor token savings in production
4. Expand to other agents as needed
