"""
JSON Minification for LLM Calls

Reduces token usage by ~30% through:
1. Compact JSON serialization (no whitespace)
2. Key abbreviation (configurable mapping)
3. Instructing LLM to respond in minified format

Usage:
    from llm.json_minifier import minify_for_llm, expand_from_llm
    
    # Before sending to LLM
    minified = minify_for_llm(data, abbreviate_keys=True)
    
    # After receiving from LLM
    expanded = expand_from_llm(llm_response)
"""

import json
import re
from typing import Any, Dict, List, Optional


# Common key abbreviations to save tokens
DEFAULT_KEY_MAP = {
    # Timesheet/Harvest fields
    "time_entries": "te",
    "spent_date": "sd",
    "hours": "h",
    "project": "p",
    "project_id": "pid",
    "task": "t",
    "task_id": "tid",
    "notes": "n",
    "user_id": "uid",
    "client": "c",
    "client_id": "cid",
    "is_running": "run",
    "is_locked": "lock",
    "is_billed": "bill",
    "is_closed": "cls",
    "created_at": "ca",
    "updated_at": "ua",
    
    # Query parameters
    "from_date": "fd",
    "to_date": "td",
    "page": "pg",
    "per_page": "pp",
    
    # Response metadata
    "total_entries": "tot",
    "total_hours": "th",
    "total_pages": "tpg",
    "next_page": "np",
    "previous_page": "prp",
    
    # Common fields
    "id": "i",
    "name": "nm",
    "description": "desc",
    "status": "st",
    "type": "ty",
    "value": "v",
    "timestamp": "ts",
    "message": "msg",
    "error": "err",
    "success": "ok",
}


def create_reverse_map(key_map: Dict[str, str]) -> Dict[str, str]:
    """Create reverse mapping for expansion"""
    return {v: k for k, v in key_map.items()}


def minify_for_llm(
    data: Any,
    abbreviate_keys: bool = True,
    key_map: Optional[Dict[str, str]] = None,
    compact: bool = True
) -> str:
    """
    Minify JSON data for LLM consumption
    
    Args:
        data: Data to minify (dict, list, or any JSON-serializable)
        abbreviate_keys: Whether to abbreviate dictionary keys
        key_map: Custom key abbreviation map (uses DEFAULT_KEY_MAP if None)
        compact: Whether to use compact JSON (no whitespace)
    
    Returns:
        Minified JSON string
    
    Example:
        >>> data = {"time_entries": [{"spent_date": "2025-11-13", "hours": 8}]}
        >>> minify_for_llm(data)
        '{"te":[{"sd":"2025-11-13","h":8}]}'
        
        Savings: 54 chars -> 32 chars (40% reduction)
    """
    if key_map is None:
        key_map = DEFAULT_KEY_MAP
    
    # Abbreviate keys if requested
    if abbreviate_keys:
        data = _abbreviate_keys(data, key_map)
    
    # Serialize to compact JSON
    if compact:
        return json.dumps(data, separators=(',', ':'), ensure_ascii=False)
    else:
        return json.dumps(data, ensure_ascii=False)


def expand_from_llm(
    minified_json: str,
    key_map: Optional[Dict[str, str]] = None
) -> Any:
    """
    Expand minified JSON from LLM response
    
    Args:
        minified_json: Minified JSON string from LLM
        key_map: Custom key abbreviation map (uses DEFAULT_KEY_MAP if None)
    
    Returns:
        Expanded Python object
    
    Example:
        >>> minified = '{"te":[{"sd":"2025-11-13","h":8}]}'
        >>> expand_from_llm(minified)
        {"time_entries": [{"spent_date": "2025-11-13", "hours": 8}]}
    """
    if key_map is None:
        key_map = DEFAULT_KEY_MAP
    
    # Create reverse mapping
    reverse_map = create_reverse_map(key_map)
    
    # Parse JSON
    data = json.loads(minified_json)
    
    # Expand keys
    return _expand_keys(data, reverse_map)


def _abbreviate_keys(data: Any, key_map: Dict[str, str]) -> Any:
    """Recursively abbreviate dictionary keys"""
    if isinstance(data, dict):
        return {
            key_map.get(k, k): _abbreviate_keys(v, key_map)
            for k, v in data.items()
        }
    elif isinstance(data, list):
        return [_abbreviate_keys(item, key_map) for item in data]
    else:
        return data


def _expand_keys(data: Any, reverse_map: Dict[str, str]) -> Any:
    """Recursively expand abbreviated keys"""
    if isinstance(data, dict):
        return {
            reverse_map.get(k, k): _expand_keys(v, reverse_map)
            for k, v in data.items()
        }
    elif isinstance(data, list):
        return [_expand_keys(item, reverse_map) for item in data]
    else:
        return data


def get_minification_instruction() -> str:
    """
    Get instruction text to append to LLM prompts
    
    Returns:
        Instruction string for LLM to respond in minified format
    """
    return """
RESPONSE FORMAT: Return minified JSON using these abbreviations:
- time_entries→te, spent_date→sd, hours→h, project→p, task→t, notes→n
- from_date→fd, to_date→td, user_id→uid, total_entries→tot
- Use compact format (no spaces): {"te":[{"sd":"2025-11-13","h":8}]}
"""


def extract_json_from_response(response: str) -> str:
    """
    Extract JSON from LLM response (handles markdown code blocks)
    
    Args:
        response: Raw LLM response that may contain JSON
    
    Returns:
        Extracted JSON string
    
    Example:
        >>> response = "Here's the data:\\n```json\\n{...}\\n```"
        >>> extract_json_from_response(response)
        '{...}'
    """
    # Remove markdown code blocks
    response = response.strip()
    
    # Check for ```json or ``` blocks
    if '```' in response:
        # Extract content between ``` markers
        match = re.search(r'```(?:json)?\s*\n?(.*?)\n?```', response, re.DOTALL)
        if match:
            response = match.group(1).strip()
    
    return response


def calculate_token_savings(original: str, minified: str) -> Dict[str, Any]:
    """
    Calculate token savings from minification
    
    Args:
        original: Original JSON string
        minified: Minified JSON string
    
    Returns:
        Dictionary with savings metrics
    """
    original_len = len(original)
    minified_len = len(minified)
    saved = original_len - minified_len
    percent_saved = (saved / original_len * 100) if original_len > 0 else 0
    
    # Rough token estimate (1 token ≈ 4 chars for English text)
    original_tokens = original_len // 4
    minified_tokens = minified_len // 4
    tokens_saved = original_tokens - minified_tokens
    
    return {
        "original_chars": original_len,
        "minified_chars": minified_len,
        "chars_saved": saved,
        "percent_saved": round(percent_saved, 1),
        "original_tokens_est": original_tokens,
        "minified_tokens_est": minified_tokens,
        "tokens_saved_est": tokens_saved
    }


# Example usage and testing
if __name__ == "__main__":
    # Example timesheet data
    example_data = {
        "time_entries": [
            {
                "id": 1,
                "spent_date": "2025-11-13",
                "hours": 8.0,
                "project": {"id": 123, "name": "Q3 2024 Autonomous Agents"},
                "task": {"id": 456, "name": "Development"},
                "notes": "Worked on agent architecture",
                "user_id": 789,
                "is_running": False,
                "is_locked": False
            },
            {
                "id": 2,
                "spent_date": "2025-11-12",
                "hours": 6.5,
                "project": {"id": 123, "name": "Q3 2024 Autonomous Agents"},
                "task": {"id": 456, "name": "Development"},
                "notes": "Implemented MCP integration",
                "user_id": 789,
                "is_running": False,
                "is_locked": False
            }
        ],
        "total_entries": 2,
        "total_hours": 14.5,
        "from_date": "2025-11-01",
        "to_date": "2025-11-30"
    }
    
    # Original JSON
    original = json.dumps(example_data, indent=2)
    print("ORIGINAL JSON:")
    print(original)
    print(f"\nLength: {len(original)} chars")
    print()
    
    # Minified JSON
    minified = minify_for_llm(example_data, abbreviate_keys=True)
    print("MINIFIED JSON:")
    print(minified)
    print(f"\nLength: {len(minified)} chars")
    print()
    
    # Calculate savings
    savings = calculate_token_savings(original, minified)
    print("SAVINGS:")
    print(f"  Characters: {savings['chars_saved']} saved ({savings['percent_saved']}%)")
    print(f"  Tokens (est): {savings['tokens_saved_est']} saved")
    print()
    
    # Test round-trip
    expanded = expand_from_llm(minified)
    print("ROUND-TRIP TEST:")
    print(f"  Original == Expanded: {example_data == expanded}")
    print()
    
    # Show instruction
    print("LLM INSTRUCTION:")
    print(get_minification_instruction())
