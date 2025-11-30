import { useState } from 'react'
import { Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { Search, Filter, Palette, BookOpen } from 'lucide-react'
import { templatesApi } from '@/services/api'
import type { Template, Style } from '@/types'
import { clsx } from 'clsx'

type TabType = 'templates' | 'styles'

export default function TemplatesPage() {
  const [activeTab, setActiveTab] = useState<TabType>('templates')
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedCategory, setSelectedCategory] = useState<string>('all')

  const { data: templates, isLoading: templatesLoading } = useQuery({
    queryKey: ['templates', selectedCategory],
    queryFn: async () => {
      const params = selectedCategory !== 'all' ? { category: selectedCategory } : {}
      const response = await templatesApi.list(params)
      return response.data as Template[]
    },
    enabled: activeTab === 'templates',
  })

  const { data: styles, isLoading: stylesLoading } = useQuery({
    queryKey: ['styles'],
    queryFn: async () => {
      const response = await templatesApi.getStyles()
      return response.data as Style[]
    },
    enabled: activeTab === 'styles',
  })

  const { data: categories } = useQuery({
    queryKey: ['templateCategories'],
    queryFn: async () => {
      const response = await templatesApi.getCategories()
      return response.data.categories as { id: string; name: string }[]
    },
  })

  const isLoading = activeTab === 'templates' ? templatesLoading : stylesLoading

  const filteredItems =
    activeTab === 'templates'
      ? templates?.filter((t) =>
          t.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
          t.name_zh?.toLowerCase().includes(searchQuery.toLowerCase())
        )
      : styles?.filter((s) =>
          s.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
          s.name_zh?.toLowerCase().includes(searchQuery.toLowerCase())
        )

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">模板和風格庫</h1>
        <p className="text-gray-600">探索 100+ 故事模板和 60+ 繪畫風格</p>
      </div>

      {/* Tabs */}
      <div className="flex items-center gap-4 border-b border-gray-200">
        <button
          onClick={() => setActiveTab('templates')}
          className={clsx(
            'flex items-center gap-2 px-4 py-3 border-b-2 font-medium transition-colors',
            activeTab === 'templates'
              ? 'border-primary-500 text-primary-600'
              : 'border-transparent text-gray-500 hover:text-gray-700'
          )}
        >
          <BookOpen className="w-5 h-5" />
          故事模板
        </button>
        <button
          onClick={() => setActiveTab('styles')}
          className={clsx(
            'flex items-center gap-2 px-4 py-3 border-b-2 font-medium transition-colors',
            activeTab === 'styles'
              ? 'border-primary-500 text-primary-600'
              : 'border-transparent text-gray-500 hover:text-gray-700'
          )}
        >
          <Palette className="w-5 h-5" />
          繪畫風格
        </button>
      </div>

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
          <input
            type="text"
            placeholder={`搜尋${activeTab === 'templates' ? '模板' : '風格'}...`}
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="input pl-10"
          />
        </div>
        {activeTab === 'templates' && categories && (
          <select
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
            className="input w-auto"
          >
            <option value="all">全部分類</option>
            {categories.map((cat) => (
              <option key={cat.id} value={cat.id}>
                {cat.name}
              </option>
            ))}
          </select>
        )}
      </div>

      {/* Content */}
      {isLoading ? (
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          {[1, 2, 3, 4, 5, 6, 7, 8].map((i) => (
            <div key={i} className="card p-4 animate-pulse">
              <div className="aspect-square bg-gray-200 rounded-lg mb-4"></div>
              <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
              <div className="h-3 bg-gray-200 rounded w-1/2"></div>
            </div>
          ))}
        </div>
      ) : filteredItems && filteredItems.length > 0 ? (
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          {activeTab === 'templates'
            ? (filteredItems as Template[]).map((template) => (
                <Link
                  key={template.id}
                  to={`/create?template=${template.id}`}
                  className="card-hover overflow-hidden group"
                >
                  <div className="aspect-square bg-gradient-to-br from-primary-100 to-secondary-100 relative">
                    {template.thumbnail_url ? (
                      <img
                        src={template.thumbnail_url}
                        alt={template.name}
                        className="w-full h-full object-cover"
                      />
                    ) : (
                      <div className="w-full h-full flex items-center justify-center">
                        <BookOpen className="w-12 h-12 text-primary-300" />
                      </div>
                    )}
                    {template.is_free && (
                      <span className="absolute top-2 right-2 badge-success">免費</span>
                    )}
                    <div className="absolute inset-0 bg-black/0 group-hover:bg-black/20 transition-colors flex items-center justify-center opacity-0 group-hover:opacity-100">
                      <span className="bg-white px-4 py-2 rounded-lg font-medium">
                        使用此模板
                      </span>
                    </div>
                  </div>
                  <div className="p-4">
                    <h3 className="font-semibold text-gray-900">
                      {template.name_zh || template.name}
                    </h3>
                    <p className="text-sm text-gray-500 mt-1">
                      {template.page_count} 頁
                      {template.age_range && ` · ${template.age_range}歲`}
                    </p>
                    {template.tags && template.tags.length > 0 && (
                      <div className="flex flex-wrap gap-1 mt-2">
                        {template.tags.slice(0, 2).map((tag) => (
                          <span key={tag} className="badge-secondary text-xs">
                            {tag}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                </Link>
              ))
            : (filteredItems as Style[]).map((style) => (
                <div key={style.id} className="card-hover overflow-hidden">
                  <div className="aspect-square bg-gradient-to-br from-primary-100 to-secondary-100">
                    {style.thumbnail_url ? (
                      <img
                        src={style.thumbnail_url}
                        alt={style.name}
                        className="w-full h-full object-cover"
                      />
                    ) : (
                      <div className="w-full h-full flex items-center justify-center">
                        <Palette className="w-12 h-12 text-primary-300" />
                      </div>
                    )}
                  </div>
                  <div className="p-4">
                    <div className="flex items-center justify-between">
                      <h3 className="font-semibold text-gray-900">
                        {style.name_zh || style.name}
                      </h3>
                      {style.is_free && (
                        <span className="badge-success text-xs">免費</span>
                      )}
                    </div>
                    <p className="text-sm text-gray-500 mt-1 line-clamp-2">
                      {style.description_zh || style.description}
                    </p>
                  </div>
                </div>
              ))}
        </div>
      ) : (
        <div className="card p-12 text-center">
          <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <Filter className="w-8 h-8 text-gray-400" />
          </div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">
            沒有找到相關{activeTab === 'templates' ? '模板' : '風格'}
          </h3>
          <p className="text-gray-600">請嘗試其他搜尋關鍵字</p>
        </div>
      )}
    </div>
  )
}
