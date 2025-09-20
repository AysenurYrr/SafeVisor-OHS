import React from 'react'
import { useAuth } from '../context/AuthContext'

export default function Navbar({ onToggleSidebar }) {
  const { user, logout } = useAuth()
  return (
    <header className="bg-white border-b border-gray-200">
      <div className="container-app h-14 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <button onClick={onToggleSidebar} className="btn btn-secondary px-3 py-1">☰</button>
          <span className="font-semibold">ISG - Occupational Safety</span>
        </div>
        <div className="flex items-center gap-3">
          <div className="text-sm text-gray-600">{user?.name} <span className="badge ml-2">{user?.role}</span></div>
          <button className="btn btn-secondary" onClick={logout}>Logout</button>
        </div>
      </div>
    </header>
  )
}
