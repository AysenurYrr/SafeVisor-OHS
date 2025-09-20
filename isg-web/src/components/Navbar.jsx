import React from 'react'
import { useAuth } from '../context/AuthContext'

export default function Navbar({ onToggleSidebar }) {
  const { user, logout } = useAuth()
  
  const getRoleColor = (role) => {
    switch (role) {
      case 'Admin (IT)': return 'bg-purple-100 text-purple-800'
      case 'Manager': return 'bg-blue-100 text-blue-800'
      case 'AssistantManager': return 'bg-green-100 text-green-800'
      case 'HSEExpert': return 'bg-orange-100 text-orange-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  return (
    <header className="bg-white border-b border-gray-200 shadow-sm">
      <div className="container-app h-16 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <button 
            onClick={onToggleSidebar} 
            className="btn btn-secondary px-3 py-2 md:px-3 md:py-1 hover:bg-gray-100 transition-colors"
            aria-label="Toggle sidebar"
          >
            ☰
          </button>
          <div className="hidden sm:flex items-center gap-2">
            <span className="text-xl">🛡️</span>
            <span className="font-bold text-gray-800">SafeVisor</span>
            <span className="text-gray-500">- Occupational Health & Safety</span>
          </div>
        </div>
        
        <div className="flex items-center gap-4">
          {/* Notification bell - placeholder for future implementation */}
          <button className="relative p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors">
            🔔
            <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"></span>
          </button>
          
          <div className="flex items-center gap-3 pl-4 border-l border-gray-200">
            <div className="text-right hidden sm:block">
              <div className="text-sm font-medium text-gray-900">{user?.name}</div>
              <div className="text-xs text-gray-500">{user?.email}</div>
            </div>
            <span className={`badge ${getRoleColor(user?.role)}`}>
              {user?.role}
            </span>
            <button 
              className="btn btn-secondary text-sm hover:bg-red-50 hover:text-red-700 transition-colors" 
              onClick={logout}
            >
              Logout
            </button>
          </div>
        </div>
      </div>
    </header>
  )
}
