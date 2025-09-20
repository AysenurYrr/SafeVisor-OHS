import React from 'react'
import { NavLink } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

function NavItem({ to, children, icon, open }) {
  return (
    <NavLink
      to={to}
      className={({ isActive }) => `
        flex items-center gap-3 px-4 py-2.5 rounded-lg text-sm font-medium transition-colors
        ${isActive 
          ? 'bg-blue-50 text-blue-700 border-l-4 border-blue-500' 
          : 'text-gray-700 hover:bg-gray-50 hover:text-gray-900'
        }
      `}
    >
      <span className="text-lg">{icon}</span>
      <span className={`${!open ? 'hidden' : ''}`}>{children}</span>
    </NavLink>
  )
}

function SectionHeader({ children, open }) {
  return (
    <div className={`px-4 py-2 text-xs font-semibold text-gray-500 uppercase tracking-wider ${!open ? 'text-center' : ''}`}>
      {open ? children : '•••'}
    </div>
  )
}

export default function Sidebar({ open }) {
  const { user } = useAuth()
  const isAdmin = user?.role === 'Admin (IT)'

  return (
    <aside className={`bg-white border-r border-gray-200 ${open ? 'w-64' : 'w-16'} transition-all duration-300 hidden md:block shadow-sm`}>
      <div className={`h-14 border-b border-gray-200 flex items-center px-4 font-bold text-gray-800 ${!open ? 'justify-center' : ''}`}>
        {open ? (
          <>
            <span className="text-blue-600 mr-2">🛡️</span>
            SafeVisor
          </>
        ) : (
          <span className="text-blue-600 text-xl">🛡️</span>
        )}
      </div>
      <nav className="p-3 space-y-1">
        <NavItem to="/dashboard" icon="📊" open={open}>Dashboard</NavItem>
        <NavItem to="/employees" icon="👥" open={open}>Employees</NavItem>
        <NavItem to="/cameras" icon="📹" open={open}>Cameras</NavItem>
        
        <SectionHeader open={open}>Events</SectionHeader>
        <NavItem to="/events/violations" icon="⚠️" open={open}>PPE Violations</NavItem>
        <NavItem to="/events/pose" icon="🏃" open={open}>Pose Alerts</NavItem>
        
        {isAdmin && (
          <>
            <SectionHeader open={open}>Admin</SectionHeader>
            <NavItem to="/admin/users" icon="⚙️" open={open}>Users</NavItem>
          </>
        )}
      </nav>
    </aside>
  )
}
