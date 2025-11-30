import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  User,
  CreditCard,
  Bell,
  Shield,
  Globe,
  LogOut,
  Check,
  Crown,
} from 'lucide-react'
import { useAuthStore } from '@/contexts/authStore'
import { userApi, authApi } from '@/services/api'
import { clsx } from 'clsx'

type SettingsTab = 'profile' | 'subscription' | 'notifications' | 'security'

const languages = [
  { code: 'zh-TW', name: '繁體中文' },
  { code: 'zh-CN', name: '简体中文' },
  { code: 'en', name: 'English' },
  { code: 'ja', name: '日本語' },
  { code: 'ko', name: '한국어' },
]

const subscriptionTiers = [
  {
    id: 'free',
    name: '免費方案',
    price: 0,
    credits: 1500,
    features: ['每故事最多 5 頁', '2 個繪本模板', '6 種繪畫風格', '有浮水印'],
  },
  {
    id: 'standard',
    name: '標準方案',
    price: 10,
    credits: 12000,
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
    id: 'professional',
    name: '專業方案',
    price: 30,
    credits: 30000,
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

export default function SettingsPage() {
  const queryClient = useQueryClient()
  const { user, credits, logout } = useAuthStore()
  const [activeTab, setActiveTab] = useState<SettingsTab>('profile')
  const [profileData, setProfileData] = useState({
    display_name: user?.display_name || '',
    username: user?.username || '',
    language: user?.language || 'zh-TW',
  })

  const { data: subscription } = useQuery({
    queryKey: ['subscription'],
    queryFn: async () => {
      const response = await userApi.getSubscription()
      return response.data
    },
  })

  const updateProfileMutation = useMutation({
    mutationFn: (data: typeof profileData) => userApi.updateProfile(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['user'] })
    },
  })

  const tabs = [
    { id: 'profile' as SettingsTab, name: '個人資料', icon: User },
    { id: 'subscription' as SettingsTab, name: '訂閱方案', icon: CreditCard },
    { id: 'notifications' as SettingsTab, name: '通知設定', icon: Bell },
    { id: 'security' as SettingsTab, name: '安全設定', icon: Shield },
  ]

  return (
    <div className="max-w-4xl mx-auto">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">設定</h1>

      <div className="flex flex-col md:flex-row gap-6">
        {/* Sidebar */}
        <div className="md:w-48">
          <nav className="space-y-1">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={clsx(
                  'w-full flex items-center gap-3 px-4 py-2.5 rounded-lg text-left transition-colors',
                  activeTab === tab.id
                    ? 'bg-primary-50 text-primary-600 font-medium'
                    : 'text-gray-600 hover:bg-gray-100'
                )}
              >
                <tab.icon className="w-5 h-5" />
                {tab.name}
              </button>
            ))}
          </nav>
        </div>

        {/* Content */}
        <div className="flex-1">
          {activeTab === 'profile' && (
            <div className="card p-6 space-y-6">
              <h2 className="text-lg font-semibold text-gray-900">個人資料</h2>

              <div className="flex items-center gap-4">
                <div className="w-20 h-20 rounded-full bg-primary-100 flex items-center justify-center">
                  {user?.avatar_url ? (
                    <img
                      src={user.avatar_url}
                      alt=""
                      className="w-20 h-20 rounded-full"
                    />
                  ) : (
                    <User className="w-10 h-10 text-primary-600" />
                  )}
                </div>
                <div>
                  <button className="btn-outline text-sm">更換頭像</button>
                </div>
              </div>

              <div className="space-y-4">
                <div>
                  <label className="label">顯示名稱</label>
                  <input
                    type="text"
                    value={profileData.display_name}
                    onChange={(e) =>
                      setProfileData({ ...profileData, display_name: e.target.value })
                    }
                    className="input"
                  />
                </div>

                <div>
                  <label className="label">用戶名</label>
                  <input
                    type="text"
                    value={profileData.username}
                    onChange={(e) =>
                      setProfileData({ ...profileData, username: e.target.value })
                    }
                    className="input"
                  />
                </div>

                <div>
                  <label className="label">電子郵件</label>
                  <input
                    type="email"
                    value={user?.email || ''}
                    disabled
                    className="input bg-gray-50"
                  />
                </div>

                <div>
                  <label className="label flex items-center gap-2">
                    <Globe className="w-4 h-4" />
                    介面語言
                  </label>
                  <select
                    value={profileData.language}
                    onChange={(e) =>
                      setProfileData({ ...profileData, language: e.target.value })
                    }
                    className="input"
                  >
                    {languages.map((lang) => (
                      <option key={lang.code} value={lang.code}>
                        {lang.name}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              <div className="pt-4 border-t">
                <button
                  onClick={() => updateProfileMutation.mutate(profileData)}
                  disabled={updateProfileMutation.isPending}
                  className="btn-primary"
                >
                  {updateProfileMutation.isPending ? '儲存中...' : '儲存變更'}
                </button>
              </div>
            </div>
          )}

          {activeTab === 'subscription' && (
            <div className="space-y-6">
              {/* Current plan */}
              <div className="card p-6">
                <h2 className="text-lg font-semibold text-gray-900 mb-4">
                  目前方案
                </h2>
                <div className="flex items-center justify-between p-4 bg-primary-50 rounded-lg">
                  <div>
                    <div className="flex items-center gap-2">
                      <Crown className="w-5 h-5 text-primary-600" />
                      <span className="font-semibold text-gray-900 capitalize">
                        {subscription?.tier || credits?.subscription_tier || 'Free'} 方案
                      </span>
                    </div>
                    <p className="text-sm text-gray-600 mt-1">
                      剩餘積分：{credits?.balance?.toLocaleString() || 0}
                    </p>
                  </div>
                  {subscription?.expires_at && (
                    <div className="text-right text-sm text-gray-500">
                      到期日：
                      {new Date(subscription.expires_at).toLocaleDateString('zh-TW')}
                    </div>
                  )}
                </div>
              </div>

              {/* Available plans */}
              <div className="card p-6">
                <h2 className="text-lg font-semibold text-gray-900 mb-4">
                  升級方案
                </h2>
                <div className="grid gap-4">
                  {subscriptionTiers.map((tier) => (
                    <div
                      key={tier.id}
                      className={clsx(
                        'p-4 rounded-lg border',
                        tier.popular
                          ? 'border-primary-500 bg-primary-50'
                          : 'border-gray-200'
                      )}
                    >
                      <div className="flex items-start justify-between">
                        <div>
                          <div className="flex items-center gap-2">
                            <h3 className="font-semibold text-gray-900">
                              {tier.name}
                            </h3>
                            {tier.popular && (
                              <span className="badge-primary">最受歡迎</span>
                            )}
                          </div>
                          <p className="text-sm text-gray-600 mt-1">
                            {tier.credits.toLocaleString()} 積分
                          </p>
                          <ul className="mt-3 space-y-1">
                            {tier.features.map((feature) => (
                              <li
                                key={feature}
                                className="flex items-center gap-2 text-sm text-gray-600"
                              >
                                <Check className="w-4 h-4 text-green-500" />
                                {feature}
                              </li>
                            ))}
                          </ul>
                        </div>
                        <div className="text-right">
                          <div className="text-2xl font-bold text-gray-900">
                            ${tier.price}
                          </div>
                          <div className="text-sm text-gray-500">/月</div>
                          <button
                            className={clsx(
                              'mt-2',
                              tier.id === (subscription?.tier || 'free')
                                ? 'btn-outline'
                                : 'btn-primary'
                            )}
                            disabled={tier.id === (subscription?.tier || 'free')}
                          >
                            {tier.id === (subscription?.tier || 'free')
                              ? '目前方案'
                              : '升級'}
                          </button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {activeTab === 'notifications' && (
            <div className="card p-6 space-y-6">
              <h2 className="text-lg font-semibold text-gray-900">通知設定</h2>

              <div className="space-y-4">
                {[
                  { id: 'email_updates', label: '電子郵件更新', description: '接收產品更新和新功能通知' },
                  { id: 'project_complete', label: '作品完成通知', description: '當您的作品生成完成時通知您' },
                  { id: 'credits_low', label: '積分不足提醒', description: '當積分餘額過低時提醒您' },
                  { id: 'marketing', label: '行銷訊息', description: '接收優惠和促銷資訊' },
                ].map((item) => (
                  <div
                    key={item.id}
                    className="flex items-center justify-between p-4 bg-gray-50 rounded-lg"
                  >
                    <div>
                      <div className="font-medium text-gray-900">{item.label}</div>
                      <div className="text-sm text-gray-500">{item.description}</div>
                    </div>
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input type="checkbox" className="sr-only peer" defaultChecked />
                      <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
                    </label>
                  </div>
                ))}
              </div>
            </div>
          )}

          {activeTab === 'security' && (
            <div className="card p-6 space-y-6">
              <h2 className="text-lg font-semibold text-gray-900">安全設定</h2>

              <div className="space-y-4">
                <div className="p-4 bg-gray-50 rounded-lg">
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="font-medium text-gray-900">變更密碼</div>
                      <div className="text-sm text-gray-500">
                        定期更新密碼以保護您的帳號
                      </div>
                    </div>
                    <button className="btn-outline">變更</button>
                  </div>
                </div>

                <div className="p-4 bg-gray-50 rounded-lg">
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="font-medium text-gray-900">登入記錄</div>
                      <div className="text-sm text-gray-500">
                        查看最近的登入活動
                      </div>
                    </div>
                    <button className="btn-outline">查看</button>
                  </div>
                </div>

                <div className="p-4 bg-red-50 rounded-lg border border-red-200">
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="font-medium text-red-900">登出所有裝置</div>
                      <div className="text-sm text-red-600">
                        這將使所有裝置上的登入失效
                      </div>
                    </div>
                    <button
                      onClick={logout}
                      className="flex items-center gap-2 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
                    >
                      <LogOut className="w-4 h-4" />
                      登出
                    </button>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
