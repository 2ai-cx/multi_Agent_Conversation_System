# 🔍 Remaining Hardcoded Logic Found

## ❌ Branding Agent (`agents/branding.py`)

### Problem 1: Hardcoded Channel Formatting
```python
# Lines 70-82
if channel_key == "sms":
    formatted = await self._format_sms(...)
elif channel_key == "email":
    formatted = await self._format_email(...)
elif channel_key == "whatsapp":
    formatted = await self._format_whatsapp(...)
elif channel_key == "teams":
    formatted = await self._format_teams(...)
```

**Issue:** Hardcoded channel-specific logic. Adding a new channel requires code changes.

**Solution:** Let LLM decide how to format based on channel requirements:
```python
async def format_response(self, request_id, response, channel, user_context):
    prompt = f"""You are a Branding Specialist.

Response to format: "{response}"
Channel: {channel}

Channel requirements:
- SMS: Plain text, max 1600 chars, no markdown
- Email: Full markdown, no length limit
- WhatsApp: Limited markdown, max 4000 chars
- Teams: Adaptive cards format

Your task:
1. Format the response appropriately for {channel}
2. Apply brand voice (professional but friendly)
3. Ensure it meets channel constraints

Return the formatted response."""

    formatted = await llm.generate(prompt)
    return formatted
```

### Problem 2: Hardcoded Max Lengths
```python
# Line 111
max_length = spec.get("max_length", 1600)  # ❌ Hardcoded 1600 for SMS

# Line 172
max_length = spec.get("max_length", 4000)  # ❌ Hardcoded 4000 for WhatsApp
```

**Issue:** Channel limits are hardcoded in code.

**Solution:** Pass channel specs to LLM, let it handle constraints.

### Problem 3: Hardcoded Markdown Stripping
```python
# Lines 212-266
def _strip_markdown(self, text: str) -> str:
    """Remove all markdown symbols"""
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)  # ❌ Hardcoded regex
    text = re.sub(r'__(.+?)__', r'\1', text)      # ❌ Hardcoded regex
    text = re.sub(r'\*(.+?)\*', r'\1', text)      # ❌ Hardcoded regex
    # ... more hardcoded patterns
```

**Issue:** Markdown removal logic is hardcoded.

**Solution:** Let LLM handle formatting - it knows how to work with/without markdown.

### Problem 4: Hardcoded Split Strategies
```python
# Lines 268-290
def _split_message(self, text: str, max_length: int, strategy: str):
    if strategy == "sentence":  # ❌ Hardcoded
        sentences = re.split(r'(?<=[.!?])\s+', text)
    elif strategy == "paragraph":  # ❌ Hardcoded
        sentences = text.split('\n\n')
```

**Issue:** Message splitting logic is hardcoded.

**Solution:** Let LLM split messages intelligently:
```python
prompt = f"""Split this message into parts under {max_length} chars each:
"{text}"

Split at natural boundaries (sentences, paragraphs).
Return JSON: {{"parts": ["part1", "part2", ...]}}"""
```

---

## ✅ What's Already Fixed

1. **Timesheet Agent** - ✅ No hardcoded query types
2. **Planner Agent** - ✅ No hardcoded orchestration
3. **Workflow** - ✅ Simple message routing
4. **Quality Agent** - ✅ Uses LLM for validation (no hardcoded rules)

---

## 🎯 Action Items

### Priority 1: Fix Branding Agent
Replace hardcoded channel formatting with LLM-based approach:

```python
async def format_response(
    self,
    request_id: str,
    response: str,
    channel: str,
    user_context: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Format response for channel using LLM.
    NO HARDCODED LOGIC.
    """
    
    prompt = f"""You are a Branding Specialist formatting responses for different channels.

Response to format:
"{response}"

Channel: {channel}
Channel constraints:
- SMS: Plain text only, max 1600 characters, no markdown, be concise
- Email: Full markdown supported, no length limit, can be detailed
- WhatsApp: Limited markdown (*bold*, _italic_), max 4000 characters
- Teams: Adaptive cards format, structured content

Brand voice: Professional but friendly, clear and helpful

Your task:
1. Format the response appropriately for {channel}
2. Apply brand voice
3. Ensure it meets channel constraints
4. If too long, intelligently truncate or split

Return JSON:
{{
    "formatted_content": "the formatted response",
    "is_split": true/false,
    "parts": ["part1", "part2"] (if split),
    "metadata": {{"length": 123, "markdown_used": true}}
}}

Return ONLY valid JSON."""

    llm_response = await self.llm_client.generate(prompt)
    result = json.loads(llm_response)
    
    return {
        "formatted_response": {
            "request_id": request_id,
            "channel": channel,
            "content": result["formatted_content"],
            "is_split": result.get("is_split", False),
            "parts": result.get("parts", []),
            "metadata": result.get("metadata", {})
        }
    }
```

### Benefits:
1. **No code changes for new channels** - Just update the prompt
2. **Intelligent formatting** - LLM understands context
3. **Flexible constraints** - Easy to adjust limits
4. **Better splitting** - LLM splits at natural boundaries

---

## Summary

### Still Hardcoded:
- ❌ Branding Agent channel formatting
- ❌ Branding Agent max lengths
- ❌ Branding Agent markdown stripping
- ❌ Branding Agent message splitting

### Already Autonomous:
- ✅ Timesheet Agent tool selection
- ✅ Planner Agent orchestration
- ✅ Workflow message routing
- ✅ Quality Agent validation

### Next Step:
Fix Branding Agent to be fully LLM-driven, then we'll have a **100% autonomous multi-agent system**!
