import { useState } from 'react'
import { Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import {
  Plus,
  Search,
  Filter,
  Grid,
  List,
  Clock,
  MoreVertical,
  Trash2,
  Edit,
  Copy,
} from 'lucide-react'
import { projectsApi } from '@/services/api'
import type { ProjectListItem } from '@/types'
import { clsx } from 'clsx'

type ViewMode = 'grid' | 'list'
type FilterStatus = 'all' | 'draft' | 'generating' | 'completed' | 'published'

export default function MyProjectsPage() {
  const [viewMode, setViewMode] = useState<ViewMode>('grid')
  const [filterStatus, setFilterStatus] = useState<FilterStatus>('all')
  const [searchQuery, setSearchQuery] = useState('')

  const { data: projects, isLoading } = useQuery({
    queryKey: ['projects', filterStatus],
    queryFn: async () => {
      const params = filterStatus !== 'all' ? { status: filterStatus } : {}
      const response = await projectsApi.list(params)
      return response.data as ProjectListItem[]
    },
  })

  const filteredProjects = projects?.filter((project) =>
    project.title.toLowerCase().includes(searchQuery.toLowerCase())
  )

  const getStatusBadge = (status: string) => {
    const badges: Record<string, { class: string; text: string }> = {
      draft: { class: 'badge-secondary', text: '草稿' },
      generating: { class: 'badge-warning', text: '生成中' },
      completed: { class: 'badge-success', text: '已完成' },
      published: { class: 'badge-primary', text: '已發佈' },
      failed: { class: 'bg-red-100 text-red-700', text: '失敗' },
    }
    const badge = badges[status] || badges.draft
    return <span className={`badge ${badge.class}`}>{badge.text}</span>
  }

  const getProjectIcon = (type: string) => {
    switch (type) {
      case 'video':
        return '🎬'
      case 'song':
        return '🎵'
      default:
        return '📖'
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">我的作品</h1>
          <p className="text-gray-600">管理您的所有創作</p>
        </div>
        <Link to="/create" className="btn-primary flex items-center gap-2">
          <Plus className="w-5 h-5" />
          新建作品
        </Link>
      </div>

      {/* Filters and search */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
          <input
            type="text"
            placeholder="搜尋作品..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="input pl-10"
          />
        </div>
        <div className="flex items-center gap-2">
          <select
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value as FilterStatus)}
            className="input w-auto"
          >
            <option value="all">全部狀態</option>
            <option value="draft">草稿</option>
            <option value="generating">生成中</option>
            <option value="completed">已完成</option>
            <option value="published">已發佈</option>
          </select>
          <div className="flex items-center border border-gray-300 rounded-lg">
            <button
              onClick={() => setViewMode('grid')}
              className={clsx(
                'p-2 rounded-l-lg',
                viewMode === 'grid' ? 'bg-gray-100' : 'hover:bg-gray-50'
              )}
            >
              <Grid className="w-5 h-5" />
            </button>
            <button
              onClick={() => setViewMode('list')}
              className={clsx(
                'p-2 rounded-r-lg',
                viewMode === 'list' ? 'bg-gray-100' : 'hover:bg-gray-50'
              )}
            >
              <List className="w-5 h-5" />
            </button>
          </div>
        </div>
      </div>

      {/* Projects */}
      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {[1, 2, 3, 4, 5, 6].map((i) => (
            <div key={i} className="card p-4 animate-pulse">
              <div className="aspect-video bg-gray-200 rounded-lg mb-4"></div>
              <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
              <div className="h-3 bg-gray-200 rounded w-1/2"></div>
            </div>
          ))}
        </div>
      ) : filteredProjects && filteredProjects.length > 0 ? (
        viewMode === 'grid' ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {filteredProjects.map((project) => (
              <div key={project.id} className="card overflow-hidden group">
                <Link to={`/project/${project.id}`}>
                  <div className="aspect-video bg-gradient-to-br from-primary-100 to-secondary-100 relative">
                    {project.cover_image_url ? (
                      <img
                        src={project.cover_image_url}
                        alt={project.title}
                        className="w-full h-full object-cover"
                      />
                    ) : (
                      <div className="w-full h-full flex items-center justify-center">
                        <span className="text-5xl">{getProjectIcon(project.project_type)}</span>
                      </div>
                    )}
                    <div className="absolute inset-0 bg-black/0 group-hover:bg-black/20 transition-colors flex items-center justify-center opacity-0 group-hover:opacity-100">
                      <span className="bg-white px-4 py-2 rounded-lg font-medium">
                        編輯
                      </span>
                    </div>
                  </div>
                </Link>
                <div className="p-4">
                  <div className="flex items-start justify-between gap-2">
                    <div className="flex-1 min-w-0">
                      <h3 className="font-semibold text-gray-900 truncate">
                        {project.title}
                      </h3>
                      <div className="flex items-center gap-2 mt-1 text-sm text-gray-500">
                        <Clock className="w-4 h-4" />
                        {new Date(project.updated_at).toLocaleDateString('zh-TW')}
                      </div>
                    </div>
                    <div className="relative">
                      <button className="p-1 hover:bg-gray-100 rounded">
                        <MoreVertical className="w-4 h-4 text-gray-400" />
                      </button>
                    </div>
                  </div>
                  <div className="flex items-center gap-2 mt-3">
                    {getStatusBadge(project.status)}
                    <span className="text-sm text-gray-500">{project.page_count} 頁</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="card overflow-hidden">
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-left text-sm font-medium text-gray-500">
                    作品
                  </th>
                  <th className="px-4 py-3 text-left text-sm font-medium text-gray-500">
                    類型
                  </th>
                  <th className="px-4 py-3 text-left text-sm font-medium text-gray-500">
                    狀態
                  </th>
                  <th className="px-4 py-3 text-left text-sm font-medium text-gray-500">
                    頁數
                  </th>
                  <th className="px-4 py-3 text-left text-sm font-medium text-gray-500">
                    更新時間
                  </th>
                  <th className="px-4 py-3 text-right text-sm font-medium text-gray-500">
                    操作
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {filteredProjects.map((project) => (
                  <tr key={project.id} className="hover:bg-gray-50">
                    <td className="px-4 py-3">
                      <Link
                        to={`/project/${project.id}`}
                        className="flex items-center gap-3"
                      >
                        <div className="w-16 h-10 bg-gradient-to-br from-primary-100 to-secondary-100 rounded flex items-center justify-center flex-shrink-0">
                          {project.cover_image_url ? (
                            <img
                              src={project.cover_image_url}
                              alt=""
                              className="w-full h-full object-cover rounded"
                            />
                          ) : (
                            <span>{getProjectIcon(project.project_type)}</span>
                          )}
                        </div>
                        <span className="font-medium text-gray-900">
                          {project.title}
                        </span>
                      </Link>
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-500">
                      {project.project_type === 'video'
                        ? '影片'
                        : project.project_type === 'song'
                        ? '歌曲'
                        : '繪本'}
                    </td>
                    <td className="px-4 py-3">{getStatusBadge(project.status)}</td>
                    <td className="px-4 py-3 text-sm text-gray-500">
                      {project.page_count} 頁
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-500">
                      {new Date(project.updated_at).toLocaleDateString('zh-TW')}
                    </td>
                    <td className="px-4 py-3 text-right">
                      <div className="flex items-center justify-end gap-1">
                        <Link
                          to={`/project/${project.id}`}
                          className="p-2 hover:bg-gray-100 rounded"
                        >
                          <Edit className="w-4 h-4 text-gray-400" />
                        </Link>
                        <button className="p-2 hover:bg-gray-100 rounded">
                          <Copy className="w-4 h-4 text-gray-400" />
                        </button>
                        <button className="p-2 hover:bg-red-100 rounded">
                          <Trash2 className="w-4 h-4 text-red-400" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )
      ) : (
        <div className="card p-12 text-center">
          <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <Filter className="w-8 h-8 text-gray-400" />
          </div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">
            {searchQuery ? '沒有找到相關作品' : '還沒有作品'}
          </h3>
          <p className="text-gray-600 mb-4">
            {searchQuery ? '請嘗試其他搜尋關鍵字' : '開始您的第一個創作吧！'}
          </p>
          {!searchQuery && (
            <Link to="/create" className="btn-primary">
              開始創作
            </Link>
          )}
        </div>
      )}
    </div>
  )
}
