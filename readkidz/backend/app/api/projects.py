"""
ReadKidz Platform - Projects API Routes
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.database import get_db
from app.models.user import User
from app.models.project import Project, ProjectPage, Character, ProjectStatus, ProjectType
from app.schemas.project import (
    ProjectCreate, ProjectUpdate, ProjectResponse, ProjectListResponse,
    PageCreate, PageUpdate, PageResponse,
    CharacterCreate, CharacterUpdate, CharacterResponse,
)
from app.api.auth import get_current_user

router = APIRouter()


@router.get("/", response_model=List[ProjectListResponse])
async def list_projects(
    project_type: Optional[str] = Query(None, description="Filter by project type"),
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all projects for current user"""
    query = select(Project).where(Project.user_id == current_user.id)

    if project_type:
        query = query.where(Project.project_type == project_type)
    if status:
        query = query.where(Project.status == status)

    query = query.order_by(Project.updated_at.desc()).offset(offset).limit(limit)
    result = await db.execute(query)
    projects = result.scalars().all()

    # Get page counts for each project
    response = []
    for project in projects:
        page_count_result = await db.execute(
            select(func.count(ProjectPage.id)).where(ProjectPage.project_id == project.id)
        )
        page_count = page_count_result.scalar() or 0

        response.append(ProjectListResponse(
            id=project.id,
            title=project.title,
            project_type=project.project_type.value,
            status=project.status.value,
            cover_image_url=project.cover_image_url,
            page_count=page_count,
            created_at=project.created_at,
            updated_at=project.updated_at,
        ))

    return response


@router.post("/", response_model=ProjectResponse)
async def create_project(
    project_data: ProjectCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new project"""
    project = Project(
        user_id=current_user.id,
        title=project_data.title,
        description=project_data.description,
        project_type=ProjectType(project_data.project_type),
        status=ProjectStatus.DRAFT,
        target_age=project_data.target_age,
        language=project_data.language,
        style_id=project_data.style_id,
        aspect_ratio=project_data.aspect_ratio,
        has_narration=project_data.has_narration,
        voice_id=project_data.voice_id,
        background_music_id=project_data.background_music_id,
    )
    db.add(project)
    await db.commit()
    await db.refresh(project)

    return ProjectResponse.model_validate(project)


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a specific project"""
    result = await db.execute(
        select(Project).where(
            Project.id == project_id,
            Project.user_id == current_user.id,
        )
    )
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Load pages and characters
    pages_result = await db.execute(
        select(ProjectPage)
        .where(ProjectPage.project_id == project_id)
        .order_by(ProjectPage.page_number)
    )
    project.pages = pages_result.scalars().all()

    characters_result = await db.execute(
        select(Character).where(Character.project_id == project_id)
    )
    project.characters = characters_result.scalars().all()

    return ProjectResponse.model_validate(project)


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: int,
    update_data: ProjectUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a project"""
    result = await db.execute(
        select(Project).where(
            Project.id == project_id,
            Project.user_id == current_user.id,
        )
    )
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    update_dict = update_data.model_dump(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(project, field, value)

    await db.commit()
    await db.refresh(project)

    return ProjectResponse.model_validate(project)


@router.delete("/{project_id}")
async def delete_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a project"""
    result = await db.execute(
        select(Project).where(
            Project.id == project_id,
            Project.user_id == current_user.id,
        )
    )
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    await db.delete(project)
    await db.commit()

    return {"message": "Project deleted successfully"}


# Pages endpoints
@router.get("/{project_id}/pages", response_model=List[PageResponse])
async def list_pages(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all pages in a project"""
    # Verify project ownership
    result = await db.execute(
        select(Project).where(
            Project.id == project_id,
            Project.user_id == current_user.id,
        )
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Project not found")

    result = await db.execute(
        select(ProjectPage)
        .where(ProjectPage.project_id == project_id)
        .order_by(ProjectPage.page_number)
    )
    pages = result.scalars().all()

    return [PageResponse.model_validate(page) for page in pages]


@router.post("/{project_id}/pages", response_model=PageResponse)
async def create_page(
    project_id: int,
    page_data: PageCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new page in a project"""
    result = await db.execute(
        select(Project).where(
            Project.id == project_id,
            Project.user_id == current_user.id,
        )
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Project not found")

    page = ProjectPage(
        project_id=project_id,
        page_number=page_data.page_number,
        story_text=page_data.story_text,
        prompt=page_data.prompt,
    )
    db.add(page)
    await db.commit()
    await db.refresh(page)

    return PageResponse.model_validate(page)


@router.put("/{project_id}/pages/{page_number}", response_model=PageResponse)
async def update_page(
    project_id: int,
    page_number: int,
    update_data: PageUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a page"""
    # Verify project ownership
    result = await db.execute(
        select(Project).where(
            Project.id == project_id,
            Project.user_id == current_user.id,
        )
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Project not found")

    result = await db.execute(
        select(ProjectPage).where(
            ProjectPage.project_id == project_id,
            ProjectPage.page_number == page_number,
        )
    )
    page = result.scalar_one_or_none()

    if not page:
        raise HTTPException(status_code=404, detail="Page not found")

    update_dict = update_data.model_dump(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(page, field, value)

    await db.commit()
    await db.refresh(page)

    return PageResponse.model_validate(page)


# Characters endpoints
@router.get("/{project_id}/characters", response_model=List[CharacterResponse])
async def list_characters(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all characters in a project"""
    result = await db.execute(
        select(Project).where(
            Project.id == project_id,
            Project.user_id == current_user.id,
        )
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Project not found")

    result = await db.execute(
        select(Character).where(Character.project_id == project_id)
    )
    characters = result.scalars().all()

    return [CharacterResponse.model_validate(char) for char in characters]


@router.post("/{project_id}/characters", response_model=CharacterResponse)
async def create_character(
    project_id: int,
    character_data: CharacterCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new character (for Character Mat)"""
    result = await db.execute(
        select(Project).where(
            Project.id == project_id,
            Project.user_id == current_user.id,
        )
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Project not found")

    character = Character(
        project_id=project_id,
        name=character_data.name,
        description=character_data.description,
        reference_image_url=character_data.reference_image_url,
        similarity_score=character_data.similarity_score,
        traits=character_data.traits,
    )
    db.add(character)
    await db.commit()
    await db.refresh(character)

    return CharacterResponse.model_validate(character)


@router.put("/{project_id}/characters/{character_id}", response_model=CharacterResponse)
async def update_character(
    project_id: int,
    character_id: int,
    update_data: CharacterUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a character"""
    result = await db.execute(
        select(Project).where(
            Project.id == project_id,
            Project.user_id == current_user.id,
        )
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Project not found")

    result = await db.execute(
        select(Character).where(
            Character.id == character_id,
            Character.project_id == project_id,
        )
    )
    character = result.scalar_one_or_none()

    if not character:
        raise HTTPException(status_code=404, detail="Character not found")

    update_dict = update_data.model_dump(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(character, field, value)

    await db.commit()
    await db.refresh(character)

    return CharacterResponse.model_validate(character)


@router.delete("/{project_id}/characters/{character_id}")
async def delete_character(
    project_id: int,
    character_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a character"""
    result = await db.execute(
        select(Project).where(
            Project.id == project_id,
            Project.user_id == current_user.id,
        )
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Project not found")

    result = await db.execute(
        select(Character).where(
            Character.id == character_id,
            Character.project_id == project_id,
        )
    )
    character = result.scalar_one_or_none()

    if not character:
        raise HTTPException(status_code=404, detail="Character not found")

    await db.delete(character)
    await db.commit()

    return {"message": "Character deleted successfully"}
