#!/usr/bin/env python3
"""
Joke Generator for Timesheet Responses
Integrates with LLM Client to add humor to timesheet check results
"""

import logging
import re
from typing import Dict, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class TimesheetJokeContext:
    """Context extracted from timesheet data for joke generation"""
    user_name: str
    total_hours: float
    total_entries: int
    missing_days_count: int
    work_pattern: str  # "overworked", "underworked", "consistent", "sporadic"
    
    @classmethod
    def from_timesheet_result(cls, user_name: str, timesheet_text: str) -> 'TimesheetJokeContext':
        """Extract context from timesheet MCP tool result"""
        # Parse timesheet result to extract key metrics
        total_hours = 0.0
        total_entries = 0
        missing_days = 0
        
        # Extract hours (e.g., "Total: 35.5 hours")
        hours_match = re.search(r'Total:\s*(\d+\.?\d*)\s*hours?', timesheet_text, re.IGNORECASE)
        if hours_match:
            total_hours = float(hours_match.group(1))
        
        # Extract entries count (e.g., "7 entries")
        entries_match = re.search(r'(\d+)\s*entr(?:y|ies)', timesheet_text, re.IGNORECASE)
        if entries_match:
            total_entries = int(entries_match.group(1))
        
        # Extract missing days (e.g., "Missing: Monday, Wednesday")
        missing_match = re.search(r'Missing:([^\n]+)', timesheet_text, re.IGNORECASE)
        if missing_match:
            missing_days = len([d.strip() for d in missing_match.group(1).split(',') if d.strip()])
        
        # Determine work pattern
        if total_hours >= 40:
            work_pattern = "overworked"
        elif total_hours < 30:
            work_pattern = "underworked"
        elif missing_days == 0:
            work_pattern = "consistent"
        else:
            work_pattern = "sporadic"
        
        return cls(
            user_name=user_name,
            total_hours=total_hours,
            total_entries=total_entries,
            missing_days_count=missing_days,
            work_pattern=work_pattern
        )


class JokeGenerator:
    """
    Generates contextual jokes for timesheet responses using LLM Client
    """
    
    def __init__(self, llm_client, llm_config):
        """
        Initialize joke generator with LLM client
        
        Args:
            llm_client: Centralized LLM client instance
            llm_config: LLM configuration
        """
        self.llm_client = llm_client
        self.llm_config = llm_config
        self.enabled = True  # Can be controlled via env var
        logger.info("✅ Joke Generator initialized")
    
    async def generate_joke(
        self,
        context: TimesheetJokeContext,
        user_id: str,
        humor_style: str = "witty",
        user_interests: list = None
    ) -> Optional[str]:
        """
        Generate a contextual joke based on timesheet data
        
        Args:
            context: Timesheet context data
            user_id: User ID for tracking
            humor_style: Style of humor (witty, punny, motivational, gentle)
            user_interests: List of user's interests for personalization
        
        Returns:
            Generated joke or None if generation fails
        """
        if not self.enabled:
            return None
        
        try:
            # Build joke generation prompt with interests
            joke_prompt = self._build_joke_prompt(context, humor_style, user_interests)
            
            # Call LLM to generate joke
            logger.info(f"🎭 Generating {humor_style} joke for {context.user_name}")
            
            response = await self.llm_client.chat_completion(
                messages=[
                    {"role": "system", "content": "You are a witty assistant that creates short, friendly jokes about work and timesheets."},
                    {"role": "user", "content": joke_prompt}
                ],
                tenant_id=user_id,
                user_id=user_id,
                temperature=0.9,  # Higher temperature for creativity
                max_tokens=100  # Keep jokes short
            )
            
            joke = response.content.strip()
            
            # Clean up joke (remove quotes if present)
            joke = joke.strip('"\'')
            
            # Ensure joke is not too long (SMS limit consideration)
            if len(joke) > 200:
                joke = joke[:197] + "..."
            
            logger.info(f"✅ Generated joke: {len(joke)} chars, ${response.cost_usd:.4f}")
            return joke
            
        except Exception as e:
            logger.error(f"❌ Failed to generate joke: {e}")
            return None
    
    def _build_joke_prompt(self, context: TimesheetJokeContext, humor_style: str, user_interests: list = None) -> str:
        """Build prompt for joke generation based on context and user interests"""
        
        # Base prompt
        prompt = f"""Generate a SHORT, friendly joke (max 2 sentences) about {context.user_name}'s timesheet.

Context:
- Total hours: {context.total_hours}
- Entries: {context.total_entries}
- Missing days: {context.missing_days_count}
- Pattern: {context.work_pattern}

Style: {humor_style}

"""
        
        # Add user interests for personalization (let AI choose which to use)
        if user_interests and len(user_interests) > 0:
            interests_str = ", ".join(user_interests)
            prompt += f"""User's interests: {interests_str}

IMPORTANT: Choose ONE or MORE interests from the list above that would make a clever, natural connection to their timesheet situation. If no interests fit naturally, generate a normal timesheet joke without forcing interest references.

"""
        
        # Add pattern-specific guidance
        if context.work_pattern == "overworked":
            prompt += "They've been working a lot! Make a light joke about dedication or work-life balance.\n"
        elif context.work_pattern == "underworked":
            prompt += "They haven't logged many hours. Make a gentle, encouraging joke.\n"
        elif context.work_pattern == "consistent":
            prompt += "They're very consistent! Make a positive, motivational joke.\n"
        elif context.work_pattern == "sporadic":
            prompt += f"They have {context.missing_days_count} missing days. Make a playful joke about filling gaps.\n"
        
        prompt += "\nJoke (short, friendly, with emoji):"
        
        return prompt
    
    def get_fallback_joke(self, context: TimesheetJokeContext) -> str:
        """Get a simple fallback joke if LLM generation fails"""
        
        fallback_jokes = {
            "overworked": f"🏆 {context.total_hours} hours? You're either super dedicated or your coffee machine is working overtime!",
            "underworked": f"😊 {context.total_hours} hours logged - quality over quantity, right?",
            "consistent": f"⏰ {context.total_entries} entries, {context.total_hours} hours - you're like clockwork!",
            "sporadic": f"📝 {context.missing_days_count} missing days - your timesheet is playing hide and seek!"
        }
        
        return fallback_jokes.get(context.work_pattern, "😄 Keep up the good work!")


async def add_joke_to_timesheet_response(
    timesheet_result: str,
    user_name: str,
    user_id: str,
    llm_client,
    llm_config,
    user_interests: list = None,
    humor_style: str = "witty"
) -> str:
    """
    Add a contextual joke to timesheet check result
    
    Args:
        timesheet_result: Original timesheet MCP tool result
        user_name: User's name
        user_id: User ID
        llm_client: LLM client instance
        llm_config: LLM configuration
        user_interests: List of user's interests for personalization
        humor_style: Style of humor
    
    Returns:
        Enhanced response with joke
    """
    try:
        # Extract context from timesheet result
        context = TimesheetJokeContext.from_timesheet_result(user_name, timesheet_result)
        
        # Generate joke with personalization
        joke_gen = JokeGenerator(llm_client, llm_config)
        joke = await joke_gen.generate_joke(context, user_id, humor_style, user_interests)
        
        # If joke generation failed, use fallback
        if not joke:
            joke = joke_gen.get_fallback_joke(context)
        
        # Combine timesheet result with joke
        enhanced_response = f"{timesheet_result}\n\n🎭 {joke}"
        
        return enhanced_response
        
    except Exception as e:
        logger.error(f"❌ Failed to add joke to response: {e}")
        # Return original response if joke generation fails
        return timesheet_result


# Example usage:
"""
# In unified_workflows.py, after check_my_timesheet tool execution:

if tool_name == "check_my_timesheet":
    # Add joke to timesheet result
    from joke_generator import add_joke_to_timesheet_response
    
    ai_response_text = await add_joke_to_timesheet_response(
        timesheet_result=str(tool_result),
        user_name=request.user_id,  # or extract from metadata
        user_id=request.user_id,
        llm_client=worker.llm_client,
        llm_config=worker.llm_config,
        humor_style="witty"  # Can be customized per user
    )
"""
