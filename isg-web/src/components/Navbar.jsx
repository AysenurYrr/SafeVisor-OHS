import React from 'react'
import { useAuth } from '../context/AuthContext'
import Icon from './Icon'
import Button from './Button'

export default function Navbar({ onToggleSidebar }) {
  const { user, logout } = useAuth()
  
  return (
    <header className="bg-white border-b border-neutral-200 shadow-soft">
      <div className="container-app h-16 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button 
            variant="ghost" 
            size="sm"
            icon="menu"
            onClick={onToggleSidebar}
            className="md:hidden"
          />
          <div className="flex items-center gap-3">
            <div className="p-2 bg-primary-600 rounded-lg">
              <Icon name="safety-solid" className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="font-bold text-lg text-neutral-900">SafeVisor</h1>
              <p className="text-xs text-neutral-600">Occupational Health & Safety</p>
            </div>
          </div>
        </div>
        
        <div className="flex items-center gap-4">
          {/* Notifications */}
          <button className="relative p-2 rounded-lg hover:bg-neutral-100 transition-colors">
            <Icon name="bell" className="w-5 h-5 text-neutral-600" />
            <span className="absolute -top-1 -right-1 w-3 h-3 bg-danger-500 rounded-full"></span>
          </button>
          
          {/* User menu */}
          <div className="flex items-center gap-3 px-3 py-2 rounded-lg bg-neutral-50">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center">
                <Icon name="user" className="w-5 h-5 text-primary-600" />
              </div>
              <div className="text-sm">
                <div className="font-medium text-neutral-900">{user?.name || 'User'}</div>
                <div className="flex items-center gap-2">
                  <span className="text-neutral-600">{user?.role?.name || user?.role || 'User'}</span>
                  {(user?.role?.name === 'Admin' || user?.role === 'Admin (IT)') && (
                    <span className="badge-primary text-xs">Admin</span>
                  )}
                </div>
              </div>
            </div>
          </div>
          
          <Button 
            variant="ghost" 
            size="sm"
            icon="logout"
            onClick={logout}
            className="text-neutral-600"
          >
            <span className="hidden sm:inline">Logout</span>
          </Button>
        </div>
      </div>
    </header>
  )
}
