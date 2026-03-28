import { Link, useLocation } from 'react-router-dom'
import { Ship, Upload, BarChart3, FileText } from 'lucide-react'

export default function Header() {
  const location = useLocation()

  const isActive = (path: string) => location.pathname === path

  return (
    <header className="bg-white shadow-sm border-b border-gray-200">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center gap-2">
            <Ship className="w-8 h-8 text-blue-600" />
            <span className="text-xl font-bold text-gray-900">ClearPath</span>
          </Link>

          {/* Navigation */}
          <nav className="flex items-center gap-6">
            <Link
              to="/"
              className={`flex items-center gap-2 px-3 py-2 rounded-lg transition ${
                isActive('/')
                  ? 'bg-blue-50 text-blue-600'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              <FileText className="w-5 h-5" />
              <span className="font-medium">Dashboard</span>
            </Link>

            <Link
              to="/upload"
              className={`flex items-center gap-2 px-3 py-2 rounded-lg transition ${
                isActive('/upload')
                  ? 'bg-blue-50 text-blue-600'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              <Upload className="w-5 h-5" />
              <span className="font-medium">Upload</span>
            </Link>

            <Link
              to="/analytics"
              className={`flex items-center gap-2 px-3 py-2 rounded-lg transition ${
                isActive('/analytics')
                  ? 'bg-blue-50 text-blue-600'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              <BarChart3 className="w-5 h-5" />
              <span className="font-medium">Analytics</span>
            </Link>
          </nav>

          {/* User Menu */}
          <div className="flex items-center gap-4">
            <button className="px-4 py-2 text-sm font-medium text-gray-700 hover:text-gray-900">
              Demo User
            </button>
          </div>
        </div>
      </div>
    </header>
  )
}
