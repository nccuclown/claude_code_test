"""
ReadKidz Platform - Illustration Generation Service
Uses DALL-E 3 or similar for generating children's book illustrations
"""
import logging
import uuid
from typing import Optional, Dict, Any, List
from app.core.config import settings

# Try to import OpenAI (optional - for demo mode without AI)
try:
    from openai import OpenAI
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False
    OpenAI = None

logger = logging.getLogger(__name__)


# Style prompt modifiers for different art styles
STYLE_PROMPTS = {
    "kindergarten": "children's kindergarten drawing style, simple shapes, bright primary colors, crayon-like texture",
    "crayon": "crayon drawing style, childlike, colorful crayon strokes, textured paper background",
    "cartoon": "cartoon style, bold outlines, vibrant colors, expressive characters, playful",
    "collage": "paper collage style, cut-out shapes, textured papers, craft aesthetic",
    "watercolor": "soft watercolor illustration, gentle colors, flowing brushstrokes, dreamy atmosphere",
    "pixar": "3D rendered Pixar-style, highly detailed, expressive characters, cinematic lighting",
    "gilded_fantasy": "gilded fantasy illustration style, golden accents, ornate details, magical atmosphere",
    "storybook_classic": "classic storybook illustration, detailed, traditional, warm colors, timeless aesthetic",
    "minimalist": "minimalist children's book style, simple shapes, limited color palette, clean design",
    "japanese": "Japanese children's book illustration, soft colors, kawaii elements, delicate linework",
}

# Aspect ratio to size mapping for DALL-E 3
ASPECT_RATIO_SIZES = {
    "16:9": "1792x1024",
    "4:3": "1024x1024",  # Closest available
    "1:1": "1024x1024",
    "3:4": "1024x1024",  # Closest available
    "9:16": "1024x1792",
}


class IllustrationService:
    """Service for generating children's book illustrations"""

    def __init__(self):
        self.openai_client = None
        if HAS_OPENAI and settings.OPENAI_API_KEY:
            self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)

    def _build_prompt(
        self,
        user_prompt: str,
        style_name: Optional[str] = None,
        character_description: Optional[str] = None,
        negative_prompt: Optional[str] = None,
    ) -> str:
        """Build the complete prompt for image generation"""

        # Start with style
        style_modifier = STYLE_PROMPTS.get(style_name, STYLE_PROMPTS["storybook_classic"])

        # Build the prompt
        prompt_parts = [
            f"A children's book illustration: {user_prompt}",
            f"Art style: {style_modifier}",
        ]

        # Add character description for consistency
        if character_description:
            prompt_parts.append(f"Main character: {character_description}")

        # Safety modifiers
        prompt_parts.extend([
            "Child-friendly, wholesome content",
            "Bright, cheerful atmosphere",
            "High quality, detailed illustration",
        ])

        full_prompt = ". ".join(prompt_parts)

        return full_prompt

    async def generate_illustration(
        self,
        prompt: str,
        style_name: Optional[str] = None,
        aspect_ratio: str = "16:9",
        character_description: Optional[str] = None,
        seed: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Generate a single illustration.

        Args:
            prompt: Description of the scene to illustrate
            style_name: Art style to use
            aspect_ratio: Image aspect ratio
            character_description: Character details for consistency
            seed: Optional seed for reproducibility

        Returns:
            Dict with image_url and metadata
        """
        full_prompt = self._build_prompt(
            prompt, style_name, character_description
        )

        size = ASPECT_RATIO_SIZES.get(aspect_ratio, "1024x1024")
        width, height = map(int, size.split("x"))

        if not self.openai_client:
            # Return demo data for development/testing
            logger.warning("OpenAI not configured, returning demo illustration data")
            demo_images = [
                "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=800",
                "https://images.unsplash.com/photo-1512058564366-18510be2db19?w=800",
                "https://images.unsplash.com/photo-1503454537195-1dcabb73ffb9?w=800",
                "https://images.unsplash.com/photo-1485546246426-74dc88dec4d9?w=800",
                "https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=800",
            ]
            import random
            return {
                "image_url": random.choice(demo_images),
                "prompt": full_prompt,
                "revised_prompt": f"[DEMO] {full_prompt}",
                "width": width,
                "height": height,
                "style": style_name,
                "model_used": "demo-mode",
            }

        try:
            response = self.openai_client.images.generate(
                model="dall-e-3",
                prompt=full_prompt,
                size=size,
                quality="standard",
                n=1,
            )

            image_url = response.data[0].url
            revised_prompt = response.data[0].revised_prompt

            return {
                "image_url": image_url,
                "prompt": full_prompt,
                "revised_prompt": revised_prompt,
                "width": width,
                "height": height,
                "style": style_name,
                "model_used": "dall-e-3",
            }

        except Exception as e:
            logger.error(f"Image generation failed: {e}")
            raise

    async def generate_batch(
        self,
        prompts: List[Dict[str, str]],
        style_name: Optional[str] = None,
        aspect_ratio: str = "16:9",
        character_description: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Generate multiple illustrations (for a complete book).

        Args:
            prompts: List of {page_number, prompt} dicts
            style_name: Consistent style for all images
            aspect_ratio: Image aspect ratio
            character_description: Character details for consistency

        Returns:
            List of image results
        """
        results = []

        for page_prompt in prompts:
            try:
                result = await self.generate_illustration(
                    prompt=page_prompt["prompt"],
                    style_name=style_name,
                    aspect_ratio=aspect_ratio,
                    character_description=character_description,
                )
                result["page_number"] = page_prompt["page_number"]
                results.append(result)
            except Exception as e:
                logger.error(f"Failed to generate page {page_prompt['page_number']}: {e}")
                results.append({
                    "page_number": page_prompt["page_number"],
                    "error": str(e),
                })

        return results

    async def edit_with_chatps(
        self,
        image_url: str,
        instruction: str,
    ) -> Dict[str, Any]:
        """
        Edit an image using natural language instruction (ChatPS feature).

        Args:
            image_url: URL of the original image
            instruction: Natural language edit instruction

        Returns:
            Dict with edited image URL
        """
        if not self.openai_client:
            # Return demo data for development/testing
            logger.warning("OpenAI not configured, returning demo edit data")
            return {
                "original_image_url": image_url,
                "edited_image_url": "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=800",
                "instruction": instruction,
                "revised_prompt": f"[DEMO] Edit: {instruction}",
            }

        # For now, we'll use DALL-E 3 to regenerate with the modification
        # In production, you might use image editing APIs like DALL-E 2 edit
        # or specialized services

        edit_prompt = f"""Recreate this children's book illustration with the following modification: {instruction}
        Maintain the same art style, character designs, and overall composition.
        Child-friendly, high quality illustration."""

        try:
            response = self.openai_client.images.generate(
                model="dall-e-3",
                prompt=edit_prompt,
                size="1024x1024",
                quality="standard",
                n=1,
            )

            return {
                "original_image_url": image_url,
                "edited_image_url": response.data[0].url,
                "instruction": instruction,
                "revised_prompt": response.data[0].revised_prompt,
            }

        except Exception as e:
            logger.error(f"ChatPS edit failed: {e}")
            raise

    def get_available_styles(self) -> List[Dict[str, str]]:
        """Get list of available art styles"""
        styles = []
        for key, description in STYLE_PROMPTS.items():
            styles.append({
                "id": key,
                "name": key.replace("_", " ").title(),
                "description": description,
            })
        return styles

    def estimate_credits(self, count: int = 1) -> int:
        """Estimate credits needed for illustration generation"""
        return settings.COST_IMAGE_GENERATION * count
