"""
ReadKidz Platform - Story Generation Service
Uses LLMs (Claude/GPT) to generate children's stories
"""
import json
import logging
from typing import Optional, Dict, Any
from app.core.config import settings

logger = logging.getLogger(__name__)

# Try to import AI clients (optional - for demo mode without AI)
try:
    from anthropic import Anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False
    Anthropic = None

try:
    from openai import OpenAI
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False
    OpenAI = None


class StoryService:
    """Service for generating children's stories using AI"""

    def __init__(self):
        self.anthropic_client = None
        self.openai_client = None

        if HAS_ANTHROPIC and settings.ANTHROPIC_API_KEY:
            self.anthropic_client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        if HAS_OPENAI and settings.OPENAI_API_KEY:
            self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)

    def _get_demo_story(self, prompt: str, page_count: int) -> Dict[str, Any]:
        """Return a demo story when AI is not available"""
        pages = []
        demo_texts = [
            "從前從前，在一個美麗的森林裡，住著一隻可愛的小兔子。",
            "小兔子每天都會在森林裡玩耍，和朋友們一起探險。",
            "有一天，小兔子發現了一條神秘的小路。",
            "小路的盡頭有一片美麗的花田。",
            "小兔子開心地在花田裡跳舞。",
            "太陽慢慢下山了，小兔子要回家了。",
            "媽媽在家門口等著小兔子。",
            "小兔子把今天的冒險告訴了媽媽。",
            "媽媽給小兔子準備了好吃的晚餐。",
            "吃完晚餐，小兔子感到很幸福。",
            "夜晚來臨，星星在天空中閃爍。",
            "小兔子進入了甜美的夢鄉。晚安！",
        ]

        for i in range(min(page_count, len(demo_texts))):
            pages.append({
                "page_number": i + 1,
                "text": demo_texts[i],
                "image_prompt": f"A cute little rabbit in a magical forest, page {i+1}, children's book illustration style"
            })

        return {
            "title": f"小兔子的冒險",
            "pages": pages,
            "word_count": sum(len(p["text"]) for p in pages),
            "page_count": len(pages),
            "model_used": "demo",
        }

    async def generate_story(
        self,
        prompt: str,
        page_count: int = 12,
        target_age: str = "3-6",
        language: str = "zh-TW",
        narrative_style: str = "warm",
        template_content: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Generate a complete children's story based on user prompt."""

        # If no AI is configured, return demo data
        if not self.anthropic_client and not self.openai_client:
            logger.warning("No AI service configured, returning demo story")
            return self._get_demo_story(prompt, page_count)

        system_prompt = self._get_story_prompt(
            prompt, page_count, target_age, language, narrative_style
        )

        user_message = f"請根據以下想法創作一個兒童繪本故事：\n\n{prompt}"

        if template_content:
            user_message += f"\n\n參考模板大綱：\n{template_content}"

        try:
            if self.anthropic_client:
                response = await self._generate_with_claude(system_prompt, user_message)
            elif self.openai_client:
                response = await self._generate_with_openai(system_prompt, user_message)
            else:
                return self._get_demo_story(prompt, page_count)

            story_data = self._parse_story_response(response)
            story_data["model_used"] = "claude" if self.anthropic_client else "openai"
            story_data["word_count"] = sum(len(p["text"]) for p in story_data["pages"])
            story_data["page_count"] = len(story_data["pages"])

            return story_data

        except Exception as e:
            logger.error(f"Story generation failed: {e}")
            return self._get_demo_story(prompt, page_count)

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
            "humorous": "幽默風趣",
            "warm": "溫馨感人",
            "adventure": "充滿冒險",
            "educational": "寓教於樂",
        }
        style_desc = style_descriptions.get(narrative_style, "溫馨感人")

        return f"""你是兒童繪本作家。請創作一個{page_count}頁的{style_desc}故事，適合{target_age}歲兒童。
每頁20-50字。以JSON格式回覆。"""

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
        )
        return response.choices[0].message.content

    def _parse_story_response(self, response: str) -> Dict[str, Any]:
        """Parse the JSON story response from AI"""
        try:
            if "```json" in response:
                start = response.find("```json") + 7
                end = response.find("```", start)
                response = response[start:end].strip()
            return json.loads(response)
        except:
            return self._get_demo_story("", 12)

    def estimate_credits(self, page_count: int) -> int:
        """Estimate credits needed for story generation"""
        return settings.COST_STORY_GENERATION + max(0, page_count - 12) * 5
