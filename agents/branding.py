"""
Branding Agent - Channel-Specific Formatter

Responsibilities:
- Format responses for specific channels (SMS, Email, WhatsApp, Teams)
- Apply style guide (tone, emojis, humor)
- Handle message splitting for length limits
- Remove/apply markdown based on channel capabilities
"""

import re
import yaml
from pathlib import Path
from typing import Dict, Any, List
from agents.base import BaseAgent
from agents.models import FormattedResponse, MessagePart, Channel


class BrandingAgent(BaseAgent):
    """
    Formatter agent that applies channel-specific formatting and style guide.
    """
    
    def __init__(self, llm_client):
        """
        Initialize Branding Agent and load configuration files.
        
        Args:
            llm_client: Centralized LLM client
        """
        super().__init__(llm_client)
        
        # Load configuration files
        config_dir = Path(__file__).parent / "config"
        
        with open(config_dir / "style_guide.yaml") as f:
            self.style_guide = yaml.safe_load(f)
        
        with open(config_dir / "channels.yaml") as f:
            self.channel_specs = yaml.safe_load(f)
    
    async def format_for_channel(
        self,
        request_id: str,
        response: str,
        channel: Channel,
        user_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Format response for specific channel.
        
        Args:
            request_id: Unique request identifier
            response: Channel-agnostic response from Planner
            channel: Target channel
            user_context: User information
            
        Returns:
            Dict with formatted_response
        """
        self.logger.info(f"🎨 [Branding] Starting formatting: {request_id}")
        
        # Determine channel
        channel_key = channel if isinstance(channel, str) else channel.value
        self.logger.info(f"📱 [Branding] Channel: {channel_key}")
        self.logger.info(f"📝 [Branding] Response length: {len(response)} chars")
        
        # NO HARDCODED LOGIC - Let LLM decide how to format
        import json
        
        prompt = f"""You are a Branding Specialist formatting responses for different communication channels.

Response to format:
"{response}"

Channel: {channel_key}

Channel requirements and constraints:
- SMS: Plain text only, max 1600 characters, no markdown, be concise and clear
- Email: Full markdown supported, no length limit, can be detailed and formatted
- WhatsApp: Limited markdown (*bold*, _italic_), max 4000 characters, friendly tone
- Teams: Structured content, markdown supported, professional tone

Brand voice: Professional but friendly, clear and helpful

Your task:
1. Format the response appropriately for {channel_key}
2. Apply the brand voice
3. Ensure it meets channel constraints (length, formatting)
4. If the response is too long for the channel, intelligently truncate or split it

Think step by step:
- What formatting is appropriate for this channel?
- Is the response within length limits?
- Should I split it into multiple parts?

Return JSON:
{{
    "formatted_content": "the formatted response text",
    "is_split": false,
    "parts": [],
    "reasoning": "brief explanation of formatting decisions",
    "metadata": {{
        "original_length": {len(response)},
        "final_length": 123,
        "markdown_used": true/false,
        "truncated": true/false
    }}
}}

Return ONLY valid JSON, no other text."""

        self.logger.info(f"🤖 [Branding] Asking LLM to format for {channel_key}...")
        llm_response = await self.llm_client.generate(prompt)
        
        # Parse LLM response
        try:
            result = json.loads(llm_response)
        except json.JSONDecodeError:
            # Try to extract JSON
            import re
            json_match = re.search(r'\{.*\}', llm_response, re.DOTALL)
            if json_match:
                try:
                    result = json.loads(json_match.group())
                except json.JSONDecodeError:
                    # Fallback: use response as-is
                    self.logger.warning(f"⚠️ [Branding] Could not parse LLM response, using original")
                    result = {
                        "formatted_content": str(llm_response),
                        "is_split": False,
                        "parts": [],
                        "reasoning": "Fallback - used original response",
                        "metadata": {"original_length": len(response), "final_length": len(str(llm_response))}
                    }
            else:
                # Fallback: use response as-is
                self.logger.warning(f"⚠️ [Branding] Could not parse LLM response, using original")
                result = {
                    "formatted_content": str(llm_response),
                    "is_split": False,
                    "parts": [],
                    "reasoning": "Fallback - used original response",
                    "metadata": {"original_length": len(response), "final_length": len(str(llm_response))}
                }
        
        self.logger.info(f"💭 [Branding] LLM reasoning: {result.get('reasoning', 'N/A')}")
        self.logger.info(f"✅ [Branding] Formatting complete. Split: {result.get('is_split')}, Final length: {result.get('metadata', {}).get('final_length')} chars")
        
        formatted = FormattedResponse(
            request_id=request_id,
            channel=Channel(channel_key) if isinstance(channel_key, str) else channel_key,
            content=result["formatted_content"],
            is_split=result.get("is_split", False),
            parts=[MessagePart(content=p, part_number=i+1, total_parts=len(result.get("parts", []))) 
                   for i, p in enumerate(result.get("parts", []))] if result.get("parts") else [],
            metadata=result.get("metadata", {})
        )
        
        return {"formatted_response": formatted.model_dump(mode='json')}
    
    async def _format_sms(
        self,
        request_id: str,
        response: str,
        spec: Dict,
        user_context: Dict
    ) -> FormattedResponse:
        """Format for SMS: plain text, no markdown, max 1600 chars"""
        # Remove markdown
        plain_text = self._strip_markdown(response)
        
        # Apply style guide
        styled = await self._apply_style(plain_text, "sms", user_context)
        
        # Check length and split if needed
        max_length = spec.get("max_length", 1600)
        
        if len(styled) <= max_length:
            return FormattedResponse(
                request_id=request_id,
                channel=Channel.SMS,
                content=styled,
                is_split=False,
                metadata={"markdown_applied": False, "emojis_used": self._extract_emojis(styled)}
            )
        else:
            # Split at sentence boundaries
            parts = self._split_message(styled, max_length, spec.get("split_strategy", "sentence"))
            return FormattedResponse(
                request_id=request_id,
                channel=Channel.SMS,
                content=parts[0].content,
                is_split=True,
                parts=parts,
                metadata={"markdown_applied": False, "split_count": len(parts)}
            )
    
    async def _format_email(
        self,
        request_id: str,
        response: str,
        spec: Dict,
        user_context: Dict
    ) -> FormattedResponse:
        """Format for Email: full markdown, no length limit"""
        # Apply markdown if not already present
        if not any(md in response for md in ["**", "#", "_", "`", "-", "*"]):
            # Add basic markdown structure
            response = f"# Timesheet Update\n\n{response}"
        
        # Apply style guide
        styled = await self._apply_style(response, "email", user_context)
        
        return FormattedResponse(
            request_id=request_id,
            channel=Channel.EMAIL,
            content=styled,
            is_split=False,
            metadata={"markdown_applied": True, "emojis_used": self._extract_emojis(styled)}
        )
    
    async def _format_whatsapp(
        self,
        request_id: str,
        response: str,
        spec: Dict,
        user_context: Dict
    ) -> FormattedResponse:
        """Format for WhatsApp: limited markdown (bold, italic), moderate length"""
        # Keep only bold and italic markdown, remove others
        response = self._limit_markdown(response, ["bold", "italic"])
        
        # Apply style guide
        styled = await self._apply_style(response, "whatsapp", user_context)
        
        # Check length
        max_length = spec.get("max_length", 4000)
        if len(styled) > max_length:
            parts = self._split_message(styled, max_length, "paragraph")
            return FormattedResponse(
                request_id=request_id,
                channel=Channel.WHATSAPP,
                content=parts[0].content,
                is_split=True,
                parts=parts,
                metadata={"markdown_applied": True}
            )
        
        return FormattedResponse(
            request_id=request_id,
            channel=Channel.WHATSAPP,
            content=styled,
            is_split=False,
            metadata={"markdown_applied": True}
        )
    
    async def _format_teams(
        self,
        request_id: str,
        response: str,
        spec: Dict,
        user_context: Dict
    ) -> FormattedResponse:
        """Format for Teams: adaptive cards format"""
        # For now, use markdown (Teams supports it)
        # TODO: Implement adaptive cards format
        styled = await self._apply_style(response, "teams", user_context)
        
        return FormattedResponse(
            request_id=request_id,
            channel=Channel.TEAMS,
            content=styled,
            is_split=False,
            metadata={"markdown_applied": True, "format": "markdown"}
        )
    
    def _strip_markdown(self, text: str) -> str:
        """Remove all markdown symbols"""
        # Remove bold
        text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
        text = re.sub(r'__(.+?)__', r'\1', text)
        
        # Remove italic
        text = re.sub(r'\*(.+?)\*', r'\1', text)
        text = re.sub(r'_(.+?)_', r'\1', text)
        
        # Remove headers
        text = re.sub(r'^#+\s+', '', text, flags=re.MULTILINE)
        
        # Remove code blocks
        text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
        text = re.sub(r'`(.+?)`', r'\1', text)
        
        # Remove links
        text = re.sub(r'\[(.+?)\]\(.+?\)', r'\1', text)
        
        return text
    
    def _limit_markdown(self, text: str, allowed: List[str]) -> str:
        """Keep only specified markdown features"""
        if "bold" not in allowed:
            text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
            text = re.sub(r'__(.+?)__', r'\1', text)
        
        if "italic" not in allowed:
            text = re.sub(r'(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)', r'\1', text)
            text = re.sub(r'_(.+?)_', r'\1', text)
        
        if "headers" not in allowed:
            text = re.sub(r'^#+\s+', '', text, flags=re.MULTILINE)
        
        return text
    
    async def _apply_style(self, text: str, channel: str, user_context: Dict) -> str:
        """Apply style guide (tone, emojis, personalization)"""
        # Add greeting if configured
        if self.style_guide.get("formatting", {}).get("greeting"):
            user_name = user_context.get("full_name", "").split()[0] if user_context.get("full_name") else None
            if user_name and self.style_guide.get("formatting", {}).get("use_user_name"):
                if not text.startswith("Hi") and not text.startswith("Hello"):
                    text = f"Hi {user_name}! {text}"
        
        # Add emojis if enabled
        if self.style_guide.get("emojis", {}).get("enabled"):
            emojis = self.style_guide.get("emojis", {})
            # Add success emoji for positive messages
            if any(word in text.lower() for word in ["great", "good", "excellent", "completed"]):
                if emojis.get("success") not in text:
                    text = f"{emojis.get('success')} {text}"
        
        return text
    
    def _split_message(self, text: str, max_length: int, strategy: str) -> List[MessagePart]:
        """Split long message into parts"""
        if strategy == "sentence":
            # Split at sentence boundaries
            sentences = re.split(r'(?<=[.!?])\s+', text)
        elif strategy == "paragraph":
            # Split at paragraph boundaries
            sentences = text.split('\n\n')
        else:
            # Split at word boundaries
            sentences = text.split()
        
        parts = []
        current_part = ""
        
        for sentence in sentences:
            if len(current_part) + len(sentence) + 1 <= max_length:
                current_part += (" " if current_part else "") + sentence
            else:
                if current_part:
                    parts.append(current_part)
                current_part = sentence
        
        if current_part:
            parts.append(current_part)
        
        # Create MessagePart objects with continuation indicators
        total_parts = len(parts)
        return [
            MessagePart(
                sequence=i + 1,
                content=part,
                continuation_indicator=f"({i + 1}/{total_parts})" if total_parts > 1 else None
            )
            for i, part in enumerate(parts)
        ]
    
    def _extract_emojis(self, text: str) -> List[str]:
        """Extract emojis from text"""
        emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"  # emoticons
            "\U0001F300-\U0001F5FF"  # symbols & pictographs
            "\U0001F680-\U0001F6FF"  # transport & map symbols
            "\U0001F1E0-\U0001F1FF"  # flags
            "\U00002702-\U000027B0"
            "\U000024C2-\U0001F251"
            "]+",
            flags=re.UNICODE
        )
        return emoji_pattern.findall(text)
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Branding agent action"""
        action = input_data.get("action")
        
        if action == "format_for_channel":
            return await self.format_for_channel(
                input_data["request_id"],
                input_data["response"],
                input_data["channel"],
                input_data.get("user_context", {})
            )
        else:
            raise ValueError(f"Unknown action: {action}")
