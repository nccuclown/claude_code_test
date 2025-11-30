import { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  ArrowLeft,
  Play,
  Download,
  Share2,
  Settings,
  Palette,
  Mic,
  Music,
  Wand2,
  RefreshCw,
  Plus,
  Trash2,
  ChevronLeft,
  ChevronRight,
} from 'lucide-react'
import { projectsApi, generateApi } from '@/services/api'
import type { Project, Page } from '@/types'
import { clsx } from 'clsx'

export default function ProjectEditorPage() {
  const { projectId } = useParams<{ projectId: string }>()
  const navigate = useNavigate()
  const queryClient = useQueryClient()

  const [selectedPage, setSelectedPage] = useState(0)
  const [isGenerating, setIsGenerating] = useState(false)

  const { data: project, isLoading } = useQuery({
    queryKey: ['project', projectId],
    queryFn: async () => {
      const response = await projectsApi.get(parseInt(projectId!))
      return response.data as Project
    },
    enabled: !!projectId,
  })

  const regenerateImageMutation = useMutation({
    mutationFn: async (pageId: number) => {
      const page = project?.pages.find((p) => p.id === pageId)
      if (!page?.prompt) throw new Error('No prompt')

      return generateApi.illustration(
        parseInt(projectId!),
        {
          prompt: page.prompt,
          aspect_ratio: project?.aspect_ratio || '16:9',
        },
        pageId
      )
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['project', projectId] })
    },
  })

  const generateAllImagesMutation = useMutation({
    mutationFn: async () => {
      setIsGenerating(true)
      return generateApi.illustrationBatch(
        parseInt(projectId!),
        project?.style_id || undefined
      )
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['project', projectId] })
      setIsGenerating(false)
    },
    onError: () => {
      setIsGenerating(false)
    },
  })

  const generateVideoMutation = useMutation({
    mutationFn: async () => {
      return generateApi.video({
        project_id: parseInt(projectId!),
        voice_id: project?.voice_id || undefined,
        background_music_id: project?.background_music_id || undefined,
      })
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['project', projectId] })
    },
  })

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-500"></div>
      </div>
    )
  }

  if (!project) {
    return (
      <div className="text-center py-12">
        <h2 className="text-xl font-semibold text-gray-900 mb-2">找不到專案</h2>
        <button onClick={() => navigate('/my-projects')} className="btn-primary">
          返回我的作品
        </button>
      </div>
    )
  }

  const currentPage = project.pages[selectedPage]

  return (
    <div className="min-h-screen -m-4 lg:-m-6 bg-gray-100">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 px-4 py-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <button
              onClick={() => navigate('/my-projects')}
              className="p-2 hover:bg-gray-100 rounded-lg"
            >
              <ArrowLeft className="w-5 h-5" />
            </button>
            <div>
              <h1 className="font-semibold text-gray-900">{project.title}</h1>
              <p className="text-sm text-gray-500">
                {project.pages.length} 頁 · {project.status === 'completed' ? '已完成' : '編輯中'}
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button className="btn-ghost flex items-center gap-2">
              <Settings className="w-4 h-4" />
              <span className="hidden sm:inline">設定</span>
            </button>
            <button className="btn-ghost flex items-center gap-2">
              <Share2 className="w-4 h-4" />
              <span className="hidden sm:inline">分享</span>
            </button>
            {project.video_url ? (
              <a
                href={project.video_url}
                download
                className="btn-primary flex items-center gap-2"
              >
                <Download className="w-4 h-4" />
                下載影片
              </a>
            ) : (
              <button
                onClick={() => generateVideoMutation.mutate()}
                disabled={generateVideoMutation.isPending}
                className="btn-primary flex items-center gap-2"
              >
                {generateVideoMutation.isPending ? (
                  <>
                    <span className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                    生成中...
                  </>
                ) : (
                  <>
                    <Play className="w-4 h-4" />
                    生成影片
                  </>
                )}
              </button>
            )}
          </div>
        </div>
      </header>

      <div className="flex h-[calc(100vh-60px)]">
        {/* Pages sidebar */}
        <div className="w-64 bg-white border-r border-gray-200 overflow-y-auto">
          <div className="p-4">
            <div className="flex items-center justify-between mb-4">
              <h2 className="font-semibold text-gray-900">頁面</h2>
              <button
                onClick={() => generateAllImagesMutation.mutate()}
                disabled={isGenerating}
                className="btn-ghost text-sm flex items-center gap-1"
              >
                <Wand2 className="w-4 h-4" />
                全部生成
              </button>
            </div>
            <div className="space-y-2">
              {project.pages.map((page, index) => (
                <button
                  key={page.id}
                  onClick={() => setSelectedPage(index)}
                  className={clsx(
                    'w-full p-2 rounded-lg text-left transition-all',
                    selectedPage === index
                      ? 'bg-primary-50 ring-2 ring-primary-500'
                      : 'hover:bg-gray-50'
                  )}
                >
                  <div className="aspect-video bg-gray-100 rounded mb-2 overflow-hidden">
                    {page.image_url ? (
                      <img
                        src={page.image_url}
                        alt={`Page ${page.page_number}`}
                        className="w-full h-full object-cover"
                      />
                    ) : (
                      <div className="w-full h-full flex items-center justify-center text-gray-400 text-xs">
                        待生成
                      </div>
                    )}
                  </div>
                  <div className="text-xs text-gray-500">第 {page.page_number} 頁</div>
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Main editor area */}
        <div className="flex-1 flex flex-col">
          {/* Canvas */}
          <div className="flex-1 p-6 flex items-center justify-center bg-gray-100">
            <div className="bg-white rounded-xl shadow-lg overflow-hidden max-w-4xl w-full">
              {currentPage?.image_url ? (
                <img
                  src={currentPage.image_url}
                  alt={`Page ${currentPage.page_number}`}
                  className="w-full aspect-video object-cover"
                />
              ) : (
                <div className="w-full aspect-video bg-gradient-to-br from-gray-100 to-gray-200 flex items-center justify-center">
                  <div className="text-center">
                    <Palette className="w-12 h-12 text-gray-400 mx-auto mb-2" />
                    <p className="text-gray-500">點擊下方按鈕生成插圖</p>
                  </div>
                </div>
              )}
              {/* Story text overlay */}
              {currentPage?.story_text && (
                <div className="p-6 bg-white border-t">
                  <p className="text-lg text-gray-800 leading-relaxed">
                    {currentPage.story_text}
                  </p>
                </div>
              )}
            </div>
          </div>

          {/* Page navigation */}
          <div className="flex items-center justify-center gap-4 py-4 bg-white border-t">
            <button
              onClick={() => setSelectedPage(Math.max(0, selectedPage - 1))}
              disabled={selectedPage === 0}
              className="btn-ghost"
            >
              <ChevronLeft className="w-5 h-5" />
            </button>
            <span className="text-sm text-gray-600">
              {selectedPage + 1} / {project.pages.length}
            </span>
            <button
              onClick={() =>
                setSelectedPage(Math.min(project.pages.length - 1, selectedPage + 1))
              }
              disabled={selectedPage === project.pages.length - 1}
              className="btn-ghost"
            >
              <ChevronRight className="w-5 h-5" />
            </button>
          </div>

          {/* Action bar */}
          <div className="bg-white border-t border-gray-200 p-4">
            <div className="flex items-center justify-between max-w-4xl mx-auto">
              <div className="flex items-center gap-2">
                <button
                  onClick={() => currentPage && regenerateImageMutation.mutate(currentPage.id)}
                  disabled={regenerateImageMutation.isPending}
                  className="btn-outline flex items-center gap-2"
                >
                  {regenerateImageMutation.isPending ? (
                    <span className="w-4 h-4 border-2 border-primary-500 border-t-transparent rounded-full animate-spin" />
                  ) : (
                    <RefreshCw className="w-4 h-4" />
                  )}
                  重新生成圖片
                </button>
                <button className="btn-outline flex items-center gap-2">
                  <Palette className="w-4 h-4" />
                  編輯風格
                </button>
              </div>
              <div className="flex items-center gap-2">
                <button className="btn-ghost flex items-center gap-2">
                  <Mic className="w-4 h-4" />
                  配音
                </button>
                <button className="btn-ghost flex items-center gap-2">
                  <Music className="w-4 h-4" />
                  背景音樂
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Right panel - Page details */}
        <div className="w-80 bg-white border-l border-gray-200 overflow-y-auto p-4">
          <h3 className="font-semibold text-gray-900 mb-4">頁面詳情</h3>

          {currentPage && (
            <div className="space-y-4">
              <div>
                <label className="label">故事文字</label>
                <textarea
                  value={currentPage.story_text || ''}
                  className="input min-h-[100px] resize-none"
                  readOnly
                />
              </div>

              <div>
                <label className="label">圖像提示詞</label>
                <textarea
                  value={currentPage.prompt || ''}
                  className="input min-h-[100px] resize-none text-sm"
                  readOnly
                />
              </div>

              {currentPage.audio_url && (
                <div>
                  <label className="label">配音</label>
                  <audio controls className="w-full">
                    <source src={currentPage.audio_url} type="audio/mpeg" />
                  </audio>
                </div>
              )}

              <div>
                <label className="label">動畫效果</label>
                <select className="input">
                  <option value="zoom_in">緩慢放大</option>
                  <option value="pan_left">向左平移</option>
                  <option value="pan_right">向右平移</option>
                  <option value="static">靜態</option>
                </select>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
