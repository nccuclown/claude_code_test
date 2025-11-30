import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import {
  BookOpen,
  Video,
  Music,
  Palette,
  Mic,
  Youtube,
  Sparkles,
  ArrowRight,
  Check,
} from 'lucide-react'

const features = [
  {
    icon: BookOpen,
    title: 'AI 故事生成',
    description: '輸入簡單提示詞，AI 自動生成完整兒童故事',
  },
  {
    icon: Palette,
    title: '60+ 繪畫風格',
    description: '從水彩到皮克斯風格，保持角色一致性',
  },
  {
    icon: Video,
    title: '一鍵影片製作',
    description: '將繪本自動轉換為動畫影片',
  },
  {
    icon: Mic,
    title: '180+ 配音選項',
    description: '專業配音讓故事更生動',
  },
  {
    icon: Music,
    title: '兒童歌曲創作',
    description: 'AI 生成適合兒童的原創歌曲',
  },
  {
    icon: Youtube,
    title: '一鍵發佈',
    description: '直接發佈至 YouTube 和 Amazon KDP',
  },
]

const pricingPlans = [
  {
    name: '免費方案',
    price: '0',
    credits: '1,500',
    features: [
      '每故事最多 5 頁',
      '2 個繪本模板',
      '6 種繪畫風格',
      '有浮水印',
    ],
  },
  {
    name: '標準方案',
    price: '10',
    credits: '12,000',
    features: [
      '每故事最多 40 頁',
      '100+ 繪本模板',
      '60+ 繪畫風格',
      '無浮水印',
      '4 個並行任務',
    ],
    popular: true,
  },
  {
    name: '專業方案',
    price: '30',
    credits: '30,000',
    features: [
      '每故事最多 50 頁',
      '100+ 繪本模板',
      '60+ 繪畫風格',
      '無浮水印',
      '5 個並行任務',
      '90 天資源儲存',
    ],
  },
]

export default function HomePage() {
  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="gradient-hero">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {/* Navigation */}
          <nav className="flex items-center justify-between mb-16">
            <Link to="/" className="flex items-center gap-2">
              <span className="text-3xl">📚</span>
              <span className="font-bold text-2xl text-primary-600">ReadKidz</span>
            </Link>
            <div className="flex items-center gap-4">
              <Link to="/login" className="btn-ghost">
                登入
              </Link>
              <Link to="/login" className="btn-primary">
                免費開始
              </Link>
            </div>
          </nav>

          {/* Hero Content */}
          <div className="text-center max-w-4xl mx-auto">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
            >
              <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-gray-900 mb-6">
                AI 驅動的
                <span className="text-primary-500"> 兒童故事 </span>
                創作平台
              </h1>
              <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
                從構思到發佈，僅需數分鐘。創建電子繪本、故事影片和兒童歌曲。
                無需繪畫、寫作或影片製作技能。
              </p>
              <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
                <Link
                  to="/login"
                  className="btn-primary text-lg px-8 py-3 flex items-center gap-2"
                >
                  <Sparkles className="w-5 h-5" />
                  免費開始創作
                </Link>
                <Link
                  to="/login"
                  className="btn-outline text-lg px-8 py-3 flex items-center gap-2"
                >
                  觀看演示
                  <ArrowRight className="w-5 h-5" />
                </Link>
              </div>
            </motion.div>

            {/* Preview Image */}
            <motion.div
              initial={{ opacity: 0, y: 40 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.2 }}
              className="mt-16"
            >
              <div className="bg-white rounded-2xl shadow-2xl p-4 max-w-4xl mx-auto">
                <div className="aspect-video bg-gradient-to-br from-primary-100 to-secondary-100 rounded-xl flex items-center justify-center">
                  <div className="text-center">
                    <span className="text-6xl">📖</span>
                    <p className="mt-4 text-gray-600">平台預覽圖</p>
                  </div>
                </div>
              </div>
            </motion.div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              一站式兒童內容創作
            </h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              ReadKidz 提供完整的 AI 創作工具，讓每個人都能成為故事創作者
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature, index) => (
              <motion.div
                key={feature.title}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
                viewport={{ once: true }}
                className="card p-6 hover:shadow-lg transition-shadow"
              >
                <div className="w-12 h-12 bg-primary-100 rounded-xl flex items-center justify-center mb-4">
                  <feature.icon className="w-6 h-6 text-primary-600" />
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-2">
                  {feature.title}
                </h3>
                <p className="text-gray-600">{feature.description}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Character Mat Feature */}
      <section className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div>
              <h2 className="text-3xl font-bold text-gray-900 mb-4">
                角色一致性技術
              </h2>
              <p className="text-xl text-gray-600 mb-6">
                獨家 Character Mat 技術，確保您的角色在每一頁都保持相同的外觀。
                上傳參考圖像，調整相似度，享受一致的視覺體驗。
              </p>
              <ul className="space-y-3">
                {[
                  '上傳角色肖像作為參考',
                  '可調整相似度參數',
                  '全書角色外觀統一',
                  '支援多種繪畫風格',
                ].map((item) => (
                  <li key={item} className="flex items-center gap-2">
                    <Check className="w-5 h-5 text-green-500" />
                    <span className="text-gray-700">{item}</span>
                  </li>
                ))}
              </ul>
            </div>
            <div className="bg-white rounded-2xl shadow-lg p-6">
              <div className="aspect-square bg-gradient-to-br from-primary-50 to-secondary-50 rounded-xl flex items-center justify-center">
                <div className="text-center">
                  <span className="text-6xl">🎨</span>
                  <p className="mt-4 text-gray-600">Character Mat 演示</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Pricing Section */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              選擇適合您的方案
            </h2>
            <p className="text-xl text-gray-600">
              從免費方案開始，隨時升級獲得更多功能
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
            {pricingPlans.map((plan) => (
              <div
                key={plan.name}
                className={`card p-6 ${
                  plan.popular
                    ? 'ring-2 ring-primary-500 relative'
                    : ''
                }`}
              >
                {plan.popular && (
                  <div className="absolute -top-3 left-1/2 -translate-x-1/2">
                    <span className="badge-primary">最受歡迎</span>
                  </div>
                )}
                <h3 className="text-xl font-semibold text-gray-900 mb-2">
                  {plan.name}
                </h3>
                <div className="mb-4">
                  <span className="text-4xl font-bold">${plan.price}</span>
                  <span className="text-gray-500">/月</span>
                </div>
                <div className="text-sm text-gray-600 mb-6">
                  {plan.credits} 積分
                </div>
                <ul className="space-y-2 mb-6">
                  {plan.features.map((feature) => (
                    <li key={feature} className="flex items-center gap-2 text-sm">
                      <Check className="w-4 h-4 text-green-500" />
                      <span>{feature}</span>
                    </li>
                  ))}
                </ul>
                <Link
                  to="/login"
                  className={`w-full ${
                    plan.popular ? 'btn-primary' : 'btn-outline'
                  }`}
                >
                  開始使用
                </Link>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 gradient-primary text-white">
        <div className="max-w-4xl mx-auto px-4 text-center">
          <h2 className="text-3xl font-bold mb-4">
            準備好開始創作了嗎？
          </h2>
          <p className="text-xl opacity-90 mb-8">
            立即註冊，獲得 1,500 免費積分，開始您的創作之旅
          </p>
          <Link
            to="/login"
            className="inline-flex items-center gap-2 bg-white text-primary-600 font-semibold px-8 py-3 rounded-lg hover:bg-gray-100 transition-colors"
          >
            <Sparkles className="w-5 h-5" />
            免費開始
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-gray-400 py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col md:flex-row items-center justify-between">
            <div className="flex items-center gap-2 mb-4 md:mb-0">
              <span className="text-2xl">📚</span>
              <span className="font-bold text-xl text-white">ReadKidz</span>
            </div>
            <div className="text-sm">
              &copy; 2024 ReadKidz. All rights reserved.
            </div>
          </div>
        </div>
      </footer>
    </div>
  )
}
