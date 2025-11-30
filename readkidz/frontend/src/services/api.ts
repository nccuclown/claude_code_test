import axios from 'axios'

const API_BASE_URL = '/api/v1'

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const authStorage = localStorage.getItem('auth-storage')
    if (authStorage) {
      try {
        const { state } = JSON.parse(authStorage)
        if (state.token) {
          config.headers.Authorization = `Bearer ${state.token}`
        }
      } catch (e) {
        console.error('Failed to parse auth storage:', e)
      }
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor to handle errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Clear auth storage and redirect to login
      localStorage.removeItem('auth-storage')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// API functions

// Auth
export const authApi = {
  login: (email: string, password: string) => {
    const formData = new URLSearchParams()
    formData.append('username', email)
    formData.append('password', password)
    return api.post('/auth/login', formData, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    })
  },
  register: (data: { email: string; password: string; username?: string }) =>
    api.post('/auth/register', data),
  getMe: () => api.get('/auth/me'),
  getCredits: () => api.get('/auth/me/credits'),
}

// Projects
export const projectsApi = {
  list: (params?: { project_type?: string; status?: string; limit?: number; offset?: number }) =>
    api.get('/projects', { params }),
  get: (id: number) => api.get(`/projects/${id}`),
  create: (data: {
    title: string
    description?: string
    project_type?: string
    target_age?: string
    language?: string
    style_id?: number
    aspect_ratio?: string
  }) => api.post('/projects', data),
  update: (id: number, data: Record<string, unknown>) => api.put(`/projects/${id}`, data),
  delete: (id: number) => api.delete(`/projects/${id}`),

  // Pages
  getPages: (projectId: number) => api.get(`/projects/${projectId}/pages`),
  createPage: (projectId: number, data: { page_number: number; story_text?: string; prompt?: string }) =>
    api.post(`/projects/${projectId}/pages`, data),
  updatePage: (projectId: number, pageNumber: number, data: Record<string, unknown>) =>
    api.put(`/projects/${projectId}/pages/${pageNumber}`, data),

  // Characters
  getCharacters: (projectId: number) => api.get(`/projects/${projectId}/characters`),
  createCharacter: (projectId: number, data: { name: string; description?: string; traits?: Record<string, string> }) =>
    api.post(`/projects/${projectId}/characters`, data),
  updateCharacter: (projectId: number, characterId: number, data: Record<string, unknown>) =>
    api.put(`/projects/${projectId}/characters/${characterId}`, data),
  deleteCharacter: (projectId: number, characterId: number) =>
    api.delete(`/projects/${projectId}/characters/${characterId}`),
}

// Generation
export const generateApi = {
  story: (projectId: number, data: {
    prompt: string
    mode?: string
    page_count?: number
    target_age?: string
    language?: string
    narrative_style?: string
  }) => api.post(`/generate/story?project_id=${projectId}`, data),

  illustration: (projectId: number, data: {
    prompt: string
    style_id?: number
    aspect_ratio?: string
    character_id?: number
    use_character_mat?: boolean
  }, pageId?: number) => {
    const params = new URLSearchParams({ project_id: projectId.toString() })
    if (pageId) params.append('page_id', pageId.toString())
    return api.post(`/generate/illustration?${params}`, data)
  },

  illustrationBatch: (projectId: number, styleId?: number) => {
    const params = new URLSearchParams({ project_id: projectId.toString() })
    if (styleId) params.append('style_id', styleId.toString())
    return api.post(`/generate/illustration/batch?${params}`)
  },

  video: (data: {
    project_id: number
    resolution?: string
    animation_types?: string[]
    transition_type?: string
    voice_id?: string
    background_music_id?: string
    has_subtitles?: boolean
  }) => api.post('/generate/video', data),

  videoStatus: (videoId: number) => api.get(`/generate/video/${videoId}/status`),

  audio: (projectId: number, data: {
    text: string
    voice_id: string
    language?: string
    speed?: number
  }, pageId?: number) => {
    const params = new URLSearchParams({ project_id: projectId.toString() })
    if (pageId) params.append('page_id', pageId.toString())
    return api.post(`/generate/audio?${params}`, data)
  },

  chatPS: (data: { image_url: string; instruction: string }) =>
    api.post('/generate/chatps', data),

  oneClickVideo: (data: {
    prompt: string
    style_id?: number
    voice_id?: string
    background_music_id?: string
    page_count?: number
    target_age?: string
    language?: string
  }) => api.post('/generate/one-click-video', data),
}

// Templates
export const templatesApi = {
  list: (params?: { category?: string; age_range?: string; is_free?: boolean; search?: string }) =>
    api.get('/templates', { params }),
  get: (id: number) => api.get(`/templates/${id}`),
  getCategories: () => api.get('/templates/categories'),

  // Styles
  getStyles: (params?: { category?: string; is_free?: boolean; search?: string }) =>
    api.get('/templates/styles', { params }),
  getStyleCategories: () => api.get('/templates/styles/categories'),

  // Voices
  getVoices: (params?: { language?: string; age_group?: string; gender?: string }) =>
    api.get('/templates/voices', { params }),
  getVoiceLanguages: () => api.get('/templates/voices/languages'),

  // Music
  getMusic: (params?: { mood?: string; genre?: string }) =>
    api.get('/templates/music', { params }),
  getMusicMoods: () => api.get('/templates/music/moods'),

  // Video options
  getVideoOptions: () => api.get('/templates/video-options'),

  // Prompts library
  getPrompts: () => api.get('/templates/prompts'),
}

// User
export const userApi = {
  getProfile: () => api.get('/users/profile'),
  updateProfile: (data: { username?: string; display_name?: string; language?: string }) =>
    api.put('/users/profile', data),
  getSubscription: () => api.get('/users/subscription'),
  getSettings: () => api.get('/users/settings'),
  updateSettings: (data: { language?: string; is_parent_account?: boolean }) =>
    api.put('/users/settings', data),
}
