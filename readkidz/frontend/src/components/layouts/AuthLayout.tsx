import { Outlet, Link } from 'react-router-dom'

export default function AuthLayout() {
  return (
    <div className="min-h-screen gradient-hero flex flex-col">
      {/* Header */}
      <header className="py-6 px-4">
        <Link to="/" className="flex items-center gap-2 w-fit mx-auto">
          <span className="text-3xl">📚</span>
          <span className="font-bold text-2xl text-primary-600">ReadKidz</span>
        </Link>
      </header>

      {/* Content */}
      <main className="flex-1 flex items-center justify-center px-4 py-8">
        <Outlet />
      </main>

      {/* Footer */}
      <footer className="py-6 px-4 text-center text-sm text-gray-500">
        <p>&copy; 2024 ReadKidz. All rights reserved.</p>
      </footer>
    </div>
  )
}
