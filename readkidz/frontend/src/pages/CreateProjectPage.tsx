import { useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { useMutation } from '@tanstack/react-query'
import {
  Video,
  BookOpen,
  Music,
  Sparkles,
  ArrowRight,
  ArrowLeft,
  Wand2,
  Palette,
  Users,
} from 'lucide-react'
import { projectsApi, generateApi } from '@/services/api'
import { clsx } from 'clsx'

type ProjectMode = 'video' | 'book' | 'song'

const projectModes = [
  {
    id: 'video' as ProjectMode,
    icon: Video,
    title: '一鍵影片',
    description: '輸入想法，AI 自動生成故事影片',
    color: 'bg-primary-500',
  },
  {
    id: 'book' as ProjectMode,
    icon: BookOpen,
    title: '繪本創作',
    description: '完整控制每一頁的故事和插圖',
    color: 'bg-secondary-500',
  },
  {
    id: 'song' as ProjectMode,
    icon: Music,
    title: '兒童歌曲',
    description: 'AI 創作原創兒童歌曲',
    color: 'bg-accent-500',
  },
]

const narrativeStyles = [
  { id: 'warm', name: '溫馨', description: '溫暖感人的故事' },
  { id: 'humorous', name: '幽默', description: '有趣好笑的故事' },
  { id: 'adventure', name: '冒險', description: '刺激的冒險旅程' },
  { id: 'educational', name: '教育', description: '寓教於樂的內容' },
]

const ageRanges = [
  { id: '0-2', name: '0-2歲', description: '嬰幼兒' },
  { id: '3-5', name: '3-5歲', description: '學齡前' },
  { id: '6-8', name: '6-8歲', description: '低年級' },
  { id: '9-12', name: '9-12歲', description: '高年級' },
]

export default function CreateProjectPage() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()

  const initialMode = (searchParams.get('mode') as ProjectMode) || 'video'

  const [step, setStep] = useState(1)
  const [mode, setMode] = useState<ProjectMode>(initialMode)
  const [formData, setFormData] = useState({
    prompt: '',
    title: '',
    narrativeStyle: 'warm',
    ageRange: '3-5',
    pageCount: 12,
    language: 'zh-TW',
  })

  const createProjectMutation = useMutation({
    mutationFn: async () => {
      // Create project first
      const projectResponse = await projectsApi.create({
        title: formData.title || '新的故事',
        project_type: mode === 'video' ? 'video' : mode === 'song' ? 'song' : 'picture_book',
        target_age: formData.ageRange,
        language: formData.language,
      })

      const project = projectResponse.data

      if (mode === 'video') {
        // Use one-click video generation
        await generateApi.oneClickVideo({
          prompt: formData.prompt,
          page_count: formData.pageCount,
          target_age: formData.ageRange,
          language: formData.language,
        })
      } else {
        // Generate story for the project
        await generateApi.story(project.id, {
          prompt: formData.prompt,
          page_count: formData.pageCount,
          target_age: formData.ageRange,
          language: formData.language,
          narrative_style: formData.narrativeStyle,
        })
      }

      return project
    },
    onSuccess: (project) => {
      navigate(`/project/${project.id}`)
    },
  })

  const handleSubmit = () => {
    createProjectMutation.mutate()
  }

  const canProceed = () => {
    if (step === 1) return mode !== null
    if (step === 2) return formData.prompt.trim().length > 0
    if (step === 3) return true
    return false
  }

  return (
    <div className="max-w-3xl mx-auto">
      {/* Progress steps */}
      <div className="flex items-center justify-center mb-8">
        {[1, 2, 3].map((s) => (
          <div key={s} className="flex items-center">
            <div
              className={clsx(
                'stepper-number',
                step === s
                  ? 'stepper-number-active'
                  : step > s
                  ? 'stepper-number-completed'
                  : 'stepper-number-pending'
              )}
            >
              {step > s ? '✓' : s}
            </div>
            {s < 3 && (
              <div
                className={clsx(
                  'w-16 h-1 mx-2 rounded',
                  step > s ? 'bg-green-500' : 'bg-gray-200'
                )}
              />
            )}
          </div>
        ))}
      </div>

      {/* Step 1: Select mode */}
      {step === 1 && (
        <div className="animate-fade-in">
          <h1 className="text-2xl font-bold text-gray-900 text-center mb-2">
            選擇創作類型
          </h1>
          <p className="text-gray-600 text-center mb-8">
            選擇您想要創作的內容類型
          </p>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
            {projectModes.map((m) => (
              <button
                key={m.id}
                onClick={() => setMode(m.id)}
                className={clsx(
                  'card p-6 text-left transition-all',
                  mode === m.id
                    ? 'ring-2 ring-primary-500 border-primary-500'
                    : 'hover:shadow-lg'
                )}
              >
                <div
                  className={clsx(
                    'w-12 h-12 rounded-xl flex items-center justify-center mb-4',
                    m.color
                  )}
                >
                  <m.icon className="w-6 h-6 text-white" />
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-1">
                  {m.title}
                </h3>
                <p className="text-gray-600 text-sm">{m.description}</p>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Step 2: Enter prompt */}
      {step === 2 && (
        <div className="animate-fade-in">
          <h1 className="text-2xl font-bold text-gray-900 text-center mb-2">
            輸入您的故事想法
          </h1>
          <p className="text-gray-600 text-center mb-8">
            描述您想要創作的故事，AI 會幫您完成其餘的部分
          </p>

          <div className="card p-6 mb-6">
            <label className="label flex items-center gap-2">
              <Wand2 className="w-4 h-4 text-primary-500" />
              故事想法
            </label>
            <textarea
              value={formData.prompt}
              onChange={(e) => setFormData({ ...formData, prompt: e.target.value })}
              placeholder="例如：一隻勇敢的小兔子在森林裡尋找失落的胡蘿蔔，途中遇到了各種有趣的動物朋友..."
              className="input min-h-[120px] resize-none"
              rows={4}
            />
            <p className="text-sm text-gray-500 mt-2">
              提示：越詳細的描述，AI 越能理解您想要的故事風格
            </p>
          </div>

          {/* Quick prompts */}
          <div className="mb-6">
            <p className="text-sm font-medium text-gray-700 mb-2">快速選擇：</p>
            <div className="flex flex-wrap gap-2">
              {[
                '小恐龍學習分享的故事',
                '勇敢的公主拯救王國',
                '太空探險家的奇幻旅程',
                '友誼的魔法',
              ].map((prompt) => (
                <button
                  key={prompt}
                  onClick={() => setFormData({ ...formData, prompt })}
                  className="badge-secondary hover:bg-secondary-200 cursor-pointer"
                >
                  {prompt}
                </button>
              ))}
            </div>
          </div>

          {/* Optional title */}
          <div className="card p-6">
            <label className="label">故事標題（選填）</label>
            <input
              type="text"
              value={formData.title}
              onChange={(e) => setFormData({ ...formData, title: e.target.value })}
              placeholder="讓 AI 自動生成標題"
              className="input"
            />
          </div>
        </div>
      )}

      {/* Step 3: Settings */}
      {step === 3 && (
        <div className="animate-fade-in">
          <h1 className="text-2xl font-bold text-gray-900 text-center mb-2">
            設定故事參數
          </h1>
          <p className="text-gray-600 text-center mb-8">
            自定義您的故事設定
          </p>

          <div className="space-y-6">
            {/* Narrative style */}
            <div className="card p-6">
              <label className="label flex items-center gap-2 mb-4">
                <Palette className="w-4 h-4 text-primary-500" />
                敘事風格
              </label>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                {narrativeStyles.map((style) => (
                  <button
                    key={style.id}
                    onClick={() =>
                      setFormData({ ...formData, narrativeStyle: style.id })
                    }
                    className={clsx(
                      'p-3 rounded-lg border text-left transition-all',
                      formData.narrativeStyle === style.id
                        ? 'border-primary-500 bg-primary-50'
                        : 'border-gray-200 hover:border-gray-300'
                    )}
                  >
                    <div className="font-medium text-gray-900">{style.name}</div>
                    <div className="text-xs text-gray-500">{style.description}</div>
                  </button>
                ))}
              </div>
            </div>

            {/* Age range */}
            <div className="card p-6">
              <label className="label flex items-center gap-2 mb-4">
                <Users className="w-4 h-4 text-primary-500" />
                目標年齡
              </label>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                {ageRanges.map((age) => (
                  <button
                    key={age.id}
                    onClick={() => setFormData({ ...formData, ageRange: age.id })}
                    className={clsx(
                      'p-3 rounded-lg border text-left transition-all',
                      formData.ageRange === age.id
                        ? 'border-primary-500 bg-primary-50'
                        : 'border-gray-200 hover:border-gray-300'
                    )}
                  >
                    <div className="font-medium text-gray-900">{age.name}</div>
                    <div className="text-xs text-gray-500">{age.description}</div>
                  </button>
                ))}
              </div>
            </div>

            {/* Page count */}
            <div className="card p-6">
              <label className="label mb-4">頁數：{formData.pageCount} 頁</label>
              <input
                type="range"
                min="6"
                max="24"
                step="2"
                value={formData.pageCount}
                onChange={(e) =>
                  setFormData({ ...formData, pageCount: parseInt(e.target.value) })
                }
                className="w-full"
              />
              <div className="flex justify-between text-xs text-gray-500 mt-1">
                <span>6 頁</span>
                <span>24 頁</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Navigation buttons */}
      <div className="flex items-center justify-between mt-8">
        <button
          onClick={() => (step > 1 ? setStep(step - 1) : navigate('/dashboard'))}
          className="btn-outline flex items-center gap-2"
        >
          <ArrowLeft className="w-4 h-4" />
          {step > 1 ? '上一步' : '返回'}
        </button>

        {step < 3 ? (
          <button
            onClick={() => setStep(step + 1)}
            disabled={!canProceed()}
            className="btn-primary flex items-center gap-2"
          >
            下一步
            <ArrowRight className="w-4 h-4" />
          </button>
        ) : (
          <button
            onClick={handleSubmit}
            disabled={createProjectMutation.isPending}
            className="btn-primary flex items-center gap-2"
          >
            {createProjectMutation.isPending ? (
              <>
                <span className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                創建中...
              </>
            ) : (
              <>
                <Sparkles className="w-4 h-4" />
                開始創作
              </>
            )}
          </button>
        )}
      </div>

      {/* Error message */}
      {createProjectMutation.isError && (
        <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-600 text-sm">
          創建失敗，請稍後再試
        </div>
      )}
    </div>
  )
}
