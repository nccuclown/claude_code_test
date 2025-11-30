import { Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import {
  Video,
  BookOpen,
  Music,
  Sparkles,
  ArrowRight,
  Clock,
  TrendingUp,
} from 'lucide-react'
import { projectsApi } from '@/services/api'
import { useAuthStore } from '@/contexts/authStore'
import type { ProjectListItem } from '@/types'

const quickActions = [
  {
    icon: Video,
    title: '一鍵生成影片',
    description: '輸入想法，AI 自動生成完整故事影片',
    href: '/create?mode=video',
    color: 'bg-primary-500',
  },
  {
    icon: BookOpen,
    title: '創建繪本',
    description: '從故事構思到插圖，一站式完成',
    href: '/create?mode=book',
    color: 'bg-secondary-500',
  },
  {
    icon: Music,
    title: '兒童歌曲',
    description: 'AI 創作適合兒童的原創歌曲',
    href: '/create?mode=song',
    color: 'bg-accent-500',
  },
]

export default function DashboardPage() {
  const { user, credits } = useAuthStore()

  const { data: recentProjects, isLoading } = useQuery({
    queryKey: ['projects', 'recent'],
    queryFn: async () => {
      const response = await projectsApi.list({ limit: 6 })
      return response.data as ProjectListItem[]
    },
  })

  return (
    <div className="space-y-8">
      {/* Welcome section */}
      <div className="bg-gradient-to-r from-primary-500 to-secondary-500 rounded-2xl p-6 md:p-8 text-white">
        <h1 className="text-2xl md:text-3xl font-bold mb-2">
          歡迎回來，{user?.display_name || user?.username || '創作者'}！
        </h1>
        <p className="text-white/90 mb-4">
          準備好創作新的兒童故事了嗎？
        </p>
        <div className="flex flex-wrap gap-4">
          <div className="bg-white/20 rounded-lg px-4 py-2">
            <div className="text-sm opacity-90">可用積分</div>
            <div className="text-xl font-bold">
              {credits?.balance?.toLocaleString() || 0}
            </div>
          </div>
          <div className="bg-white/20 rounded-lg px-4 py-2">
            <div className="text-sm opacity-90">方案</div>
            <div className="text-xl font-bold capitalize">
              {credits?.subscription_tier || 'Free'}
            </div>
          </div>
        </div>
      </div>

      {/* Quick actions */}
      <div>
        <h2 className="text-xl font-semibold text-gray-900 mb-4">
          開始創作
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {quickActions.map((action) => (
            <Link
              key={action.title}
              to={action.href}
              className="card-hover p-6 flex flex-col"
            >
              <div
                className={`w-12 h-12 ${action.color} rounded-xl flex items-center justify-center mb-4`}
              >
                <action.icon className="w-6 h-6 text-white" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-1">
                {action.title}
              </h3>
              <p className="text-gray-600 text-sm flex-1">
                {action.description}
              </p>
              <div className="flex items-center gap-1 mt-4 text-primary-600 text-sm font-medium">
                開始創作
                <ArrowRight className="w-4 h-4" />
              </div>
            </Link>
          ))}
        </div>
      </div>

      {/* Recent projects */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold text-gray-900">
            最近的作品
          </h2>
          <Link
            to="/my-projects"
            className="text-primary-600 text-sm font-medium hover:text-primary-700 flex items-center gap-1"
          >
            查看全部
            <ArrowRight className="w-4 h-4" />
          </Link>
        </div>

        {isLoading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {[1, 2, 3].map((i) => (
              <div key={i} className="card p-4 animate-pulse">
                <div className="aspect-video bg-gray-200 rounded-lg mb-4"></div>
                <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
                <div className="h-3 bg-gray-200 rounded w-1/2"></div>
              </div>
            ))}
          </div>
        ) : recentProjects && recentProjects.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {recentProjects.map((project) => (
              <Link
                key={project.id}
                to={`/project/${project.id}`}
                className="card-hover overflow-hidden"
              >
                <div className="aspect-video bg-gradient-to-br from-primary-100 to-secondary-100 flex items-center justify-center">
                  {project.cover_image_url ? (
                    <img
                      src={project.cover_image_url}
                      alt={project.title}
                      className="w-full h-full object-cover"
                    />
                  ) : (
                    <span className="text-4xl">
                      {project.project_type === 'video' ? '🎬' : project.project_type === 'song' ? '🎵' : '📖'}
                    </span>
                  )}
                </div>
                <div className="p-4">
                  <h3 className="font-semibold text-gray-900 truncate">
                    {project.title}
                  </h3>
                  <div className="flex items-center gap-4 mt-2 text-sm text-gray-500">
                    <span className="flex items-center gap-1">
                      <Clock className="w-4 h-4" />
                      {new Date(project.updated_at).toLocaleDateString('zh-TW')}
                    </span>
                    <span className="badge-secondary">
                      {project.page_count} 頁
                    </span>
                  </div>
                  <div className="mt-2">
                    <span
                      className={`badge ${
                        project.status === 'completed'
                          ? 'badge-success'
                          : project.status === 'generating'
                          ? 'badge-warning'
                          : 'badge-secondary'
                      }`}
                    >
                      {project.status === 'completed'
                        ? '已完成'
                        : project.status === 'generating'
                        ? '生成中'
                        : project.status === 'draft'
                        ? '草稿'
                        : project.status}
                    </span>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        ) : (
          <div className="card p-12 text-center">
            <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <Sparkles className="w-8 h-8 text-gray-400" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              還沒有作品
            </h3>
            <p className="text-gray-600 mb-4">
              開始您的第一個創作吧！
            </p>
            <Link to="/create" className="btn-primary">
              開始創作
            </Link>
          </div>
        )}
      </div>

      {/* Tips section */}
      <div className="card p-6 bg-gradient-to-r from-primary-50 to-secondary-50">
        <div className="flex items-start gap-4">
          <div className="w-10 h-10 bg-primary-100 rounded-lg flex items-center justify-center flex-shrink-0">
            <TrendingUp className="w-5 h-5 text-primary-600" />
          </div>
          <div>
            <h3 className="font-semibold text-gray-900 mb-1">創作小技巧</h3>
            <p className="text-gray-600 text-sm">
              使用「Character Mat」功能可以確保您的角色在每一頁都保持一致的外觀。
              只需上傳一張角色參考圖，AI 就會自動在所有插圖中保持角色的特徵！
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
