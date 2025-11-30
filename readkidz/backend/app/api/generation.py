"""
ReadKidz Platform - AI Generation API Routes
Core AI functionality for story, illustration, video, and audio generation
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.models.user import User
from app.models.project import Project, ProjectPage, Character, ProjectStatus
from app.models.content import Story, Illustration, Video, Audio, GenerationStatus
from app.schemas.content import (
    StoryGenerateRequest, StoryResponse,
    IllustrationGenerateRequest, IllustrationResponse,
    VideoGenerateRequest, VideoResponse,
    AudioGenerateRequest, AudioResponse,
    ChatPSEditRequest, ChatPSEditResponse,
    OneClickVideoRequest, GenerationStatusResponse,
)
from app.services.story_service import StoryService
from app.services.illustration_service import IllustrationService
from app.services.video_service import VideoService
from app.services.audio_service import AudioService
from app.services.credits_service import CreditsService
from app.api.auth import get_current_user

router = APIRouter()


# ============ Story Generation ============

@router.post("/story", response_model=StoryResponse)
async def generate_story(
    request: StoryGenerateRequest,
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Generate a complete children's story from a prompt.

    This endpoint uses AI to create a full story with:
    - Title
    - Multiple pages with text
    - Image prompts for each page
    """
    # Verify project ownership
    result = await db.execute(
        select(Project).where(
            Project.id == project_id,
            Project.user_id == current_user.id,
        )
    )
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Check credits
    credits_service = CreditsService(db)
    estimated_cost = credits_service.estimate_operation_cost(
        "story", page_count=request.page_count
    )

    success, message = await credits_service.check_and_deduct_credits(
        current_user.id, estimated_cost, "story_generation"
    )
    if not success:
        raise HTTPException(status_code=402, detail=message)

    # Generate story
    story_service = StoryService()

    try:
        story_data = await story_service.generate_story(
            prompt=request.prompt,
            page_count=request.page_count,
            target_age=request.target_age,
            language=request.language,
            narrative_style=request.narrative_style,
        )

        # Save story to database
        story = Story(
            project_id=project_id,
            original_prompt=request.prompt,
            mode=request.mode,
            title=story_data["title"],
            full_text="\n".join(p["text"] for p in story_data["pages"]),
            pages_content=story_data["pages"],
            word_count=story_data["word_count"],
            page_count=story_data["page_count"],
            narrative_style=request.narrative_style,
            model_used=story_data.get("model_used", "unknown"),
            status=GenerationStatus.COMPLETED,
            credits_used=estimated_cost,
        )
        db.add(story)

        # Update project title if not set
        if not project.title or project.title == "Untitled":
            project.title = story_data["title"]

        # Create project pages
        for page_data in story_data["pages"]:
            page = ProjectPage(
                project_id=project_id,
                page_number=page_data["page_number"],
                story_text=page_data["text"],
                prompt=page_data["image_prompt"],
            )
            db.add(page)

        project.status = ProjectStatus.GENERATING
        await db.commit()
        await db.refresh(story)

        return StoryResponse(
            id=story.id,
            project_id=project_id,
            title=story_data["title"],
            pages=story_data["pages"],
            word_count=story_data["word_count"],
            page_count=story_data["page_count"],
            narrative_style=request.narrative_style,
            status=story.status.value,
            credits_used=estimated_cost,
            created_at=story.created_at,
        )

    except Exception as e:
        # Refund credits on failure
        await credits_service.add_credits(
            current_user.id, estimated_cost, f"Refund: story generation failed - {str(e)}"
        )
        raise HTTPException(status_code=500, detail=f"Story generation failed: {str(e)}")


# ============ Illustration Generation ============

@router.post("/illustration", response_model=IllustrationResponse)
async def generate_illustration(
    request: IllustrationGenerateRequest,
    project_id: int,
    page_id: int = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Generate an illustration using AI.

    Features:
    - Multiple art styles (60+)
    - Character Mat support for consistency
    - Various aspect ratios
    """
    # Verify project ownership
    result = await db.execute(
        select(Project).where(
            Project.id == project_id,
            Project.user_id == current_user.id,
        )
    )
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Check credits
    credits_service = CreditsService(db)
    estimated_cost = credits_service.estimate_operation_cost("illustration", count=1)

    success, message = await credits_service.check_and_deduct_credits(
        current_user.id, estimated_cost, "illustration_generation"
    )
    if not success:
        raise HTTPException(status_code=402, detail=message)

    # Get character description if using Character Mat
    character_description = None
    if request.use_character_mat and request.character_id:
        result = await db.execute(
            select(Character).where(
                Character.id == request.character_id,
                Character.project_id == project_id,
            )
        )
        character = result.scalar_one_or_none()
        if character:
            # Build character description from traits
            traits = character.traits or {}
            description_parts = [character.description] if character.description else []
            for key, value in traits.items():
                description_parts.append(f"{key}: {value}")
            character_description = ", ".join(description_parts)

    # Generate illustration
    illustration_service = IllustrationService()

    try:
        result_data = await illustration_service.generate_illustration(
            prompt=request.prompt,
            style_name=str(request.style_id) if request.style_id else None,
            aspect_ratio=request.aspect_ratio,
            character_description=character_description,
            seed=request.seed,
        )

        # Save illustration to database
        illustration = Illustration(
            project_id=project_id,
            page_id=page_id,
            prompt=request.prompt,
            negative_prompt=request.negative_prompt,
            style_id=request.style_id,
            character_id=request.character_id if request.use_character_mat else None,
            use_character_mat=request.use_character_mat,
            aspect_ratio=request.aspect_ratio,
            seed=request.seed,
            image_url=result_data["image_url"],
            width=result_data["width"],
            height=result_data["height"],
            model_used=result_data.get("model_used", "dall-e-3"),
            status=GenerationStatus.COMPLETED,
            credits_used=estimated_cost,
        )
        db.add(illustration)

        # Update page image if page_id provided
        if page_id:
            result = await db.execute(
                select(ProjectPage).where(ProjectPage.id == page_id)
            )
            page = result.scalar_one_or_none()
            if page:
                page.image_url = result_data["image_url"]

        await db.commit()
        await db.refresh(illustration)

        return IllustrationResponse(
            id=illustration.id,
            project_id=project_id,
            page_id=page_id,
            prompt=request.prompt,
            style_id=request.style_id,
            image_url=result_data["image_url"],
            thumbnail_url=result_data.get("thumbnail_url"),
            width=result_data["width"],
            height=result_data["height"],
            status=illustration.status.value,
            credits_used=estimated_cost,
            created_at=illustration.created_at,
        )

    except Exception as e:
        await credits_service.add_credits(
            current_user.id, estimated_cost, f"Refund: illustration generation failed - {str(e)}"
        )
        raise HTTPException(status_code=500, detail=f"Illustration generation failed: {str(e)}")


@router.post("/illustration/batch", response_model=List[IllustrationResponse])
async def generate_illustrations_batch(
    project_id: int,
    style_id: int = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    background_tasks: BackgroundTasks = None,
):
    """
    Generate illustrations for all pages in a project.

    This will generate images for each page based on their prompts.
    """
    # Verify project and get pages
    result = await db.execute(
        select(Project).where(
            Project.id == project_id,
            Project.user_id == current_user.id,
        )
    )
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    result = await db.execute(
        select(ProjectPage)
        .where(ProjectPage.project_id == project_id)
        .order_by(ProjectPage.page_number)
    )
    pages = result.scalars().all()

    if not pages:
        raise HTTPException(status_code=400, detail="No pages found in project")

    # Check credits
    credits_service = CreditsService(db)
    estimated_cost = credits_service.estimate_operation_cost("illustration", count=len(pages))

    success, message = await credits_service.check_and_deduct_credits(
        current_user.id, estimated_cost, "batch_illustration_generation"
    )
    if not success:
        raise HTTPException(status_code=402, detail=message)

    # Generate illustrations
    illustration_service = IllustrationService()
    prompts = [{"page_number": p.page_number, "prompt": p.prompt} for p in pages if p.prompt]

    try:
        results = await illustration_service.generate_batch(
            prompts=prompts,
            style_name=str(style_id) if style_id else None,
            aspect_ratio=project.aspect_ratio,
        )

        responses = []
        for result_data in results:
            if "error" not in result_data:
                illustration = Illustration(
                    project_id=project_id,
                    prompt=result_data.get("prompt", ""),
                    style_id=style_id,
                    aspect_ratio=project.aspect_ratio,
                    image_url=result_data["image_url"],
                    width=result_data["width"],
                    height=result_data["height"],
                    model_used=result_data.get("model_used", "dall-e-3"),
                    status=GenerationStatus.COMPLETED,
                    credits_used=estimated_cost // len(pages),
                )
                db.add(illustration)

                # Update page
                page_num = result_data["page_number"]
                for page in pages:
                    if page.page_number == page_num:
                        page.image_url = result_data["image_url"]
                        break

                responses.append(IllustrationResponse(
                    id=0,  # Will be updated after commit
                    project_id=project_id,
                    page_id=None,
                    prompt=result_data.get("prompt", ""),
                    style_id=style_id,
                    image_url=result_data["image_url"],
                    thumbnail_url=None,
                    width=result_data["width"],
                    height=result_data["height"],
                    status="completed",
                    credits_used=estimated_cost // len(pages),
                    created_at=illustration.created_at,
                ))

        await db.commit()
        return responses

    except Exception as e:
        await credits_service.add_credits(
            current_user.id, estimated_cost, f"Refund: batch generation failed - {str(e)}"
        )
        raise HTTPException(status_code=500, detail=f"Batch generation failed: {str(e)}")


# ============ ChatPS AI Image Editing ============

@router.post("/chatps", response_model=ChatPSEditResponse)
async def edit_image_with_chatps(
    request: ChatPSEditRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Edit an image using natural language instructions.

    Examples:
    - "Make the dragon's scales blue"
    - "Add a moon in the sky"
    - "Change the astronaut's helmet to silver"
    """
    credits_service = CreditsService(db)
    estimated_cost = credits_service.estimate_operation_cost("chatps")

    success, message = await credits_service.check_and_deduct_credits(
        current_user.id, estimated_cost, "chatps_edit"
    )
    if not success:
        raise HTTPException(status_code=402, detail=message)

    illustration_service = IllustrationService()

    try:
        result_data = await illustration_service.edit_with_chatps(
            image_url=request.image_url,
            instruction=request.instruction,
        )

        return ChatPSEditResponse(
            original_image_url=request.image_url,
            edited_image_url=result_data["edited_image_url"],
            instruction=request.instruction,
            credits_used=estimated_cost,
        )

    except Exception as e:
        await credits_service.add_credits(
            current_user.id, estimated_cost, f"Refund: ChatPS edit failed - {str(e)}"
        )
        raise HTTPException(status_code=500, detail=f"ChatPS edit failed: {str(e)}")


# ============ Audio/TTS Generation ============

@router.post("/audio", response_model=AudioResponse)
async def generate_audio(
    request: AudioGenerateRequest,
    project_id: int,
    page_id: int = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Generate audio/TTS for text.

    Features:
    - 180+ professional voices
    - Multiple languages
    - Speed and pitch control
    """
    # Verify project ownership
    result = await db.execute(
        select(Project).where(
            Project.id == project_id,
            Project.user_id == current_user.id,
        )
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Project not found")

    # Check credits
    credits_service = CreditsService(db)
    estimated_cost = credits_service.estimate_operation_cost(
        "tts", char_count=len(request.text)
    )

    success, message = await credits_service.check_and_deduct_credits(
        current_user.id, estimated_cost, "tts_generation"
    )
    if not success:
        raise HTTPException(status_code=402, detail=message)

    audio_service = AudioService()

    try:
        result_data = await audio_service.generate_speech(
            text=request.text,
            voice_id=request.voice_id,
            language=request.language,
            speed=request.speed,
        )

        # Save audio to database
        audio = Audio(
            project_id=project_id,
            page_id=page_id,
            text=request.text,
            voice_id=request.voice_id,
            language=request.language,
            speed=request.speed,
            audio_url=result_data.get("audio_url", ""),
            duration=result_data.get("duration", 0),
            format="mp3",
            model_used="elevenlabs",
            status=GenerationStatus.COMPLETED,
            credits_used=estimated_cost,
        )
        db.add(audio)

        # Update page audio if page_id provided
        if page_id:
            result = await db.execute(
                select(ProjectPage).where(ProjectPage.id == page_id)
            )
            page = result.scalar_one_or_none()
            if page:
                page.audio_url = result_data.get("audio_url", "")
                page.audio_duration = result_data.get("duration", 0)

        await db.commit()
        await db.refresh(audio)

        return AudioResponse(
            id=audio.id,
            project_id=project_id,
            page_id=page_id,
            audio_url=result_data.get("audio_url", ""),
            duration=result_data.get("duration", 0),
            voice_id=request.voice_id,
            status=audio.status.value,
            credits_used=estimated_cost,
            created_at=audio.created_at,
        )

    except Exception as e:
        await credits_service.add_credits(
            current_user.id, estimated_cost, f"Refund: audio generation failed - {str(e)}"
        )
        raise HTTPException(status_code=500, detail=f"Audio generation failed: {str(e)}")


# ============ Video Generation ============

@router.post("/video", response_model=VideoResponse)
async def generate_video(
    request: VideoGenerateRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Generate a video from a project.

    This combines all pages with:
    - Animations and transitions
    - TTS narration
    - Background music
    - Subtitles
    """
    # Verify project ownership and get pages
    result = await db.execute(
        select(Project).where(
            Project.id == request.project_id,
            Project.user_id == current_user.id,
        )
    )
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    result = await db.execute(
        select(ProjectPage)
        .where(ProjectPage.project_id == request.project_id)
        .order_by(ProjectPage.page_number)
    )
    pages = result.scalars().all()

    if not pages:
        raise HTTPException(status_code=400, detail="No pages found in project")

    # Check credits
    credits_service = CreditsService(db)
    has_narration = request.voice_id is not None
    estimated_cost = credits_service.estimate_operation_cost(
        "video", page_count=len(pages), has_narration=has_narration
    )

    success, message = await credits_service.check_and_deduct_credits(
        current_user.id, estimated_cost, "video_generation"
    )
    if not success:
        raise HTTPException(status_code=402, detail=message)

    # Create video record
    video = Video(
        project_id=request.project_id,
        resolution=request.resolution,
        animation_types=request.animation_types,
        transition_type=request.transition_type,
        has_subtitles=request.has_subtitles,
        subtitle_font=request.subtitle_font,
        font_effect=request.font_effect,
        voice_id=request.voice_id,
        background_music_id=request.background_music_id,
        has_narration=has_narration,
        status=GenerationStatus.PROCESSING,
        progress=0,
        credits_used=estimated_cost,
    )
    db.add(video)
    await db.commit()
    await db.refresh(video)

    # Start background video generation
    # In production, this would be handled by a task queue (Celery)
    # For now, we return immediately with processing status

    return VideoResponse(
        id=video.id,
        project_id=request.project_id,
        video_url=None,
        thumbnail_url=pages[0].image_url if pages else None,
        duration=None,
        resolution=request.resolution,
        status=video.status.value,
        progress=0,
        credits_used=estimated_cost,
        created_at=video.created_at,
    )


@router.get("/video/{video_id}/status", response_model=GenerationStatusResponse)
async def get_video_status(
    video_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get the status of a video generation task"""
    result = await db.execute(
        select(Video).where(Video.id == video_id)
    )
    video = result.scalar_one_or_none()

    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    # Verify project ownership
    result = await db.execute(
        select(Project).where(
            Project.id == video.project_id,
            Project.user_id == current_user.id,
        )
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Video not found")

    return GenerationStatusResponse(
        task_id=str(video.id),
        task_type="video",
        status=video.status.value,
        progress=video.progress,
        result_url=video.video_url,
        error_message=video.error_message,
        credits_used=video.credits_used,
    )


# ============ One-Click Video ============

@router.post("/one-click-video", response_model=GenerationStatusResponse)
async def one_click_video(
    request: OneClickVideoRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Generate a complete video from just a prompt.

    This one-click feature:
    1. Generates a story from the prompt
    2. Creates illustrations for each page
    3. Generates TTS narration
    4. Compiles everything into a video

    Processing time: 10-30 minutes
    """
    # Estimate total credits
    credits_service = CreditsService(db)
    story_cost = credits_service.estimate_operation_cost("story", page_count=request.page_count)
    illustration_cost = credits_service.estimate_operation_cost("illustration", count=request.page_count)
    video_cost = credits_service.estimate_operation_cost("video", page_count=request.page_count, has_narration=True)
    total_cost = story_cost + illustration_cost + video_cost

    # Check credits
    success, message = await credits_service.check_and_deduct_credits(
        current_user.id, total_cost, "one_click_video"
    )
    if not success:
        raise HTTPException(status_code=402, detail=message)

    # Create project
    project = Project(
        user_id=current_user.id,
        title="Generating...",
        project_type="video",
        status=ProjectStatus.GENERATING,
        target_age=request.target_age,
        language=request.language,
        style_id=request.style_id,
        has_narration=True,
        voice_id=request.voice_id,
        background_music_id=request.background_music_id,
    )
    db.add(project)
    await db.commit()
    await db.refresh(project)

    # In production, queue the full pipeline as a background task
    # For now, return processing status

    return GenerationStatusResponse(
        task_id=str(project.id),
        task_type="one_click_video",
        status="processing",
        progress=0,
        result_url=None,
        error_message=None,
        credits_used=total_cost,
    )
