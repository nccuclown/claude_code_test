"""
ReadKidz Platform - Templates and Styles API Routes
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.models.user import User, Subscription
from app.models.template import Template, Style, Voice, BackgroundMusic
from app.schemas.template import (
    TemplateResponse, StyleResponse, VoiceResponse, MusicResponse
)
from app.services.illustration_service import IllustrationService
from app.services.audio_service import AudioService
from app.services.video_service import VideoService
from app.api.auth import get_current_user

router = APIRouter()


# ============ Templates ============

@router.get("/", response_model=List[TemplateResponse])
async def list_templates(
    category: Optional[str] = Query(None, description="Filter by category"),
    age_range: Optional[str] = Query(None, description="Filter by age range"),
    is_free: Optional[bool] = Query(None, description="Filter by free/paid"),
    search: Optional[str] = Query(None, description="Search query"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List available story templates"""
    query = select(Template).where(Template.is_active == True)

    if category:
        query = query.where(Template.category == category)
    if age_range:
        query = query.where(Template.age_range == age_range)
    if is_free is not None:
        query = query.where(Template.is_free == is_free)
    if search:
        query = query.where(
            Template.name.ilike(f"%{search}%") |
            Template.name_zh.ilike(f"%{search}%") |
            Template.description.ilike(f"%{search}%")
        )

    query = query.order_by(Template.sort_order, Template.use_count.desc())
    query = query.offset(offset).limit(limit)

    result = await db.execute(query)
    templates = result.scalars().all()

    return [TemplateResponse.model_validate(t) for t in templates]


@router.get("/categories")
async def list_template_categories(
    db: AsyncSession = Depends(get_db),
):
    """List all template categories"""
    result = await db.execute(
        select(Template.category).distinct().where(Template.is_active == True)
    )
    categories = result.scalars().all()

    return {
        "categories": [
            {"id": c, "name": c.replace("_", " ").title()}
            for c in categories if c
        ]
    }


@router.get("/{template_id}", response_model=TemplateResponse)
async def get_template(
    template_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get a specific template"""
    result = await db.execute(
        select(Template).where(Template.id == template_id)
    )
    template = result.scalar_one_or_none()

    if not template:
        return {"error": "Template not found"}

    return TemplateResponse.model_validate(template)


# ============ Styles ============

@router.get("/styles", response_model=List[StyleResponse])
async def list_styles(
    category: Optional[str] = Query(None, description="Filter by category"),
    is_free: Optional[bool] = Query(None, description="Filter by free/paid"),
    search: Optional[str] = Query(None, description="Search query"),
    limit: int = Query(60, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List available art styles (60+ styles)"""
    query = select(Style).where(Style.is_active == True)

    if category:
        query = query.where(Style.category == category)
    if is_free is not None:
        query = query.where(Style.is_free == is_free)
    if search:
        query = query.where(
            Style.name.ilike(f"%{search}%") |
            Style.name_zh.ilike(f"%{search}%")
        )

    query = query.order_by(Style.sort_order, Style.use_count.desc())
    query = query.offset(offset).limit(limit)

    result = await db.execute(query)
    styles = result.scalars().all()

    # If no styles in database, return built-in styles
    if not styles:
        illustration_service = IllustrationService()
        built_in = illustration_service.get_available_styles()
        return [
            StyleResponse(
                id=i + 1,
                name=s["name"],
                name_zh=s["name"],
                description=s["description"],
                description_zh=s["description"],
                category="official",
                tags=[],
                thumbnail_url=None,
                sample_images=[],
                is_free=True,
                supported_ratios=["16:9", "4:3", "1:1", "3:4", "9:16"],
                use_count=0,
            )
            for i, s in enumerate(built_in)
        ]

    return [StyleResponse.model_validate(s) for s in styles]


@router.get("/styles/categories")
async def list_style_categories():
    """List all style categories"""
    return {
        "categories": [
            {"id": "classic", "name": "Classic Revival", "name_zh": "經典復刻"},
            {"id": "official", "name": "Official", "name_zh": "官方"},
        ]
    }


# ============ Voices ============

@router.get("/voices", response_model=List[VoiceResponse])
async def list_voices(
    language: Optional[str] = Query(None, description="Filter by language"),
    age_group: Optional[str] = Query(None, description="Filter by age group (child/adult)"),
    gender: Optional[str] = Query(None, description="Filter by gender"),
    is_free: Optional[bool] = Query(None, description="Filter by free/paid"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List available voices (180+ options)"""
    query = select(Voice).where(Voice.is_active == True)

    if language:
        query = query.where(Voice.language == language)
    if age_group:
        query = query.where(Voice.age_group == age_group)
    if gender:
        query = query.where(Voice.gender == gender)
    if is_free is not None:
        query = query.where(Voice.is_free == is_free)

    query = query.order_by(Voice.sort_order)
    query = query.offset(offset).limit(limit)

    result = await db.execute(query)
    voices = result.scalars().all()

    # If no voices in database, return built-in voices
    if not voices:
        audio_service = AudioService()
        built_in = audio_service.get_available_voices(language=language, age_group=age_group)
        return [
            VoiceResponse(
                id=i + 1,
                name=v["name"],
                name_zh=v["name"],
                description=None,
                gender=v["gender"],
                age_group=v["age_group"],
                language=v["language"],
                accent=None,
                sample_audio_url=None,
                is_child_voice=v["is_child_voice"],
                is_free=True,
            )
            for i, v in enumerate(built_in)
        ]

    return [VoiceResponse.model_validate(v) for v in voices]


@router.get("/voices/languages")
async def list_voice_languages():
    """List supported voice languages"""
    return {
        "languages": [
            {"code": "zh", "name": "Chinese", "name_zh": "中文"},
            {"code": "zh-TW", "name": "Chinese (Taiwan)", "name_zh": "中文（台灣）"},
            {"code": "en", "name": "English", "name_zh": "英文"},
            {"code": "ja", "name": "Japanese", "name_zh": "日文"},
            {"code": "ko", "name": "Korean", "name_zh": "韓文"},
            {"code": "es", "name": "Spanish", "name_zh": "西班牙文"},
            {"code": "fr", "name": "French", "name_zh": "法文"},
            {"code": "pt", "name": "Portuguese", "name_zh": "葡萄牙文"},
        ]
    }


# ============ Background Music ============

@router.get("/music", response_model=List[MusicResponse])
async def list_background_music(
    mood: Optional[str] = Query(None, description="Filter by mood"),
    genre: Optional[str] = Query(None, description="Filter by genre"),
    is_free: Optional[bool] = Query(None, description="Filter by free/paid"),
    limit: int = Query(20, ge=1, le=50),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List available background music"""
    query = select(BackgroundMusic).where(BackgroundMusic.is_active == True)

    if mood:
        query = query.where(BackgroundMusic.mood == mood)
    if genre:
        query = query.where(BackgroundMusic.genre == genre)
    if is_free is not None:
        query = query.where(BackgroundMusic.is_free == is_free)

    query = query.order_by(BackgroundMusic.sort_order)
    query = query.offset(offset).limit(limit)

    result = await db.execute(query)
    music_list = result.scalars().all()

    return [MusicResponse.model_validate(m) for m in music_list]


@router.get("/music/moods")
async def list_music_moods():
    """List available music moods"""
    return {
        "moods": [
            {"id": "calm", "name": "Calm", "name_zh": "平靜"},
            {"id": "happy", "name": "Happy", "name_zh": "快樂"},
            {"id": "adventurous", "name": "Adventurous", "name_zh": "冒險"},
            {"id": "dreamy", "name": "Dreamy", "name_zh": "夢幻"},
            {"id": "playful", "name": "Playful", "name_zh": "活潑"},
            {"id": "mysterious", "name": "Mysterious", "name_zh": "神秘"},
        ]
    }


# ============ Video Options ============

@router.get("/video-options")
async def get_video_options():
    """Get available video customization options"""
    video_service = VideoService()

    return {
        "animations": video_service.get_available_animations(),
        "transitions": video_service.get_available_transitions(),
        "subtitles": video_service.get_subtitle_options(),
        "resolutions": [
            {"id": "720p", "name": "720p HD", "width": 1280, "height": 720},
            {"id": "1080p", "name": "1080p Full HD", "width": 1920, "height": 1080},
        ],
        "aspect_ratios": [
            {"id": "16:9", "name": "16:9 (Landscape)", "description": "Best for YouTube"},
            {"id": "4:3", "name": "4:3 (Traditional)", "description": "Classic ratio"},
            {"id": "1:1", "name": "1:1 (Square)", "description": "Best for Instagram"},
            {"id": "3:4", "name": "3:4 (Portrait)", "description": "Vertical format"},
            {"id": "9:16", "name": "9:16 (Vertical)", "description": "Best for Shorts/Stories"},
        ],
    }


# ============ Prompts Library ============

@router.get("/prompts")
async def get_prompt_library():
    """Get the built-in prompt library for image generation"""
    return {
        "categories": [
            {
                "id": "body",
                "name": "Body Features",
                "name_zh": "身體特徵",
                "prompts": [
                    {"id": "golden_curly_hair", "en": "golden curly hair", "zh": "金色捲髮"},
                    {"id": "brown_short_hair", "en": "brown short hair", "zh": "棕色短髮"},
                    {"id": "black_long_hair", "en": "black long hair", "zh": "黑色長髮"},
                    {"id": "big_blue_eyes", "en": "big blue eyes", "zh": "大大的藍眼睛"},
                    {"id": "small_nose", "en": "small nose", "zh": "小鼻子"},
                    {"id": "rosy_cheeks", "en": "rosy cheeks", "zh": "紅潤的臉頰"},
                ]
            },
            {
                "id": "clothing",
                "name": "Clothing",
                "name_zh": "服裝",
                "prompts": [
                    {"id": "blue_dress", "en": "wearing a blue dress", "zh": "穿著藍色連衣裙"},
                    {"id": "red_sweater", "en": "wearing a red sweater", "zh": "穿著紅色毛衣"},
                    {"id": "overalls", "en": "wearing overalls", "zh": "穿著吊帶褲"},
                    {"id": "princess_dress", "en": "wearing a princess dress", "zh": "穿著公主裙"},
                ]
            },
            {
                "id": "personality",
                "name": "Personality",
                "name_zh": "性格",
                "prompts": [
                    {"id": "brave", "en": "brave and adventurous", "zh": "勇敢愛冒險"},
                    {"id": "curious", "en": "curious and wondering", "zh": "好奇心強"},
                    {"id": "kind", "en": "kind and gentle", "zh": "善良溫柔"},
                    {"id": "playful", "en": "playful and energetic", "zh": "活潑好動"},
                ]
            },
            {
                "id": "backgrounds",
                "name": "Backgrounds",
                "name_zh": "背景",
                "prompts": [
                    {"id": "white_bg", "en": "pure white background", "zh": "純白背景"},
                    {"id": "forest", "en": "magical forest background", "zh": "魔法森林背景"},
                    {"id": "bedroom", "en": "cozy bedroom", "zh": "溫馨臥室"},
                    {"id": "garden", "en": "beautiful garden", "zh": "美麗花園"},
                ]
            },
        ]
    }
