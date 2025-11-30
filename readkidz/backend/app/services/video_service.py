"""
ReadKidz Platform - Video Generation Service
Combines images, audio, and animations to create story videos
"""
import logging
import asyncio
from typing import Optional, Dict, Any, List, Callable
from app.core.config import settings

logger = logging.getLogger(__name__)


# Animation types
ANIMATION_TYPES = {
    "zoom_in": "Slow zoom into the image center",
    "zoom_out": "Slow zoom out from the image",
    "pan_left": "Slow pan from right to left",
    "pan_right": "Slow pan from left to right",
    "pan_up": "Slow pan from bottom to top",
    "pan_down": "Slow pan from top to bottom",
    "ken_burns_1": "Ken Burns effect - zoom and pan combination",
    "ken_burns_2": "Ken Burns effect - reverse direction",
    "shake": "Gentle shake effect",
    "bounce": "Subtle bounce effect",
    "fade_zoom": "Fade in with slow zoom",
    "static": "No animation - static image",
}

# Transition types
TRANSITION_TYPES = {
    "fade": "Crossfade transition",
    "slide_left": "Slide from right to left",
    "slide_right": "Slide from left to right",
    "slide_up": "Slide from bottom to top",
    "slide_down": "Slide from top to bottom",
    "wipe": "Wipe transition",
    "dissolve": "Dissolve effect",
    "none": "Cut directly",
}

# Font options for subtitles
SUBTITLE_FONTS = {
    "default": "Noto Sans TC",
    "rounded": "Noto Sans TC Rounded",
}

# Font effects
FONT_EFFECTS = {
    "none": "Plain text",
    "shadow": "Drop shadow effect",
}


class VideoService:
    """Service for generating story videos"""

    def __init__(self):
        # In production, you would initialize video processing libraries
        # like MoviePy, FFmpeg wrappers, etc.
        pass

    async def generate_video(
        self,
        project_id: int,
        pages: List[Dict[str, Any]],
        settings_dict: Dict[str, Any],
        progress_callback: Optional[Callable[[int], None]] = None,
    ) -> Dict[str, Any]:
        """
        Generate a complete story video from pages.

        Args:
            project_id: Project ID
            pages: List of page data with images, text, and audio
            settings_dict: Video generation settings
            progress_callback: Optional callback for progress updates

        Returns:
            Dict with video URL and metadata
        """
        total_steps = len(pages) + 3  # Pages + intro + outro + finalize
        current_step = 0

        def update_progress(step: int):
            if progress_callback:
                progress = int((step / total_steps) * 100)
                progress_callback(progress)

        try:
            # Step 1: Prepare assets
            logger.info(f"Preparing video assets for project {project_id}")
            current_step += 1
            update_progress(current_step)

            # Step 2: Process each page
            video_segments = []
            for page in pages:
                segment = await self._create_page_segment(
                    page=page,
                    animation_type=settings_dict.get("animation_types", ["zoom_in"])[0],
                    transition_type=settings_dict.get("transition_type", "fade"),
                    has_subtitles=settings_dict.get("has_subtitles", True),
                    subtitle_font=settings_dict.get("subtitle_font", "default"),
                    font_effect=settings_dict.get("font_effect", "shadow"),
                )
                video_segments.append(segment)
                current_step += 1
                update_progress(current_step)

            # Step 3: Add background music
            logger.info("Adding background music")
            current_step += 1
            update_progress(current_step)

            # Step 4: Combine and export
            logger.info("Finalizing video")
            video_path = await self._combine_segments(
                segments=video_segments,
                background_music_id=settings_dict.get("background_music_id"),
                resolution=settings_dict.get("resolution", "1080p"),
            )
            current_step += 1
            update_progress(current_step)

            # Calculate total duration
            total_duration = sum(s.get("duration", 5) for s in video_segments)

            return {
                "video_url": video_path,
                "thumbnail_url": pages[0].get("image_url") if pages else None,
                "duration": total_duration,
                "resolution": settings_dict.get("resolution", "1080p"),
                "page_count": len(pages),
            }

        except Exception as e:
            logger.error(f"Video generation failed: {e}")
            raise

    async def _create_page_segment(
        self,
        page: Dict[str, Any],
        animation_type: str,
        transition_type: str,
        has_subtitles: bool,
        subtitle_font: str,
        font_effect: str,
    ) -> Dict[str, Any]:
        """Create a video segment for a single page"""

        # In production, this would use MoviePy or FFmpeg
        # to create the actual video segment

        # Calculate duration based on audio length or text
        duration = page.get("audio_duration", 5)  # Default 5 seconds
        if not page.get("audio_url"):
            # Estimate based on text length
            text = page.get("story_text", "")
            duration = max(3, len(text) * 0.15)  # ~6-7 chars/second reading speed

        return {
            "page_number": page.get("page_number"),
            "image_url": page.get("image_url"),
            "audio_url": page.get("audio_url"),
            "text": page.get("story_text"),
            "duration": duration,
            "animation": animation_type,
            "transition": transition_type,
        }

    async def _combine_segments(
        self,
        segments: List[Dict[str, Any]],
        background_music_id: Optional[str],
        resolution: str,
    ) -> str:
        """Combine all segments into final video"""

        # In production, this would:
        # 1. Download all images and audio files
        # 2. Apply animations to each image
        # 3. Add transitions between segments
        # 4. Overlay narration audio
        # 5. Add background music
        # 6. Render final video
        # 7. Upload to storage

        # For now, return a placeholder
        logger.info(f"Would combine {len(segments)} segments into {resolution} video")
        return f"https://storage.readkidz.com/videos/mock-video.mp4"

    async def add_watermark(
        self,
        video_path: str,
        watermark_text: str = "ReadKidz",
    ) -> str:
        """Add watermark to video (for free tier)"""
        # In production, use FFmpeg to add watermark
        return video_path

    async def remove_watermark(
        self,
        video_path: str,
    ) -> str:
        """Remove watermark from video (for paid tiers)"""
        # In production, regenerate without watermark
        return video_path

    def get_available_animations(self) -> List[Dict[str, str]]:
        """Get list of available animation types"""
        return [
            {"id": k, "name": k.replace("_", " ").title(), "description": v}
            for k, v in ANIMATION_TYPES.items()
        ]

    def get_available_transitions(self) -> List[Dict[str, str]]:
        """Get list of available transition types"""
        return [
            {"id": k, "name": k.replace("_", " ").title(), "description": v}
            for k, v in TRANSITION_TYPES.items()
        ]

    def get_subtitle_options(self) -> Dict[str, List[Dict[str, str]]]:
        """Get available subtitle customization options"""
        return {
            "fonts": [
                {"id": k, "name": v} for k, v in SUBTITLE_FONTS.items()
            ],
            "effects": [
                {"id": k, "name": v} for k, v in FONT_EFFECTS.items()
            ],
        }

    def estimate_duration(self, pages: List[Dict[str, Any]]) -> int:
        """Estimate total video duration in seconds"""
        total = 0
        for page in pages:
            if page.get("audio_duration"):
                total += page["audio_duration"]
            else:
                text = page.get("story_text", "")
                total += max(3, len(text) * 0.15)
        return int(total)

    def estimate_processing_time(self, page_count: int, resolution: str) -> int:
        """Estimate processing time in minutes"""
        base_time = page_count * 1.5  # 1.5 minutes per page
        if resolution == "1080p":
            base_time *= 1.2
        elif resolution == "4k":
            base_time *= 2.0
        return int(base_time)

    def estimate_credits(self, page_count: int, has_narration: bool = True) -> int:
        """Estimate credits needed for video generation"""
        base_cost = settings.COST_VIDEO_GENERATION
        page_cost = page_count * 10
        narration_cost = page_count * 5 if has_narration else 0
        return base_cost + page_cost + narration_cost
