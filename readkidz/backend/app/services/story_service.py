"""
ReadKidz Platform - Story Generation Service
Uses LLMs (Claude/GPT) to generate children's stories
"""
import json
import logging
from typing import Optional, List, Dict, Any
from anthropic import Anthropic
from openai import OpenAI
from app.core.config import settings

logger = logging.getLogger(__name__)


class StoryService:
    """Service for generating children's stories using AI"""

    def __init__(self):
        self.anthropic_client = None
        self.openai_client = None

        if settings.ANTHROPIC_API_KEY:
            self.anthropic_client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        if settings.OPENAI_API_KEY:
            self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)

    def _get_story_prompt(
        self,
        user_prompt: str,
        page_count: int,
        target_age: str,
        language: str,
        narrative_style: str,
    ) -> str:
        """Build the system prompt for story generation"""

        style_descriptions = {
            "humorous": "幽默風趣，包含有趣的轉折和笑點",
            "warm": "溫馨感人，傳達愛和友情的正面訊息",
            "adventure": "充滿冒險和刺激，有英雄旅程元素",
            "educational": "寓教於樂，包含學習元素",
        }

        style_desc = style_descriptions.get(narrative_style, style_descriptions["warm"])

        system_prompt = f"""你是一位專業的兒童繪本作家，擅長創作適合{target_age}歲兒童的故事。

請根據用戶的想法創作一個完整的兒童繪本故事，需遵循以下要求：

1. 故事結構：
   - 共{page_count}頁
   - 每頁字數控制在20-50字，適合兒童閱讀
   - 開頭引人入勝，中間有趣味衝突，結尾溫馨正面

2. 風格要求：{style_desc}

3. 內容安全：
   - 所有內容必須適合兒童閱讀
   - 不包含任何暴力、恐怖或負面內容
   - 傳達正面價值觀（友愛、勇氣、誠實等）

4. 插圖提示：
   - 為每頁提供一個詳細的圖像生成提示詞（英文）
   - 提示詞應描述場景、角色和氛圍
   - 保持角色描述一致性

請以JSON格式回覆，格式如下：
{{
    "title": "故事標題",
    "pages": [
        {{
            "page_number": 1,
            "text": "這一頁的故事文字",
            "image_prompt": "English prompt for image generation describing this scene"
        }},
        ...
    ]
}}"""

        return system_prompt

    async def generate_story(
        self,
        prompt: str,
        page_count: int = 12,
        target_age: str = "3-6",
        language: str = "zh-TW",
        narrative_style: str = "warm",
        template_content: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Generate a complete children's story based on user prompt.

        Args:
            prompt: User's story idea/prompt
            page_count: Number of pages to generate
            target_age: Target age range (e.g., "3-6")
            language: Output language code
            narrative_style: Story style (humorous, warm, adventure)
            template_content: Optional template story outline to adapt

        Returns:
            Dict containing title and list of pages with text and image prompts
        """
        system_prompt = self._get_story_prompt(
            prompt, page_count, target_age, language, narrative_style
        )

        user_message = f"請根據以下想法創作一個兒童繪本故事：\n\n{prompt}"

        if template_content:
            user_message += f"\n\n參考模板大綱：\n{template_content}"

        try:
            # Try Claude first, fall back to GPT
            if self.anthropic_client:
                response = await self._generate_with_claude(system_prompt, user_message)
            elif self.openai_client:
                response = await self._generate_with_openai(system_prompt, user_message)
            else:
                raise ValueError("No AI provider configured")

            # Parse the JSON response
            story_data = self._parse_story_response(response)
            story_data["model_used"] = "claude" if self.anthropic_client else "openai"
            story_data["word_count"] = sum(len(p["text"]) for p in story_data["pages"])
            story_data["page_count"] = len(story_data["pages"])

            return story_data

        except Exception as e:
            logger.error(f"Story generation failed: {e}")
            raise

    async def _generate_with_claude(self, system_prompt: str, user_message: str) -> str:
        """Generate story using Claude API"""
        message = self.anthropic_client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}],
        )
        return message.content[0].text

    async def _generate_with_openai(self, system_prompt: str, user_message: str) -> str:
        """Generate story using OpenAI API"""
        response = self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            max_tokens=4096,
            temperature=0.8,
        )
        return response.choices[0].message.content

    def _parse_story_response(self, response: str) -> Dict[str, Any]:
        """Parse the JSON story response from AI"""
        # Try to extract JSON from response
        try:
            # Find JSON block if wrapped in markdown
            if "```json" in response:
                start = response.find("```json") + 7
                end = response.find("```", start)
                response = response[start:end].strip()
            elif "```" in response:
                start = response.find("```") + 3
                end = response.find("```", start)
                response = response[start:end].strip()

            return json.loads(response)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse story JSON: {e}")
            # Return a fallback structure
            return {
                "title": "Untitled Story",
                "pages": [
                    {
                        "page_number": 1,
                        "text": response[:200] if response else "Story generation failed",
                        "image_prompt": "A children's storybook illustration",
                    }
                ],
            }

    async def regenerate_page(
        self,
        story_context: str,
        page_number: int,
        current_text: str,
        instruction: Optional[str] = None,
    ) -> Dict[str, str]:
        """
        Regenerate a specific page of the story.

        Args:
            story_context: The full story for context
            page_number: Which page to regenerate
            current_text: Current text of the page
            instruction: Optional specific instruction for regeneration

        Returns:
            Dict with new text and image_prompt
        """
        prompt = f"""請重新生成第{page_number}頁的內容。

故事全文：
{story_context}

當前第{page_number}頁內容：
{current_text}

{f'修改要求：{instruction}' if instruction else '請生成一個不同但同樣合適的版本'}

請以JSON格式回覆：
{{"text": "新的故事文字", "image_prompt": "新的圖像提示詞"}}"""

        try:
            if self.anthropic_client:
                response = await self._generate_with_claude("你是兒童繪本作家", prompt)
            else:
                response = await self._generate_with_openai("你是兒童繪本作家", prompt)

            return json.loads(response)
        except Exception as e:
            logger.error(f"Page regeneration failed: {e}")
            return {"text": current_text, "image_prompt": "children's book illustration"}

    def estimate_credits(self, page_count: int) -> int:
        """Estimate credits needed for story generation"""
        base_cost = settings.COST_STORY_GENERATION
        # Additional cost per page over 12
        extra_pages = max(0, page_count - 12)
        return base_cost + (extra_pages * 5)
