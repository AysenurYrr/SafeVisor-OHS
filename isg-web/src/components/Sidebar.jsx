import React from 'react'
import { NavLink } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

function NavItem({ to, children }) {
  return (
    <NavLink
      to={to}
      className={({ isActive }) => `block px-4 py-2 rounded-md hover:bg-gray-100 ${isActive ? 'bg-gray-200 font-medium' : ''}`}
    >
      {children}
    </NavLink>
  )
}

export default function Sidebar({ open }) {
  const { user } = useAuth()
  const isAdmin = user?.role === 'Admin (IT)'

  return (
    <aside className={`bg-white border-r border-gray-200 ${open ? 'w-64' : 'w-16'} transition-all hidden md:block`}>
      <div className="h-14 border-b border-gray-200 flex items-center px-4 font-semibold">Menu</div>
      <nav className="p-3 space-y-1">
        <NavItem to="/dashboard">Dashboard</NavItem>
        <NavItem to="/employees">Employees</NavItem>
        <NavItem to="/cameras">Cameras</NavItem>
        <div className="px-4 mt-3 text-xs uppercase tracking-wide text-gray-500">Events</div>
        <NavItem to="/events/violations">PPE Violations</NavItem>
        <NavItem to="/events/pose">Pose Alerts</NavItem>
        {isAdmin && (
          <>
            <div className="px-4 mt-3 text-xs uppercase tracking-wide text-gray-500">Admin</div>
            <NavItem to="/admin/users">Users</NavItem>
          </>
        )}
      </nav>
    </aside>
  )
}
