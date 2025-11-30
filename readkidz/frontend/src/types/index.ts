// User types
export interface User {
  id: number
  email: string
  username: string | null
  display_name: string | null
  avatar_url: string | null
  language: string
  is_active: boolean
  is_verified: boolean
  is_parent_account: boolean
  created_at: string
}

export interface Credits {
  balance: number
  total_earned: number
  total_spent: number
  expires_at: string | null
  subscription_tier: string
}

export interface Subscription {
  tier: string
  started_at: string
  expires_at: string | null
  is_active: boolean
  max_pages_per_story: number
  max_concurrent_tasks: number
  has_watermark: boolean
  storage_days: number
}

// Project types
export type ProjectType = 'picture_book' | 'video' | 'song'
export type ProjectStatus = 'draft' | 'generating' | 'completed' | 'published' | 'failed'

export interface Project {
  id: number
  user_id: number
  title: string
  description: string | null
  project_type: ProjectType
  status: ProjectStatus
  target_age: string | null
  language: string
  style_id: number | null
  aspect_ratio: string
  has_narration: boolean
  voice_id: string | null
  background_music_id: string | null
  character_mat: Record<string, unknown> | null
  cover_image_url: string | null
  pdf_url: string | null
  video_url: string | null
  is_public: boolean
  youtube_url: string | null
  kdp_asin: string | null
  created_at: string
  updated_at: string
  pages: Page[]
  characters: Character[]
}

export interface ProjectListItem {
  id: number
  title: string
  project_type: ProjectType
  status: ProjectStatus
  cover_image_url: string | null
  page_count: number
  created_at: string
  updated_at: string
}

export interface Page {
  id: number
  project_id: number
  page_number: number
  story_text: string | null
  prompt: string | null
  image_url: string | null
  thumbnail_url: string | null
  audio_url: string | null
  audio_duration: number | null
  animation_type: string | null
  transition_type: string | null
  created_at: string
}

export interface Character {
  id: number
  project_id: number
  name: string
  description: string | null
  reference_image_url: string | null
  similarity_score: number
  traits: Record<string, string> | null
  created_at: string
}

// Template types
export interface Template {
  id: number
  name: string
  name_zh: string | null
  description: string | null
  description_zh: string | null
  category: string
  tags: string[]
  age_range: string | null
  page_count: number
  thumbnail_url: string | null
  preview_images: string[]
  is_free: boolean
  use_count: number
}

export interface Style {
  id: number
  name: string
  name_zh: string | null
  description: string | null
  description_zh: string | null
  category: string
  tags: string[]
  thumbnail_url: string | null
  sample_images: string[]
  is_free: boolean
  supported_ratios: string[]
  use_count: number
}

export interface Voice {
  id: number
  name: string
  name_zh: string | null
  description: string | null
  gender: string
  age_group: string
  language: string
  accent: string | null
  sample_audio_url: string | null
  is_child_voice: boolean
  is_free: boolean
}

export interface BackgroundMusic {
  id: number
  name: string
  name_zh: string | null
  description: string | null
  audio_url: string | null
  duration: number | null
  mood: string
  genre: string
  is_free: boolean
}

// Generation types
export interface StoryGenerateRequest {
  prompt: string
  mode: 'original' | 'adaptation'
  template_id?: number
  page_count: number
  target_age: string
  language: string
  narrative_style: string
}

export interface StoryPage {
  page_number: number
  text: string
  image_prompt: string
}

export interface StoryResponse {
  id: number
  project_id: number
  title: string
  pages: StoryPage[]
  word_count: number
  page_count: number
  narrative_style: string
  status: string
  credits_used: number
  created_at: string
}

export interface IllustrationGenerateRequest {
  prompt: string
  style_id?: number
  aspect_ratio: string
  character_id?: number
  use_character_mat: boolean
  negative_prompt?: string
  seed?: number
}

export interface GenerationStatus {
  task_id: string
  task_type: string
  status: 'pending' | 'processing' | 'completed' | 'failed'
  progress: number
  result_url: string | null
  error_message: string | null
  credits_used: number
}

// API response types
export interface TokenResponse {
  access_token: string
  token_type: string
  expires_in: number
  user: User
}

export interface ApiError {
  detail: string
}
