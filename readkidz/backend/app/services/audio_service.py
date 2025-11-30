"""
ReadKidz Platform - Audio/TTS Service
Uses ElevenLabs or similar for text-to-speech generation
"""
import logging
from typing import Optional, Dict, Any, List
from app.core.config import settings

logger = logging.getLogger(__name__)


# Voice configurations
VOICES = {
    # Children's voices
    "child_zh_female": {
        "name": "小美 (Xiao Mei)",
        "provider": "elevenlabs",
        "voice_id": "EXAVITQu4vr4xnSDxMaL",
        "gender": "female",
        "age_group": "child",
        "language": "zh",
    },
    "child_zh_male": {
        "name": "小明 (Xiao Ming)",
        "provider": "elevenlabs",
        "voice_id": "VR6AewLTigWG4xSOukaG",
        "gender": "male",
        "age_group": "child",
        "language": "zh",
    },
    "child_en_female": {
        "name": "Lily",
        "provider": "elevenlabs",
        "voice_id": "MF3mGyEYCl7XYWbV9V6O",
        "gender": "female",
        "age_group": "child",
        "language": "en",
    },
    "child_en_male": {
        "name": "Tommy",
        "provider": "elevenlabs",
        "voice_id": "CYw3kZ02Hs0563khs1Fj",
        "gender": "male",
        "age_group": "child",
        "language": "en",
    },
    # Adult narrators
    "narrator_zh_female": {
        "name": "李阿姨 (Aunt Li)",
        "provider": "elevenlabs",
        "voice_id": "21m00Tcm4TlvDq8ikWAM",
        "gender": "female",
        "age_group": "adult",
        "language": "zh",
    },
    "narrator_zh_male": {
        "name": "王叔叔 (Uncle Wang)",
        "provider": "elevenlabs",
        "voice_id": "AZnzlk1XvdvUeBnXmlld",
        "gender": "male",
        "age_group": "adult",
        "language": "zh",
    },
    "narrator_en_female": {
        "name": "Emily",
        "provider": "elevenlabs",
        "voice_id": "EXAVITQu4vr4xnSDxMaL",
        "gender": "female",
        "age_group": "adult",
        "language": "en",
    },
    "narrator_en_male": {
        "name": "James",
        "provider": "elevenlabs",
        "voice_id": "VR6AewLTigWG4xSOukaG",
        "gender": "male",
        "age_group": "adult",
        "language": "en",
    },
}


class AudioService:
    """Service for generating audio/TTS content"""

    def __init__(self):
        self.elevenlabs_client = None
        if settings.ELEVENLABS_API_KEY:
            try:
                from elevenlabs import ElevenLabs
                self.elevenlabs_client = ElevenLabs(api_key=settings.ELEVENLABS_API_KEY)
            except ImportError:
                logger.warning("ElevenLabs package not installed")

    async def generate_speech(
        self,
        text: str,
        voice_id: str,
        language: str = "zh-TW",
        speed: int = 100,
        output_format: str = "mp3",
    ) -> Dict[str, Any]:
        """
        Generate speech from text using TTS.

        Args:
            text: Text to convert to speech
            voice_id: Voice ID to use
            language: Language code
            speed: Speech speed (50-200, 100 is normal)
            output_format: Output audio format

        Returns:
            Dict with audio_url and duration
        """
        if not self.elevenlabs_client:
            # Return mock data for development
            logger.warning("ElevenLabs not configured, returning mock data")
            return {
                "audio_url": "https://example.com/mock-audio.mp3",
                "duration": len(text) * 100,  # Rough estimate: 100ms per character
                "voice_id": voice_id,
                "format": output_format,
            }

        try:
            # Get the actual voice ID from our configuration
            voice_config = VOICES.get(voice_id, {})
            provider_voice_id = voice_config.get("voice_id", voice_id)

            # Generate audio using ElevenLabs
            audio = self.elevenlabs_client.text_to_speech.convert(
                text=text,
                voice_id=provider_voice_id,
                model_id="eleven_multilingual_v2",
                output_format="mp3_44100_128",
            )

            # In production, save to storage and return URL
            # For now, return placeholder
            return {
                "audio_data": audio,
                "voice_id": voice_id,
                "format": output_format,
                "duration": len(text) * 100,
            }

        except Exception as e:
            logger.error(f"TTS generation failed: {e}")
            raise

    async def generate_batch(
        self,
        pages: List[Dict[str, Any]],
        voice_id: str,
        language: str = "zh-TW",
    ) -> List[Dict[str, Any]]:
        """
        Generate audio for multiple pages.

        Args:
            pages: List of {page_number, text} dicts
            voice_id: Voice ID to use
            language: Language code

        Returns:
            List of audio results
        """
        results = []

        for page in pages:
            try:
                result = await self.generate_speech(
                    text=page["text"],
                    voice_id=voice_id,
                    language=language,
                )
                result["page_number"] = page["page_number"]
                results.append(result)
            except Exception as e:
                logger.error(f"Failed to generate audio for page {page['page_number']}: {e}")
                results.append({
                    "page_number": page["page_number"],
                    "error": str(e),
                })

        return results

    def get_available_voices(
        self,
        language: Optional[str] = None,
        age_group: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Get list of available voices with optional filtering"""
        voices = []

        for voice_id, config in VOICES.items():
            if language and config["language"] != language:
                continue
            if age_group and config["age_group"] != age_group:
                continue

            voices.append({
                "id": voice_id,
                "name": config["name"],
                "gender": config["gender"],
                "age_group": config["age_group"],
                "language": config["language"],
                "is_child_voice": config["age_group"] == "child",
            })

        return voices

    def estimate_credits(self, text_length: int) -> int:
        """Estimate credits needed for TTS generation"""
        # Base cost plus additional cost per 500 characters
        base_cost = settings.COST_TTS_GENERATION
        extra_chars = max(0, text_length - 500)
        return base_cost + (extra_chars // 500) * 5

    def estimate_duration(self, text: str, speed: int = 100) -> int:
        """Estimate audio duration in milliseconds"""
        # Rough estimate: average speaking rate is about 150 words/minute
        # For Chinese: about 3 characters per second
        # For English: about 2.5 words per second

        chars = len(text)
        base_duration = chars * 300  # 300ms per character as baseline
        adjusted_duration = base_duration * (100 / speed)
        return int(adjusted_duration)
